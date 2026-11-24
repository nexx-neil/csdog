"""Measured sphere/edge support with explicit lifetime in a scheduled stance."""
from dataclasses import dataclass,asdict
import torch
from .contact_tick_preview import contract as parent_contract
TAG='csdog_measured_edge_foothold_obs175_v56'

@dataclass(frozen=True)
class PatchConfig:
    sphere_radius_m:float=.018
    minimum_vertical_force_n:float=1.
    minimum_ray_disagreement_m:float=.005
    minimum_ray_joint_margin_rad:float=.03

def measured_patch(points,normal_forces,ray_heights,cfg=None):
    """Equivalent bottom height: mean contact point + R*normal_z - R.

    Resultant normal approximates a multi-point contact normal. Use only a
    positive loaded contact and >5mm disagreement; no fictitious contact on NaN.
    """
    c=cfg or PatchConfig()
    if points.shape!=normal_forces.shape or points.shape!=(*ray_heights.shape,3):raise ValueError('Contact/ray shapes differ')
    norm=normal_forces.norm(dim=-1)
    valid=torch.isfinite(points).all(-1)&torch.isfinite(normal_forces).all(-1)&torch.isfinite(ray_heights)&(normal_forces[...,2]>c.minimum_vertical_force_n)
    height=points[...,2]+c.sphere_radius_m*normal_forces[...,2]/norm.clamp_min(1e-6)-c.sphere_radius_m
    valid &= height>ray_heights+c.minimum_ray_disagreement_m
    return torch.where(valid,height,ray_heights),valid

class PatchMemory:
    def __init__(self,n,device='cpu',cfg=None):
        self.cfg=cfg or PatchConfig();self.active=torch.zeros(n,4,dtype=torch.bool,device=device)
        self.height=torch.zeros(n,4,device=device);self.xy=torch.zeros(n,4,2,device=device);self.last_tick=-1
    def reset(self,ids):
        self.active[ids]=False;self.height[ids]=0.;self.xy[ids]=0.
    def update(self,tick,stance,points,forces,actual_rays,foot_positions,unsafe_ray,active_env):
        if tick==self.last_tick:return self.active
        height,edge=measured_patch(points,forces,actual_rays,self.cfg)
        self.active &= stance&active_env[:,None]
        enter=~self.active&stance&edge&unsafe_ray&active_env[:,None]
        self.height=torch.where(enter,height,self.height)
        self.xy=torch.where(enter[...,None],foot_positions[...,:2],self.xy)
        self.active |= enter;self.last_tick=tick
        return self.active
    def continuing(self,phase,tau,period_s,duty):
        local=torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)
        # Do not reuse this anchor after a future liftoff and touchdown.
        return self.active&(local+tau/period_s<duty)

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=56,compatibility_tag=TAG)
    d['measured_contact_patch']={**asdict(PatchConfig()),'sensor':'four single-body contact-point sensors filtered to physical terrain Mesh; average contact point and resultant normal force; noiseless simulation only','activation':'loaded contact + equivalent support height > actual-foot-center vertical ray by5mm + current basic ray reference error>50um or joint margin<30mrad','reference':'hold measured actual foot-center worldXY and equivalent support height until scheduled liftoff, including transient contact loss; no force invented during contact loss','datum':'replace raw actual foot ray by held equivalent support height only for activated feet; actual measured normal force still determines support averaging','forecast':'same stored foothold only until this stance ends; other legs/future swings retain v55 reference','clock':'memory updates once per physical control counter; subset reset clears anchors','measurement_limits':'resultant-normal sphere reconstruction is an estimate, not exact multi-contact geometry; original physical/evaluation height and all hard limits unchanged','neural_transfer':'same175 tensors, explicit policy-only controller transfer; no new learning'}
    return d
