#!/usr/bin/env python3
"""Fresh residual-policy development, with in-process deterministic screening.

This launcher is intentionally separate from legacy checkpoint refinement.
No policy from the old MDP is loaded. All final-use decisions remain gated.
"""
import argparse
import copy
import json
from pathlib import Path
import random
import time
import traceback
from isaaclab.app import AppLauncher

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output",type=Path,required=True)
parser.add_argument("--num-envs",type=int,default=256)
parser.add_argument("--max-updates",type=int,default=100)
parser.add_argument("--segment",type=int,default=25)
parser.add_argument("--seed",type=int,default=42)
parser.add_argument("--stage",choices=("low","full","speed","style","clean","transfer","backward"),default="low")
parser.add_argument("--initialize-from",type=Path,help="Explicit low-to-full weights-only transfer; optimizer is new")
parser.add_argument("--evaluate",type=Path)
parser.add_argument("--full-commands",action="store_true")
parser.add_argument("--speed-commands",action="store_true")
parser.add_argument("--holdout",action="store_true")
parser.add_argument("--backward-holdout",action="store_true")
parser.add_argument("--disturbance",action="store_true",help="At6s add opposite-sign root velocity offsets to the evaluation replicas")
AppLauncher.add_app_launcher_args(parser)
args=parser.parse_args()
if args.output.exists() or args.num_envs<18 or args.max_updates<0 or args.segment<1:
    parser.error("New output directory, at least18 environments, nonnegative updates and positive segment required")
if (args.full_commands or args.speed_commands or args.holdout or args.backward_holdout or args.disturbance) and args.evaluate is None:
    parser.error("Full/holdout/disturbance protocols are evaluation-only")
if sum((args.full_commands,args.speed_commands,args.holdout,args.backward_holdout))>1:parser.error("Select one evaluation protocol")
if args.initialize_from and (args.stage not in ("full","speed","style","clean","transfer","backward") or args.evaluate):parser.error("Initialization is only for new full-stage training")
if args.stage in ("full","speed","style","clean","transfer","backward") and not (args.initialize_from or args.evaluate):parser.error("Full stage requires an explicit low-stage parent or evaluation checkpoint")
app=AppLauncher(args)

import gymnasium as gym
import numpy as np
import torch
from tensordict import TensorDict
from rsl_rl.runners import OnPolicyRunner
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_residual import MotionResidualEnvCfg,MotionResidualFullEnvCfg,MotionResidualSpeedEnvCfg,MotionResidualStyleEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_clean import MotionCleanEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_transfer import MotionTransferEnvCfg,MotionBackwardEnvCfg
from csdog_motion.residual_learning import low_command_cases,holdout_cases
from csdog_motion.speed_learning import speed_cases
from csdog_motion.backward_validation import backward_holdout_cases
from csdog_motion.evaluation import default_cases,profile_at,protocol_hash,regression_gate
from csdog_motion.training import install_checkpoint_records,bound_learning_rate,file_hash,validate_checkpoint

TASK={"low":"CSDog-Motion-Residual-Low-Direct-v0","full":"CSDog-Motion-Residual-Full-Direct-v0","speed":"CSDog-Motion-Residual-Speed-Direct-v0","style":"CSDog-Motion-Residual-Style-Direct-v0","clean":"CSDog-Motion-Clean-Direct-v0","transfer":"CSDog-Motion-Transfer-Direct-v0","backward":"CSDog-Motion-Backward-Direct-v0"}[args.stage]


