#!/usr/bin/env python3
"""Zero-residual reference execution: dynamics evidence, never policy promotion."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time
import traceback

from isaaclab.app import AppLauncher

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output",type=Path,required=True)
parser.add_argument("--replicas",type=int,default=2)
parser.add_argument("--seconds",type=float,default=20.)
parser.add_argument("--profile",type=Path)
parser.add_argument("--trace",action="store_true",help="Record per-foot samples for the first replica of seven basic commands")
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
if args.output.exists() or args.replicas<1 or args.seconds<=0:
    parser.error("New output, positive replicas/seconds required")
app=AppLauncher(args)

import gymnasium as gym
import numpy as np
import torch
import isaaclab.utils.math as math_utils
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reference import MotionReferenceEnvCfg, configure_reference
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_calibrated_cfg import MotionPostureEnvCfg
from csdog_motion.evaluation import default_cases,profile_at
from csdog_motion.reference_control import reference_contract
from csdog_motion.training import file_hash


def run():
    torch.set_num_threads(1)
    cases=default_cases("lateral_grid")
    cfg=MotionReferenceEnvCfg()
    if args.profile:
        configure_reference(cfg,json.loads(args.profile.read_text()))
    assert not cfg.training_enabled
    assert MotionPostureEnvCfg().motion_commands["nominal_height_m"]==.386, "Diagnostic mutated previous task"
    count=len(cases);n=count*args.replicas
    cfg.scene.num_envs=n;cfg.sim.device=args.device;cfg.seed=42
    cfg.periodic_commands=False
    cfg.episode_length_s=args.seconds+5
    cfg.command_ranges={key:(0.,0.) for key in cfg.command_ranges}
    env=gym.make("CSDog-Motion-Reference-Diagnostic-v0",cfg=cfg)
    raw=env.unwrapped
    try:
        obs,_=env.reset()
        assert obs["policy"].shape==(n,66)
        zero=torch.zeros(n,12,device=raw.device)
        sums=torch.zeros(count,3,device=raw.device);squared=torch.zeros_like(sums)
        samples=torch.zeros(count,device=raw.device)
        failure=torch.zeros(n,device=raw.device);first_failure=torch.full((n,),float("inf"),device=raw.device)
        height=torch.zeros(count,device=raw.device);tilt=torch.zeros_like(height)
        contacts_sum=torch.zeros(count,4,device=raw.device);agreement=torch.zeros_like(height)
        speed_limited=torch.zeros_like(height);finite=torch.ones(count,dtype=torch.bool,device=raw.device)
        violations=torch.zeros_like(height);saturation=torch.zeros_like(height)
        max_torque=torch.zeros_like(height);max_joint_velocity=torch.zeros_like(height)
        max_target_velocity=torch.zeros_like(height);reference_error=torch.zeros_like(height)
        previous_target=raw._robot.data.default_joint_pos[:,raw._actuated_joint_ids].clone()
        trace=[]
        max_fk_error=0.;warmup=2.
        steps=round((args.seconds+warmup)/raw.step_dt)
        started=time.monotonic()
        with torch.inference_mode():
            for step in range(steps):
                seconds=step*raw.step_dt-warmup
                requested=[profile_at(c["profile"],max(seconds,0.))[0] if seconds>=0 else [0.,0.,0.] for c in cases]
                request=torch.tensor(requested,device=raw.device).repeat_interleave(args.replicas,0)
                raw.set_motion_request(request)
                obs,reward,terminated,truncated,_=env.step(zero)
                failure+=terminated
                first_failure=torch.where(terminated&(first_failure==float("inf")),step*raw.step_dt,first_failure)
                robot=raw._robot.data
                q=robot.joint_pos[:,raw._actuated_joint_ids].reshape(n,4,3)
                if step in (0,100,500):
                    prediction,_=raw.reference_model.fk(q)
                    relative=robot.body_pos_w[:,raw._robot_foot_ids]-robot.root_pos_w[:,None]
                    quat=robot.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
                    actual=math_utils.quat_apply_inverse(quat,relative.reshape(-1,3)).reshape(n,4,3)
                    max_fk_error=max(max_fk_error,float(torch.linalg.vector_norm(prediction-actual,dim=-1).max()))
                finite&=(torch.isfinite(obs["policy"]).all(1)&torch.isfinite(q).all(dim=(1,2))&torch.isfinite(reward)).reshape(count,-1).all(1)
                target_speed=(raw._processed_actions-previous_target).abs()/raw.step_dt
                previous_target.copy_(raw._processed_actions)
                if terminated.any():
                    previous_target[terminated]=robot.default_joint_pos[terminated][:,raw._actuated_joint_ids]
                limits=robot.soft_joint_pos_limits[:,raw._actuated_joint_ids]
                violations+=((raw._processed_actions<limits[:,:,0]-1e-6)|(raw._processed_actions>limits[:,:,1]+1e-6)).reshape(count,-1).sum(1)
                reference_error=torch.maximum(reference_error,raw.reference_error.reshape(count,-1).amax(1))
                max_target_velocity=torch.maximum(max_target_velocity,target_speed.reshape(count,-1).amax(1))
                if seconds>=0:
                    velocity=torch.cat((robot.root_lin_vel_b[:,:2],robot.root_ang_vel_b[:,2:3]),dim=1)
                    sums+=velocity.reshape(count,args.replicas,3).sum(1)
                    squared+=(velocity-request).square().reshape(count,args.replicas,3).sum(1)
                    samples+=args.replicas
                    height+=(robot.root_pos_w[:,2]-raw._terrain.env_origins[:,2]).reshape(count,-1).sum(1)
                    tilt+=torch.acos((-robot.projected_gravity_b[:,2]).clamp(-1,1)).square().reshape(count,-1).sum(1)
                    contact=torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:,raw._foot_ids],dim=-1)>1.
                    contacts_sum+=contact.reshape(count,args.replicas,4).float().sum(1)
                    expected=raw.reference_stance | (raw.motion.blend[:,None]<1e-6)
                    agreement+=(contact==expected).reshape(count,args.replicas,4).float().mean(2).sum(1)
                    speed_limited+=raw.target_speed_limited.reshape(count,-1).sum(1)
                    torque=robot.applied_torque[:,raw._actuated_joint_ids].abs()
                    max_torque=torch.maximum(max_torque,torque.reshape(count,-1).amax(1))
                    saturation+=(torque>=11.99).reshape(count,args.replicas,12).float().mean(2).sum(1)
                    max_joint_velocity=torch.maximum(max_joint_velocity,robot.joint_vel[:,raw._actuated_joint_ids].abs().reshape(count,-1).amax(1))
                    if args.trace and step%2==0:
                        ids=torch.arange(7,device=raw.device)*args.replicas
                        relative=robot.body_pos_w[ids][:,raw._robot_foot_ids]-robot.root_pos_w[ids,None]
                        quat=robot.root_quat_w[ids,None].expand(-1,4,-1).reshape(-1,4)
                        foot_body=math_utils.quat_apply_inverse(quat,relative.reshape(-1,3)).reshape(7,4,3)
                        reference_foot,_=raw.reference_model.fk(raw.reference_q[ids].reshape(7,4,3))
                        trace.append({"seconds":seconds,"phase":raw.motion.phase[ids].cpu().numpy(),
                            "actual_foot_body":foot_body.cpu().numpy(),"reference_foot_body":reference_foot.cpu().numpy(),
                            "actual_foot_world_height":(robot.body_pos_w[ids][:,raw._robot_foot_ids,2]-raw._terrain.env_origins[ids,2:3]).cpu().numpy(),
                            "contact_force_world":raw._contact_sensor.data.net_forces_w[ids][:,raw._foot_ids].cpu().numpy(),
                            "scheduled_stance":raw.reference_stance[ids].cpu().numpy(),
                            "joint_position":q[ids].cpu().numpy(),"joint_target":raw._processed_actions[ids].reshape(7,4,3).cpu().numpy(),
                            "joint_torque":robot.applied_torque[ids][:,raw._actuated_joint_ids].reshape(7,4,3).cpu().numpy()})
                if step%250==0:
                    print("reference step",step,"/",steps,"unexpected terminations",int(failure.sum()),flush=True)
        result={"complete":True,"scope":"open-loop geometric reference, zero learned residual; nominal cloned resets, no robustness or policy-release claim",
                "task":"CSDog-Motion-Reference-Diagnostic-v0","policy_gradient_updates":0,"training_enabled":False,
                "motion_contract":cfg.motion_contract,"reference_parameters":cfg.reference_parameters,
                "warmup_seconds":warmup,"measured_seconds":args.seconds,
                "replicas_per_case":args.replicas,"loop_wall_seconds":time.monotonic()-started,
                "fk_vs_simulator_max_error_m":max_fk_error,"cases":[]}
        result["actuators"]={key:{field:getattr(a,field) for field in ("stiffness","damping","effort_limit_sim","velocity_limit_sim")} for key,a in cfg.robot.actuators.items()}
        for i,c in enumerate(cases):
            fs=first_failure.reshape(count,-1)[i].tolist()
            result["cases"].append({"name":c["name"],"profile":c["profile"],"finite":bool(finite[i]),
                "failures":int(failure.reshape(count,-1)[i].sum()),"first_failure_seconds":[x if x!=float("inf") else None for x in fs],
                "mean_actual_twist":(sums[i]/samples[i]).tolist(),"all_rmse":(squared[i]/samples[i]).sqrt().tolist(),
                "body_height_mean_m":float(height[i]/samples[i]),"body_tilt_rms_deg":float((tilt[i]/samples[i]).sqrt()*180/torch.pi),
                "foot_contact_duty_factor":(contacts_sum[i]/samples[i]).tolist(),"contact_schedule_agreement":float(agreement[i]/samples[i]),
                "target_speed_limited_fraction":float(speed_limited[i]/samples[i]),"target_limit_violations":int(violations[i]),
                "max_reference_ik_error_m":float(reference_error[i]),"peak_target_joint_velocity_rad_s":float(max_target_velocity[i]),
                "peak_actual_joint_velocity_rad_s":float(max_joint_velocity[i]),"peak_applied_torque_nm":float(max_torque[i]),
                "torque_saturation_fraction":float(saturation[i]/samples[i])})
        result["physical_screen"]="PASS" if all(c["finite"] and c["failures"]==0 and c["target_limit_violations"]==0 for c in result["cases"]) and max_fk_error<.0001 else "FAIL"
        result["source_files_sha256"]={str(p.relative_to(Path.cwd())):file_hash(p) for folder in ("source","scripts") for p in sorted(Path(folder).resolve().rglob("*.py"))}
        args.output.parent.mkdir(parents=True,exist_ok=True)
        if trace:
            trace_path=args.output.with_suffix(".trace.npz")
            np.savez_compressed(trace_path,**{key:np.array([x[key] for x in trace]) for key in trace[0]})
            result["trace"]={"path":str(trace_path.resolve()),"sha256":file_hash(trace_path),"cases":[c["name"] for c in cases[:7]],"period_s":raw.step_dt*2}
        args.output.write_text(json.dumps(result,indent=2)+"\n")
        print("Reference physical screen",result["physical_screen"])
        for c in result["cases"]:print(c["name"],"actual",[round(x,3) for x in c["mean_actual_twist"]],"tilt",round(c["body_tilt_rms_deg"],2),"failures",c["failures"])
    finally:
        env.close()


try:
    run()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
