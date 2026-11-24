#!/usr/bin/env python3
"""External stair-backward replay/contact cost; native inference task unchanged."""
import argparse,copy,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint',type=Path,default=Path('outputs/motion_foundation/lesson22_candidate/candidate.pt'))
p.add_argument('--reference',type=Path,default=Path('outputs/motion_foundation/lesson21_candidate/candidate.pt'))
p.add_argument('--output',type=Path,required=True)
p.add_argument('--max-updates',type=int,default=50)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.max_updates!=50:p.error('New output and registered50-update budget required')
app=AppLauncher(a)
import torch,numpy as np
from rsl_rl.runners import OnPolicyRunner
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
from csdog_motion.contact_curriculum import PROFILE,CommandReplay,activation,additional_slide_reward
from csdog_motion.teacher_anchor import configure_teacher_anchor,preservation_check
from csdog_motion.terrain_dense_evaluation import evaluate
from csdog_motion.training import validate_checkpoint,file_hash,bound_learning_rate,install_checkpoint_records
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv

class ReplayWrapper(RslRlVecEnvWrapper):
 def __init__(self,env):
  super().__init__(env,clip_actions=None);self.replay=CommandReplay(env);self.extra_cost_sum=0.;self.active_cost_env_steps=0
 def step(self,actions):
  e=self.unwrapped;self.replay.request();hits=e.height_scanner.data.ray_hits_w[:,:,2]
  gate=activation(e.motion.applied[:,:3],hits.amax(1)-hits.amin(1))
  obs,rewards,dones,extras=super().step(actions)
  cost=additional_slide_reward(e.last_reward_terms['stance_slide'],gate)
  self.extra_cost_sum+=float(cost.sum());self.active_cost_env_steps+=int((gate>0).sum())
  self.replay.on_dones(dones)
  return obs,rewards+cost,dones,extras

def main():
 torch.set_num_threads(1);torch.manual_seed(2027);np.random.seed(2027)
 cfg=MotionScannedRoughEnvCfg()
 for cp in [a.checkpoint,a.reference]:
  m=validate_checkpoint(cp,cfg,policy_only=True);assert m['checkpoint_sha256']==file_hash(cp)
 cfg.scene.num_envs=144;cfg.sim.device=a.device;cfg.seed=2027;cfg.terrain.terrain_generator.seed=2027;cfg.terrain_row=3;cfg.periodic_commands=False;cfg.episode_length_s=18.
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve());env=MotionScannedRoughEnv(cfg)
 d={'status':'RUNNING','parent_checkpoint':str(a.checkpoint.resolve()),'parent_sha256':file_hash(a.checkpoint),'reference_checkpoint':str(a.reference.resolve()),'external_training_adapter':PROFILE,'seed':2027,'row':3,'num_envs':144,'rollout_steps':64,'new_ppo_updates':0,'optimizer_steps':0,'evaluations':[]}
 def save(): (a.output/'experiment.json').write_text(json.dumps(d,indent=2)+'\n')
 save()
 try:
  agent={'num_steps_per_env':64,'save_interval':10,'logger':'tensorboard','obs_groups':{'policy':['policy'],'critic':['policy']},'policy':{'class_name':'ActorCritic','init_noise_std':.2,'actor_obs_normalization':False,'critic_obs_normalization':False,'actor_hidden_dims':[256,256,128],'critic_hidden_dims':[256,256,128],'activation':'elu'},'algorithm':{'class_name':'PPO','value_loss_coef':1.,'use_clipped_value_loss':True,'clip_param':.2,'entropy_coef':.003,'num_learning_epochs':5,'num_mini_batches':4,'learning_rate':1e-5,'schedule':'fixed','gamma':.99,'lam':.95,'desired_kl':.01,'max_grad_norm':1.}}
  wrapper=ReplayWrapper(env);runner=OnPolicyRunner(wrapper,copy.deepcopy(agent),log_dir=str(a.output),device=a.device);runner.logger_type='tensorboard';policy=runner.alg.policy
  policy.load_state_dict(torch.load(a.reference,map_location=a.device,weights_only=True)['model_state_dict']);policy.eval()
  reference=evaluate(env,policy,a.reference,a.output/'reference_full.json',profile='full_range')
  policy.load_state_dict(torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']);policy.eval()
  teacher=configure_teacher_anchor(runner.alg,coefficient=1.,action_scale=.1)
  lr,_=bound_learning_rate(runner.alg,1e-5,1e-5);counts=install_checkpoint_records(runner,cfg,'CSDog-Scanned-Rough-Contact-Replay',parent=a.checkpoint,lr_audit=lr,resume_semantics='Explicit external command/reward curriculum; teacher and exploration noise frozen; fresh Adam; native inference controller unchanged')
  recorded_save=runner.save
  def save_with_profile(path,infos=None):
   recorded_save(path,infos);p=Path(str(path)+'.metadata.json');m=json.loads(p.read_text());m['external_training_adapter']=PROFILE;m['teacher_checkpoint_sha256']=file_hash(a.checkpoint);p.write_text(json.dumps(m,indent=2)+'\n')
  runner.save=save_with_profile
  runner.save(str(a.output/'initial.pt'));baseline=evaluate(env,policy,a.checkpoint,a.output/'validation_0000.json',profile='full_range');d['evaluations'].append({'updates':0,'gate':baseline['gate']});save()
  if baseline['gate']!='PASS' or reference['gate']!='PASS':d['status']='INITIALIZATION_REJECTED';save();return
  for _ in range(5):
   wrapper.replay.reset();runner.learn(10,init_at_random_ep_len=False);u=counts['updates_in_this_run'];assert preservation_check(policy,teacher)
   cp=a.output/f'segment_{u:04d}.pt';runner.save(str(cp));d.update(new_ppo_updates=u,optimizer_steps=lr['optimizer_steps'],teacher_and_noise_bitwise_preserved=True,extra_cost_sum=wrapper.extra_cost_sum,active_cost_env_steps=wrapper.active_cost_env_steps,targeted_bouts=wrapper.replay.targeted_bouts,total_bouts=wrapper.replay.total_bouts);save()
   result=evaluate(env,policy,cp,a.output/f'validation_{u:04d}.json',profile='full_range');d['evaluations'].append({'updates':u,'gate':result['gate']});save()
   if result['gate']!='PASS':d['status']='FUNCTIONAL_GATE_REJECTED';save();return
  d['status']='BUDGET_COMPLETED_NOT_PROMOTED';save()
 except BaseException as exc:d.update(status='ERROR',exception=repr(exc));save();raise
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
