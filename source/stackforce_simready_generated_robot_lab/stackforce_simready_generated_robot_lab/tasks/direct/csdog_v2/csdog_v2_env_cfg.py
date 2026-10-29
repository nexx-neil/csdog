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
        # Exported zero pose and elevated spawn are used only for fixed-base
        # direction tests.  A standing pose/height must be measured separately.
        init_state=ArticulationCfg.InitialStateCfg(pos=(0.0, 0.0, 0.50), joint_pos=DEFAULT_JOINT_ANGLES),
        actuators={
            "calibration_joints": ImplicitActuatorCfg(
                joint_names_expr=JOINT_NAMES,
                # Independently selected low-gain diagnostic values.  Do not
                # use for standing/training without completing the PD gate.
                stiffness=8.0,
                damping=0.8,
                effort_limit_sim=5.0,
                velocity_limit_sim=3.0,
            )
        },
        soft_joint_pos_limit_factor=0.90,
    )

    reward_scales = {key: 0.0 for key in GeneratedRobotEnvCfg.reward_scales}
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

    # Disabled placeholders: they are explicit v2 values so v1 geometry cannot
    # leak into calibration.  Standing diagnostics must override them after a
    # valid pose is established.
    base_height_target = 0.30
    min_base_height = 0.12
    termination_contact_force_threshold = 80.0
