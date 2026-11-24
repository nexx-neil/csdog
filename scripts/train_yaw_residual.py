#!/usr/bin/env python3
"""Small flat-residual lesson: observed yaw state, new Adam, strict old-range gates."""
import argparse,copy,json,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--initialize-from',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--max-updates',type=int,default=10);p.add_argument('--segment',type=int,default=5);p.add_argument('--num-envs',type=int,default=256)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.max_updates<0 or a.max_updates>50 or a.segment<1 or a.num_envs<144:p.error('New output,0..50 updates, positive segment, >=144 environments required')
app=AppLauncher(a)
import gymnasium as gym
import torch,numpy as np
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from rsl_rl.runners import OnPolicyRunner
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw_learning import MotionYawLearningEnvCfg
from csdog_motion.training import validate_checkpoint,file_hash,bound_learning_rate,install_checkpoint_records
from csdog_motion.diagnostic_evaluation import evaluate
from csdog_motion.residual_learning import low_command_cases
from csdog_motion.speed_learning import speed_cases
from csdog_motion.adaptive_speed import fast_cases
from csdog_motion.evaluation import default_cases,regression_gate
TASK='CSDog-Motion-Yaw-Learning-Direct-v0'


def main():
 torch.set_num_threads(1);torch.manual_seed(42);np.random.seed(42)
 parent=MotionYawEnvCfg();metadata=validate_checkpoint(a.initialize_from,parent,policy_only=True);assert metadata['checkpoint_sha256']==file_hash(a.initialize_from)
 cfg=MotionYawLearningEnvCfg();assert cfg.residual_training_enabled and not cfg.training_enabled
 old=copy.deepcopy(parent.motion_contract);new=copy.deepcopy(cfg.motion_contract)
 for c in (old,new):
  for k in ('schema_version','compatibility_tag','learning_replay'):c.pop(k,None)
 assert old==new,'Learning may only change sampling and identity'
 a.output.mkdir(parents=True);cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device;cfg.seed=42;cfg.episode_length_s=30.;cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 agent={'num_steps_per_env':64,'save_interval':25,'logger':'tensorboard','obs_groups':{'policy':['policy'],'critic':['policy']},
  'policy':{'class_name':'ActorCritic','init_noise_std':.25,'actor_obs_normalization':False,'critic_obs_normalization':False,'actor_hidden_dims':[256,256,128],'critic_hidden_dims':[256,256,128],'activation':'elu'},
  'algorithm':{'class_name':'PPO','value_loss_coef':1.,'use_clipped_value_loss':True,'clip_param':.2,'entropy_coef':.003,'num_learning_epochs':5,'num_mini_batches':4,'learning_rate':3e-5,'schedule':'fixed','gamma':.99,'lam':.95,'desired_kl':.01,'max_grad_norm':1.}}
 env=gym.make(TASK,cfg=cfg)
 try:
  wrapped=RslRlVecEnvWrapper(env,clip_actions=None);runner=OnPolicyRunner(wrapped,copy.deepcopy(agent),log_dir=str(a.output),device=a.device);runner.logger_type='tensorboard'
  state=torch.load(a.initialize_from,map_location=a.device,weights_only=True)['model_state_dict'];runner.alg.policy.load_state_dict(state);assert all(torch.equal(v,state[k]) for k,v in runner.alg.policy.state_dict().items())
  lr_audit,_=bound_learning_rate(runner.alg,3e-5,3e-5);counts=install_checkpoint_records(runner,cfg,TASK,parent=a.initialize_from,lr_audit=lr_audit,resume_semantics='explicit76D same-controller tensor copy; new Adam; only sampling identity changes; physical environment reset')
  manifest={'date':'2026-11-09','parent_checkpoint':str(a.initialize_from.resolve()),'parent_sha256':file_hash(a.initialize_from),'maximum_updates':a.max_updates,'segment':a.segment,'agent':agent,'motion_contract':cfg.motion_contract,'num_envs':a.num_envs,'status':'RUNNING','evaluations':[]}
  def record():
   manifest['completed_updates']=counts['updates_in_this_run'];manifest['optimizer_audit']=dict(lr_audit);(a.output/'experiment.json').write_text(json.dumps(manifest,indent=2)+'\n')
  record();initial=a.output/'initial.pt';runner.save(str(initial))
  suites={'low':low_command_cases,'full':lambda:default_cases('lateral_grid'),'previous':speed_cases,'fast':fast_cases};reference={}
  def check(checkpoint,updates):
   results={}
   for label,case_fn in suites.items():
    output=a.output/f'{label}_validation_{updates:04d}.json';result=evaluate(env,runner.alg.policy,checkpoint,output,cases=case_fn(),seed=42,protocol_name={'low':'residual_low18','full':'residual_full18','previous':'residual_axis_speed18','fast':'adaptive_speed18'}[label],task=TASK)
    if updates:result['regression_vs_initial']=regression_gate(result,reference[label]);output.write_text(json.dumps(result,indent=2)+'\n')
    results[label]=result
    if result['development_safety_gate']['status']!='PASS' or (updates and result['regression_vs_initial']['status']!='PASS'):return results,False
   return results,True
  reference,passed=check(initial,0);manifest['evaluations'].append({'updates':0,'passed':passed});record()
  if not passed:manifest['status']='INITIALIZATION_REJECTED';record();return
  while counts['updates_in_this_run']<a.max_updates:
   amount=min(a.segment,a.max_updates-counts['updates_in_this_run']);runner.learn(amount,init_at_random_ep_len=False);updates=counts['updates_in_this_run'];checkpoint=a.output/f'segment_{updates:04d}.pt';runner.save(str(checkpoint));manifest['status']='VALIDATING';record()
   results,passed=check(checkpoint,updates);manifest['evaluations'].append({'updates':updates,'passed':passed});manifest['status']='RUNNING';record()
   if not passed:manifest['status']='STOPPED_REGRESSION_OR_SAFETY_REJECTED';record();return
  manifest['status']='DEVELOPMENT_BUDGET_COMPLETED';manifest['decision']='NO_AUTOMATIC_PROMOTION; require speed/gait improvement and independent holdout';record()
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
