#!/usr/bin/env python3
"""Teacher-anchored scan-only PPO: frozen legacy actor, unchanged terrain controller."""
import argparse,copy,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--mode',choices=('probe','train'),default='train');p.add_argument('--steps',type=int,default=750);p.add_argument('--num-envs',type=int,default=160);p.add_argument('--row',type=int,default=1);p.add_argument('--seed',type=int,default=82);p.add_argument('--max-updates',type=int,default=50);p.add_argument('--segment',type=int,default=10);p.add_argument('--no-foot-adaptation',action='store_true');AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.num_envs%40 or not 0<=a.row<=3 or a.steps<1 or a.max_updates<1 or a.segment<1:p.error('New output, env count multiple40, row0..3, positive steps required')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from rsl_rl.runners import OnPolicyRunner
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg
from csdog_motion.rough_sensing import extend_inputs,TAG
from csdog_motion.anchored_ppo import configure_scan_adapter,preservation_check
from csdog_motion.rough_evaluation import evaluate
from csdog_motion.training import validate_checkpoint,file_hash,bound_learning_rate,install_checkpoint_records

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 cfg=MotionScannedRoughEnvCfg();cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device;cfg.seed=a.seed;cfg.terrain.terrain_generator.seed=a.seed;cfg.terrain_row=a.row;cfg.sensor_reference_enabled=not a.no_foot_adaptation;cfg.motion_contract['rough_sensing']['sensor_reference_enabled']=cfg.sensor_reference_enabled;cfg.periodic_commands=a.mode=='train';cfg.episode_length_s=18.
 tag=json.loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag'];old=(tag!=TAG);meta=validate_checkpoint(a.checkpoint,MotionYawEnvCfg() if old else MotionScannedRoughEnvCfg(),policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve());env=MotionScannedRoughEnv(cfg);manifest={'status':'RUNNING','mode':a.mode,'parent_checkpoint':str(a.checkpoint.resolve()),'parent_sha256':file_hash(a.checkpoint),'new_ppo_updates':0,'optimizer_steps':0,'explicit_76to175_input_migration':old,'motion_contract':cfg.motion_contract,'row':a.row,'seed':a.seed,'evaluations':[]}
 def save(): (a.output/'experiment.json').write_text(json.dumps(manifest,indent=2)+'\n')
 save()
 try:
  state=torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']
  if a.mode=='train':
   agent={'num_steps_per_env':64,'save_interval':25,'logger':'tensorboard','obs_groups':{'policy':['policy'],'critic':['policy']},'policy':{'class_name':'ActorCritic','init_noise_std':.2,'actor_obs_normalization':False,'critic_obs_normalization':False,'actor_hidden_dims':[256,256,128],'critic_hidden_dims':[256,256,128],'activation':'elu'},'algorithm':{'class_name':'PPO','value_loss_coef':1.,'use_clipped_value_loss':True,'clip_param':.2,'entropy_coef':.003,'num_learning_epochs':5,'num_mini_batches':4,'learning_rate':1e-5,'schedule':'fixed','gamma':.99,'lam':.95,'desired_kl':.01,'max_grad_norm':1.}}
   runner=OnPolicyRunner(RslRlVecEnvWrapper(env,clip_actions=None),copy.deepcopy(agent),log_dir=str(a.output),device=a.device);runner.logger_type='tensorboard';policy=runner.alg.policy
  else:
   with torch.inference_mode():obs,_=env.reset()
   policy=ActorCritic(TensorDict(obs,batch_size=[a.num_envs]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device)
  copied=extend_inputs(state,policy.state_dict()) if old else state;policy.load_state_dict(copied);policy.eval();assert all(torch.equal(v,copied[k]) for k,v in policy.state_dict().items())
  initial=a.output/'initial.pt';torch.save({'model_state_dict':policy.state_dict(),'iter':0},initial)
  if a.mode=='train':
   teacher=configure_scan_adapter(runner.alg,coefficient=1.,action_scale=.1);manifest['training_constraint']={'train_actor':'only99 scan input columns','frozen':'all76 legacy columns, remaining actor layers/biases and exploration std','teacher_coefficient':1.,'teacher_action_scale':.1,'critic':'train full','teacher_sha256':file_hash(a.checkpoint)};lr,_=bound_learning_rate(runner.alg,1e-5,1e-5);counts=install_checkpoint_records(runner,cfg,'CSDog-Scanned-Rough-Residual-v28',parent=a.checkpoint,lr_audit=lr,resume_semantics='Scan-only anchored PPO; all legacy actor parameters frozen; teacher in total loss before clipping; fresh Adam; no optimizer transfer')
   runner.save(str(initial));manifest['agent']=agent
  baseline=evaluate(env,policy,initial,a.output/'validation_0000.json',a.steps);manifest['evaluations'].append({'updates':0,'gate':baseline['gate']});save()
  if a.mode=='probe':manifest['status']='EVALUATION_COMPLETE';save();return
  if baseline['gate']!='PASS':manifest['status']='INITIALIZATION_REJECTED';save();return
  while counts['updates_in_this_run']<a.max_updates:
   runner.learn(min(a.segment,a.max_updates-counts['updates_in_this_run']),init_at_random_ep_len=False);u=counts['updates_in_this_run'];assert preservation_check(policy,teacher);manifest['legacy_actor_bitwise_preserved']=True;manifest['scan_adapter_weight_norm']=float(policy.actor[0].weight[:,76:].norm());cp=a.output/f'segment_{u:04d}.pt';runner.save(str(cp));manifest.update(new_ppo_updates=u,optimizer_steps=lr['optimizer_steps']);save();result=evaluate(env,policy,cp,a.output/f'validation_{u:04d}.json',a.steps);manifest['evaluations'].append({'updates':u,'gate':result['gate']});save()
   if result['gate']!='PASS':manifest['status']='STOPPED_SAFETY_OR_FUNCTIONAL_REJECTED';save();return
  manifest['status']='BUDGET_COMPLETED_NOT_PROMOTED';save()
 except BaseException as exc:manifest.update(status='ERROR',exception=repr(exc));save();raise
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
