#!/usr/bin/env python3
"""Explicit frozen-policy comparison of larger commands and timing adaptation."""
import argparse,json,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--profile',choices=('adaptive','exposed','baseline','yaw'),default='adaptive')
p.add_argument('--suite',choices=('fast','previous','holdout','agile-holdout','low','full'),default='fast')
p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--seed',type=int,default=42);p.add_argument('--num-envs',type=int,default=144);p.add_argument('--disturbance',action='store_true')
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.num_envs<18:p.error('New output and at least18 environments required')
if a.profile=='baseline' and a.suite=='fast':p.error('Original baseline does not accept enlarged commands; use exposed counterfactual')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import gymnasium as gym
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_transfer import MotionBackwardEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_adaptive_speed import MotionAdaptiveSpeedEnvCfg,MotionExposedSpeedEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg
from csdog_motion.yaw_integral import extend_policy_inputs
from csdog_motion.residual_learning import low_command_cases
from csdog_motion.evaluation import default_cases
from csdog_motion.adaptive_speed import fast_cases,fast_holdout_cases
from csdog_motion.speed_learning import speed_cases
from csdog_motion.backward_validation import backward_holdout_cases
from csdog_motion.diagnostic_evaluation import evaluate
from csdog_motion.training import validate_checkpoint,file_hash


def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 parent=MotionBackwardEnvCfg();metadata=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert metadata['checkpoint_sha256']==file_hash(a.checkpoint)
 cfg={'adaptive':MotionAdaptiveSpeedEnvCfg,'exposed':MotionExposedSpeedEnvCfg,'baseline':MotionBackwardEnvCfg,'yaw':MotionYawEnvCfg}[a.profile]()
 cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device;cfg.seed=a.seed;cfg.episode_length_s=30.;cfg.periodic_commands=False
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 task={'adaptive':'CSDog-Motion-Adaptive-Speed-Diagnostic-v0','exposed':'CSDog-Motion-Exposed-Speed-Diagnostic-v0','baseline':'CSDog-Motion-Backward-Direct-v0','yaw':'CSDog-Motion-Yaw-Diagnostic-v0'}[a.profile]
 env=gym.make(task,cfg=cfg);raw=env.unwrapped
 try:
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[a.num_envs]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(raw.device)
  state=torch.load(a.checkpoint,map_location=raw.device,weights_only=True)['model_state_dict']
  copied=extend_policy_inputs(state,policy.state_dict()) if a.profile=='yaw' else state
  policy.load_state_dict(copied);policy.eval();assert all(torch.equal(v,copied[k]) for k,v in policy.state_dict().items())
  checkpoint=a.checkpoint
  if a.profile=='yaw':
   checkpoint=a.output/'initial.pt';torch.save({'model_state_dict':policy.state_dict(),'iter':0,'infos':{'new_ppo_updates':0,'optimizer_state':'not copied or created'}},checkpoint)
   root=Path(__file__).resolve().parents[1]
   record={'checkpoint_sha256':file_hash(checkpoint),'checkpoint_compatibility_tag':cfg.checkpoint_compatibility_tag,'actuated_joint_names':list(cfg.actuated_joint_names),'observations':76,'actions':12,'motion_contract':cfg.motion_contract,'initialization_only':True,'parent_checkpoint':str(a.checkpoint.resolve()),'parent_sha256':file_hash(a.checkpoint),'new_ppo_updates':0,'optimizer_steps':0,'migration':'actor/critic first74 input columns exactly copied; two appended columns zero; every other tensor exactly copied; no optimizer state','source_files_sha256':{str(p.relative_to(root)):file_hash(p) for folder in ('source','scripts') for p in sorted((root/folder).rglob('*.py'))}}
   Path(str(checkpoint)+'.metadata.json').write_text(json.dumps(record,indent=2)+'\n')
  cases={'fast':fast_cases,'previous':speed_cases,'holdout':backward_holdout_cases,'agile-holdout':fast_holdout_cases,'low':low_command_cases,'full':lambda:default_cases('lateral_grid')}[a.suite]()
  result=evaluate(env,policy,checkpoint,a.output/'evaluation.json',cases=cases,seed=a.seed,disturbance=a.disturbance,protocol_name={'fast':'adaptive_speed18','previous':'residual_axis_speed18','holdout':'backward_holdout18','agile-holdout':'agile_holdout18','low':'residual_low18','full':'residual_full18'}[a.suite],task=task)
  result.update(new_ppo_updates=0,all_network_tensors_bitwise_v14=a.profile!='yaw',zero_extended_74to76=a.profile=='yaw',parent_checkpoint_sha256=file_hash(a.checkpoint),profile=a.profile)
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
