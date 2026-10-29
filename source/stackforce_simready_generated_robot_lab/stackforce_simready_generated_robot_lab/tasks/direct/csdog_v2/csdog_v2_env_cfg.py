"""Calibration-only configuration for the isolated CSDog v2 asset.

None of the v1 standing pose, action scale, PD gains, height thresholds, or
actuator limits are inherited.  Values marked provisional are conservative
diagnostic bounds, not validated hardware parameters.  PPO is blocked by the
training entry point while ``training_enabled`` is false.
"""

from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.utils import configclass

from ..generated_robot.generated_robot_env_cfg import GeneratedRobotEnvCfg


ASSET_DIR = Path(__file__).resolve().parents[3] / "assets" / "robots" / "csdog_v2"
URDF_PATH = ASSET_DIR / "robot_sim.urdf"

JOINT_NAMES = [
    "joint_lr_1", "joint_lr_2", "joint_lr_3",
    "joint_lf_1", "joint_lf_2", "joint_lf_3",
    "joint_rf_1", "joint_rf_2", "joint_rf_3",
    "joint_rr_1", "joint_rr_2", "joint_rr_3",
]
DEFAULT_JOINT_ANGLES = {name: 0.0 for name in JOINT_NAMES}
V2_REWARD_KEYS = (
    "termination",
    "tracking_lin_vel",
    "tracking_lin_vel_x",
    "tracking_lin_vel_y",
    "tracking_ang_vel",
    "tracking_lin_vel_l2",
    "tracking_lin_vel_x_l2",
    "tracking_lin_vel_y_l2",
    "tracking_ang_vel_l2",
    "lin_vel_z",
    "ang_vel_xy",
    "orientation",
    "torques",
    "dof_vel",
    "dof_acc",
    "base_height",
    "feet_air_time",
    "collision",
    "feet_stumble",
    "action_rate",
    "action_magnitude",
    "action_overflow",
    "joint_deviation",
    "feet_slide",
    "swing_foot_clearance",
    "feet_contact_count",
    "diagonal_gait",
    "gait_contact_schedule",
    "gait_stance_contact",
    "gait_swing_release",
    "inactive_axis_vel",
    "stand_still",
    "custom_reward",
)


@configclass
class CSDogV2CalibrationEnvCfg(GeneratedRobotEnvCfg):
    model_id = "csdog_v2"
    checkpoint_compatibility_tag = "csdog_v2_joint_order_v1"
    training_enabled = False
    training_block_reason = (
        "CSDog v2 locomotion training remains blocked until the joint-direction, "
        "30-second PD standing, and contact gates pass."
    )

    # Independent, calibration-only command range and action bound.  These are
    # intentionally not copied from GeneratedRobotEnvCfg.
    action_scale = 0.20
    action_clip = 0.50
    command_ranges = {
        "lin_vel_x": (0.0, 0.0),
        "lin_vel_y": (0.0, 0.0),
        "ang_vel_yaw": (0.0, 0.0),
    }

    robot: ArticulationCfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UrdfFileCfg(
            asset_path=str(URDF_PATH),
            fix_base=False,
            merge_fixed_joints=False,
            self_collision=False,
            replace_cylinders_with_capsules=True,
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=20.0,
                max_angular_velocity=30.0,
                max_depenetration_velocity=2.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=2,
            ),
            joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
                gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.0, damping=0.0)
            ),
        ),
        # The 0.41 m spawn and zero joint pose are selected by the recorded
        # standing-pose grid; settled base height is about 0.386 m.
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.41), joint_pos=DEFAULT_JOINT_ANGLES),
        actuators={
            "calibration_joints": ImplicitActuatorCfg(
                joint_names_expr=JOINT_NAMES,
                # Provisional simulation standing profile.  These are not
                # validated hardware gains or continuous motor limits.
                stiffness=40.0,
                damping=1.5,
                effort_limit_sim=12.0,
                velocity_limit_sim=10.0,
            )
        },
        soft_joint_pos_limit_factor=0.90,
    )

    # Keep calibration reward-free.  Do not access the decorated base class's
    # instance fields at class-definition time; doing so prevents the task
    # configuration module from importing under Isaac Lab.
    reward_scales = {key: 0.0 for key in V2_REWARD_KEYS}
    default_joint_angles = DEFAULT_JOINT_ANGLES
    actuated_joint_names = JOINT_NAMES
    foot_link_names = ["link_lr_sole", "link_lf_sole", "link_rf_sole", "link_rr_sole"]
    joint_child_link_names = [
        "link_lr_hip_roll", "link_lr_hip_pitch", "link_lr_knee",
        "link_lf_hip_roll", "link_lf_hip_pitch", "link_lf_knee",
        "link_rf_hip_roll", "link_rf_hip_pitch", "link_rf_knee",
        "link_rr_hip_roll", "link_rr_hip_pitch", "link_rr_knee",
    ]
    joint_foot_link_names = [
        "link_lr_sole", "link_lr_sole", "link_lr_sole",
        "link_lf_sole", "link_lf_sole", "link_lf_sole",
        "link_rf_sole", "link_rf_sole", "link_rf_sole",
        "link_rr_sole", "link_rr_sole", "link_rr_sole",
    ]
    undesired_contact_body_names = [
        "base",
        "link_lr_hip_roll", "link_lr_hip_pitch",
        "link_lr_knee",
        "link_lf_hip_roll", "link_lf_hip_pitch",
        "link_lf_knee",
        "link_rf_hip_roll", "link_rf_hip_pitch",
        "link_rf_knee",
        "link_rr_hip_roll", "link_rr_hip_pitch",
        "link_rr_knee",
    ]
    base_link_name = "base"

    # v2 values measured by the zero-pose standing diagnostic; no v1 geometry
    # or thresholds are reused.
    base_height_target = 0.386
    min_base_height = 0.22
    termination_contact_force_threshold = 80.0


