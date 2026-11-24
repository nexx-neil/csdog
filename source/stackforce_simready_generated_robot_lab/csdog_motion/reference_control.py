"""Explicit identity and bounds for the isolated reference-controller diagnostic."""
import json
import math
from .calibration import ASSET, calibrated_data, calibrated_contract
from .contracts import JOINT_NAMES

REFERENCE_TAG = "csdog_mesh_reference_trajectory_diagnostic_obs66_v5"


def reference_data():
    data = json.loads((ASSET / "reference_control.json").read_text())
    if data["geometry_sha256"] != calibrated_data()["diagnostic_urdf_sha256"]:
        raise ValueError("Reference profile geometry mismatch")
    if len(data["nominal_joint_positions_rad"]) != len(JOINT_NAMES):
        raise ValueError("Reference nominal pose order mismatch")
    return data


def reference_contract(data=None):
    data = reference_data() if data is None else data
    if data["geometry_sha256"] != calibrated_data()["diagnostic_urdf_sha256"]:
        raise ValueError("Reference profile geometry mismatch")
    if len(data["nominal_joint_positions_rad"]) != 12 or not all(math.isfinite(x) for x in data["nominal_joint_positions_rad"]):
        raise ValueError("Invalid reference nominal joints")
    value = calibrated_contract()
    value.update(schema_version=5, compatibility_tag=REFERENCE_TAG, observations=66)
    value["nominal_joint_positions_rad"] = data["nominal_joint_positions_rad"]
    value["height"]["nominal_m"] = data["nominal_height_m"]
    value["observation_layout"] = dict(value["observation_layout"], reference_joint_offset=[54, 66])
    value["action"] = {
        "type": "bounded_joint_residual_on_URDF_IK_foot_reference",
        "residual_scale_rad": data["joint_residual_limit_rad"],
        "residual_clip": 1., "blend": "observed gait_blend multiplies foot excursion and clipped joint residual",
        "total_offset_limit_rad": data["joint_target_offset_limit_rad"],
        "target_speed_limit_rad_s": data["joint_target_speed_limit_rad_s"],
        "previous_action_observation": "actual total target minus nominal, divided by total_offset_limit_rad",
    }
    value["reference_trajectory"] = data["trajectory"]
    value["reference_sole_positions_body_m"] = data["nominal_sole_positions_body_m"]
    value["diagnostic_pd_gains"] = data.get("pd_gains", {"stiffness":40.,"damping":1.5})
    value["support_feedback"] = data.get("support_feedback")
    if data.get("velocity_feedforward",False):
        value["action"]["velocity_target"] = "finite difference of bounded executed joint-position targets, limited to target_speed_limit_rad_s; reset starts from nominal"
    value["scope"] = "diagnostic controller only; optimization is blocked until coherent reward and validation are implemented"
    return value
