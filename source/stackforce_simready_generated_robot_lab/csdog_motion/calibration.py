"""Geometry and nominal-pose identity for the isolated mesh-reference task."""
import hashlib
import json
from pathlib import Path
from .contracts import contract, JOINT_NAMES

CALIBRATED_TAG = "csdog_motion_foundation_flat_obs54_mesh_reference_pose_v3"
POSTURE_TAG = "csdog_motion_foundation_flat_obs54_mesh_reference_posture_v4"
ASSET = Path(__file__).resolve().parents[1] / "stackforce_simready_generated_robot_lab/assets/robots/csdog_v2_mesh_reference"


def calibrated_data():
    data = json.loads((ASSET / "calibration.json").read_text())
    path = ASSET / "robot_sim.urdf"
    if hashlib.sha256(path.read_bytes()).hexdigest() != data["diagnostic_urdf_sha256"]:
        raise ValueError("Calibrated geometry hash mismatch")
    if set(data["standing_joint_angles"]) != set(JOINT_NAMES):
        raise ValueError("Calibrated pose joint order mismatch")
    return data


def calibrated_contract():
    data = calibrated_data()
    value = contract()
    value["schema_version"] = 3
    value["compatibility_tag"] = CALIBRATED_TAG
    value["robot_geometry"] = {
        "urdf_sha256": data["diagnostic_urdf_sha256"],
        "source_mesh_urdf_sha256": data["source_mesh_urdf_sha256"],
        "profile_sha256": data["hardware_profile_sha256"],
        "contact_reference": "source-mesh-derived sole spheres; nominal joints calibrated instead of moving soles to align zero angles",
    }
    value["nominal_joint_positions_rad"] = [data["standing_joint_angles"][name] for name in JOINT_NAMES]
    return value


def posture_contract():
    value = calibrated_contract()
    value["schema_version"] = 4
    value["compatibility_tag"] = POSTURE_TAG
    value["action"]["posture_blend"] = "executed normalized offset = clipped policy output * observed gait_blend; zero residual in stand"
    value["action"]["previous_action_observation"] = "executed normalized offset after clipping and gait_blend"
    return value
