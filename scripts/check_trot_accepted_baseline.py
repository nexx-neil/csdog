#!/usr/bin/env python3
"""Independent76D flat trot experiment, explicit tensor transfer and fixed regressions."""
import argparse,copy,json,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=('baseline','probe','train'),required=True);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--max-updates',type=int,default=100);p.add_argument('--segment',type=int,default=25);p.add_argument('--num-envs',type=int,default=256);p.add_argument('--seed',type=int,default=42);p.add_argument('--holdout',action='store_true')
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.num_envs<144 or not 0<=a.max_updates<=500 or a.segment<1:p.error('New output, >=144 envs,0..500 updates,positive segment required')
app=AppLauncher(a)
import gymnasium as gym
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from rsl_rl.runners import OnPolicyRunner
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg,MotionYawEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_course import MotionTrotEnvCfg,MotionTrotEnv
from csdog_motion.training import validate_checkpoint,file_hash,bound_learning_rate,install_checkpoint_records
from csdog_motion.residual_learning import low_command_cases
from csdog_motion.adaptive_speed import fast_cases,fast_holdout_cases
from csdog_motion.evaluation import default_cases,regression_gate
from csdog_motion.trot_course import cases
from csdog_motion.diagnostic_evaluation import evaluate
from csdog_motion.trot_policy_routing import routing_record,with_saved_routing

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 tag=json.loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag']
 parent=MotionTrotEnvCfg() if tag==MotionTrotEnvCfg().checkpoint_compatibility_tag else MotionYawEnvCfg();meta=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 if a.mode!='baseline':assert json.loads(Path('analysis/motion_foundation_20261111/lesson20/trot_preflight.json').read_text())['gate']=='PASS'
 cfg=parent if a.mode=='baseline' else MotionTrotEnvCfg();cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device;cfg.seed=a.seed;cfg.episode_length_s=30.;cfg.periodic_commands=a.mode=='train';cfg.residual_training_enabled=a.mode=='train'
 route=routing_record(a.checkpoint)
 if route is not None:
  if a.mode=='train':raise ValueError('Routed inference candidate cannot resume single-actor training')
  cfg.motion_contract=dict(cfg.motion_contract,policy_routing=route)
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve());env=MotionYawEnv(cfg) if a.mode=='baseline' else MotionTrotEnv(cfg)
 manifest={'status':'RUNNING','mode':a.mode,'parent':str(a.checkpoint.resolve()),'parent_sha256':file_hash(a.checkpoint),'contract':cfg.motion_contract,'seed':a.seed,'new_ppo_updates':0,'optimizer_steps':0,'evaluations':[],'automatic_promotion':False}
 def save(): (a.output/'experiment.json').write_text(json.dumps(manifest,indent=2)+'\n')
 save()
 try:
  state=torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']
  if a.mode!='train':
   with torch.inference_mode():obs,_=env.reset()
  agent={'num_steps_per_env':64,'save_interval':25,'logger':'tensorboard','obs_groups':{'policy':['policy'],'critic':['policy']},'policy':{'class_name':'ActorCritic','init_noise_std':.25,'actor_obs_normalization':False,'critic_obs_normalization':False,'actor_hidden_dims':[256,256,128],'critic_hidden_dims':[256,256,128],'activation':'elu'},'algorithm':{'class_name':'PPO','value_loss_coef':1.,'use_clipped_value_loss':True,'clip_param':.2,'entropy_coef':.003,'num_learning_epochs':5,'num_mini_batches':4,'learning_rate':3e-5,'schedule':'fixed','gamma':.99,'lam':.95,'desired_kl':.01,'max_grad_norm':1.}}
  if a.mode=='train':
   runner=OnPolicyRunner(RslRlVecEnvWrapper(env,clip_actions=None),copy.deepcopy(agent),log_dir=str(a.output),device=a.device);runner.logger_type='tensorboard';policy=runner.alg.policy;policy.load_state_dict(state)
   lr_audit,_=bound_learning_rate(runner.alg,3e-5,3e-5);counts=install_checkpoint_records(runner,cfg,'CSDog-Motion-Trot-Course-v25',parent=a.checkpoint,lr_audit=lr_audit,resume_semantics='Explicit same-shape76D counterfactual tensor copy; changed high-vx reference; new Adam; no automatic deployment');manifest['agent']=agent
  else:
   policy=ActorCritic(TensorDict(obs,batch_size=[a.num_envs]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device);policy.load_state_dict(state)
  assert all(torch.equal(v,state[k]) for k,v in policy.state_dict().items());policy.eval();manifest['initial_primary_actor_tensors_exact']=True
  if route is not None:policy=with_saved_routing(policy,a.checkpoint);manifest['routing']=route
  reference={}
  from csdog_motion.trot_course import cases as previous_cases
  def suite():
   old=fast_cases()
   for c in previous_cases(False):
    if c['name']!='stand':old.append(dict(c,name='previous_'+c['name']))
   return old
  suites={'combined':suite}
  def check(cp,updates):
   passed=True;results={}
   for label,fn in suites.items():
    path=a.output/f'{label}_{updates:04d}.json';result=evaluate(env,policy,cp,path,cases=fn(),seed=a.seed,protocol_name='lesson27_old_baseline_'+label,task='CSDog-Trot-Course' if a.mode!='baseline' else 'CSDog-Yaw-Baseline')
    if updates:
     result['regression_vs_initial']=regression_gate(result,reference[label]);path.write_text(json.dumps(result,indent=2)+'\n')
     passed &= result['regression_vs_initial']['status']=='PASS'
    passed &= result['development_safety_gate']['status']=='PASS';results[label]=result
   manifest['evaluations'].append({'updates':updates,'passed':passed});save();return results,bool(passed)
  initial=a.checkpoint
  if a.mode=='train':initial=a.output/'initial.pt';runner.save(str(initial))
  reference,ok=check(initial,0)
  if not ok:manifest['status']='INITIALIZATION_REJECTED';save();return
  if a.mode!='train':manifest['status']='EVALUATION_COMPLETE';save();return
  while counts['updates_in_this_run']<a.max_updates:
   runner.learn(min(a.segment,a.max_updates-counts['updates_in_this_run']),init_at_random_ep_len=False)
   updates=counts['updates_in_this_run'];manifest['new_ppo_updates']=updates;manifest['optimizer_steps']=updates*20;manifest['optimizer_audit']=dict(lr_audit)
   cp=a.output/f'segment_{updates:04d}.pt';runner.save(str(cp));manifest['status']='VALIDATING';save();_,ok=check(cp,updates)
   if not ok:manifest['status']='STOPPED_REGRESSION_OR_SAFETY_REJECTED';save();return
  manifest['status']='BUDGET_COMPLETED_NOT_PROMOTED';save()
 except BaseException as exc:manifest['status']='ERROR';manifest['exception']=repr(exc);save();raise
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
