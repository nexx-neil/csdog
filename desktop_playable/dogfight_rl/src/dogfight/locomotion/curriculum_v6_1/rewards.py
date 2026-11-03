"""Continuous, translation-conditioned swing guidance with raw physical evidence."""
import torch
from ..curriculum_v6.rewards import signed_progress,terms

def guidance(clearance,raw_force,shin,contact,air,excursion,relative_v,progress):
    support=contact.sum(-1)
    valid=(~contact)&(raw_force<1.)&(~shin)&(clearance>.015)&(air<.6)
    height=((clearance-.008)/.022).clamp(0,1)
    travel=(excursion/.04).clamp(0,1)
    swing_speed=(relative_v/.15).clamp(0,1)
    # No payment for the 20–40ms fragments observed in V6. Guidance ramps
    # continuously during sustained flight, before the landing event.
    duration=((air-.04)/.04).clamp(0,1)
    return (valid*height*travel*swing_speed*duration).mean(-1)*(support>=1)*(support<=3)*progress.clamp(0,1)

def gait_guide(env):
    from ..spot_v2.contacts import contact_state
    from .contacts import physical_events
    from isaaclab.utils.math import quat_apply_inverse
    s=contact_state(env);r=env.scene['robot'];c=env.command_manager.get_command('base_velocity')
    key=env.common_step_counter
    if getattr(env,'_v61_guide_key',None)==key:return env._v61_guide_value
    env._v61_guide_key=key
    q=r.data.root_quat_w[:,None,:].expand(-1,4,-1)
    relative=quat_apply_inverse(q,s.tip_position-r.data.root_pos_w[:,None,:])[:,:,0]
    vel=quat_apply_inverse(q,s.tip_velocity-r.data.root_lin_vel_w[:,None,:])[:,:,0]
    if not hasattr(env,'_v61_liftoff'):env._v61_liftoff=relative.clone()
    reset=(env.episode_length_buf<=1)[:,None]
    env._v61_liftoff=torch.where(s.contact|reset,relative,env._v61_liftoff)
    progress=signed_progress(c[:,0],r.data.root_lin_vel_b[:,0])*(c[:,0].abs()>.04)
    env._v61_guide_value=guidance(s.clearance,s.raw_force,s.shin,s.contact,physical_events(env).air_ticks.float()*.002,
        (relative-env._v61_liftoff)*c[:,0,None].sign(),vel*c[:,0,None].sign(),progress)
    return env._v61_guide_value


def landing_motion_gate(landings,excursion,progress,moving):
    # Vertical-only lifting has zero return even when another leg drags the body.
    return (landings&(excursion>.02)).float().mean(-1)*progress.clamp(0,1)*moving

def completed_swing(env):
    from .contacts import physical_events
    from isaaclab.utils.math import quat_apply_inverse
    s=physical_events(env);r=env.scene['robot'];c=env.command_manager.get_command('base_velocity')
    if not hasattr(s.raw,'tip_position'):s.raw.update()  # First reward call can install the verifier after physics.
    q=r.data.root_quat_w[:,None,:].expand(-1,4,-1)
    relative=quat_apply_inverse(q,s.raw.tip_position-r.data.root_pos_w[:,None,:])[:,:,:2]
    if not hasattr(env,'_v61_landing_origin'):env._v61_landing_origin=relative.clone()
    reset=(env.episode_length_buf<=1)[:,None,None]
    env._v61_landing_origin=torch.where(reset,relative,env._v61_landing_origin)
    desired=torch.stack((c[:,0,None]-c[:,2,None]*relative[:,:,1],c[:,2,None]*relative[:,:,0]),-1)
    direction=desired/desired.norm(dim=-1,keepdim=True).clamp_min(.04)
    excursion=((relative-env._v61_landing_origin)*direction).sum(-1)
    progress=terms(c,r.data.root_lin_vel_b,r.data.root_ang_vel_b[:,2])[0]
    value=landing_motion_gate(s.landings,excursion,progress,c.norm(dim=-1)>.04)
    env._v61_landing_origin=torch.where(s.raw.contact[:,:,None],relative,env._v61_landing_origin)
    return value
