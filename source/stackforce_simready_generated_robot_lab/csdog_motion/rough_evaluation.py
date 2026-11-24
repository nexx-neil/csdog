"""Fixed multi-direction terrain tests without route-following feedback."""
import json,time,math
from pathlib import Path
import torch,numpy as np
from tensordict import TensorDict
from isaaclab.utils.math import quat_apply_inverse
from .training import file_hash
KINDS=['flat_a','flat_b','slope_up','slope_down','stairs_up','stairs_down','boxes','rough']
DIRECTIONS=['forward','backward','left','right','advance_then_turn']

def evaluate(env,policy,checkpoint,output,steps=750):
    n=env.num_envs;assert n%40==0
    oldperiodic=env.cfg.periodic_commands;env.cfg.periodic_commands=False;env._external_commands=True
    with torch.inference_mode():obs,_=env.reset()
    policy.eval();failure=torch.zeros(n,device=env.device);clip=torch.zeros_like(failure);rate=torch.zeros_like(failure);peakq=torch.zeros_like(failure);peake=torch.zeros_like(failure);finite=torch.ones(n,dtype=torch.bool,device=env.device)
    trace=[];clock_ok=True;start=time.monotonic();dirs=(torch.arange(n,device=env.device)//8)%5
    with torch.inference_mode():
        for step in range(steps):
            t=step*.02;cmd=torch.zeros(n,3,device=env.device)
            if 2<=t<12:
                cmd[dirs==0,0]=.2;cmd[dirs==1,0]=-.2;cmd[dirs==2,1]=.18;cmd[dirs==3,1]=-.18
            if 2<=t<10:cmd[dirs==4,0]=.2
            if 10<=t<13:cmd[dirs==4,2]=.3
            env.set_motion_request(cmd);act=policy.act_inference(TensorDict(obs,batch_size=[n]));obs,rew,term,trunc,_=env.step(act)
            r=env._robot.data;failure+=term;finite&=torch.isfinite(obs['policy']).all(1)&torch.isfinite(rew);clip+=env.target_box_limited.float().mean(1);rate+=env.target_speed_limited.float();peakq=torch.maximum(peakq,env._processed_velocity_targets.abs().amax(1));peake=torch.maximum(peake,env.reference_error.amax(1))
            if step%250==0:
                before=[env.motion.phase.clone(),env.motion.command_age.clone(),env.yaw_control.integral.clone()]
                for _ in range(3):env._get_observations()
                clock_ok &= all(torch.equal(x,y) for x,y in zip(before,[env.motion.phase,env.motion.command_age,env.yaw_control.integral]))
            if step%5==0:
                w,x,y,z=r.root_quat_w.unbind(-1);yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z));scan=env.height_scanner.data.ray_hits_w[:,:,2]
                quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4);body=quat_apply_inverse(quat,(r.body_pos_w[:,env._robot_foot_ids]-r.root_pos_w[:,None]).reshape(-1,3)).reshape(-1,4,3);ref,_=env.reference_model.fk(env.reference_q.reshape(-1,4,3));ferror=(body-ref).square().sum(2).mean(1);contact=torch.linalg.vector_norm(env._contact_sensor.data.net_forces_w[:,env._foot_ids],dim=-1)>1.;slide=(torch.linalg.vector_norm(r.body_lin_vel_w[:,env._robot_foot_ids,:2],dim=-1)*contact).sum(1)/contact.sum(1).clamp_min(1)
                trace.append({'foot_error_mean_square_m2':ferror.cpu().tolist(),'contact_slide_proxy_mps':slide.cpu().tolist(),'seconds':(step+1)*.02,'position':(r.root_pos_w-env._terrain.env_origins).cpu().tolist(),'ground_height_w':env._surfaces()[:,0].cpu().tolist(),'support_height':env._support_height().cpu().tolist(),'tilt_deg':(torch.acos((-r.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi).cpu().tolist(),'yaw':yaw.cpu().tolist(),'command':cmd.cpu().tolist(),'twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1).cpu().tolist(),'scan_height_range_m':(scan.amax(1)-scan.amin(1)).cpu().tolist()})
            if step%250==0:print('rough evaluate',step,'terminations',int(failure.sum()),flush=True)
    pos=np.array([r['position'] for r in trace]);height=np.array([r['support_height'] for r in trace]);tilt=np.array([r['tilt_deg'] for r in trace]);twist=np.array([r['twist'] for r in trace]);commands=np.array([r['command'] for r in trace]);yaw=np.unwrap(np.array([r['yaw'] for r in trace]),axis=0);times=np.array([r['seconds'] for r in trace]);rows=[]
    for case in range(40):
        ids=np.arange(case,n,40);direction=case//8;kind=KINDS[case%8];axis=1 if direction in (2,3) else 0;sgn=-1 if direction in (1,3) else 1
        progress=sgn*(pos[-1,ids,axis]-pos[0,ids,axis]);other=1-axis;cross=float(np.abs(pos[:,ids,other]-pos[0,ids,other]).max());yr=float((yaw[times>=12.9][0,ids]-yaw[times>=10][0,ids]).mean()) if times[-1]>=12.9 else 0.
        mask=(times>=3)&(times<9) if direction==4 else (times>=3)&(times<12)
        steady_rmse=np.sqrt(np.square(twist[mask][:,ids]-commands[mask][:,ids]).mean((0,1))) if mask.any() else np.zeros(3)
        foot_error=np.array([v['foot_error_mean_square_m2'] for v in trace]);slides=np.array([v['contact_slide_proxy_mps'] for v in trace])
        row={'foot_reference_rms_m':float(np.sqrt(foot_error[mask][:,ids].mean())) if mask.any() else 0.,'contact_slide_proxy_mps':float(slides[mask][:,ids].mean()) if mask.any() else 0.,'steady_rmse':steady_rmse.tolist(),'surface_height_change_m':float(np.array(trace[-1]['ground_height_w'])[ids].mean()-np.array(trace[0]['ground_height_w'])[ids].mean()),'name':kind+'_'+DIRECTIONS[direction],'kind':kind,'direction':DIRECTIONS[direction],'failures':int(failure[ids].sum()),'finite':bool(finite[ids].all()),'progress_m':progress.tolist(),'max_cross_track_m':cross,'mean_relative_height_m':float(height[:,ids].mean()),'minimum_relative_height_m':float(height[:,ids].min()),'tilt_rms_deg':float(np.sqrt(np.square(tilt[:,ids]).mean())),'peak_tilt_deg':float(tilt[:,ids].max()),'peak_target_qspeed_rad_s':float(peakq[ids].max()),'max_ik_error_m':float(peake[ids].max()),'target_box_clip_fraction':float(clip[ids].mean()/steps),'target_rate_clip_fraction':float(rate[ids].mean()/steps),'turn_10to13s_rad':yr}
        progress_gate=bool((progress>({0:1.3,1:1.3,2:1.17,3:1.17,4:1.04}[direction])).all()) if steps==750 else True
        ok=row['finite'] and not row['failures'] and progress_gate and cross<.4 and abs(row['mean_relative_height_m']-env.cfg.base_height_target)<.04 and row['minimum_relative_height_m']>.25 and row['tilt_rms_deg']<10 and row['peak_tilt_deg']<20 and row['peak_target_qspeed_rad_s']<=8.0001 and row['max_ik_error_m']<.001 and row['target_box_clip_fraction']<.1 and row['target_rate_clip_fraction']<.2 and (direction!=4 or steps<750 or yr>.6)
        row['gate']='PASS' if ok else 'FAIL';rows.append(row)
    result={'complete':True,'steps':steps,'gate':'PASS' if clock_ok and all(r['gate']=='PASS' for r in rows) else 'FAIL','observation_reads_do_not_advance_clocks':clock_ok,'physics_contract':{'urdf_sha256':file_hash(env.cfg.robot.spawn.asset_path),'physics_dt':env.cfg.sim.dt,'decimation':env.cfg.decimation,'actuators':{k:{f:getattr(v,f) for f in ('stiffness','damping','effort_limit_sim','velocity_limit_sim')} for k,v in env.cfg.robot.actuators.items()}},'checkpoint_sha256':file_hash(checkpoint),'motion_contract':env.cfg.motion_contract,'terrain_row':env.cfg.terrain_row,'terrain_seed':env.cfg.terrain.terrain_generator.seed,'clones_per_case':n//40,'scope':'Actual generated terrain, noiseless simulation rays, pure velocity commands; no analytic course/path feedback. Nominal clones, not general robustness proof.','wall_seconds':time.monotonic()-start,'cases':rows,'trace':trace};Path(output).write_text(json.dumps(result,indent=2)+'\n');print('Rough gate',result['gate'],flush=True)
    for row in rows:
        if row['gate']!='PASS':print('FAIL',row,flush=True)
    env.cfg.periodic_commands=oldperiodic;env._external_commands=False
    with torch.inference_mode():env.reset()
    env.extras['log']={}
    return result
