"""Same v38 execution; explicit separate high-speed contact-quality learning MDP."""
from isaaclab.utils import configclass
from .motion_trot_flight import MotionTrotFlightEnvCfg, MotionTrotFlightEnv

TAG='csdog_forward_trot_contact_quality_obs76_v44'
@configclass
class MotionTrotGripEnvCfg(MotionTrotFlightEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__()
        self.reward_scales=dict(self.reward_scales,stance_slide=-20.,contact_schedule=4.,swing_load=-2.)
        self.motion_contract.update(schema_version=44,compatibility_tag=TAG)
        self.motion_contract['learning_reward_scales']=dict(self.reward_scales)
        self.motion_contract['contact_quality_learning']={'stance_slide_penalty':-20.,'contact_schedule_reward':4.,'swing_load_penalty':-2.,'controller':'v38 identical; separate learning MDP','learning_rate':1e-5,'reason':'v40 25/50 updates still exceeded declared .075m/s slide cap; restart original lesson20 with stronger physical stance-slide penalty, same controller and acceptance gates'}

class MotionTrotGripEnv(MotionTrotFlightEnv):pass
