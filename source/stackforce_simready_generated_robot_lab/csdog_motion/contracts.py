"""Versioned policy interface; the legacy 50 columns keep their original order."""

import hashlib
import json

LEGACY_OBSERVATIONS = 50
FOUNDATION_OBSERVATIONS = 54
FOUNDATION_TAG = "csdog_motion_foundation_flat_obs54_v1"
JOINT_NAMES = [f"joint_{leg}_{index}" for leg in ("lr", "lf", "rf", "rr") for index in (1, 2, 3)]
OBSERVATION_LAYOUT = {
    "linear_velocity_body": [0, 3], "angular_velocity_body": [3, 6],
    "projected_gravity_body": [6, 9], "applied_twist_command": [9, 12],
    "joint_position_minus_nominal": [12, 24], "joint_velocity": [24, 36],
    "previous_clipped_action": [36, 48], "gait_phase_sin_cos": [48, 50],
    "height_command_minus_nominal": [50, 51], "height_command_rate": [51, 52],
    "gait_blend": [52, 53], "standing_mode": [53, 54],
}


def contract(action_scale=0.35, nominal_height=0.386):
    return {
        "schema_version": 1, "compatibility_tag": FOUNDATION_TAG,
        "observations": FOUNDATION_OBSERVATIONS, "actions": 12,
        "observation_layout": OBSERVATION_LAYOUT, "joint_names": JOINT_NAMES,
        "frame": "body: X forward, Y left, Z up", "units": "m, s, kg, rad",
        "policy_dt_s": 0.02, "physics_dt_s": 0.005,
        "action": {"type": "nominal_joint_position_offset", "scale_rad": action_scale, "clip": 1.0},
        "height": {"reference": "base above flat environment plane", "nominal_m": nominal_height},
        "terrain_support": "flat only; local terrain sensing and variable-height actuation require later validation",
        "command_update": "next policy observation, after each physical control step",
        "gait_clock": "independent physical-time clock; continues in stand for legacy initialization compatibility",
    }


def contract_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def migrate_observation_weights(state_dict):
    """Preserve the actor/critic function; added input columns start at zero."""
    result = {key: value.detach().clone() for key, value in state_dict.items()}
    for key in ("actor.0.weight", "critic.0.weight"):
        value = result[key]
        if value.ndim != 2 or value.shape[1] != LEGACY_OBSERVATIONS:
            raise ValueError(f"Expected a 50-column legacy input at {key}, got {tuple(value.shape)}")
        result[key] = value.new_zeros(value.shape[0], FOUNDATION_OBSERVATIONS)
        result[key][:, :LEGACY_OBSERVATIONS] = value
    return result
