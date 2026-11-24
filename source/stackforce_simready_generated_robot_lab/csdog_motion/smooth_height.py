"""Rest-to-rest C2 height segments with orderly queued reversals and fault freeze."""
import torch
from .commands import MotionCommandState


class HeightSegments:
    def __init__(self,count,nominal,device='cpu'):
        self.value=torch.full((count,),nominal,device=device)
        self.start=self.value.clone();self.end=self.value.clone()
        self.age=torch.zeros_like(self.value);self.duration=torch.ones_like(self.value)
        self.active=torch.zeros(count,device=device,dtype=torch.bool)
        self.velocity=torch.zeros_like(self.value);self.acceleration=torch.zeros_like(self.value)

    def reset(self,ids,height):
        for value in (self.value,self.start,self.end):value[ids]=height
        for value in (self.age,self.velocity,self.acceleration):value[ids]=0
        self.active[ids]=False

    def tick(self,dt,ids,goal,frozen):
        frozen_ids=ids[frozen]
        self.reset(frozen_ids,self.value[frozen_ids])
        new=(~self.active[ids]) & (~frozen) & ((goal-self.end[ids]).abs()>1e-6)
        selected=ids[new]
        self.start[selected]=self.value[selected];self.end[selected]=goal[new]
        self.age[selected]=0
        self.duration[selected]=((self.end[selected]-self.start[selected]).abs()/.06).clamp_min(.3)
        self.active[selected]=True
        live=ids[self.active[ids]&~frozen]
        self.age[live]=torch.minimum(self.age[live]+dt,self.duration[live])
        s=(self.age[live]/self.duration[live]).clamp(0,1)
        f=(s.pow(3)*(10+s*(-15+6*s))).clamp(0,1)
        distance=self.end[live]-self.start[live];duration=self.duration[live]
        self.value[live]=self.start[live]+distance*f
        self.velocity[live]=distance/duration*(30*s.square()*(1-s).square())
        self.acceleration[live]=distance/duration.square()*(60*s*(1-s)*(1-2*s))
        done=self.age[live]>=duration-1e-6
        completed=live[done];self.value[completed]=self.end[completed]
        self.velocity[completed]=0;self.acceleration[completed]=0;self.active[completed]=False
        return self.value[ids]


class SmoothHeightCommandState(MotionCommandState):
    def __init__(self,count,device='cpu',config=None):
        super().__init__(count,device,config)
        self.height_segments=HeightSegments(count,self.cfg.nominal_height_m,device)
        self.freeze_height=torch.zeros(count,device=device,dtype=torch.bool)

    def reset(self,ids=None):
        ids=torch.arange(len(self.phase),device=self.device) if ids is None else ids
        super().reset(ids)
        if hasattr(self,'height_segments'):
            self.height_segments.reset(ids,self.cfg.nominal_height_m);self.freeze_height[ids]=False

    def tick(self,dt,ids=None,foot_contact=None):
        ids=torch.arange(len(self.phase),device=self.device) if ids is None else ids
        goal=self.request[ids,3].clone()
        # Safety freeze overrides smooth completion and discards queued posture.
        frozen=self.freeze_height[ids]
        if frozen.any():self.height_segments.reset(ids[frozen],self.applied[ids[frozen],3])
        self.request[ids,3]=self.height_segments.tick(dt,ids,goal,frozen)
        super().tick(dt,ids,foot_contact)
        self.request[ids,3]=goal
