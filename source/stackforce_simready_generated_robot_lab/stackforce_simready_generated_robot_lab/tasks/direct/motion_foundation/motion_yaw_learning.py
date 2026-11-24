"""Only a dedicated gated launcher may optimize this flat residual task."""
from isaaclab.utils import configclass
from csdog_motion.yaw_learning import TAG,learning_contract,sample_commands
from .motion_yaw import MotionYawEnvCfg,MotionYawEnv
import torch


@configclass
class MotionYawLearningEnvCfg(MotionYawEnvCfg):
    checkpoint_compatibility_tag=TAG
    training_enabled=False
    residual_training_enabled=True
    periodic_commands=True

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=learning_contract(self.motion_contract)


class MotionYawLearningEnv(MotionYawEnv):
    def _sample_commands(self,env_ids):
        if self.motion is None:return super()._sample_commands(env_ids)
        cmd,_=sample_commands(len(env_ids),self.device)
        self.motion.set_request(cmd,env_ids)
        self._commands[env_ids]=self.motion.applied[env_ids,:3]
        low,high=self.cfg.command_resampling_interval_s
        self._command_remaining[env_ids]=torch.empty(len(env_ids),device=self.device).uniform_(low,high)
