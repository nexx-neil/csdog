"""Separate deeper/faster crouch experiment; locomotion remains v14."""
from isaaclab.utils import configclass
from csdog_motion.skill_supervisor import SkillConfig, SkillSupervisor
from .motion_skills import MotionSkillsEnv, MotionBackwardSkillsEnvCfg, skills_contract

TAG = 'csdog_responsive_guarded_crouch_diagnostic_obs74_v16'
DROP_M = .06
HEIGHT_RATE_MPS = .06


def responsive_contract():
    value = skills_contract(backward=True)
    value.update(schema_version=16, compatibility_tag=TAG)
    nominal = SkillConfig().nominal_height_m
    value['height'] = dict(value['height'], range_m=[nominal-DROP_M, nominal], rate_m_s=HEIGHT_RATE_MPS)
    value['skill_supervisor']['limits'] = vars(SkillConfig(maximum_drop_m=DROP_M))
    value['skill_supervisor']['default_drop_m'] = DROP_M
    return value


@configclass
class MotionResponsiveSkillsEnvCfg(MotionBackwardSkillsEnvCfg):
    checkpoint_compatibility_tag = TAG
    motion_contract = responsive_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract = responsive_contract()
        self.motion_commands = dict(self.motion_commands, height_min_m=self.base_height_target-DROP_M,
                                    height_rate_m_s=HEIGHT_RATE_MPS)


class MotionResponsiveSkillsEnv(MotionSkillsEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg, **kwargs)
        self.skills = SkillSupervisor(self.num_envs, self.device,
            SkillConfig(nominal_height_m=cfg.base_height_target, maximum_drop_m=DROP_M))

    def request_crouch(self, drop_m=DROP_M, env_ids=None):
        self.skills.request_crouch(drop_m, env_ids)
