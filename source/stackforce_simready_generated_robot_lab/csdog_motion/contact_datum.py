"""Measured support-contact height, not a plane estimate or terrain-kind oracle."""
import copy
from dataclasses import dataclass
import torch

TAG='csdog_contact_datum_workspace_obs175_v49'

@dataclass(frozen=True)
class DatumConfig:
    response_radps:float=12.
    maximum_speed_mps:float=.08
    maximum_acceleration_mps2:float=.4
    maximum_measured_offset_m:float=.03
    minimum_contact_count:int=2

def measured_goal(root_ground,foot_ground,normal_force,cfg=None):
    cfg=cfg or DatumConfig()
    if foot_ground.shape!=normal_force.shape or foot_ground.shape!=(len(root_ground),4):
        raise ValueError('Expected root ground and four measured foot grounds/forces')
    if not all(torch.isfinite(v).all()for v in (root_ground,foot_ground,normal_force)):
        raise ValueError('Nonfinite support measurement')
    contact=normal_force>1.
    good=contact.sum(1)>=cfg.minimum_contact_count
    mean=(foot_ground*contact).sum(1)/contact.sum(1).clamp_min(1)
    goal=root_ground+(mean-root_ground).clamp(-cfg.maximum_measured_offset_m,cfg.maximum_measured_offset_m)
    return goal,good

class ContactDatum:
    def __init__(self,count,device='cpu',cfg=None):
        self.cfg=cfg or DatumConfig();self.value=torch.zeros(count,device=device)
        self.velocity=self.value.clone();self.acceleration=self.value.clone();self.goal=self.value.clone()
        self.valid=torch.zeros(count,device=device,dtype=torch.bool);self.last_tick=-1
    def reset(self,ids):
        self.valid[ids]=False;self.velocity[ids]=0;self.acceleration[ids]=0
    def update(self,root_ground,foot_ground,normal_force,tick,dt,active):
        if dt<=0:raise ValueError('Positive dt required')
        invalid=~self.valid
        self.value[invalid]=root_ground[invalid];self.goal[invalid]=root_ground[invalid]
        self.velocity[invalid]=0;self.acceleration[invalid]=0;self.valid[invalid]=True
        if tick==self.last_tick:return self.value
        proposed,measured=measured_goal(root_ground,foot_ground,normal_force,self.cfg)
        self.goal=torch.where(measured&active,proposed,self.goal)
        cfg=self.cfg
        acceleration=(cfg.response_radps**2*(self.goal-self.value)-2*cfg.response_radps*self.velocity).clamp(-cfg.maximum_acceleration_mps2,cfg.maximum_acceleration_mps2)
        velocity=(self.velocity+dt*acceleration).clamp(-cfg.maximum_speed_mps,cfg.maximum_speed_mps)
        self.acceleration=torch.where(active,(velocity-self.velocity)/dt,self.acceleration)
        self.value=torch.where(active,self.value+dt*velocity,self.value)
        self.velocity=torch.where(active,velocity,self.velocity);self.last_tick=tick
        return self.value

def contract(parent):
    d=copy.deepcopy(parent);d.update(schema_version=49,compatibility_tag=TAG)
    d['height']['contact_datum']={**vars(DatumConfig()),
        'measurement':'equal mean of actual contact-foot ground rays, contact normal force >1N; at least2 contacts; otherwise retain previous goal',
        'not_a_plane_estimate':True,'frame':'bounded velocity/acceleration world-height datum; initialize from measured root-ground ray',
        'preview':'current filtered datum plus measured datum velocity times horizon; same bounded common-height response as v36',
        'reference':'actual landing ground minus filtered support datum minus automatic height offset',
        'force_target':'nominal + automatic offset + filtered datum minus actual root-ground; physical height measurement unchanged',
        'observation50':'effective root-ground-relative height command difference',
        'observation51':'world height-goal rate: datum velocity plus automatic offset velocity; no derivative of discontinuous root-ground ray',
        'limits':'original IK/joint/target-speed/actuator and auto-height caps unchanged; actual root-ground-relative evaluation unchanged',
        'neural_transfer':'explicit same175 tensors, no optimizer; not semantic compatibility'}
    return d
