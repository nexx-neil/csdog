from pathlib import Path

import isaaclab.sim as sim_utils
from isaaclab.actuators import ImplicitActuatorCfg
from isaaclab.assets import ArticulationCfg
from isaaclab.envs import DirectRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.sim import SimulationCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.terrains.config.rough import ROUGH_TERRAINS_CFG
from isaaclab.utils import configclass


ASSET_DIR = Path(__file__).resolve().parents[3] / "assets" / "robots" / "generated_robot"
URDF_PATH = ASSET_DIR / "urdf" / "generated_robot.urdf"


@configclass
class GeneratedRobotEnvCfg(DirectRLEnvCfg):
    episode_length_s = 20.0
    decimation = 4
    action_scale = 0.5
    action_space = 12
    observation_space = 48
    state_space = 0

    sim: SimulationCfg = SimulationCfg(
        dt=1 / 200,
        render_interval=decimation,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
    )

    terrain = TerrainImporterCfg(
        prim_path="/World/ground",
        terrain_type="plane",
        collision_group=-1,
        physics_material=sim_utils.RigidBodyMaterialCfg(
            friction_combine_mode="multiply",
            restitution_combine_mode="multiply",
            static_friction=1.0,
            dynamic_friction=1.0,
            restitution=0.0,
        ),
        debug_vis=False,
    )

    scene: InteractiveSceneCfg = InteractiveSceneCfg(num_envs=1024, env_spacing=4.0, replicate_physics=True)

    robot: ArticulationCfg = ArticulationCfg(
        prim_path="/World/envs/env_.*/Robot",
        spawn=sim_utils.UrdfFileCfg(
            asset_path=str(URDF_PATH),
            fix_base=False,
            merge_fixed_joints=True,
            self_collision=False,
            replace_cylinders_with_capsules=True,
            activate_contact_sensors=True,
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                disable_gravity=False,
                retain_accelerations=False,
                linear_damping=0.0,
                angular_damping=0.0,
                max_linear_velocity=1000.0,
                max_angular_velocity=1000.0,
                max_depenetration_velocity=5.0,
            ),
            articulation_props=sim_utils.ArticulationRootPropertiesCfg(
                enabled_self_collisions=False,
                solver_position_iteration_count=8,
                solver_velocity_iteration_count=1,
            ),
            joint_drive=sim_utils.UrdfConverterCfg.JointDriveCfg(
                gains=sim_utils.UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.0, damping=0.0)
            ),
        ),
        init_state=ArticulationCfg.InitialStateCfg(
            # The mirrored deep stance settles near 0.1327 m. Add
            # 20 mm clearance so the first physics step starts cleanly.
            pos=(0.0, 0.0, 0.1527),
            joint_pos={
        "FR1_joint": -0.3,
        "FR2_joint": 0.9,
        "FR3_joint": -1.3,
        "FL1_joint": 0.3,
        "FL2_joint": 0.9,
        "FL3_joint": -1.3,
        "RL1_joint": 0.3,
        "RL2_joint": 0.9,
        "RL3_joint": -1.3,
        "RR1_joint": -0.3,
        "RR2_joint": 0.9,
        "RR3_joint": -1.3,
    },
        ),
        actuators={
            "joints": ImplicitActuatorCfg(
                joint_names_expr=["FR1_joint", "FR2_joint", "FR3_joint", "FL1_joint", "FL2_joint", "FL3_joint", "RL1_joint", "RL2_joint", "RL3_joint", "RR1_joint", "RR2_joint", "RR3_joint"],
                stiffness={
        "FR1_joint": 20.0,
        "FR2_joint": 20.0,
        "FR3_joint": 20.0,
        "FL1_joint": 20.0,
        "FL2_joint": 20.0,
        "FL3_joint": 20.0,
        "RL1_joint": 20.0,
        "RL2_joint": 20.0,
        "RL3_joint": 20.0,
        "RR1_joint": 20.0,
        "RR2_joint": 20.0,
        "RR3_joint": 20.0,
    },
                damping={
        "FR1_joint": 0.5,
        "FR2_joint": 0.5,
        "FR3_joint": 0.5,
        "FL1_joint": 0.5,
        "FL2_joint": 0.5,
        "FL3_joint": 0.5,
        "RL1_joint": 0.5,
        "RL2_joint": 0.5,
        "RL3_joint": 0.5,
        "RR1_joint": 0.5,
        "RR2_joint": 0.5,
        "RR3_joint": 0.5,
    },
                effort_limit_sim={
        "FR1_joint": 10.0,
        "FR2_joint": 10.0,
        "FR3_joint": 10.0,
        "FL1_joint": 10.0,
        "FL2_joint": 10.0,
        "FL3_joint": 10.0,
        "RL1_joint": 10.0,
        "RL2_joint": 10.0,
        "RL3_joint": 10.0,
        "RR1_joint": 10.0,
        "RR2_joint": 10.0,
        "RR3_joint": 10.0,
    },
                velocity_limit_sim={
        "FR1_joint": 5.0,
        "FR2_joint": 5.0,
        "FR3_joint": 5.0,
        "FL1_joint": 5.0,
        "FL2_joint": 5.0,
        "FL3_joint": 5.0,
        "RL1_joint": 5.0,
        "RL2_joint": 5.0,
        "RL3_joint": 5.0,
        "RR1_joint": 5.0,
        "RR2_joint": 5.0,
        "RR3_joint": 5.0,
    },
            ),
        },
        soft_joint_pos_limit_factor=0.95,
    )

    contact_sensor: ContactSensorCfg = ContactSensorCfg(
        prim_path="/World/envs/env_.*/Robot/.*",
        history_length=3,
        update_period=0.02,
        track_air_time=True,
    )

    command_ranges = {
        "lin_vel_x": (-0.8, 0.8),
        "lin_vel_y": (-0.8, 0.8),
        "ang_vel_yaw": (-0.8, 0.8),
    }
    command_sampling = "single_axis"
    command_min_magnitude = 0.15
    stand_command_probability = 0.1

    reward_scales = {
        "termination": -200.0,
        "tracking_lin_vel": 0.0,
        "tracking_lin_vel_x": 5.0,
        "tracking_lin_vel_y": 5.0,
        "tracking_ang_vel": 5.0,
        "tracking_lin_vel_l2": 0.0,
        "tracking_lin_vel_x_l2": -5.0,
        "tracking_lin_vel_y_l2": -5.0,
        "tracking_ang_vel_l2": -2.5,
        "lin_vel_z": -2.0,
        "ang_vel_xy": -0.05,
        "orientation": -1.0,
        "torques": -0.00001,
        "dof_vel": 0.0,
        "dof_acc": -2.5e-7,
        "base_height": -1.0,
        "feet_air_time": 0.25,
        "collision": -1.0,
        "feet_stumble": 0.0,
        "action_rate": -0.01,
        "action_magnitude": -0.1,
        "action_overflow": -0.02,
        "joint_deviation": -0.5,
        "feet_slide": -0.1,
        "swing_foot_clearance": 0.0,
        "feet_contact_count": 0.0,
        "diagonal_gait": 0.0,
        "inactive_axis_vel": 0.0,
        "stand_still": 0.0,
        "custom_reward": 0.0,
    }
    tracking_lin_vel_std = 0.5
    tracking_ang_vel_std = 0.5
    default_joint_angles = {
        "FR1_joint": -0.3,
        "FR2_joint": 0.9,
        "FR3_joint": -1.3,
        "FL1_joint": 0.3,
        "FL2_joint": 0.9,
        "FL3_joint": -1.3,
        "RL1_joint": 0.3,
        "RL2_joint": 0.9,
        "RL3_joint": -1.3,
        "RR1_joint": -0.3,
        "RR2_joint": 0.9,
        "RR3_joint": -1.3,
    }
    actuated_joint_names = ["FR1_joint", "FR2_joint", "FR3_joint", "FL1_joint", "FL2_joint", "FL3_joint", "RL1_joint", "RL2_joint", "RL3_joint", "RR1_joint", "RR2_joint", "RR3_joint"]
    foot_link_names = ["FR3", "FL3", "RL3", "RR3"]
    undesired_contact_body_names = [
        "base_link",
        "FR1",
        "FR2",
        "FL1",
        "FL2",
        "RL1",
        "RL2",
        "RR1",
        "RR2",
    ]
    base_link_name = "base_link"
    auto_ground_spawn_height = 1
    auto_ground_clearance = 0.02
    auto_ground_complete = False
    base_height_target = 0.1327
    feet_air_time_threshold = 0.1
    # Body-origin height above a flat terrain plane.  Generic exports keep the
    # corresponding reward disabled; robot-specific tasks must calibrate it.
    swing_foot_height_target = 0.05
    swing_foot_height_std = 0.015
    swing_foot_count_normalizer = 2.0
    action_clip = 1.0
    visual_disable_resets = False
    termination_grace_time_s = 2.0
    termination_contact_force_threshold = 20.0
    fallen_projected_gravity_z = -0.35
    fallen_termination_time_s = 0.5
    min_base_height = 0.08
    randomize_initial_episode_length = False
