#!/usr/bin/env python3
"""Composed trot/quick crouch tests, including a moving0.8m/s trigger."""
import argparse,json,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=('clean','backward','responsive','agile','yaw'),default='yaw');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--fast-commands',action='store_true');p.add_argument('--legacy',action='store_true')
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists():p.error('New output required')
app=AppLauncher(a)
import numpy as np,torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import gymnasium as gym
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_clean import MotionCleanEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_skills import MotionSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_transfer import MotionBackwardEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_skills import MotionBackwardSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_responsive_skills import MotionResponsiveSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_agile_skills import MotionAgileSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg,MotionYawSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_quick_crouch import MotionQuickCrouchEnvCfg,MotionQuickCrouchEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawSkillsEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_bounded_skills import MotionBoundedSkillsEnvCfg,MotionBoundedSkillsEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_bounded import MotionTrotBoundedEnvCfg
from csdog_motion.skill_supervisor import SkillMode
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.trot_flight_policy import compose,record

NAMES=['forward_crouch_resume','lateral_crouch_turn','interrupt_lower_to_move','repeat_crouch_rise','crouch_balance','ordinary_combination']
REPLICAS=3

def main():
 torch.set_num_threads(1)
 tag=json.loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag']
 parent=MotionTrotBoundedEnvCfg();assert tag==parent.checkpoint_compatibility_tag
 metadata=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert metadata['checkpoint_sha256']==file_hash(a.checkpoint)
 cfg=MotionBoundedSkillsEnvCfg();route=record(Path('outputs/motion_foundation/lesson20_candidate/candidate.pt'))
 if route is not None:cfg.motion_contract=dict(cfg.motion_contract,policy_routing=route)
 assert not cfg.training_enabled and not cfg.residual_training_enabled
 cfg.scene.num_envs=18;cfg.sim.device=a.device;cfg.seed=713;cfg.episode_length_s=30.
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/"converted_asset").resolve());env=MotionBoundedSkillsEnv(cfg);raw=env.unwrapped
 try:
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[18]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu')
  state=torch.load(a.checkpoint,map_location=raw.device,weights_only=True)['model_state_dict'];policy.load_state_dict(state);policy.to(raw.device).eval();assert all(torch.equal(v,state[k]) for k,v in policy.state_dict().items());policy=compose(policy,Path('outputs/motion_foundation/lesson20_candidate/candidate.pt'))
  def ids(case):return torch.arange(case*3,(case+1)*3,device=raw.device)
  def move(case,cmd):raw.set_motion_request(cmd,ids(case))
  def crouch(case):raw.request_crouch(raw.skills.cfg.maximum_drop_m,ids(case))
  def stand(case):raw.request_stand(ids(case))
  box_clips=torch.zeros(18,device=raw.device);measured_steps=0
  failures=torch.zeros(18,device=raw.device);faults=torch.zeros(18,device=raw.device,dtype=torch.bool);finite=torch.ones_like(faults)
  invariant=torch.zeros_like(failures);peak_target=torch.zeros_like(failures);peak_ik=torch.zeros_like(failures);trace=[];began=time.monotonic();observation_reads_ok=True
  with torch.inference_mode():
   for step in range(1200):
    if step==0:move(0,[.95,0,0]);move(1,[0,(.4 if a.profile in ("agile","yaw") else .35) if a.fast_commands else .2,0]);move(5,[.2,.12,.2])
    if step==100:
     for case in (2,3,4):crouch(case)
    if step==115:move(2,[.95,0,0])
    if step==150:crouch(0);crouch(1)
    if step==400:
     env_ids=ids(4);vel=raw._robot.data.root_vel_w[env_ids].clone();sign=torch.tensor([1.,-1.,1.],device=raw.device)
     vel[:,0]+=.05*sign;vel[:,1]-=.04*sign;vel[:,5]+=.08*sign
     raw._robot.write_root_velocity_to_sim(vel,env_ids=env_ids);obs=raw._get_observations()
    if step==450:stand(3)
    if step==500:move(0,[.95,0,0]);move(1,[0,0,(.8 if a.profile in ("agile","yaw") else .6) if a.fast_commands else .3])
    if step==650:crouch(3)
    if step==750:stand(4)
    if step==900:
     for case in (0,1,2,5):move(case,[0,0,0])
     stand(3)
    if step%200==0:
     clock_states=[raw.skills.mode_age,raw.skills.stable_time,raw.skills.mode,raw.motion.phase]
     if hasattr(raw,'yaw_control'):clock_states += [raw.yaw_control.integral,raw.yaw_control.filtered_error,raw.yaw_control.moment]
     before=[x.clone() for x in clock_states]
     for _ in range(3):raw._get_observations()
     clock_after=[raw.skills.mode_age,raw.skills.stable_time,raw.skills.mode,raw.motion.phase]
     if hasattr(raw,'yaw_control'):clock_after += [raw.yaw_control.integral,raw.yaw_control.filtered_error,raw.yaw_control.moment]
     observation_reads_ok &= all(torch.equal(x,y) for x,y in zip(before,clock_after))
    previous_mode=raw.skills.mode.clone()
    action=policy.act_inference(TensorDict(obs,batch_size=[18]));obs,reward,term,trunc,_=env.step(action);failures+=term
    box_clips+=raw.target_box_limited.float().mean(1);measured_steps+=1
    r=raw._robot.data;h=r.root_pos_w[:,2]-raw._terrain.env_origins[:,2]
    finite&=torch.isfinite(obs['policy']).all(1)&torch.isfinite(reward)
    faults|=raw.skills.mode==SkillMode.FAULT
    low=raw.motion.applied[:,3]<cfg.base_height_target-.0005
    bad=low&((raw.motion.applied[:,:3].abs().amax(1)>.0001)|(raw.motion.blend>.001))
    released=(previous_mode!=SkillMode.LOCOMOTION)&(raw.skills.mode==SkillMode.LOCOMOTION)
    bad|=released&((h-cfg.base_height_target).abs()>raw.skills.cfg.posture_height_tolerance_m)
    invariant+=bad
    peak_target=torch.maximum(peak_target,raw._processed_velocity_targets.abs().amax(1));peak_ik=torch.maximum(peak_ik,raw.reference_error.amax(1))
    if True:
     trace.append({'seconds':(step+1)*.02,'mode':raw.skills.mode.cpu().tolist(),'fault':raw.skills.fault.cpu().tolist(),
      'height':h.cpu().tolist(),'applied_height':raw.motion.applied[:,3].cpu().tolist(),
      'command':raw.motion.applied[:,:3].cpu().tolist(),'actual_twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1).cpu().tolist(),
      'tilt_deg':(torch.acos((-r.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi).cpu().tolist(),
      'torque_peak_nm':r.applied_torque[:,raw._actuated_joint_ids].abs().amax(1).cpu().tolist(),
      'q':r.joint_pos[:,raw._actuated_joint_ids].cpu().tolist(),'root_quat_wxyz':r.root_quat_w.cpu().tolist(),'blend':raw.motion.blend.cpu().tolist(),'contacts':(torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:,raw._foot_ids],dim=-1)>1).cpu().tolist()})
    if step%300==0:print('guarded skills',step,'failures',int(failures.sum()),'faulted',int(faults.sum()),flush=True)
  tm=np.array([x['seconds'] for x in trace]);heights=np.array([x['height'] for x in trace]);modes=np.array([x['mode'] for x in trace]);twist=np.array([x['actual_twist'] for x in trace])
  result={'complete':True,'profile':'bounded_return_trot_quick','script_sha256':file_hash(__file__),'training_updates':0,'parent_checkpoint':str(a.checkpoint.resolve()),'checkpoint_sha256':file_hash(a.checkpoint),
   'primary_network_tensors_bitwise_checkpoint':True,'routing':route,'fast_commands':a.fast_commands,'motion_contract':cfg.motion_contract,'observation_reads_do_not_advance_supervisor':observation_reads_ok,
   'scope':'nominal cloned deterministic transition tests, no general terrain/jump/belly-contact capability','wall_seconds':time.monotonic()-began,'cases':[]}
  for case,name in enumerate(NAMES):
   sl=slice(case*3,(case+1)*3);seen=set(int(x) for x in modes[:,sl].reshape(-1));row={'name':('trot_crouch_resume' if case==0 else name),'failures':int(failures[sl].sum()),'faulted_replicas':int(faults[sl].sum()),
    'finite':bool(finite[sl].all()),'invariant_violations':int(invariant[sl].sum()),'visited_modes':[SkillMode(m).name for m in sorted(seen)],
    'joint_target_box_clip_fraction':float(box_clips[sl].mean()/measured_steps),
    'minimum_actual_height_m':heights[:,sl].min(0).tolist(),'final_height_mean_m':float(heights[tm>=22,sl].mean()),
    'peak_target_speed_rad_s':float(peak_target[sl].max()),'max_ik_error_m':float(peak_ik[sl].max()),'resumed_twist_mean_14to17s':twist[(tm>=14)&(tm<17),sl].mean((0,1)).tolist()}
   expected={SkillMode.LOCOMOTION} if case==5 else {SkillMode.BRAKE,SkillMode.LOWER,SkillMode.RISE,SkillMode.SETTLE,SkillMode.LOCOMOTION}
   if case in (0,1,3,4):expected.add(SkillMode.HOLD)
   live=all(int(x) in seen for x in expected)
   row['peak_tilt_deg']=max(max(t['tilt_deg'][sl]) for t in trace)
   row['peak_torque_nm']=max(max(t['torque_peak_nm'][sl]) for t in trace)
   row['first_hold_seconds']=[next((t['seconds'] for t in trace if t['mode'][j]==int(SkillMode.HOLD)),None) for j in range(case*3,(case+1)*3)]
   holdmask=modes[:,sl]==int(SkillMode.HOLD)
   row['hold_height_mean_m']=float(heights[:,sl][holdmask].mean()) if holdmask.any() else None
   trigger=3. if case in (0,1) else 2.
   row['trigger_to_first_hold_s']=[None if t is None else t-trigger for t in row['first_hold_seconds']] if case!=5 else []
   posture=(modes[:,sl]==int(SkillMode.LOWER))|(modes[:,sl]==int(SkillMode.HOLD))|(modes[:,sl]==int(SkillMode.RISE))
   contact_array=np.array([t['contacts'] for t in trace])[:,sl].all(2)
   row['posture_all_four_contact_fraction']=float(contact_array[posture].mean()) if posture.any() else 1.
   row['required_modes_reached']=live
   passed=row['finite'] and row['peak_tilt_deg']<=12 and row['peak_torque_nm']<=12.0001 and row['posture_all_four_contact_fraction']>=.99 and not row['failures'] and not row['faulted_replicas'] and not row['invariant_violations'] and live and observation_reads_ok and row['peak_target_speed_rad_s']<=8.0001 and row['max_ik_error_m']<=.001 and abs(row['final_height_mean_m']-cfg.base_height_target)<.01
   row['gate']='PASS' if passed else 'FAIL';result['cases'].append(row)
  result['gate']='PASS' if all(c['gate']=='PASS' for c in result['cases']) else 'FAIL';result['trace']=trace
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');print('guarded skills',result['gate'],flush=True)
  for c in result['cases']:print(c['name'],c['gate'],c['visited_modes'],c['faulted_replicas'],flush=True)
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
