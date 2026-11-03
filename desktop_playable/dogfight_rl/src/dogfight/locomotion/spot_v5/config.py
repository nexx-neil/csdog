import torch
from isaaclab.envs.mdp.commands import UniformVelocityCommand
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp import GaitReward
from ..spot_v4.config import V4EnvCfg,V4PPOCfg
from ..spot_v4.rewards import joint_position_penalty,gait_phase_eligible
from ..spot_v2.contacts import contact_state

class BalancedVelocityCommand(UniformVelocityCommand):
 def _resample_command(self,env_ids):
  n=len(env_ids); device=self.device
  k=torch.multinomial(torch.tensor(self.cfg.v5_options['probabilities'],device=device),n,replacement=True)
  v=torch.zeros(n,3,device=device); opts=self.cfg.v5_options
  def uniform(bounds):return torch.empty(n,device=device).uniform_(*bounds)
  f=uniform(opts['forward_range']);b=uniform(opts['backward_range']);lat=uniform(opts['lateral_range']);yaw=uniform(opts['yaw_range'])
  v[:,0]=torch.where(k==1,f,torch.where(k==2,b,0.))
  v[:,1]=torch.where(k==3,lat,torch.where(k==4,-lat,0.))
  v[:,2]=torch.where(k==5,yaw,torch.where(k==6,-yaw,0.))
  angle=uniform([-torch.pi,torch.pi]);speed=uniform(opts['forward_range'])
  v[:,0]=torch.where(k==7,speed*torch.cos(angle),v[:,0]);v[:,1]=torch.where(k==7,speed*torch.sin(angle),v[:,1])
  self.vel_command_b[env_ids]=v;self.is_standing_env[env_ids]=(k==0)
  if not hasattr(self,'sample_counts'):self.sample_counts=torch.zeros(8,device=device,dtype=torch.long)
  self.sample_counts+=torch.bincount(k,minlength=8)

def translating(env):
 c=env.command_manager.get_command('base_velocity')
 return (c[:,:2].norm(dim=-1)>.08)&(c[:,2].abs()<.12)

def position_cost(env,stand_still_scale=5.,translation_scale=1.):
 value=joint_position_penalty(env,stand_still_scale)
 return value*torch.where(translating(env),translation_scale,1.)

def smoothness_cost(env,translation_scale=1.):
 value=(env.action_manager.action-env.action_manager.prev_action).norm(dim=-1)
 return value*torch.where(translating(env),translation_scale,1.)

class TranslationGait(GaitReward):
 def __init__(self,cfg,env):
  super().__init__(cfg,env);self.synced_feet_pairs=[[0,3],[1,2]]
 def __call__(self,env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg):
  s=contact_state(env);sensor=self.contact_sensor;self.contact_sensor=s
  try:value=super().__call__(env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg)
  finally:self.contact_sensor=sensor
  c=env.command_manager.get_command('base_velocity')
  applicable=(c[:,:2].norm(dim=-1)>.12)&(c[:,2].abs()<.35)
  trustworthy=(s.contact|((s.raw_force<1.)&(s.clearance>.005))).all(-1)&~s.shin.any(-1)
  env._gait_applicable=applicable;env._gait_trustworthy=trustworthy
  return value*applicable*trustworthy*gait_phase_eligible(s.contact,s.clearance,s.raw_force)

def build(options,num_envs,seed,device='cuda:0'):
 cfg=V4EnvCfg();cfg.scene.num_envs=num_envs;cfg.seed=seed;cfg.sim.device=device
 a=V4PPOCfg();a.seed=seed;a.device=device
 if options['commands']['distribution']=='uniform':
  ranges=options['commands'].get('uniform_ranges',{})
  for key in ['lin_vel_x','lin_vel_y','ang_vel_z']:
   if key in ranges:setattr(cfg.commands.base_velocity.ranges,key,tuple(ranges[key]))
  cfg.commands.base_velocity.rel_standing_envs=options['commands'].get('standing_probability',.1)
 if 'resampling_time_range' in options['commands']:cfg.commands.base_velocity.resampling_time_range=tuple(options['commands']['resampling_time_range'])
 for name in ['learning_rate','schedule','entropy_coef','desired_kl']:setattr(a.algorithm,name,options['ppo'][name])
 a.policy.init_noise_std=options['ppo']['init_noise_std']
 if options['commands']['distribution']=='balanced':
  cfg.commands.base_velocity.class_type=BalancedVelocityCommand
  cfg.commands.base_velocity.v5_options=options['commands']
 r=options['rewards']
 for key,name in [('linear_velocity','base_linear_velocity'),('angular_velocity','base_angular_velocity'),('joint_position','joint_pos'),('action_smoothness','action_smoothness'),('gait','gait'),('foot_slip','foot_slip')]:getattr(cfg.rewards,name).weight=r[key]
 if r['translation_joint_position']!=r['joint_position']:
  cfg.rewards.joint_pos.func=position_cost
  cfg.rewards.joint_pos.params=dict(stand_still_scale=5.,translation_scale=r['translation_joint_position']/r['joint_position'])
 if r['translation_action_smoothness']!=r['action_smoothness']:
  cfg.rewards.action_smoothness.func=smoothness_cost
  cfg.rewards.action_smoothness.params=dict(translation_scale=r['translation_action_smoothness']/r['action_smoothness'])
 if r['repair_lateral_gate']:cfg.rewards.gait.func=TranslationGait
 return cfg,a
