#!/usr/bin/env python3
"""Original48-case evaluation with a passive50Hz recorder for backward stairs."""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--profile',choices=('foundation','full_range'),default='full_range')
p.add_argument('--seed',type=int,default=2027)
p.add_argument('--row',type=int,default=3)
p.add_argument('--num-envs',type=int,default=144)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.num_envs<=0 or a.num_envs%48 or not 0<=a.row<4:
 p.error('New output, positive multiple48 environments and row0..3 required')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.terrain_turn_evaluation import evaluate
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 cfg=MotionScannedRoughEnvCfg();meta=validate_checkpoint(a.checkpoint,cfg,policy_only=True)
 assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 a.output.mkdir(parents=True);cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device
 cfg.seed=a.seed;cfg.terrain.terrain_generator.seed=a.seed;cfg.terrain_row=a.row
 cfg.periodic_commands=False;cfg.episode_length_s=18.;cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 env=MotionScannedRoughEnv(cfg)
 try:
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[a.num_envs]),{'policy':['policy'],'critic':['policy']},12,
      actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device)
  policy.load_state_dict(torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']);policy.eval()
  raw={k:[] for k in ['time','phase','planned_stance','force','velocity','omega','clearance','ground_z','support_weights','twist','torque','contact','position']};original_step=env.step;ids=torch.tensor([12,60,108],device=env.device)
  def recorded_step(actions):
   phase=torch.remainder(env.motion.phase[ids,None]+env.motion.phase.new_tensor([0,.5,0,.5]),1).clone();weights=env._support_weights()[ids].clone()
   result=original_step(actions);r=env._robot.data;force=env._contact_sensor.data.net_forces_w[ids][:,env._foot_ids]
   values={'time':(len(raw['time'])+1)*.02,'phase':phase,'planned_stance':env.reference_stance[ids],'force':force,'velocity':r.body_lin_vel_w[ids][:,env._robot_foot_ids],'omega':r.body_ang_vel_w[ids][:,env._robot_foot_ids],'clearance':env._foot_clearance()[ids],'ground_z':env._surfaces()[ids,1:],'support_weights':weights,'twist':torch.cat((r.root_lin_vel_b[ids,:2],r.root_ang_vel_b[ids,2:3]),1),'torque':r.applied_torque[ids][:,env._actuated_joint_ids],'contact':torch.linalg.vector_norm(force,dim=-1)>1,'position':r.root_pos_w[ids]-env._terrain.env_origins[ids]}
   for key,value in values.items():raw[key].append(value.detach().cpu().numpy().copy() if torch.is_tensor(value) else value)
   return result
  env.step=recorded_step
  evaluate(env,policy,a.checkpoint,a.output/'evaluation.json',profile=a.profile)
  np.savez_compressed(a.output/'backward_trace.npz',**{k:np.array(v) for k,v in raw.items()})
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
