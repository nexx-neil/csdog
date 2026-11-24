"""Bounded quasi-static wrench distribution for isolated reference diagnostics."""
import torch


def support_forces(foot_body,com_body,weights,gravity_body,velocity_body,angular_velocity_body,
                   requested_twist,height_error,parameters):
    mass=parameters["mass_kg"]
    desired=mass*(-gravity_body)
    desired[:,:2]+=mass*parameters["velocity_gain_s_inv"]*(requested_twist[:,:2]-velocity_body[:,:2])
    desired[:,2]+=mass*(parameters["height_gain_s_inv2"]*height_error-parameters["height_damping_s_inv"]*velocity_body[:,2])
    desired[:,2]=desired[:,2].clamp(.25*mass*9.81,1.75*mass*9.81)
    desired[:,:2]=desired[:,:2].clamp(-.3*mass*9.81,.3*mass*9.81)
    # Gravity direction encodes roll/pitch error without Euler-angle branches.
    attitude=torch.stack((gravity_body[:,1],-gravity_body[:,0]),dim=-1)/9.81
    moment=parameters["attitude_gain_nm_rad"]*attitude-parameters["attitude_damping_nm_s_rad"]*angular_velocity_body[:,:2]
    moment=moment.clamp(-3.,3.)
    share=weights/weights.sum(1,keepdim=True).clamp_min(1.)
    force_xy=share[:,:,None]*desired[:,None,:2]
    r=foot_body-com_body[None,None,:]
    centered=r[:,:,:2]-(share[:,:,None]*r[:,:,:2]).sum(1,keepdim=True)
    tangent=torch.stack((-centered[:,:,1],centered[:,:,0]),dim=-1)
    yaw_gain=parameters.get("yaw_gain_nm_s_rad",0.)
    transition=parameters.get("transition")
    if transition and transition.get("scope")=="backward":
        strength=transfer_strength(requested_twist,transition)
        yaw_gain=yaw_gain+(transition["backward_yaw_gain_nm_s_rad"]-yaw_gain)*strength
    yaw_moment=yaw_gain*(requested_twist[:,2]-angular_velocity_body[:,2])
    if "yaw_extra_moment_nm" in parameters:
        yaw_moment=yaw_moment+parameters["yaw_extra_moment_nm"]
    yaw_moment=yaw_moment.clamp(-2.,2.)
    radius=(share*centered.square().sum(-1)).sum(1).clamp_min(.001)
    force_xy+=share[:,:,None]*tangent*(yaw_moment/radius)[:,None,None]
    matrix=torch.stack((torch.ones_like(r[:,:,0]),r[:,:,1],-r[:,:,0]),dim=1)
    rhs=torch.stack((desired[:,2],moment[:,0]+(r[:,:,2]*force_xy[:,:,1]).sum(1),
                     moment[:,1]-(r[:,:,2]*force_xy[:,:,0]).sum(1)),dim=1)
    weighted=matrix*weights[:,None,:]
    dual=torch.linalg.solve(weighted@matrix.transpose(-1,-2)+.001*torch.eye(3,device=r.device,dtype=r.dtype),rhs[:,:,None])
    normal=(weights[:,:,None]*(matrix.transpose(-1,-2)@dual)).squeeze(-1).clamp_min(0)
    normal=normal*(desired[:,2:3]/normal.sum(1,keepdim=True).clamp_min(1.))
    magnitude=torch.linalg.vector_norm(force_xy,dim=-1).clamp_min(1e-6)
    friction_scale=(.5*normal/magnitude).clamp_max(1.)
    return torch.cat((force_xy*friction_scale[:,:,None],normal[:,:,None]),dim=-1)


def support_weights(phase, blend, stance_fraction, transition=None, twist=None):
    """Support allocation; default retains the existing controller exactly."""
    local=torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)
    if transition is None:
        progress=((local-stance_fraction)/(1-stance_fraction)).clamp(0,1)
        fade=(torch.minimum(progress,1-progress)/.1).clamp(0,1)
        fade=fade.square()*(3-2*fade)
        return 1-fade*blend[:,None]
    lead=transition['unload_lead_phase']
    reload=transition['reload_phase']
    invalid = (not bool(((stance_fraction > lead) & (stance_fraction < 1-reload)).all())
               if torch.is_tensor(stance_fraction)
               else not (0 < lead < stance_fraction and 0 < reload < 1-stance_fraction))
    if lead <= 0 or reload <= 0 or invalid:
        raise ValueError('Invalid support transition interval')
    def smooth(value):
        s=value.clamp(0,1)
        return (s.pow(3)*(10+s*(-15+6*s))).clamp(0,1)
    unload=1-smooth((local-(stance_fraction-lead))/lead)
    load=smooth((local-(1-reload))/reload)
    allocation=torch.where(local<stance_fraction,unload,load)
    early=1-blend[:,None]+blend[:,None]*allocation
    if transition.get('scope')=='backward':
        if twist is None:
            raise ValueError('Backward support allocation requires the applied twist')
        original=support_weights(phase,blend,stance_fraction)
        strength=transfer_strength(twist,transition)[:,None]
        mixed=(original+strength*(early-original)).clamp(0,1)
        return torch.where(strength>0,mixed,original)
    return early


def transfer_strength(twist, transition):
    start=transition['speed_start_mps']
    full=transition['speed_full_mps']
    if not 0 <= start < full:
        raise ValueError('Invalid backward support activation range')
    s=((-twist[:,0]-start)/(full-start)).clamp(0,1)
    strength=(s.pow(3)*(10+s*(-15+6*s))).clamp(0,1)
    mixture=(twist[:,1].abs()/.3+twist[:,2].abs()/.4).clamp(0,1)
    return strength*(1-mixture)
