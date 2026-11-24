"""Command-dependent swing clearance, a distinct reference-control experiment."""
import torch
from .trajectory import foot_reference
from .speed_learning import speed_learning_contract

CLEAN_TAG='csdog_reference_adaptive_clearance_residual_obs74_v11'


def extra_clearance(twist):
    # Single-axis motion has more joint-speed reserve than combined motion.
    normalized=twist.abs()/twist.new_tensor([.4,.3,.4])
    mixture=((normalized.sum(1)-normalized.amax(1))*.5).clamp(0,1)
    return .007*(1-mixture)


def clean_foot_reference(phase,twist,nominal,config,blend=None,height_delta=None):
    target,stance=foot_reference(phase,twist,nominal,config,blend=blend,height_delta=height_delta)
    local=torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)
    progress=((local-config.stance_fraction)/(1-config.stance_fraction)).clamp(0,1)
    bump=64*progress.pow(3)*(1-progress).pow(3)
    amplitude=extra_clearance(twist)
    if blend is not None:amplitude=amplitude*blend
    target[:,:,2]+=amplitude[:,None]*bump
    return target,stance


def clean_learning_contract():
    value=speed_learning_contract()
    value.update(schema_version=11,compatibility_tag=CLEAN_TAG)
    value['reference_lift_policy']={'additional_clearance_m':.007,'single_axis_total_clearance_m':.032,
        'normalized_command_axes':[.4,.3,.4],'mixture':'clamp((L1(normalized_twist)-Linf(normalized_twist))/2,0,1)',
        'extra_clearance_formula_m':'.007*(1-mixture)','phase_bump':'same C2 bump, same diagonal phase and stance timing',
        'scope':'explicit controller change; prior policy tensors are a counterfactual initialization, not semantic compatibility'}
    return value
