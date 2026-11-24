"""Separate high-speed return trajectory and explicit contact-quality learning."""
import torch
from isaaclab.utils import configclass
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.trot_return import TAG,ReturnCommands,contract,valid_request,reference,duty,sample_commands
from .motion_trot_flight import MotionTrotFlightEnv
from .motion_trot_quality import MotionTrotQualityEnvCfg

@configclass
class MotionTrotReturnEnvCfg(MotionTrotQualityEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=contract(self.motion_contract)
        self.motion_contract['contact_quality_learning']['reason']='Separate C2 velocity-plateau return; retain .4 duty to avoid extra flight; same v40 learning rewards and acceptance limits'

class MotionTrotReturnEnv(MotionTrotFlightEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.motion=ReturnCommands(self.num_envs,self.device,MotionCommandConfig(**cfg.motion_commands))
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
    def _support_weights(self):
        # v25 already uses the same .4 high-speed duty and original force limits.
        from .motion_trot_course import MotionTrotEnv
        return MotionTrotEnv._support_weights(self)
