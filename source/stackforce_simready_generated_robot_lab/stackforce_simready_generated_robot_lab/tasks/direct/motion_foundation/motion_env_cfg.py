from dataclasses import asdict

from isaaclab.utils import configclass

from csdog_motion.commands import MotionCommandConfig
from csdog_motion.contracts import FOUNDATION_TAG, FOUNDATION_OBSERVATIONS, contract
from csdog_motion.action_bounds import ENVELOPE_TAG, KNEE_CLIP, envelope_contract
from ..csdog_v2.csdog_v2_env_cfg import CSDogV2TeleopEnvCfg
from ..csdog_v2.agents.rsl_rl_ppo_cfg import CSDogV2TeleopPPORunnerCfg


@configclass
class MotionFoundationEnvCfg(CSDogV2TeleopEnvCfg):
    """Flat-ground foundation. This is a new MDP, not a trained capability claim."""

    checkpoint_compatibility_tag = FOUNDATION_TAG
    observation_space = FOUNDATION_OBSERVATIONS
    motion_contract = contract()
    motion_commands = asdict(MotionCommandConfig())
    command_resampling_interval_s = (3.0, 6.0)
    periodic_commands = True
    randomize_initial_episode_length = False
    record_reward_terms = False
    command_curriculum = "legacy"
    action_clip_per_joint = None
    posture_blend_actions = False
    reward_scales = {
        "tracking_twist": 4.0, "twist_error": -1.0,
        "base_height": -2.0, "orientation": -2.0, "ang_vel_xy": -0.1,
        "normal_velocity": -2.0, "contact_schedule": 2.0,
        "swing_clearance": -0.25, "stance_velocity": -0.1,
        "feet_slide_proxy": -0.25, "collision": -2.0,
        "torques": -0.00002, "dof_acc": -2.5e-7,
        "action_rate": -0.02, "action_magnitude": -0.08,
        "action_overflow": -0.1, "joint_deviation": -0.1, "termination": -100.0,
    }


@configclass
class MotionFoundationRunnerCfg(CSDogV2TeleopPPORunnerCfg):
    experiment_name = "csdog_motion_foundation"
    max_iterations = 5
    save_interval = 1
    # Launch-time synchronization also applies this to restored optimizer groups.
    def __post_init__(self):
        parent_post_init = getattr(super(), "__post_init__", None)
        if parent_post_init is not None:
            parent_post_init()
        self.algorithm.learning_rate = 1e-5
        self.algorithm.schedule = "fixed"


@configclass
class MotionEnvelopeEnvCfg(MotionFoundationEnvCfg):
    """Experimental knee workspace; a distinct control contract, never a silent upgrade."""
    checkpoint_compatibility_tag = ENVELOPE_TAG
    motion_contract = envelope_contract()
    action_clip_per_joint = KNEE_CLIP


@configclass
class MotionEnvelopeRunnerCfg(MotionFoundationRunnerCfg):
    experiment_name = "csdog_motion_envelope"
