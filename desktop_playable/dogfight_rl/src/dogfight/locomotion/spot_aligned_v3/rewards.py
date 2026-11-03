"""Spot kernels adapted only where CSDog has no separate foot body.
NVIDIA BSD-3-Clause attribution: ../THIRD_PARTY_NOTICES.md and ../LICENSE.NVIDIA.
"""
import torch
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp import GaitReward
from ..spot_v2.contacts import contact_state

def is_moving(env):
 c=env.command_manager.get_command('base_velocity')
 return (c[:,:2].norm(dim=-1)>.04)|(c[:,2].abs()>.12)

def air_time_reward(env,mode_time=.25,velocity_threshold=.1):
 s=contact_state(env);air=s.data.current_air_time;stance=s.data.current_contact_time
 maximum=torch.maximum(air,stance);bounded=maximum.clamp(max=mode_time)
 # Official dense mode-time kernel. Geometric veto excludes force-free near-ground flicker.
 known=s.contact|((s.raw_force<1.)&(s.clearance>.005))
 moving_reward=torch.where(maximum<mode_time,bounded,0.)*known
 standing_reward=(stance-air).clamp(-mode_time,mode_time)
 return torch.where(is_moving(env)[:,None],moving_reward,standing_reward).sum(-1)

def air_time_variance_penalty(env):
 s=contact_state(env)
 return s.data.last_air_time.clamp(max=.5).var(-1)+s.data.last_contact_time.clamp(max=.5).var(-1)

def foot_clearance_reward(env,target_height=.03,std=.0045,tanh_mult=2.):
 s=contact_state(env)
 error=(s.clearance-target_height).square()
 speed=torch.tanh(tanh_mult*s.tip_velocity[:,:,:2].norm(dim=-1))
 return torch.exp(-(error*speed).sum(-1)/std)

def foot_slip_penalty(env,threshold=1.):
 s=contact_state(env)
 return (s.velocity[:,:,:2].norm(dim=-1)*s.contact*(s.force>threshold)).sum(-1)

class DistalGaitReward(GaitReward):
 def __init__(self,cfg,env):
  super().__init__(cfg,env)
  self.synced_feet_pairs=[[0,3],[1,2]]
 def __call__(self,env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg):
  s=contact_state(env);sensor=self.contact_sensor;self.contact_sensor=s
  try:value=super().__call__(env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg)
  finally:self.contact_sensor=sensor
  c=env.command_manager.get_command('base_velocity')
  # Translation only; yaw and low lateral commands are free to learn other contact sequences.
  applicable=(c[:,:2].norm(dim=-1)>.12)&(c[:,0].abs()>.08)&(c[:,2].abs()<.35)
  trustworthy=(s.contact|((s.raw_force<1.)&(s.clearance>.005))).all(-1)&~s.shin.any(-1)
  env._gait_applicable=applicable;env._gait_trustworthy=trustworthy
  return value*applicable*trustworthy
