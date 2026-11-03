"""Reuse V3 architecture and all Spot terms; repair stopping semantics only."""
from isaaclab.utils import configclass
from isaaclab.managers import RewardTermCfg
from ..spot_aligned_v3.config import AlignedEnvCfg,AlignedPPOCfg
from . import rewards
from .gait import GroundedGaitReward
@configclass
class V4EnvCfg(AlignedEnvCfg):
 def __post_init__(self):
  super().__post_init__()
  self.rewards.gait.func=GroundedGaitReward
  self.rewards.joint_pos.func=rewards.joint_position_penalty
  self.rewards.joint_pos.params={'stand_still_scale':5.}
  self.rewards.stand_motion=RewardTermCfg(func=rewards.stand_motion_penalty,weight=-1.)
  # Preserve the last V3 experiment's calibrated learning regularization, not its static-policy first round.
  self.rewards.action_smoothness.weight=-.2
@configclass
class V4PPOCfg(AlignedPPOCfg):
 experiment_name='csdog_ppo_spot_v4'
 # CLI supplies the actual update count; inherited official algorithm is unchanged.
 policy=AlignedPPOCfg().policy.copy()
 def __post_init__(self):
  self.policy.init_noise_std=.4
