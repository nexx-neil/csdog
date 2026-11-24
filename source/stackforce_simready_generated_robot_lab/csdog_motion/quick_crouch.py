"""Bounded short C2 height segments; four-foot support still required by supervisor."""
import torch
from .smooth_height import HeightSegments,SmoothHeightCommandState

class QuickHeightSegments(HeightSegments):
    def tick(self,dt,ids,goal,frozen):
        self.reset(ids[frozen],self.value[ids[frozen]])
        new=(~self.active[ids])&(~frozen)&((goal-self.end[ids]).abs()>1e-6)
        selected=ids[new];self.start[selected]=self.value[selected];self.end[selected]=goal[new];self.age[selected]=0
        # 6 cm in 0.4 s; smaller changes retain at least 0.25 s.
        self.duration[selected]=((self.end[selected]-self.start[selected]).abs()/.15).clamp_min(.25)
        self.active[selected]=True
        live=ids[self.active[ids]&~frozen];self.age[live]=torch.minimum(self.age[live]+dt,self.duration[live])
        s=(self.age[live]/self.duration[live]).clamp(0,1);distance=self.end[live]-self.start[live];duration=self.duration[live]
        self.value[live]=self.start[live]+distance*s.pow(3)*(10+s*(-15+6*s))
        self.velocity[live]=distance/duration*(30*s.square()*(1-s).square())
        self.acceleration[live]=distance/duration.square()*(60*s*(1-s)*(1-2*s))
        done=live[self.age[live]>=self.duration[live]-1e-6];self.value[done]=self.end[done];self.velocity[done]=0;self.acceleration[done]=0;self.active[done]=False
        return self.value[ids]

class QuickHeightCommands(SmoothHeightCommandState):
    def __init__(self,count,device='cpu',config=None):
        super().__init__(count,device,config)
        self.height_segments=QuickHeightSegments(count,self.cfg.nominal_height_m,device)
