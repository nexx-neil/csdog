"""Recover a feasible stance reference from a recent real loaded contact."""
import torch
from .post_filter_contacts import PostFilterMemory,contract as parent_contract
from .contact_patch import measured_patch

TAG='csdog_recent_loaded_foothold_obs175_v64'
MAX_AGE_S=.06
MAX_DISTANCE_M=.03

class RecentContactMemory(PostFilterMemory):
    def __init__(self,n,device='cpu',cfg=None,control_dt=.02):
        super().__init__(n,device,cfg);self.control_dt=control_dt
        self.contact_tick=torch.full((n,4),-1000000000,dtype=torch.long,device=device)
        self.contact_valid=torch.zeros(n,4,dtype=torch.bool,device=device)
        self.contact_xyz=torch.zeros(n,4,3,device=device);self.contact_height=torch.zeros(n,4,device=device)
        self.archive_tick=-1;self.recent_bind_tick=-1;self.recent_events=0;self.max_recent_age_s=0.;self.max_recent_distance_m=0.
    def reset(self,ids):
        super().reset(ids);self.contact_valid[ids]=False;self.contact_tick[ids]=-1000000000;self.contact_xyz[ids]=0;self.contact_height[ids]=0
    def update(self,tick,stance,points,forces,actual_rays,foot_positions,unsafe_ray,active_env,hard_invalid=None):
        if tick!=self.archive_tick:
            height,_=measured_patch(points,forces,actual_rays,self.cfg)
            loaded=torch.isfinite(points).all(-1)&torch.isfinite(forces).all(-1)&torch.isfinite(foot_positions).all(-1)&torch.isfinite(actual_rays)&(forces[...,2]>self.cfg.minimum_vertical_force_n)&active_env[:,None]
            self.contact_xyz=torch.where(loaded[:,:,None],foot_positions,self.contact_xyz);self.contact_height=torch.where(loaded,height,self.contact_height)
            self.contact_tick=torch.where(loaded,torch.full_like(self.contact_tick,tick),self.contact_tick);self.contact_valid|=loaded;self.archive_tick=tick
        return super().update(tick,stance,points,forces,actual_rays,foot_positions,unsafe_ray,active_env,hard_invalid)
    def late_bind(self,tick,stance,points,forces,actual_rays,foot_positions,error,margin,active_env):
        if tick==self.recent_bind_tick:return torch.zeros_like(self.active)
        current=super().late_bind(tick,stance,points,forces,actual_rays,foot_positions,error,margin,active_env)
        age=(tick-self.contact_tick).to(foot_positions.dtype)*self.control_dt
        distance=(foot_positions-self.contact_xyz).norm(dim=-1)
        recent=self.contact_valid&(age>=0)&(age<=MAX_AGE_S+1e-6)&(distance<=MAX_DISTANCE_M)
        edge=self.contact_height>actual_rays+self.cfg.minimum_ray_disagreement_m
        unsafe=(error>.00005)|(edge&(margin<self.cfg.minimum_ray_joint_margin_rad))
        enter=~self.active&stance&active_env[:,None]&recent&unsafe
        self.height=torch.where(enter,self.contact_height,self.height);self.xy=torch.where(enter[:,:,None],self.contact_xyz[:,:,:2],self.xy);self.xyz=torch.where(enter[:,:,None],self.contact_xyz,self.xyz)
        self.active|=enter;self.recent_bind_tick=tick;self.recent_events+=int(enter.sum());self.late_events+=int(enter.sum())
        if enter.any():
            self.max_recent_age_s=max(self.max_recent_age_s,float(age[enter].max()));self.max_recent_distance_m=max(self.max_recent_distance_m,float(distance[enter].max()));self.peak_late_error_m=max(self.peak_late_error_m,float(error[enter].max()))
        return current|enter

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=64,compatibility_tag=TAG)
    d['recent_loaded_foothold']={'maximum_age_s':MAX_AGE_S,'maximum_actual_foot_displacement_m':MAX_DISTANCE_M,
        'record':'finite measured contact point,normal forceZ>1N,actual foot center and actual foot ray;also record real late-swing touchdown contacts',
        'activation':'after current filters, scheduled stance reference unreachable or edge near-margin;current loaded contact retains priority;otherwise use recent real loaded foothold',
        'not_current_support':'cache only constructs a desired foot target;body datum and support measurement still use current real forces;past force is never substituted',
        'lifetime':'same activated stance ends at scheduled liftoff;existing measured liftoff handover follows;subset reset clears archive',
        'workspace':'original0.5rad software target envelope and realURDF bounds,8radps target speed,12Nm torque,IK/quality gates unchanged',
        'clock':'integer control-counter age;archive and late binding each idempotent;no extra physics or filter ticks'}
    return d
