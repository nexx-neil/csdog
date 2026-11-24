"""First larger envelope; bounded high-vx timing, never a hardware capability claim."""
from types import SimpleNamespace
import torch
from .speed_learning import LEGACY_LIMITS
from .support_transfer import transfer_contract
from .clean_gait import clean_foot_reference

LIMITS = (.6, .4, .8)
ADAPTIVE_TAG = 'csdog_adaptive_fast_reference_diagnostic_obs74_v17'
EXPOSED_TAG = 'csdog_exposed_fast_reference_diagnostic_obs74_v18'


def valid_request(twist):
    finite = torch.isfinite(twist).all(-1)
    legacy = (twist.abs() <= twist.new_tensor(LEGACY_LIMITS)+1e-6).all(-1)
    single = (twist.abs()>1e-6).sum(-1)<=1
    within = (twist.abs() <= twist.new_tensor(LIMITS)+1e-6).all(-1)
    return finite & within & (legacy | single)


def stance_fraction(twist):
    s=((twist[:,0].abs()-.5)/.1).clamp(0,1)
    strength=(s.pow(3)*(10+s*(-15+6*s))).clamp(0,1)
    return .55-.04*strength


def scheduled_config(twist, config):
    return SimpleNamespace(period_s=config.period_s,clearance_m=config.clearance_m,
                           stance_fraction=stance_fraction(twist)[:,None])


def adaptive_reference(phase,twist,nominal,config,blend=None,height_delta=None):
    # Exact SE(2) stance and C2 swing at each scheduled duty, not a position blend.
    legacy,old_mask=clean_foot_reference(phase,twist,nominal,config,blend,height_delta)
    adaptive,new_mask=clean_foot_reference(phase,twist,nominal,scheduled_config(twist,config),blend,height_delta)
    active=twist[:,0].abs()>.5
    # Tensor timing arithmetic can round differently from Python scalar timing.
    # Retain the scalar legacy evaluation exactly when this branch is inactive.
    return torch.where(active[:,None,None],adaptive,legacy),torch.where(active[:,None],new_mask,old_mask)


def fast_contract(adaptive=True):
    value=transfer_contract(backward=True)
    value.update(schema_version=17 if adaptive else 18,
                 compatibility_tag=ADAPTIVE_TAG if adaptive else EXPOSED_TAG)
    value['command_envelope']['single_axis_extension']=list(LIMITS)
    value['training_command_ranges']={k:[-v,v] for k,v in zip(('vx','vy','yaw'),LIMITS)}
    value['fast_timing']={'enabled':adaptive,'legacy_duty':.55,'fast_duty':.51,
        'vx_activation_mps':[.5,.6], 'blend':'quintic smoothstep of abs(applied vx)',
        'period_s':.5,'support_and_swing_share_same_duty':True,
        'scope':'diagnostic enlarged single-axis commands; no PPO training or release'}
    return value


def fast_cases():
    from .speed_learning import speed_cases
    cases=speed_cases()
    commands={'forward':[.6,0,0],'backward':[-.6,0,0],'left':[0,.4,0],
              'right':[0,-.4,0],'turn_left':[0,0,.8],'turn_right':[0,0,-.8]}
    for case in cases:
        if case['name'] in commands:case['profile']=[[20.,commands[case['name']]]]
    for case in cases:
        if case['name']=='start_stop':case['profile']=[[2.,[0,0,0]],[8.,[.6,0,0]],[20.,[0,0,0]]]
        if case['name']=='reverse':case['profile']=[[6.,[.6,0,0]],[12.,[-.6,0,0]],[20.,[0,0,0]]]
    return cases


def fast_holdout_cases():
    """Unseen points and timings within the frozen proposed keyboard envelope."""
    commands={'stand':[0,0,0],'forward_054':[.54,0,0],'forward_057':[.57,0,0],
        'forward_059':[.59,0,0],'backward_047':[-.47,0,0],
        'left_037':[0,.37,0],'right_037':[0,-.37,0],'left_039':[0,.39,0],'right_039':[0,-.39,0],
        'turn_left_068':[0,0,.68],'turn_right_068':[0,0,-.68],
        'turn_left_076':[0,0,.76],'turn_right_076':[0,0,-.76],
        'old_mixed':[.32,.18,.28],'old_back_mixed':[-.28,.08,.12]}
    cases=[{'name':k,'profile':[[20.,v]],'protected':True} for k,v in commands.items()]
    cases += [
        {'name':'fast_start_stop','profile':[[2.6,[0,0,0]],[8.3,[.57,0,0]],[13.1,[0,0,0]],[17.,[.54,0,0]],[20.,[0,0,0]]],'protected':False},
        {'name':'fast_reverse','profile':[[5.3,[.57,0,0]],[10.4,[-.47,0,0]],[15.1,[.54,0,0]],[20.,[0,0,0]]],'protected':False},
        {'name':'fast_axis_switch','profile':[[4.7,[.57,0,0]],[9.3,[0,0,.76]],[14.2,[0,-.37,0]],[20.,[0,0,0]]],'protected':False}]
    return cases
