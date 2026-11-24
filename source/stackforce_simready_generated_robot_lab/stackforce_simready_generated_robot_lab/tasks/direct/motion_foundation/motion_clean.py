"""Isolated adaptive-clearance reference, explicitly migrated from a speed policy."""
from isaaclab.utils import configclass
from csdog_motion.clean_gait import CLEAN_TAG,clean_learning_contract,clean_foot_reference
from .motion_residual import MotionResidualSpeedEnvCfg,MotionResidualSpeedEnv


@configclass
class MotionCleanEnvCfg(MotionResidualSpeedEnvCfg):
    checkpoint_compatibility_tag=CLEAN_TAG
    motion_contract=clean_learning_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=clean_learning_contract()


class MotionCleanEnv(MotionResidualSpeedEnv):
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=clean_foot_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,
            self.reference_config,blend=self.motion.blend)
        q,error=self.reference_model.solve(target,iterations=12)
        self._reference_cache=(q.flatten(1),error,stance)
        self._reference_tick=self.common_step_counter
        return self._reference_cache
