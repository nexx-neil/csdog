"""Isolated first trot curriculum; prior mixed commands and actuator limits retained."""
import copy
from types import SimpleNamespace
import torch
from .commands import MotionCommandState
from .adaptive_speed import adaptive_reference,stance_fraction,valid_request as old_valid
from .clean_gait import clean_foot_reference

TAG='csdog_trot_course_obs76_v25'

def strength(twist):
    s=((twist[:,0]-.6)/.12).clamp(0,1)
    return s.pow(3)*(10+s*(-15+6*s))

def period(twist):
    return .5-.06*strength(twist)

def duty(twist):
    return stance_fraction(twist)-.11*strength(twist)

def valid_request(twist):
    extension=(twist[:,0]>=0)&(twist[:,0]<=.8+1e-6)&(twist[:,1:].abs()<=1e-6).all(1)
    return torch.isfinite(twist).all(1)&(old_valid(twist)|extension)

def reference(phase,twist,nominal,config,blend=None,height_delta=None):
    previous,old_stance=adaptive_reference(phase,twist,nominal,config,blend,height_delta)
    cfg=SimpleNamespace(period_s=period(twist)[:,None],stance_fraction=duty(twist)[:,None],clearance_m=config.clearance_m)
    target,stance=clean_foot_reference(phase,twist,nominal,cfg,blend,height_delta)
    active=twist[:,0]>.6
    return torch.where(active[:,None,None],target,previous),torch.where(active[:,None],stance,old_stance)

class TrotCommands(MotionCommandState):
    def tick(self,dt,ids=None,foot_contacts=None):
        ids=torch.arange(len(self.phase),device=self.device) if ids is None else ids
        super().tick(dt,ids,foot_contacts)
        # The clock and foot trajectories use exactly the same scheduled period.
        extra=dt*(1/period(self.applied[ids,:3])-1/self.cfg.gait_period_s)
        self.phase[ids]=torch.remainder(self.phase[ids]+extra,1.)

def contract(base,training=False):
    value=copy.deepcopy(base);value.update(schema_version=25,compatibility_tag=TAG)
    value['trot_course']={'forward_command_max_mps':.8,'period_s':[.5,.44],'duty':[.51,.4],
        'activation_vx_mps':[.6,.72],'blend':'C2 smoothstep; exact old reference when vx<=.6',
        'old_envelope_preserved':True,'not_a_measured_speed_claim':True,'actuator_limits_unchanged':True,
        'clock_period_matches_reference':True,'terrain':'flat only','training':training}
    value['command_envelope']['forward_single_axis_extension_mps']=.8
    value['learning_replay']={'low':.2,'legacy_mixed':.3,'previous_fast_axes':.2,'forward_trot':.3}
    return value

def sample_commands(count,device):
    cmd=torch.rand(count,3,device=device)*2-1;cmd*=cmd.new_tensor([.4,.3,.4]);cat=torch.rand(count,device=device)
    low=cat<.2;cmd[low]*=cmd.new_tensor([.375,1/3,.375])
    fast=(cat>=.5)&(cat<.7);idx=torch.where(fast)[0];axis=torch.randint(0,3,(len(idx),),device=device)
    cmd[idx]=0;cmd[idx,axis]=cmd.new_tensor([.5,.4,.8])[axis]*torch.empty(len(idx),device=device).uniform_(.7,1.)*torch.where(torch.rand(len(idx),device=device)<.5,-1.,1.)
    forward=cat>=.7;cmd[forward]=0;cmd[forward,0]=torch.empty(int(forward.sum()),device=device).uniform_(.6,.8)
    return cmd

def cases(holdout=False):
    speeds=[.63,.69,.77] if holdout else [.6,.7,.8]
    out=[{'name':'stand','profile':[[20.,[0,0,0]]],'protected':True}]
    out += [{'name':f'forward_{s:.2f}','profile':[[20.,[s,0,0]]],'protected':True} for s in speeds]
    out += [{'name':'trot_start_stop','profile':[[2.,[0,0,0]],[9.,[speeds[-1],0,0]],[20.,[0,0,0]]],'protected':False},
            {'name':'trot_to_turn','profile':[[7.,[speeds[-1],0,0]],[13.,[0,0,.8]],[20.,[0,-.4,0]]],'protected':False}]
    return out
