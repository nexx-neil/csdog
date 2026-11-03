"""Spot kernels with measured distal-contact timing, true point velocities and command gating.
NVIDIA BSD-3-Clause attribution and license: ../THIRD_PARTY_NOTICES.md, ../LICENSE.NVIDIA.
"""
import torch
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp import GaitReward
from .contacts import contact_state

def moving(env):
 c=env.command_manager.get_command('base_velocity')
 return (c[:,:2].norm(dim=-1)>.04)|(c[:,2].abs()>.12)

def slip(env):
 s=contact_state(env)
 # Official Spot uses SUM of speed norms, not squared norms.
 return (s.velocity[:,:,:2].norm(dim=-1)*s.contact).sum(-1)

def air_time(env):
 s=contact_state(env)
 # Reward only completed, genuinely lifted swings lasting 0.10--0.40s.
 # minimum clearance reached during swing is not enough; track peak.
 if not hasattr(s,'peak'):s.peak=torch.zeros_like(s.force)
 s.peak[env.episode_length_buf<=1]=0.
 s.peak=torch.maximum(s.peak,s.clearance)
 t=s.data.last_air_time
 reward=(s.first&(t>.10)&(t<.40)&(s.peak>.02)&~s.shin).float()*torch.clamp(t-.08,0.,.18)
 s.peak=torch.where(s.contact,0.,s.peak)
 return reward.sum(-1)*moving(env)

def clearance(env,target_height=.03):
 s=contact_state(env)
 swing=(s.raw_force<1.)&~s.shin
 speed=s.tip_velocity[:,:,:2].norm(dim=-1)
 return (torch.exp(-((s.clearance-target_height)/.015)**2)*torch.tanh(5.*speed)*swing).sum(-1)*moving(env)

def stand_still(env):
 r=env.scene['robot'];stop=~moving(env)
 return (torch.linalg.norm(r.data.joint_pos-r.data.default_joint_pos,dim=-1)+
  4.*r.data.root_lin_vel_b[:,:2].square().sum(-1)+r.data.root_ang_vel_b[:,2].square()+.02*r.data.joint_vel.square().sum(-1))*stop

def saturation(env):
 a=getattr(env,'_raw_policy_action',env.action_manager.action)
 return torch.relu(a.abs()-.9).square().sum(-1)

class DistalGaitReward(GaitReward):
 """Reuse all six official time kernels; substitute verified 50Hz distal clocks.

 Pure yaw, zero command and slow lateral commands do not receive trot pressure.
 """
 def __init__(self,cfg,env):
  super().__init__(cfg,env)
  self.synced_feet_pairs=[[0,3],[1,2]] # adapter order LF RF LR RR
 def __call__(self,env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg):
  s=contact_state(env);original=self.contact_sensor;self.contact_sensor=s
  try:value=super().__call__(env,std,max_err,velocity_threshold,synced_feet_pair_names,asset_cfg,sensor_cfg)
  finally:self.contact_sensor=original
  c=env.command_manager.get_command('base_velocity')
  gate=(c[:,:2].norm(dim=-1)>.15)&(c[:,0].abs()>.10)&(c[:,2].abs()<.35)&~s.shin.any(-1)&(s.contact|(s.clearance>.01)).all(-1)
  return value*gate