def evaluate(env,policy,checkpoint,output,full=False,speed_protocol=False):
    raw=env.unwrapped;cfg=raw.cfg;n=raw.num_envs
    cases=backward_holdout_cases() if args.backward_holdout else (speed_cases() if speed_protocol else (holdout_cases() if args.holdout else (default_cases("lateral_grid") if full else low_command_cases())))
    replicas=min(8,n//len(cases));used=replicas*len(cases);count=len(cases)
    cfg.periodic_commands=False;raw._external_commands=True
    with torch.inference_mode():
        obs,_=env.reset()
    policy.eval()
    sums=torch.zeros(count,3,device=raw.device);square=torch.zeros_like(sums);steady=torch.zeros_like(sums)
    steady_count=torch.zeros(count,device=raw.device);samples=0
    failures=torch.zeros(count,device=raw.device);valid=torch.ones(count,dtype=torch.bool,device=raw.device)
    height=torch.zeros(count,device=raw.device);height2=torch.zeros_like(height);tilt2=torch.zeros_like(height)
    change2=torch.zeros_like(height);clip=torch.zeros_like(height);boxclip=torch.zeros_like(height);rateclip=torch.zeros_like(height)
    limits_count=torch.zeros_like(height);slide=torch.zeros_like(height);contact_count=torch.zeros_like(height)
    duty=torch.zeros(count,4,device=raw.device);peak_speed=torch.zeros_like(height)
    max_torque=torch.zeros_like(height);error_ik=torch.zeros_like(height)
    contact_agreement=torch.zeros_like(height);foot_error=torch.zeros(count,4,device=raw.device)
    swing_contact=torch.zeros_like(foot_error);swing_count=torch.zeros_like(foot_error)
    began=time.monotonic()
    with torch.inference_mode():
        for step in range(1100):
            seconds=step*raw.step_dt-2.
            commands,ages=zip(*(profile_at(c["profile"],max(seconds,0)) for c in cases))
            requested=torch.zeros(n,3,device=raw.device)
            if seconds>=0:requested[:used]=torch.tensor(commands,device=raw.device).repeat_interleave(replicas,0)
            raw.set_motion_request(requested)
            if args.disturbance and step==400:
                velocity=raw._robot.data.root_vel_w.clone()
                sign=torch.where(torch.arange(n,device=raw.device)%2==0,1.,-1.)
                velocity[:,0]+=.05*sign;velocity[:,1]-=.04*sign;velocity[:,5]+=.08*sign
                raw._robot.write_root_velocity_to_sim(velocity)
                obs=raw._get_observations()
            action=policy.act_inference(TensorDict(obs,batch_size=[n]))
            executed_blend=raw.motion.blend[:used].clone()
            obs,reward,terminated,truncated,_=env.step(action)
            failures+=terminated[:used].reshape(count,replicas).sum(1)
            valid&=(torch.isfinite(obs["policy"][:used]).all(1)&torch.isfinite(reward[:used])).reshape(count,replicas).all(1)
            robot=raw._robot.data
            limits=robot.soft_joint_pos_limits[:,raw._actuated_joint_ids]
            outside=(raw._processed_actions<limits[:,:,0]-1e-6)|(raw._processed_actions>limits[:,:,1]+1e-6)
            limits_count+=outside[:used].reshape(count,-1).sum(1)
            speed=raw._processed_velocity_targets[:used].abs().reshape(count,-1).amax(1)
            peak_speed=torch.maximum(peak_speed,speed)
            error_ik=torch.maximum(error_ik,raw.reference_error[:used].reshape(count,-1).amax(1))
            if seconds<0:continue
            actual=torch.cat((robot.root_lin_vel_b[:,:2],robot.root_ang_vel_b[:,2:3]),dim=1)[:used]
            error=(actual-requested[:used]).reshape(count,replicas,3)
            sums+=actual.reshape(count,replicas,3).sum(1);square+=error.square().sum(1);samples+=replicas
            stable=torch.tensor(ages,device=raw.device)>=1.
            steady+=error.square().sum(1)*stable[:,None];steady_count+=stable*replicas
            h=(robot.root_pos_w[:,2]-raw._terrain.env_origins[:,2])[:used].reshape(count,replicas)
            height+=h.sum(1);height2+=h.square().sum(1)
            angle=torch.acos((-robot.projected_gravity_b[:used,2]).clamp(-1,1))
            tilt2+=angle.square().reshape(count,replicas).sum(1)
            change=((raw._processed_actions-raw.previous_joint_targets)/cfg.action_scale)[:used]
            change2+=change.square().reshape(count,replicas,12).mean(2).sum(1)
            clip+=(action[:used].abs()>=1.).reshape(count,replicas,12).float().mean(2).sum(1)
            boxclip+=raw.target_box_limited[:used].reshape(count,replicas,12).float().mean(2).sum(1)
            rateclip+=raw.target_speed_limited[:used].reshape(count,replicas).sum(1)
            forces=torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:used,raw._foot_ids],dim=-1)
            contact=forces>1.
            duty+=contact.float().reshape(count,replicas,4).sum(1)
            vfoot=torch.linalg.vector_norm(robot.body_lin_vel_w[:used,raw._robot_foot_ids,:2],dim=-1)
            slide+=(vfoot*contact).reshape(count,-1).sum(1);contact_count+=contact.reshape(count,-1).sum(1)
            max_torque=torch.maximum(max_torque,robot.applied_torque[:used,raw._actuated_joint_ids].abs().reshape(count,-1).amax(1))
            desired_contact=1-(~raw.reference_stance[:used]).float()*executed_blend[:,None]
            contact_agreement+=(1-(contact.float()-desired_contact).abs()).reshape(count,replicas,4).mean(2).sum(1)
            swing=(~raw.reference_stance[:used])&(executed_blend[:,None]>.95)
            swing_contact+=(contact&swing).reshape(count,replicas,4).sum(1)
            swing_count+=swing.reshape(count,replicas,4).sum(1)
            from isaaclab.utils.math import quat_apply_inverse
            q=robot.root_quat_w[:used,None].expand(-1,4,-1).reshape(-1,4)
            relative=robot.body_pos_w[:used,raw._robot_foot_ids]-robot.root_pos_w[:used,None]
            foot_body=quat_apply_inverse(q,relative.reshape(-1,3)).reshape(used,4,3)
            reference_foot,_=raw.reference_model.fk(raw.reference_q[:used].reshape(-1,4,3))
            foot_error+=(foot_body-reference_foot).square().sum(2).reshape(count,replicas,4).sum(1)
    result={"complete":True,"task":TASK,"checkpoint":str(checkpoint.resolve()),"checkpoint_sha256":file_hash(checkpoint),
            "protocol_name":"backward_holdout18" if args.backward_holdout else "residual_axis_speed18" if speed_protocol else "residual_holdout18" if args.holdout else ("residual_full18" if full else "residual_low18"),
            "protocol_sha256":protocol_hash(cases,1100,raw.step_dt,replicas,args.seed),
            "protocol_detail":{"warmup_s":2.,"measurement_s":20.,"steady_exclusion_s":1.,"clones_not_independent_trials":True},
            "physics_contract":{"motion_contract":cfg.motion_contract,"urdf_sha256":file_hash(cfg.robot.spawn.asset_path),
                "physics_dt":cfg.sim.dt,"decimation":cfg.decimation,"soft_joint_factor":cfg.robot.soft_joint_pos_limit_factor,
                "actuators":{k:{f:getattr(a,f) for f in ("stiffness","damping","effort_limit_sim","velocity_limit_sim")} for k,a in cfg.robot.actuators.items()}},
            "loop_wall_seconds":time.monotonic()-began,"cases":[]}
    if args.disturbance:
        result["disturbance"]={"measurement_seconds":6.,"root_velocity_world_offset":[.05,-.04,0.,0.,0.,.08],"replica_signs":"alternating +/-; controlled counterfactual, not random robustness estimation"}
        result["protocol_sha256"]=__import__("hashlib").sha256((result["protocol_sha256"]+json.dumps(result["disturbance"],sort_keys=True)).encode()).hexdigest()
    for i,case in enumerate(cases):
        result["cases"].append({"name":case["name"],"protected":case["protected"],"profile":case["profile"],"finite":bool(valid[i]),
            "failures":int(failures[i]),"mean_actual_twist":(sums[i]/samples).tolist(),"all_rmse":(square[i]/samples).sqrt().tolist(),
            "steady_rmse":(steady[i]/steady_count[i].clamp_min(1)).sqrt().tolist(),"steady_samples":int(steady_count[i]),
            "body_height_mean_m":float(height[i]/samples),"body_height_std_m":float((height2[i]/samples-(height[i]/samples).square()).clamp_min(0).sqrt()),
            "body_tilt_rms_deg":float((tilt2[i]/samples).sqrt()*180/torch.pi),"action_change_rms_per_step":float((change2[i]/samples).sqrt()),
            "action_clip_fraction":float(clip[i]/samples),"total_target_box_clip_fraction":float(boxclip[i]/samples),
            "target_rate_limited_fraction":float(rateclip[i]/samples),"target_limit_violations":int(limits_count[i]),
            "foot_contact_duty_factor":(duty[i]/samples).tolist(),"contact_slide_speed_proxy_mps":float(slide[i]/contact_count[i].clamp_min(1)),
            "contact_schedule_agreement":float(contact_agreement[i]/samples),
            "foot_reference_tracking_rms_m":(foot_error[i]/samples).sqrt().tolist(),
            "planned_swing_contact_fraction":(swing_contact[i]/swing_count[i].clamp_min(1)).tolist(),
            "peak_target_velocity_rad_s":float(peak_speed[i]),"peak_applied_torque_nm":float(max_torque[i]),"max_ik_error_m":float(error_ik[i])})
    reasons=[]
    for c in result["cases"]:
        if not c["finite"] or c["failures"] or c["target_limit_violations"]:reasons.append(c["name"]+":finite_failure_limit")
        if c["body_tilt_rms_deg"]>10 or abs(c["body_height_mean_m"]-cfg.base_height_target)>.04:reasons.append(c["name"]+":posture")
        if c["peak_target_velocity_rad_s"]>8.0001 or c["max_ik_error_m"]>.001:reasons.append(c["name"]+":reference_target")
        if c["action_clip_fraction"]>.2 or c["total_target_box_clip_fraction"]>.1 or c["target_rate_limited_fraction"]>.2:reasons.append(c["name"]+":clipping")
        if c["name"]=="stand" and any(abs(x)>t for x,t in zip(c["mean_actual_twist"],[.01,.01,.02])):reasons.append("stand:drift")
    result["development_safety_gate"]={"status":"FAIL" if reasons else "PASS","reasons":reasons,
        "meaning":"development stability only; does not certify velocity tracking or legacy-skill preservation"}
    output.write_text(json.dumps(result,indent=2)+"\n")
    print("[RESIDUAL]",output.name,result["development_safety_gate"],flush=True)
    for c in result["cases"][:7]:print(c["name"],[round(x,3) for x in c["mean_actual_twist"]],flush=True)
    cfg.periodic_commands=True;raw._external_commands=False
    with torch.inference_mode():
        env.reset()
    raw.extras["log"]={}
    return result


