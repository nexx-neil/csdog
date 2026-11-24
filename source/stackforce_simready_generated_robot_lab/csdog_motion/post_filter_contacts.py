"""Bind measured loaded footholds against final current-tick reference geometry."""
import math
import torch
from .stance_foothold import FootholdMemory
from .contact_patch import measured_patch
from .liftoff_handover import contract as parent_contract

TAG='csdog_post_filter_contact_timebase_obs175_v63'

def sensor_settings(physics_dt,old_period=.02,old_history=3):
    if not math.isfinite(physics_dt)or physics_dt<=0:raise ValueError('Positive physical dt required')
    if old_period<0 or old_history<0:raise ValueError('Invalid original sensor cadence')
    return {'update_period':0.,'history_length':max(old_history,math.ceil(old_history*old_period/physics_dt))}

class PostFilterMemory(FootholdMemory):
    def __init__(self,n,device='cpu',cfg=None):
        super().__init__(n,device,cfg);self.late_tick=-1;self.late_events=0;self.peak_late_error_m=0.
    def late_bind(self,tick,stance,points,forces,actual_rays,foot_positions,error,margin,active_env):
        if tick==self.late_tick:return torch.zeros_like(self.active)
        if tick!=self.last_tick:raise RuntimeError('Post-filter binding requires current-tick primary memory update')
        height,edge=measured_patch(points,forces,actual_rays,self.cfg)
        loaded=torch.isfinite(points).all(-1)&torch.isfinite(forces).all(-1)&torch.isfinite(foot_positions).all(-1)&(forces[...,2]>self.cfg.minimum_vertical_force_n)
        unsafe=(error>.00005)|(margin<self.cfg.minimum_ray_joint_margin_rad)
        enter=~self.active&stance&loaded&((edge&unsafe)|(error>.00005))&active_env[:,None]
        self.height=torch.where(enter,height,self.height);self.xy=torch.where(enter[:,:,None],foot_positions[:,:,:2],self.xy);self.xyz=torch.where(enter[:,:,None],foot_positions,self.xyz)
        self.active|=enter;self.late_tick=tick;self.late_events+=int(enter.sum())
        if enter.any():self.peak_late_error_m=max(self.peak_late_error_m,float(error[enter].max()))
        return enter

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=63,compatibility_tag=TAG)
    d['post_filter_foothold_binding']={'reason':'a positively loaded non-edge foot can become unreachable after current datum/height integrations;early predicate alone misses it',
        'clock':'one early binding pass for datum/preview plus one additive late binding pass after the same tick filters;each idempotent at physical counter;filters/motion advance only once',
        'measurement':'same finite real contact point,normal force>1N,actual foot/ray;no invented support',
        'activation':'same non-edge error>50um or edge/near-margin predicate against final current-tick datum and height',
        'execution':'frozen62 minimum vertical stance repair and measured liftoff handover;new late support enters common height forecast next tick',
        'limits_and_gates':'unchanged;no IK or force-consistency tolerance relaxation'}
    d['contact_sensor_timebase']={'primary_and_point_update_period_s':0.,'physics_dt_s':.005,'primary_history_samples':12,
        'original_primary_period_s':.02,'original_primary_history_samples':3,
        'history_scope':'at least original60ms nominal coverage;denser physical-step samples cannot erase an old20ms contact within that window',
        'reason':'avoid0.02s float32 timestamp threshold skipping a physical step after16s;sample both sources at each physics step',
        'agreement_gate_n':.001,'observation_dimension':175}
    return d
