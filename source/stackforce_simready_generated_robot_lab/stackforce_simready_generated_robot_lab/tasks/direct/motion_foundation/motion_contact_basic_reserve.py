"""Independent stricter mandatory basic preview; v49 execution unchanged."""
from dataclasses import replace
from isaaclab.utils import configclass
from csdog_motion.contact_basic_reserve import TAG,contract,RESERVE_RAD
from .motion_contact_datum import MotionContactDatumEnvCfg,MotionContactDatumEnv
@configclass
class MotionContactReserveEnvCfg(MotionContactDatumEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
class MotionContactReserveEnv(MotionContactDatumEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.height_coordinator.cfg=replace(self.height_coordinator.cfg,joint_reserve_rad=RESERVE_RAD)
