"""Reusable inference metrics, copied without threshold changes from the residual launcher.

All cases and identities are supplied explicitly; different physics identities still
require an audited comparison rather than weakening the legacy contract checker.
"""
import json,time
import torch
from tensordict import TensorDict
from .evaluation import profile_at,protocol_hash
from .training import file_hash

def evaluate(env,policy,checkpoint,output,*,cases,seed=42,disturbance=False,protocol_name="adaptive_speed18",task="explicit_diagnostic_transfer"):
    raw=env.unwrapped;cfg=raw.cfg;n=raw.num_envs
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
            if disturbance and step==400:
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
    result={"complete":True,"task":task,"checkpoint":str(checkpoint.resolve()),"checkpoint_sha256":file_hash(checkpoint),
            "protocol_name":protocol_name,
            "protocol_sha256":protocol_hash(cases,1100,raw.step_dt,replicas,seed),
            "protocol_detail":{"warmup_s":2.,"measurement_s":20.,"steady_exclusion_s":1.,"clones_not_independent_trials":True},
            "physics_contract":{"motion_contract":cfg.motion_contract,"urdf_sha256":file_hash(cfg.robot.spawn.asset_path),
                "physics_dt":cfg.sim.dt,"decimation":cfg.decimation,"soft_joint_factor":cfg.robot.soft_joint_pos_limit_factor,
                "actuators":{k:{f:getattr(a,f) for f in ("stiffness","damping","effort_limit_sim","velocity_limit_sim")} for k,a in cfg.robot.actuators.items()}},
            "loop_wall_seconds":time.monotonic()-began,"cases":[]}
    if disturbance:
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

