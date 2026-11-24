"""Same v38 execution; explicit separate high-speed contact-quality learning MDP."""
from isaaclab.utils import configclass
from .motion_trot_flight import MotionTrotFlightEnvCfg, MotionTrotFlightEnv

TAG='csdog_forward_trot_contact_quality_obs76_v40'
@configclass
class MotionTrotQualityEnvCfg(MotionTrotFlightEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__()
        self.reward_scales=dict(self.reward_scales,stance_slide=-5.,contact_schedule=4.,swing_load=-2.)
        self.motion_contract.update(schema_version=40,compatibility_tag=TAG)
        self.motion_contract['learning_reward_scales']=dict(self.reward_scales)
        self.motion_contract['contact_quality_learning']={'stance_slide_penalty':-5.,'contact_schedule_reward':4.,'swing_load_penalty':-2.,'controller':'v38 identical; separate learning MDP','learning_rate':1e-5,'reason':'v38 first25 updates increased speed but contact slide regressed; new trial from original frozen lesson20, no continuation of rejected actor'}

class MotionTrotQualityEnv(MotionTrotFlightEnv):pass
