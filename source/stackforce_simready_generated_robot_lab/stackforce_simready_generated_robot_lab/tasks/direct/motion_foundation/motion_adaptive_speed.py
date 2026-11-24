"""Explicit v14 tensor transfer into two untrainable larger-envelope diagnostics."""
from isaaclab.utils import configclass
from csdog_motion.adaptive_speed import LIMITS, ADAPTIVE_TAG, EXPOSED_TAG, fast_contract, valid_request, adaptive_reference, stance_fraction
from csdog_motion.support_feedback import support_weights
from .motion_transfer import MotionBackwardEnvCfg, MotionBackwardEnv
from .motion_reference import MotionReferenceEnv
import torch


@configclass
class MotionAdaptiveSpeedEnvCfg(MotionBackwardEnvCfg):
    checkpoint_compatibility_tag=ADAPTIVE_TAG
    adaptive_timing=True
    training_enabled=False
    residual_training_enabled=False
    periodic_commands=False
    motion_contract=fast_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_commands=dict(self.motion_commands,limits=LIMITS)
        self.motion_contract=fast_contract(self.adaptive_timing)


@configclass
class MotionExposedSpeedEnvCfg(MotionAdaptiveSpeedEnvCfg):
    checkpoint_compatibility_tag=EXPOSED_TAG
    adaptive_timing=False
    motion_contract=fast_contract(False)


class MotionAdaptiveSpeedEnv(MotionBackwardEnv):
    def set_motion_request(self,request,env_ids=None):
        twist=torch.as_tensor(request,device=self.device)[...,:3]
        if not valid_request(twist).all():
            raise ValueError('Only the legacy mixed box or declared fast single axes are allowed')
        MotionReferenceEnv.set_motion_request(self,request,env_ids)

    def _sample_commands(self,env_ids):
        self._commands[env_ids]=0
        if self.motion is not None:
            self.motion.set_request([0.,0.,0.],env_ids)
            self._command_remaining[env_ids]=1e6

    def _reference(self):
        if not self.cfg.adaptive_timing:return super()._reference()
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,
            self.reference_config,blend=self.motion.blend)
        q,error=self.reference_model.solve(target,iterations=12)
        self._reference_cache=(q.flatten(1),error,stance);self._reference_tick=self.common_step_counter
        return self._reference_cache

    def _support_weights(self):
        if not self.cfg.adaptive_timing:return super()._support_weights()
        weights=support_weights(self.motion.phase,self.motion.blend,
            stance_fraction(self.motion.applied[:,:3])[:,None],
            self.cfg.reference_parameters['support_feedback'].get('transition'),twist=self.motion.applied[:,:3])
        return torch.where((self.motion.applied[:,0].abs()>.5)[:,None],weights,super()._support_weights())
