"""Independent v32 controller; all prior terrain and flat tasks remain frozen."""
import copy
from isaaclab.utils import configclass
from csdog_motion.terrain_control import TAG,YAW,contract
from .motion_scanned_rough import MotionScannedRoughEnvCfg
from .motion_reachable_clearance import MotionReachableRoughEnv


@configclass
class MotionTerrainControlEnvCfg(MotionScannedRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG
        self.motion_contract=contract(self.motion_contract)
        self.reference_parameters=copy.deepcopy(self.reference_parameters)
        self.reference_parameters['support_feedback']['yaw_integral']=self.motion_contract['support_feedback']['yaw_integral']


class MotionTerrainControlEnv(MotionReachableRoughEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.yaw_control.cfg=YAW
