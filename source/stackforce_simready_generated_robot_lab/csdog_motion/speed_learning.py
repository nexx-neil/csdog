"""Axis-speed extension; preserve the complete previously validated mixed box."""
import torch
from .residual_learning import full_learning_contract
from .evaluation import default_cases

SPEED_TAG="csdog_reference_velocity_support_residual_axis_speed_obs74_v8"
LEGACY_LIMITS=(.4,.3,.4)
SPEED_LIMITS=(.5,.35,.6)


def valid_speed_request(twist):
    legacy=twist.new_tensor(LEGACY_LIMITS)
    speed=twist.new_tensor(SPEED_LIMITS)
    within_speed=(twist.abs()<=speed+1e-6).all(-1)
    within_legacy=(twist.abs()<=legacy+1e-6).all(-1)
    single_axis=(twist.abs()>1e-6).sum(-1)<=1
    return torch.isfinite(twist).all(-1)&within_speed&(within_legacy|single_axis)


def speed_learning_contract():
    value=full_learning_contract()
    value.update(schema_version=8,compatibility_tag=SPEED_TAG)
    value["training_command_ranges"]={k:[-v,v] for k,v in zip(("vx","vy","yaw"),SPEED_LIMITS)}
    value["training_replay"]={"legacy_full_probability":.4,"low_probability":.2,"backward_probability":.2,"fast_single_axis_probability":.2}
    value["command_envelope"]={"legacy_mixed_box":list(LEGACY_LIMITS),"single_axis_extension":list(SPEED_LIMITS),
        "outside_legacy_box":"only one nonzero twist axis allowed; other requests rejected, never silently clipped",
        "limits_are_commands_not_measured_capability":True}
    return value


def speed_cases():
    cases=default_cases("lateral_grid")
    commands={"forward":[.5,0.,0.],"backward":[-.5,0.,0.],"left":[0.,.35,0.],"right":[0.,-.35,0.],
              "turn_left":[0.,0.,.6],"turn_right":[0.,0.,-.6]}
    for case in cases:
        if case["name"] in commands:case["profile"]=[[20.,commands[case["name"]]]]
    return cases


STYLE_TAG="csdog_reference_velocity_support_residual_style_obs74_v10"


def style_reward_scales():
    from .residual_learning import REWARD_SCALES
    return dict(REWARD_SCALES,foot_reference=3.,contact_schedule=2.,swing_load=-1.)


def style_learning_contract():
    value=speed_learning_contract()
    value.update(schema_version=10,compatibility_tag=STYLE_TAG)
    value["learning_reward_scales"]=style_reward_scales()
    return value
