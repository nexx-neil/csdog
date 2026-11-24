"""C2 return stroke with a finite velocity plateau; old <=.8 gait is exact."""
import copy
from types import SimpleNamespace
import torch
from . import trot_course as previous
from .trot_extension_flight import strength, valid_request, sample_commands, cases
from .clean_gait import clean_foot_reference

TAG='csdog_forward_trot_plateau_return_obs76_v45'
RAMP=.2

def period(twist):
    return previous.period(twist)-.04*strength(twist)

def duty(twist):
    return previous.duty(twist)

def swing_displacement(progress, vx, swing_time, stance_fraction=.4, ramp=RAMP):
    """Integrate a C1 velocity: -vx -> plateau -> -vx; position is C2.

    Both end velocities match a stationary stance foot. The plateau velocity is
    determined by the exact return distance, rather than arbitrary clipping.
    """
    if not 0<ramp<.5:
        raise ValueError('Return ramp must occupy less than half the swing')
    s=progress.clamp(0,1)
    plateau=vx*(stance_fraction/(1-stance_fraction)+ramp)/(1-ramp)
    def integral(u):return u.pow(3)-.5*u.pow(4)
    u=(s/ramp).clamp(0,1)
    w=((s-(1-ramp))/ramp).clamp(0,1)
    first=swing_time*(-vx*s+(plateau+vx)*ramp*integral(u))
    at_ramp=swing_time*(-vx*ramp+(plateau+vx)*ramp*.5)
    middle=at_ramp+swing_time*plateau*(s-ramp)
    at_last=at_ramp+swing_time*plateau*(1-2*ramp)
    last=at_last+swing_time*(plateau*(s-1+ramp)-(plateau+vx)*ramp*integral(w))
    return torch.where(s<ramp,first,torch.where(s<=1-ramp,middle,last))

def reference(phase,twist,nominal,config,blend=None,height_delta=None):
    old,old_stance=previous.reference(phase,twist,nominal,config,blend,height_delta)
    timing=period(twist)[:,None]
    cfg=SimpleNamespace(period_s=timing,stance_fraction=.4,clearance_m=config.clearance_m)
    target,stance=clean_foot_reference(phase,twist,nominal,cfg,blend,height_delta)
    local=torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)
    s=((local-.4)/.6).clamp(0,1)
    nominal=torch.as_tensor(nominal,device=phase.device,dtype=phase.dtype)
    vx=twist[:,0,None]
    x=nominal[None,:,0]-vx*timing*.4/2+swing_displacement(s,vx,timing*.6)
    if blend is not None:x=nominal[None,:,0]+blend[:,None]*(x-nominal[None,:,0])
    alpha=strength(twist)[:,None]
    target[:,:,0]=torch.where(stance,target[:,:,0],target[:,:,0]+alpha*(x-target[:,:,0]))
    active=twist[:,0]>.8
    return torch.where(active[:,None,None],target,old),torch.where(active[:,None],stance,old_stance)

class ReturnCommands(previous.TrotCommands):
    def tick(self,dt,ids=None,foot_contacts=None):
        ids=torch.arange(len(self.phase),device=self.device) if ids is None else ids
        super().tick(dt,ids,foot_contacts)
        extra=dt*(1/period(self.applied[ids,:3])-1/previous.period(self.applied[ids,:3]))
        self.phase[ids]=torch.remainder(self.phase[ids]+extra,1.)

def contract(base):
    value=copy.deepcopy(base);value.update(schema_version=45,compatibility_tag=TAG)
    value['command_envelope']['forward_single_axis_extension_mps']=1.
    value['forward_extension']={'command_range_mps':[.8,1.],'period_s':[.44,.4],
        'stance_fraction':.4,'ramp_fraction_of_swing':RAMP,'velocity_profile':'integrated C1 cubic ramps and constant velocity plateau; C2 position; exact endpoint displacement/velocity/acceleration',
        'activation':'C2 quintic of applied vx .8..1.0; exact old trajectory <=.8',
        'support_and_reference_use_same_period':True,'terrain':'flat only','actuator_limits_unchanged':True,
        'learning_replay':'20% .65...8, 80% .8..1.0; frozen previous actor for evaluation <=.8'}
    return value