def main():
    torch.set_num_threads(1);random.seed(args.seed);np.random.seed(args.seed);torch.manual_seed(args.seed)
    cfg={"low":MotionResidualEnvCfg,"full":MotionResidualFullEnvCfg,"speed":MotionResidualSpeedEnvCfg,"style":MotionResidualStyleEnvCfg,"clean":MotionCleanEnvCfg,"transfer":MotionTransferEnvCfg,"backward":MotionBackwardEnvCfg}[args.stage]()
    assert cfg.residual_training_enabled and not cfg.training_enabled
    cfg.scene.num_envs=args.num_envs;cfg.sim.device=args.device;cfg.seed=args.seed;cfg.episode_length_s=30.
    args.output.mkdir(parents=True)
    cfg.robot.spawn.usd_dir=str((args.output/"converted_asset").resolve())
    agent={"num_steps_per_env":64,"save_interval":25,"logger":"tensorboard","obs_groups":{"policy":["policy"],"critic":["policy"]},
        "policy":{"class_name":"ActorCritic","init_noise_std":.25,"actor_obs_normalization":False,"critic_obs_normalization":False,
                  "actor_hidden_dims":[256,256,128],"critic_hidden_dims":[256,256,128],"activation":"elu"},
        "algorithm":{"class_name":"PPO","value_loss_coef":1.,"use_clipped_value_loss":True,"clip_param":.2,
            "entropy_coef":.003,"num_learning_epochs":5,"num_mini_batches":4,"learning_rate":1e-4,"schedule":"fixed",
            "gamma":.99,"lam":.95,"desired_kl":.01,"max_grad_norm":1.}}
    env=gym.make(TASK,cfg=cfg)
    wrapped=RslRlVecEnvWrapper(env,clip_actions=None)
    runner=OnPolicyRunner(wrapped,copy.deepcopy(agent),log_dir=str(args.output),device=args.device)
    runner.logger_type="tensorboard"
    if args.evaluate:
        validate_checkpoint(args.evaluate,cfg,policy_only=True)
        assert file_hash(args.evaluate)==json.loads(Path(str(args.evaluate)+".metadata.json").read_text())["checkpoint_sha256"]
        runner.load(str(args.evaluate),load_optimizer=False,map_location=args.device)
        evaluate(env,runner.alg.policy,args.evaluate,args.output/"evaluation.json",full=args.full_commands,speed_protocol=args.speed_commands)
        env.close();return
    if args.initialize_from:
        parent_cfg=MotionCleanEnvCfg() if args.stage in ("transfer","backward") else (MotionResidualSpeedEnvCfg() if args.stage in ("style","clean") else (MotionResidualFullEnvCfg() if args.stage=="speed" else MotionResidualEnvCfg()))
        parent_metadata=validate_checkpoint(args.initialize_from,parent_cfg,policy_only=True)
        assert parent_metadata["checkpoint_sha256"]==file_hash(args.initialize_from)
        old=copy.deepcopy(parent_cfg.motion_contract);new=copy.deepcopy(cfg.motion_contract)
        if args.stage in ("transfer","backward"):
            from csdog_motion.support_transfer import TRANSITION,BACKWARD_TRANSITION
            expected=BACKWARD_TRANSITION if args.stage=="backward" else TRANSITION
            assert new["support_feedback"].pop("transition")==expected
            new.pop("support_transition_scope")
        for value in (old,new):
            for key in ("schema_version","compatibility_tag","training_command_ranges","training_replay","command_envelope","learning_reward_scales","reference_lift_policy"):value.pop(key,None)
        assert old==new,"Transfer changed policy control/observation semantics"
        state=torch.load(args.initialize_from,map_location=args.device,weights_only=True)["model_state_dict"]
        runner.alg.policy.load_state_dict(state)
        assert all(torch.equal(v,state[k]) for k,v in runner.alg.policy.state_dict().items())
    else:
        with torch.no_grad():
            runner.alg.policy.actor[-1].weight.zero_();runner.alg.policy.actor[-1].bias.zero_()
        assert runner.alg.policy.act_inference(wrapped.get_observations()).abs().max()==0
    lr_audit,_=bound_learning_rate(runner.alg,1e-4,1e-4)
    semantics="explicit development-stage transfer of bitwise-equal policy/value tensors; optimizer fresh; sampling/reward/reference-controller changes explicitly recorded in contracts/manifest; RNG/physical state not restored" if args.initialize_from else "fresh actor/critic and optimizer; actor output layer zeroed for exact zero-mean residual; no prior checkpoint loaded; RNG recorded, not physical-state continuation"
    counts=install_checkpoint_records(runner,cfg,TASK,lr_audit=lr_audit,parent=args.initialize_from,resume_semantics=semantics)
    manifest={"task":TASK,"stage":args.stage,"seed":args.seed,"fresh_initialization":args.initialize_from is None,
        "parent_checkpoint":str(args.initialize_from) if args.initialize_from else None,"parent_sha256":file_hash(args.initialize_from) if args.initialize_from else None,
        "optimizer":"new Adam","agent":agent,
        "maximum_updates":args.max_updates,"segment_updates":args.segment,"num_envs":args.num_envs,"command_ranges":cfg.command_ranges,
        "reward_scales":cfg.reward_scales,"parent_reward_scales":parent_cfg.reward_scales if args.initialize_from else None,"motion_contract":cfg.motion_contract,"evaluations":[],"status":"RUNNING"}
    manifest_path=args.output/"experiment.json"
    def record():manifest_path.write_text(json.dumps(manifest,indent=2)+"\n")
    record()
    initial=args.output/"initial.pt";runner.save(str(initial))
    reference=evaluate(env,runner.alg.policy,initial,args.output/"validation_0000.json")
    manifest["evaluations"].append({"updates":0,"report":"validation_0000.json","checkpoint":"initial.pt","gate":reference["development_safety_gate"]});record()
    if reference["development_safety_gate"]["status"]!="PASS":
        manifest["status"]="INITIALIZATION_REJECTED";record();env.close();return
    full_reference=None
    if args.stage in ("full","speed","style","clean","transfer","backward"):
        full_reference=evaluate(env,runner.alg.policy,initial,args.output/"full_validation_0000.json",full=True)
        if full_reference["development_safety_gate"]["status"]!="PASS":
            manifest["status"]="FULL_INITIALIZATION_REJECTED";record();env.close();return
    speed_reference=None
    if args.stage in ("speed","style","clean","transfer","backward"):
        speed_reference=evaluate(env,runner.alg.policy,initial,args.output/"speed_validation_0000.json",speed_protocol=True)
        if speed_reference["development_safety_gate"]["status"]!="PASS":
            manifest["status"]="SPEED_INITIALIZATION_REJECTED";record();env.close();return
    while counts["updates_in_this_run"]<args.max_updates:
        amount=min(args.segment,args.max_updates-counts["updates_in_this_run"])
        runner.learn(amount,init_at_random_ep_len=False)
        done=counts["updates_in_this_run"]
        checkpoint=args.output/f"segment_{done:04d}.pt";runner.save(str(checkpoint))
        report_path=args.output/f"validation_{done:04d}.json"
        report=evaluate(env,runner.alg.policy,checkpoint,report_path)
        comparison_key="regression_vs_transferred_parent" if args.stage in ("full","speed","style","clean","transfer","backward") else "regression_vs_zero_residual"
        comparison=regression_gate(report,reference)
        report[comparison_key]=comparison
        report_path.write_text(json.dumps(report,indent=2)+"\n")
        manifest["evaluations"].append({"updates":done,"report":report_path.name,"checkpoint":checkpoint.name,"gate":report["development_safety_gate"],"regression":comparison})
        if report["development_safety_gate"]["status"]!="PASS":
            manifest["status"]="STOPPED_DEVELOPMENT_SAFETY_REJECTED";record();break
        if args.stage in ("full","speed","style","clean","transfer","backward") and comparison["status"]!="PASS":
            manifest["status"]="STOPPED_LOW_REGRESSION_REJECTED";record();break
        if args.stage in ("full","speed","style","clean","transfer","backward"):
            full_path=args.output/f"full_validation_{done:04d}.json"
            full=evaluate(env,runner.alg.policy,checkpoint,full_path,full=True)
            full["regression_vs_transferred_parent"]=regression_gate(full,full_reference)
            full_path.write_text(json.dumps(full,indent=2)+"\n")
            manifest["evaluations"][-1]["full_report"]=full_path.name
            if full["development_safety_gate"]["status"]!="PASS" or full["regression_vs_transferred_parent"]["status"]!="PASS":
                manifest["status"]="STOPPED_FULL_REGRESSION_REJECTED";record();break
        if args.stage in ("speed","style","clean","transfer","backward"):
            speed_path=args.output/f"speed_validation_{done:04d}.json"
            speed_report=evaluate(env,runner.alg.policy,checkpoint,speed_path,speed_protocol=True)
            speed_report["regression_vs_transferred_parent"]=regression_gate(speed_report,speed_reference)
            speed_path.write_text(json.dumps(speed_report,indent=2)+"\n")
            manifest["evaluations"][-1]["speed_report"]=speed_path.name
            if speed_report["development_safety_gate"]["status"]!="PASS":
                manifest["status"]="STOPPED_SPEED_SAFETY_REJECTED";record();break
        record()
    if counts["updates_in_this_run"]==args.max_updates and manifest["status"]=="RUNNING":manifest["status"]="DEVELOPMENT_BUDGET_COMPLETED"
    manifest["completed_updates"]=counts["updates_in_this_run"];manifest["learning_rate_audit"]=lr_audit
    manifest["decision"]="NO_AUTOMATIC_PROMOTION";record();env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
