"""Bounded body-height preview experiment; no previous controller is modified."""
import copy
from dataclasses import dataclass
import torch
TAG='csdog_workspace_height_preview_obs175_v34'

@dataclass(frozen=True)
class HeightPlanConfig:
    maximum_offset_m:float=.03
    maximum_speed_mps:float=.12
    maximum_acceleration_mps2:float=.8
    response_radps:float=12.
    joint_reserve_rad:float=.01
    solve_tolerance_m:float=.00005
    preview_seconds:tuple=(0.,.06,.12,.18)
    replanning_steps:int=5
    candidates:int=13

def contract(parent):
    d=copy.deepcopy(parent);d.update(schema_version=34,compatibility_tag=TAG)
    d['height']['automatic_workspace_preview']={**HeightPlanConfig().__dict__,'preview_seconds':list(HeightPlanConfig().preview_seconds),'scope':'same measured static terrain rays; base swing reference at four future phases; fixed-twist pose extrapolation; one common bounded vertical body offset; no map-kind/path oracle','observation':'existing height-command difference/rate columns50/51 now carry effective automatic height target/rate','support':'effective height target in existing support force servo; actual measured support height remains unmodified','reference':'subtract common world-vertical offset from terrain-projected foot targets; unchanged ground query/XY/nominal lift and surplus allocator','limits':'all original IK, joint, target-rate, yaw and actuator limits retained','failure':'original hard IK rejection remains mandatory; no feasible preview is logged, not a claim of future feasibility'}
    return d

def select_height(error,margin,candidates,previous,cfg=None):
    cfg=cfg or HeightPlanConfig()
    good=((error<=cfg.solve_tolerance_m)&(margin>=cfg.joint_reserve_rad)).all(dim=(2,3))
    cost=candidates.abs()[None]+.25*(candidates[None]-previous[:,None]).abs()
    feasible_cost=torch.where(good,cost,torch.inf)
    # An infeasible forecast is advisory; the executed reference still has its hard guard.
    violation=(error/cfg.solve_tolerance_m+torch.relu(cfg.joint_reserve_rad-margin)/.01).amax(dim=(2,3))
    index=torch.where(good.any(1),feasible_cost.argmin(1),(violation+cost).argmin(1))
    return candidates[index],good.any(1)

class HeightCoordinator:
    def __init__(self,count,device='cpu',cfg=None):
        self.cfg=cfg or HeightPlanConfig();self.value=torch.zeros(count,device=device);self.velocity=self.value.clone();self.acceleration=self.value.clone();self.goal=self.value.clone()
    def reset(self,ids):
        for v in (self.value,self.velocity,self.acceleration,self.goal):v[ids]=0
    def tick(self,dt,active):
        c=self.cfg;acc=(c.response_radps**2*(self.goal-self.value)-2*c.response_radps*self.velocity).clamp(-c.maximum_acceleration_mps2,c.maximum_acceleration_mps2)
        vel=(self.velocity+dt*acc).clamp(-c.maximum_speed_mps,c.maximum_speed_mps)
        value=(self.value+dt*vel).clamp(-c.maximum_offset_m,c.maximum_offset_m)
        vel=torch.where((value>=c.maximum_offset_m)&(vel>0)|(value<=-c.maximum_offset_m)&(vel<0),0.,vel)
        self.acceleration=torch.where(active,(vel-self.velocity)/dt,self.acceleration)
        self.value=torch.where(active,value,self.value);self.velocity=torch.where(active,vel,self.velocity)
        return self.value