@configclass
class CSDogV2LocomotionEnvCfg(CSDogV2CalibrationEnvCfg):
    """Trainable flat-ground v2 task unlocked by the recorded dynamic gates."""

    checkpoint_compatibility_tag = "csdog_v2_locomotion_joint_order_v1"
    training_enabled = True
    training_block_reason = ""
    action_scale = 0.35
    action_clip = 1.0
    command_ranges = {
        "lin_vel_x": (-0.4, 0.4),
        "lin_vel_y": (-0.4, 0.4),
        "ang_vel_yaw": (-0.6, 0.6),
    }
    command_sampling = "single_axis"
    command_min_magnitude = 0.20
    stand_command_probability = 0.10
    visual_disable_resets = False
    reward_scales = {
        "termination": -100.0,
        "tracking_lin_vel": 0.0,
        "tracking_lin_vel_x": 4.0,
        "tracking_lin_vel_y": 4.0,
        "tracking_ang_vel": 4.0,
        "tracking_lin_vel_l2": 0.0,
        "tracking_lin_vel_x_l2": -2.0,
        "tracking_lin_vel_y_l2": -2.0,
        "tracking_ang_vel_l2": -1.0,
        "lin_vel_z": -2.0,
        "ang_vel_xy": -0.10,
        "orientation": -2.0,
        "torques": -0.00002,
        "dof_vel": 0.0,
        "dof_acc": -2.5e-7,
        "base_height": -2.0,
        "feet_air_time": 0.25,
        "collision": -2.0,
        "feet_stumble": 0.0,
        "action_rate": -0.02,
        "action_magnitude": -0.05,
        "action_overflow": -0.10,
        "joint_deviation": -0.10,
        "feet_slide": -0.25,
        # Sole origin rests near 0.018 m.  A 0.050 m target therefore asks for
        # roughly 3.2 cm of visible sole clearance during a valid swing phase.
        "swing_foot_clearance": 0.50,
        "feet_contact_count": -0.15,
        "diagonal_gait": 0.25,
        # Penalize velocity on axes whose command is zero.  This directly
        # addresses the lateral drift observed after the yaw phase.
        "inactive_axis_vel": -3.0,
        "stand_still": -0.25,
        "custom_reward": 0.0,
    }
    swing_foot_height_target = 0.050
    swing_foot_rest_height = 0.018
    swing_foot_height_std = 0.015
    swing_foot_count_normalizer = 2.0


@configclass
class CSDogV2PhaseGaitEnvCfg(CSDogV2LocomotionEnvCfg):
    """Phase-observed task that explicitly alternates diagonal support legs."""

    checkpoint_compatibility_tag = "csdog_v2_phase_gait_obs_v1"
    observation_space = 50
    include_gait_phase_observation = True
    gait_cycle_time_s = 0.50
    reward_scales = {
        "termination": -100.0,
        "tracking_lin_vel": 0.0,
        "tracking_lin_vel_x": 4.0,
        "tracking_lin_vel_y": 4.0,
        "tracking_ang_vel": 4.0,
        "tracking_lin_vel_l2": 0.0,
        "tracking_lin_vel_x_l2": -2.0,
        "tracking_lin_vel_y_l2": -2.0,
        "tracking_ang_vel_l2": -1.0,
        "lin_vel_z": -2.0,
        "ang_vel_xy": -0.10,
        "orientation": -2.0,
        "torques": -0.00002,
        "dof_vel": 0.0,
        "dof_acc": -2.5e-7,
        "base_height": -2.0,
        "feet_air_time": 0.25,
        "collision": -2.0,
        "feet_stumble": 0.0,
        "action_rate": -0.02,
        "action_magnitude": -0.05,
        "action_overflow": -0.10,
        "joint_deviation": -0.10,
        "feet_slide": -0.25,
        "swing_foot_clearance": 2.00,
        "feet_contact_count": 0.0,
        "diagonal_gait": 0.0,
        "gait_contact_schedule": 0.0,
        # Stance and swing are intentionally asymmetric: a foot that never
        # lands must not receive half credit merely because it is airborne
        # during its scheduled swing half-cycle.
        "gait_stance_contact": 4.00,
        "gait_swing_release": 1.00,
        "inactive_axis_vel": -3.0,
        "stand_still": -0.25,
        "custom_reward": 0.0,
    }
