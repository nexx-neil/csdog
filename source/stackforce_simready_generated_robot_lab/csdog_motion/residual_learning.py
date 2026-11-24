"""New residual-MDP identity, development protocol and explicit reward units."""
import json
from pathlib import Path
import torch
from .calibration import ASSET
from .reference_control import reference_contract
from .evaluation import default_cases

RESIDUAL_TAG="csdog_reference_velocity_support_residual_obs74_v6"
FULL_RESIDUAL_TAG="csdog_reference_velocity_support_residual_full_obs74_v7"


def learning_profile():
    return json.loads((ASSET/"residual_learning.json").read_text())


def learning_contract():
    value=reference_contract(learning_profile())
    value.update(schema_version=6,compatibility_tag=RESIDUAL_TAG,observations=74,
                 scope="new residual-learning MDP; independent initialization, no old-policy compatibility or release claim")
    value["observation_layout"].update(contact_force_over_body_weight=[66,70],foot_clearance_over_0_05m=[70,74])
    value["training_command_ranges"]={"vx":[-.15,.15],"vy":[-.1,.1],"yaw":[-.15,.15]}
    return value


def full_learning_contract():
    value=learning_contract()
    value.update(schema_version=7,compatibility_tag=FULL_RESIDUAL_TAG)
    value["training_command_ranges"]={"vx":[-.4,.4],"vy":[-.3,.3],"yaw":[-.4,.4]}
    value["training_replay"]={"low_command_probability":.4,"scales":[.375,1/3,.375]}
    return value


def low_command_cases():
    cases=default_cases("lateral_grid")
    for case in cases:
        for entry in case["profile"]:
            entry[1]=[entry[1][0]*.375,entry[1][1]/3,entry[1][2]*.375]
    return cases


def holdout_cases():
    """Fixed commands/timings excluded from checkpoint selection, within training ranges."""
    commands={"stand":[0.,0.,0.],"forward":[.125,0.,0.],"backward":[-.125,0.,0.],
        "left":[0.,.075,0.],"right":[0.,-.075,0.],"turn_left":[0.,0.,.125],"turn_right":[0.,0.,-.125],
        "forward_turn":[.10,0.,.10],"lateral_turn":[0.,.06,.10],"right_turn":[0.,-.06,-.10],"diagonal":[.10,.06,0.],
        "left_low":[0.,.05,0.],"left_mid":[0.,.085,0.],"right_low":[0.,-.05,0.],"right_mid":[0.,-.085,0.]}
    result=[{"name":name,"profile":[[20.,command]],"protected":True} for name,command in commands.items()]
    result += [
        {"name":"start_stop","profile":[[2.6,[0.,0.,0.]],[7.4,[.12,0.,0.]],[12.8,[0.,0.,0.]],[16.,[.08,0.,0.]],[20.,[0.,0.,0.]]],"protected":False},
        {"name":"reverse","profile":[[5.4,[.12,0.,0.]],[10.6,[-.12,0.,0.]],[15.3,[.08,0.,0.]],[20.,[0.,0.,0.]]],"protected":False},
        {"name":"combination_switch","profile":[[3.7,[0.,.075,0.]],[9.2,[0.,.06,.10]],[14.1,[0.,-.06,-.10]],[20.,[0.,0.,0.]]],"protected":False},
    ]
    return result


REWARD_SCALES={
    "track_x":2.,"track_y":2.,"track_yaw":1.5,"foot_reference":1.,
    "contact_schedule":1.,"swing_height":.5,"swing_load":-.5,
    "height":-.5,"tilt":-.5,"angular_xy":-.05,"vertical_velocity":-.25,
    "stance_slide":-.5,"torque":-1e-5,"joint_acceleration":-1e-7,
    "total_target_change":-.05,"residual_size":-.1,"residual_overflow":-.2,
    "target_box_clip":-.1,"termination":-100.,
}


def reward_terms(state):
    error=state["twist"]-state["command"]
    swing=(~state["stance"]).float()*state["blend"][:,None]
    desired_contact=1-swing
    return {
        "track_x":torch.exp(-(error[:,0]/.15).square()),
        "track_y":torch.exp(-(error[:,1]/.12).square()),
        "track_yaw":torch.exp(-(error[:,2]/.2).square()),
        "foot_reference":torch.exp(-((state["foot_body"]-state["reference_foot"]).square().sum(-1)/.03**2).mean(1)),
        "contact_schedule":1-(state["contacts"].float()-desired_contact).abs().mean(1),
        "swing_height":(torch.exp(-((state["clearance"]-state["desired_clearance"])/.025).square())*swing).mean(1),
        "swing_load":(state["force_over_weight"]*swing).mean(1),
        "height":((state["height"]-state["height_command"])/.03).square(),
        "tilt":state["gravity"][:,:2].square().sum(1)/.2**2,
        "angular_xy":state["angular_xy"].square().sum(1),
        "vertical_velocity":state["vertical_velocity"].square(),
        "stance_slide":(state["foot_world_velocity"][:,:,:2].square().sum(-1)*state["contacts"]).mean(1),
        "torque":state["torque"].square().sum(1),
        "joint_acceleration":state["joint_acceleration"].square().sum(1),
        "total_target_change":((state["target"]-state["previous_target"])/.16).square().mean(1),
        "residual_size":state["residual"].square().mean(1),
        "residual_overflow":torch.relu(state["raw_action"].abs()-1).square().mean(1),
        "target_box_clip":state["target_box_clip"].float().mean(1),
        "termination":state["terminated"].float(),
    }
