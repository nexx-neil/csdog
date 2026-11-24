#!/usr/bin/env python3
"""Paired per-foot, per-phase diagnosis; no controller or metric changes."""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);p.add_argument('--seed',type=int,default=2027);AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists():p.error('New output required')
app=AppLauncher(a)
import numpy as np,torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from csdog_motion.training import validate_checkpoint,file_hash
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv
class Env(MotionScannedRoughEnv):
 def _setup_scene(self):
  super()._setup_scene();self.terrain_columns[:]=4;self._terrain.env_origins[:]=self._terrain.terrain_origins[3,4]
def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed);a.output.mkdir(parents=True)
 cfg=MotionScannedRoughEnvCfg();cfg.scene.num_envs=6;cfg.sim.device=a.device;cfg.seed=a.seed;cfg.terrain.terrain_generator.seed=a.seed;cfg.terrain_row=3;cfg.periodic_commands=False;cfg.episode_length_s=18.;cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 env=Env(cfg)
 try:
  with torch.inference_mode():obs,_=env.reset()
  policies=[];paths=[Path('outputs/motion_foundation/lesson21_candidate/candidate.pt'),Path('outputs/motion_foundation/lesson22_candidate/candidate.pt')]
  for cp in paths:
   m=validate_checkpoint(cp,MotionScannedRoughEnvCfg(),policy_only=True);assert m['checkpoint_sha256']==file_hash(cp)
   policy=ActorCritic(TensorDict({'policy':obs['policy'][:3]},batch_size=[3]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device);policy.load_state_dict(torch.load(cp,map_location=a.device,weights_only=True)['model_state_dict']);policies.append(policy.eval())
  data={k:[] for k in ['time','phase','planned_stance','force','velocity','omega','tread_bottom_velocity','clearance','ground_z','support_weights','twist','torque','target_velocity','contact','position','residual']};failures=0
  with torch.inference_mode():
   for step in range(750):
    t=step*.02;env.set_motion_request([-.25,0,0] if 2<=t<12 else [0,0,0]);phase=torch.remainder(env.motion.phase[:,None]+env.motion.phase.new_tensor([0,.5,0,.5]),1).clone();weights=env._support_weights().clone()
    acts=torch.cat([policies[i].act_inference(TensorDict({'policy':obs['policy'][i*3:i*3+3]},batch_size=[3])) for i in range(2)])
    obs,_,term,_,_=env.step(acts);r=env._robot.data;failures+=int(term.sum());v=r.body_lin_vel_w[:,env._robot_foot_ids];omega=r.body_ang_vel_w[:,env._robot_foot_ids];offset=torch.zeros_like(v);offset[:,:,2]=-.018;bottom=v+torch.cross(omega,offset,dim=-1);force=env._contact_sensor.data.net_forces_w[:,env._foot_ids]
    values={'time':(step+1)*.02,'phase':phase,'planned_stance':env.reference_stance,'force':force,'velocity':v,'omega':omega,'tread_bottom_velocity':bottom,'clearance':env._foot_clearance(),'ground_z':env._surfaces()[:,1:],'support_weights':weights,'twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1),'torque':r.applied_torque[:,env._actuated_joint_ids],'target_velocity':env._processed_velocity_targets,'contact':torch.linalg.vector_norm(force,dim=-1)>1,'position':r.root_pos_w-env._terrain.env_origins,'residual':env.last_residual_actions}
    for k,value in values.items():data[k].append(value.cpu().numpy().copy() if torch.is_tensor(value) else value)
  data={k:np.array(v) for k,v in data.items()};np.savez_compressed(a.output/'trace.npz',**data)
  summary={'complete':True,'failures':failures,'seed':a.seed,'column':4,'row':3,'command':[-.25,0,0],'feet':['lr','lf','rf','rr'],'checkpoints':[{'path':str(cp),'sha256':file_hash(cp)} for cp in paths],'contact_point_scope':'vertical tread-bottom approximation v+omega cross(0,0,-.018); not exact contact point/edge normal','groups':[]}
  for group,name in enumerate(['initial21','learned22']):
   ids=slice(group*3,group*3+3);mask=(data['time']>=3)&(data['time']<12);speed=np.linalg.norm(data['velocity'][mask,ids,:,:2],axis=-1);bottom=np.linalg.norm(data['tread_bottom_velocity'][mask,ids,:,:2],axis=-1);contact=data['contact'][mask,ids];stance=data['planned_stance'][mask,ids];force=data['force'][mask,ids];phase=data['phase'][mask,ids]
   rows=[]
   for f,leg in enumerate(summary['feet']):
    c=contact[:,:,f];s=stance[:,:,f];rows.append({'leg':leg,'contact_speed_mps':float(speed[:,:,f][c].mean()),'bottom_speed_mps':float(bottom[:,:,f][c].mean()),'contact_in_swing_fraction':float((c&~s).sum()/max(1,(~s).sum())),'stance_contact_fraction':float((c&s).sum()/max(1,s.sum())),'phase_bins':[{'lo':lo,'hi':hi,'contact_frames':int((c&(phase[:,:,f]>=lo)&(phase[:,:,f]<hi)).sum()),'mean_speed_mps':float(speed[:,:,f][c&(phase[:,:,f]>=lo)&(phase[:,:,f]<hi)].mean()) if (c&(phase[:,:,f]>=lo)&(phase[:,:,f]<hi)).any() else None} for lo,hi in [(0,.1),(.1,.45),(.45,.55),(.55,.7),(.7,.9),(.9,1.)]]})
   proxy=(speed*contact).sum(2)/np.maximum(1,contact.sum(2));summary['groups'].append({'name':name,'mean_slide_proxy_mps':float(proxy.mean()),'peak_torque_nm':float(np.abs(data['torque'][mask,ids]).max()),'rows':rows})
  (a.output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,indent=2),flush=True)
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
