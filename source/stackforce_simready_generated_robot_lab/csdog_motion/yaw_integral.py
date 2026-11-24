"""Bounded, observed yaw correction; no gain/actuator limit increase."""
import copy,math
from dataclasses import dataclass
import torch
from .support_feedback import transfer_strength
from .support_transfer import BACKWARD_TRANSITION


@dataclass(frozen=True)
class YawConfig:
    integral_gain_nm_rad: float = 1.2
    maximum_moment_nm: float = .6
    filter_seconds: float = .15
    turn_start_radps: float = .4
    turn_full_radps: float = .8

    def __post_init__(self):
        if not all(math.isfinite(v) and v>0 for v in vars(self).values()):raise ValueError('Invalid yaw thresholds')
        if self.maximum_moment_nm>2 or self.turn_start_radps>=self.turn_full_radps:raise ValueError('Invalid yaw scope or moment cap')


def strength(twist,config=None):
    cfg=config or YawConfig()
    s=((twist[:,2].abs()-cfg.turn_start_radps)/(cfg.turn_full_radps-cfg.turn_start_radps)).clamp(0,1)
    turn=(s.pow(3)*(10+s*(-15+6*s))).clamp(0,1)
    turn*=1-(twist[:,0].abs()/.4+twist[:,1].abs()/.3).clamp(0,1)
    return torch.maximum(turn,transfer_strength(twist,BACKWARD_TRANSITION))


class YawIntegral:
    def __init__(self,count,device='cpu',config=None):
        self.cfg=config or YawConfig()
        self.integral=torch.zeros(count,device=device)
        self.filtered_error=torch.zeros_like(self.integral)
        self.moment=torch.zeros_like(self.integral)
        self.previous_request=torch.zeros(count,3,device=device)

    def reset(self,ids):
        for value in (self.integral,self.filtered_error,self.moment,self.previous_request):value[ids]=0

    def tick(self,dt,applied,requested,actual_yaw,p_moment,active):
        n=len(self.integral)
        if not math.isfinite(dt) or not 0<dt<=.1:raise ValueError('Invalid yaw clock')
        if applied.shape!=(n,3) or requested.shape!=(n,3) or any(x.shape!=(n,) for x in (actual_yaw,p_moment,active)):raise ValueError('Yaw state shape mismatch')
        if not all(torch.isfinite(x).all() for x in (applied,requested,actual_yaw,p_moment)):raise ValueError('Nonfinite yaw controller input')
        changed=(requested-self.previous_request).abs().amax(1)>1e-5
        reset=changed|~active
        self.integral[reset]=0;self.filtered_error[reset]=0
        self.previous_request.copy_(requested)
        error=applied[:,2]-actual_yaw
        # A stop/posture request disables correction throughout the braking ramp.
        enabled=strength(applied,self.cfg)*(requested.abs().amax(1)>1e-6)
        alpha=1-math.exp(-dt/self.cfg.filter_seconds)
        filtered=self.filtered_error+alpha*(error-self.filtered_error)
        self.filtered_error=torch.where(active,filtered,0.)
        increment=self.cfg.integral_gain_nm_rad*self.filtered_error*dt*enabled
        total=p_moment+self.integral*enabled
        windup=((total>=2.)&(increment>0))|((total<=-2.)&(increment<0))
        increment=torch.where(windup|~active,0.,increment)
        next_i=(self.integral+increment).clamp(-self.cfg.maximum_moment_nm,self.cfg.maximum_moment_nm)
        # Inactive regions discard accumulated bias; ordinary gait stays exact.
        self.integral=torch.where((enabled>0)&active,next_i,0.)
        self.moment=self.integral*enabled
        return self.moment


YAW_TAG='csdog_observed_yaw_integral_diagnostic_obs76_v22'
YAW_SKILLS_TAG='csdog_observed_yaw_smooth_skills_diagnostic_obs76_v23'


def yaw_contract(base,skills=False):
    value=copy.deepcopy(base)
    value.update(schema_version=23 if skills else 22,compatibility_tag=YAW_SKILLS_TAG if skills else YAW_TAG,observations=76)
    value['observation_layout']['yaw_integral_and_filtered_error']=[74,76]
    value['support_feedback']['yaw_integral']={**vars(YawConfig()),
        'scope':'backward .15→.35m/s or pure turn .4→.8rad/s; quintic activation',
        'anti_windup':'bounded integral; freeze outward integration at +/-2Nm total yaw moment',
        'reset':'new requested twist, reset, disabled region, or posture/stop request',
        'update':'once per policy step, inactive reset environments excluded',
        'observation':'integral/.6Nm and filtered yaw error/.8rad/s, unclipped',
        'limits':'existing +/-2Nm total yaw moment and actuator/target limits unchanged'}
    return value


def extend_policy_inputs(state,target):
    """Zero-extend only actor/critic input columns; reject every other mismatch."""
    keys={'actor.0.weight','critic.0.weight'}
    if state.keys()!=target.keys():raise ValueError('Policy tensor keys differ')
    result={}
    for key,value in state.items():
        expected=target[key]
        if key in keys:
            if value.ndim!=2 or value.shape[1]!=74 or expected.shape!=(value.shape[0],76):raise ValueError('Expected explicit74→76 input migration')
            expanded=torch.zeros_like(expected);expanded[:,:74]=value
            result[key]=expanded
        else:
            if value.shape!=expected.shape:raise ValueError(f'Unexpected policy change: {key}')
            result[key]=value.clone()
    return result
