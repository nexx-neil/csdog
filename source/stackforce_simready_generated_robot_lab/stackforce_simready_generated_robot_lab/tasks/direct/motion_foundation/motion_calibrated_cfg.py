from isaaclab.utils import configclass
from csdog_motion.calibration import ASSET, CALIBRATED_TAG, POSTURE_TAG, calibrated_data, calibrated_contract, posture_contract
from .motion_env_cfg import MotionFoundationEnvCfg, MotionFoundationRunnerCfg


@configclass
class MotionCalibratedEnvCfg(MotionFoundationEnvCfg):
    checkpoint_compatibility_tag = CALIBRATED_TAG
    motion_contract = calibrated_contract()
    record_nominal_pose_in_physics_contract = True

    def __post_init__(self):
        parent = getattr(super(), "__post_init__", None)
        if parent is not None:
            parent()
        data = calibrated_data()
        self.robot.spawn.asset_path = str(ASSET / "robot_sim.urdf")
        self.robot.init_state.joint_pos = dict(data["standing_joint_angles"])
        self.default_joint_angles = dict(data["standing_joint_angles"])


@configclass
class MotionCalibratedRunnerCfg(MotionFoundationRunnerCfg):
    experiment_name = "csdog_motion_calibrated"


@configclass
class MotionPostureEnvCfg(MotionCalibratedEnvCfg):
    checkpoint_compatibility_tag = POSTURE_TAG
    motion_contract = posture_contract()
    posture_blend_actions = True


@configclass
class MotionPostureRunnerCfg(MotionCalibratedRunnerCfg):
    experiment_name = "csdog_motion_posture"
