"""A measured worldXYZ stance foothold, independent of commanded root-height lag."""
import torch
from .contact_patch import PatchMemory,measured_patch,contract as parent_contract
TAG='csdog_world_stance_foothold_obs175_v57'
class FootholdMemory(PatchMemory):
    def __init__(self,n,device='cpu',cfg=None):
        super().__init__(n,device,cfg);self.xyz=torch.zeros(n,4,3,device=device)
    def reset(self,ids):
        super().reset(ids);self.xyz[ids]=0.
    def update(self,tick,stance,points,forces,actual_rays,foot_positions,unsafe_ray,active_env,hard_invalid=None):
        if tick==self.last_tick:return self.active
        height,edge=measured_patch(points,forces,actual_rays,self.cfg)
        loaded=torch.isfinite(points).all(-1)&torch.isfinite(forces).all(-1)&torch.isfinite(foot_positions).all(-1)&(forces[...,2]>self.cfg.minimum_vertical_force_n)
        if hard_invalid is None:hard_invalid=torch.zeros_like(stance)
        self.active &= stance&active_env[:,None]
        enter=~self.active&stance&loaded&((edge&unsafe_ray)|hard_invalid)&active_env[:,None]
        self.height=torch.where(enter,height,self.height);self.xy=torch.where(enter[...,None],foot_positions[...,:2],self.xy);self.xyz=torch.where(enter[...,None],foot_positions,self.xyz)
        self.active|=enter;self.last_tick=tick
        return self.active

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=57,compatibility_tag=TAG)
    d['measured_contact_patch']['reference']='for activated loaded stance feet, hold actual measured foot-center worldXYZ until scheduled liftoff; execution transforms from actual root pose; common body-height support force remains active and bounded'
    d['measured_contact_patch']['activation']='v56 edge/near-margin gate OR positive measured contact with basic ray-reference IK error>50um; non-edge merely near-margin cases remain unchanged'
    d['measured_contact_patch']['forecast']='hold same worldXYZ until this stance ends; candidate body goal uses nominal+predicted datum+response-aware automatic height, while execution uses actual root pose; this deliberately distinguishes planned body height from measured body height'
    return d
