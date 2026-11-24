"""Bounded inference only; migrate weights explicitly from v45 without Adam."""
import torch
from isaaclab.utils import configclass
from csdog_motion.trot_bounded import TAG,CAP,valid_request,contract
from .motion_trot_return import MotionTrotReturnEnvCfg,MotionTrotReturnEnv
@configclass
class MotionTrotBoundedEnvCfg(MotionTrotReturnEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__();self.motion_commands=dict(self.motion_commands,limits=(CAP,.4,.8));self.motion_contract=contract(self.motion_contract)
        self.residual_training_enabled=False;self.periodic_commands=False
class MotionTrotBoundedEnv(MotionTrotReturnEnv):
    def set_motion_request(self,request,env_ids=None):
        value=torch.as_tensor(request,device=self.device);twist=value.reshape(-1,value.shape[-1])[:,:3]
        if not valid_request(twist).all():raise ValueError('Bounded forward cap .95; old mixed and other axis limits retained')
        return super().set_motion_request(request,env_ids)
