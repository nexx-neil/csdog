import copy
from isaaclab.utils import configclass
from csdog_motion.terrain_yaw_gain import TAG,contract,TerrainYawIntegral,YAW
from .motion_scanned_rough import MotionScannedRoughEnvCfg
from .motion_terrain_control import MotionTerrainControlEnv

@configclass
class MotionTerrainTurnEnvCfg(MotionScannedRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
        self.reference_parameters=copy.deepcopy(self.reference_parameters)
        self.reference_parameters['support_feedback']['yaw_integral']=self.motion_contract['support_feedback']['yaw_integral']

class MotionTerrainTurnEnv(MotionTerrainControlEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.yaw_control=TerrainYawIntegral(self.num_envs,self.device,YAW)
