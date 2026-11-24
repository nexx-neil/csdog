"""Independent complete control-tick sampling; v54 sources remain frozen."""
from dataclasses import replace
from isaaclab.utils import configclass
from csdog_motion.contact_tick_preview import TAG,contract,PREVIEW_SECONDS
from .motion_contact_basic_reserve import MotionContactReserveEnvCfg,MotionContactReserveEnv
@configclass
class MotionContactTickEnvCfg(MotionContactReserveEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
class MotionContactTickEnv(MotionContactReserveEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.height_coordinator.cfg=replace(self.height_coordinator.cfg,preview_seconds=PREVIEW_SECONDS)
