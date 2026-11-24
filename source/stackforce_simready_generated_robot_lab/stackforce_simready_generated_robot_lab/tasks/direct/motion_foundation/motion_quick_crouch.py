"""Separate shallow quick-crouch diagnostic; same 76-D walking network, no jump."""
import copy
from isaaclab.utils import configclass
from csdog_motion.quick_crouch import QuickHeightCommands
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.skill_supervisor import SkillConfig,SkillSupervisor,SkillMode
from csdog_motion.adaptive_speed import valid_request
from .motion_yaw import MotionYawSkillsEnvCfg,MotionYawSkillsEnv

TAG='csdog_quick_four_foot_crouch_obs76_v26'

@configclass
class MotionQuickCrouchEnvCfg(MotionYawSkillsEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__()
        self.motion_commands=dict(self.motion_commands,height_rate_m_s=.3)
        self.motion_contract=copy.deepcopy(self.motion_contract)
        self.motion_contract.update(schema_version=26,compatibility_tag=TAG)
        self.motion_contract['height']['rate_m_s']=.3
        self.motion_contract['height_profile'].update(full_6cm_duration_s=.4,peak_6cm_speed_mps=.28125)
        self.motion_contract['skill_supervisor']['limits']=vars(SkillConfig(nominal_height_m=self.base_height_target,maximum_drop_m=.06,stable_seconds=.06))
        self.motion_contract['quick_crouch']={'scope':'flat stationary four-foot support; moving trigger needs separate validation','no_shell_or_belly_contact':True,'target_duration_not_measured_latency':True,'stable_gate_seconds':.06,'old_fault_limits_retained':True,'brake_requires_applied_twist_zero':True}

class MotionQuickCrouchEnv(MotionYawSkillsEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.skills=SkillSupervisor(self.num_envs,self.device,SkillConfig(nominal_height_m=cfg.base_height_target,maximum_drop_m=.06,stable_seconds=.06),request_validator=valid_request)
        self.motion=QuickHeightCommands(self.num_envs,self.device,MotionCommandConfig(**cfg.motion_commands))

    def _before_observations(self):
        # Physical rest can precede the command ramp reaching zero. Accumulate
        # the short readiness dwell only once both are ready; keep fault clocks live.
        if hasattr(self,'skills') and self._skill_tick!=self.common_step_counter:
            pending=(self.skills.mode==SkillMode.BRAKE)&(self.motion.applied[:,:3].abs().amax(1)>1e-4)
            self.skills.stable_time[pending]=0
        super()._before_observations()
