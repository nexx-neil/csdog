"""Task-conditioned rewards; no motion-independent positive term on moving tasks."""
import torch

def signed_progress(command, actual, deadband=.04):
    active=command.abs()>deadband
    return torch.where(active,(actual*command.sign()/command.abs().clamp_min(deadband)).clamp(-1.,1.),0.)

def terms(command, velocity, yaw):
    x=command[:,0]; z=command[:,2]; mx=x.abs()>.04; mz=z.abs()>.04
    moving=mx|mz
    progress=(signed_progress(x,velocity[:,0])+signed_progress(z,yaw))/(mx.float()+mz.float()).clamp_min(1.)
    # Center tracking at the physically stationary baseline. This is diagnostic-friendly;
    # the separate signed progress term supplies the exploration objective.
    tx=torch.exp(-((velocity[:,0]-x)/.15).square())-torch.exp(-(x/.15).square())
    tz=torch.exp(-((yaw-z)/.3).square())-torch.exp(-(z/.3).square())
    tracking=(tx*mx+tz*mz)/(mx.float()+mz.float()).clamp_min(1.)
    unwanted=velocity[:,1].square()+velocity[:,0].square()*(~mx)+.25*yaw.square()*(~mz)
    stop=torch.exp(-velocity[:,:2].square().sum(-1)/.0025-yaw.square()/.01)*(~moving)
    return progress,tracking,unwanted,stop

def core(env, index):
    r=env.scene['robot'];c=env.command_manager.get_command('base_velocity')
    return terms(c,r.data.root_lin_vel_b,r.data.root_ang_vel_b[:,2])[index]

def stability(env):
    d=env.scene['robot'].data
    return d.projected_gravity_b[:,:2].square().sum(-1)+.05*d.root_ang_vel_b[:,:2].square().sum(-1)+.2*d.root_lin_vel_b[:,2].square()

def posture(env):
    d=env.scene['robot'].data;c=env.command_manager.get_command('base_velocity')
    return (d.joint_pos-d.default_joint_pos).square().sum(-1)*torch.where(c.norm(dim=-1)<.04,3.,1.)

def slip(env):
    from ..spot_v2.contacts import contact_state
    s=contact_state(env)
    return (s.velocity[:,:,:2].square().sum(-1)*s.contact).sum(-1)/s.contact.sum(-1).clamp_min(1)

def swing(env):
    from ..spot_v2.contacts import contact_state
    s=contact_state(env);moving=env.command_manager.get_command('base_velocity').norm(dim=-1)>.04
    # Pay only completed, genuine distal-foot swing landings, not permanent suspension,
    # foot motion while in contact, or infinitesimal contact chatter.
    if not hasattr(env,'_v6_peak'):env._v6_peak=torch.zeros_like(s.clearance)
    env._v6_peak[env.episode_length_buf<=1]=0.
    env._v6_peak=torch.maximum(env._v6_peak,s.clearance)
    good=s.first&(s.data.last_air_time>=.06)&(s.data.last_air_time<=.6)&(env._v6_peak>.015)&(~s.shin)
    env._v6_peak=torch.where(s.contact,0.,env._v6_peak)
    return good.float().mean(-1)*moving
