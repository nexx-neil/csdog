"""Command-only smooth stopping weight: no speed escape from the stand multiplier."""
import torch

def stop_weight(command,linear_deadband=.02,linear_full_motion=.08,yaw_deadband=.04,yaw_full_motion=.16):
 """C1 continuous, exactly one at zero, exactly zero outside the low-command band."""
 linear=command[:,:2].norm(dim=-1)
 l=((linear-linear_deadband)/(linear_full_motion-linear_deadband)).clamp(0.,1.)
 a=((command[:,2].abs()-yaw_deadband)/(yaw_full_motion-yaw_deadband)).clamp(0.,1.)
 # Product keeps smoothness at the intersection of translation/yaw transition bands.
 return (1.-l*l*(3.-2.*l))*(1.-a*a*(3.-2.*a))

def command_stop_weight(env,tau=.25):
 target=stop_weight(env.command_manager.get_command('base_velocity'))
 key=env.common_step_counter
 if not hasattr(env,'_v4_stop_w'):
  env._v4_stop_w=target.clone();env._v4_stop_key=None
 if env._v4_stop_key!=key:
  alpha=1.-__import__('math').exp(-env.step_dt/tau)
  old=env._v4_stop_w
  ramp=old+alpha*(target-old)
  # Release immediately for a moving command; ramp only into stronger stop control.
  env._v4_stop_w=torch.where(target<old,target,ramp)
  env._v4_stop_w=torch.where(env.episode_length_buf<=1,target,env._v4_stop_w)
  env._v4_stop_key=key
 return env._v4_stop_w

def joint_position_penalty(env,stand_still_scale=5.):
 r=env.scene['robot'];w=command_stop_weight(env)
 return (r.data.joint_pos-r.data.default_joint_pos).norm(dim=-1)*(1.+(stand_still_scale-1.)*w)

def stand_motion_penalty(env):
 r=env.scene['robot'];w=command_stop_weight(env)
 # Every term is monotone in unwanted actual motion; moving commands outside band have zero cost.
 return w*(4.*r.data.root_lin_vel_b[:,:2].square().sum(-1)+r.data.root_ang_vel_b.square().sum(-1)
           +.03*r.data.joint_vel.square().sum(-1)+.05*(env.action_manager.action-env.action_manager.prev_action).square().sum(-1))

def gait_phase_eligible(contact,clearance,raw_force):
 count=contact.sum(-1)
 swing=(~contact)&(clearance>.005)&(raw_force<1.)
 return (count>=1)&(count<=3)&swing.any(-1)

