"""Nonpromoted support-timing experiment, isolated from v11."""
import copy
from isaaclab.utils import configclass
from csdog_motion.support_transfer import TRANSFER_TAG,TRANSITION,transfer_contract
from .motion_clean import MotionCleanEnvCfg,MotionCleanEnv


@configclass
class MotionTransferEnvCfg(MotionCleanEnvCfg):
    checkpoint_compatibility_tag=TRANSFER_TAG
    motion_contract=transfer_contract()

    def __post_init__(self):
        super().__post_init__()
        self.reference_parameters=copy.deepcopy(self.reference_parameters)
        self.reference_parameters['support_feedback']['transition']=dict(TRANSITION)
        self.motion_contract=transfer_contract()


class MotionTransferEnv(MotionCleanEnv):
    pass


from csdog_motion.support_transfer import BACKWARD_TAG,BACKWARD_TRANSITION


@configclass
class MotionBackwardEnvCfg(MotionTransferEnvCfg):
    checkpoint_compatibility_tag=BACKWARD_TAG
    motion_contract=transfer_contract(backward=True)

    def __post_init__(self):
        super().__post_init__()
        self.reference_parameters['support_feedback']['transition']=dict(BACKWARD_TRANSITION)
        self.motion_contract=transfer_contract(backward=True)


class MotionBackwardEnv(MotionTransferEnv):
    pass
