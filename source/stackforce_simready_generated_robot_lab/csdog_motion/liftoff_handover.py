"""A measured swing start after an exceptional remembered stance foothold."""
import torch
from .stance_preview_rank import contract as parent_contract

TAG='csdog_measured_liftoff_handover_obs175_v62'
MAX_OFFSET_M=.05

def local_phase(phase):
    return torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)

def fade(local,duty):
    s=((local-duty[:,None])/(1-duty[:,None])/.5).clamp(0,1)
    return 1-s.pow(3)*(10+s*(-15+6*s))

class LiftOffMemory:
    def __init__(self,n,device='cpu'):
        self.was_patch=torch.zeros(n,4,dtype=torch.bool,device=device)
        self.active=self.was_patch.clone();self.offset=torch.zeros(n,4,3,device=device)
        self.last_tick=-1;self.events=0;self.peak_offset_m=0.
    def reset(self,ids):
        self.was_patch[ids]=False;self.active[ids]=False;self.offset[ids]=0.
    def prepare(self,tick,phase,stance,patch,preferred_world,actual_world,duty):
        if tick==self.last_tick:return self.forecast(phase,0.,.5,duty)
        local=local_phase(phase);weight=fade(local,duty)
        self.active &= ~stance
        enter=self.was_patch&~stance&~self.active
        if enter.any():
            if (weight[enter]<.1).any():raise RuntimeError('Measured liftoff handover arrived after its allowed swing window')
            offset=(actual_world-preferred_world)/weight.clamp_min(.1)[:,:,None]
            if not torch.isfinite(offset[enter]).all():raise RuntimeError('Nonfinite measured liftoff target')
            size=offset.norm(dim=-1)
            if (size[enter]>MAX_OFFSET_M).any():raise RuntimeError('Measured liftoff correction exceeds5cm bound')
            self.offset=torch.where(enter[:,:,None],offset,self.offset)
            self.events+=int(enter.sum());self.peak_offset_m=max(self.peak_offset_m,float(size[enter].max()))
        self.active|=enter;self.was_patch.copy_(patch&stance);self.last_tick=tick
        return torch.where(self.active[:,:,None],self.offset*weight[:,:,None],torch.zeros_like(self.offset))
    def forecast(self,phase,tau,period,duty):
        current=local_phase(phase);future=current+tau/period
        keep=self.active&(future<1.)&(future>=duty[:,None])
        return torch.where(keep[:,:,None],self.offset*fade(future,duty)[:,:,None],torch.zeros_like(self.offset))

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=62,compatibility_tag=TAG)
    d['measured_liftoff_handover']={'activation':'only scheduled liftoff immediately following a remembered loaded stance; no generic gait replacement',
        'start':'first swing reference worldXYZ equals current measured physical foot center; offset capped at5cm or hard reject',
        'return':'offset fades with quintic smootherstep over first half of actual scheduled swing; original terrain-relative trajectory thereafter',
        'continuity_scope':'C2 offset envelope; does not claim globally C2 terrain rays, measured body motion or optimized targets',
        'preview':'current offset projected into future body pose until same swing ends; newly detected liftoff becomes available after current bounded height planning tick',
        'workspace':'same minimum stance projection and constrained swing allocator; all joint/torque/rate/IK and physical quality gates retained',
        'terrain_geometry_scope':'original noiseless rays and sampled clearance proxy retained; no full swept-collision guarantee',
        'learning':'same175 actor; no newPPO; default27/23 not changed'}
    return d
