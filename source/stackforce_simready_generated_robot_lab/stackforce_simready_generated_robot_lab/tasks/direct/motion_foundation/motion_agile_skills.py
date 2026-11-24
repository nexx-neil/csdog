"""Adaptive locomotion and smooth stationary crouch; lie/jump remain unavailable."""
from isaaclab.utils import configclass
import torch
from csdog_motion.adaptive_speed import fast_contract,valid_request,LIMITS,adaptive_reference,stance_fraction
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.smooth_height import SmoothHeightCommandState
from csdog_motion.skill_supervisor import SkillSupervisor,SkillConfig,SkillMode
from csdog_motion.support_feedback import support_weights
from .motion_responsive_skills import MotionResponsiveSkillsEnvCfg,MotionResponsiveSkillsEnv

TAG='csdog_adaptive_smooth_guarded_skills_diagnostic_obs74_v19'


def agile_contract():
    from .motion_responsive_skills import responsive_contract
    value=responsive_contract();fast=fast_contract()
    for key in ('command_envelope','training_command_ranges','fast_timing'):value[key]=fast[key]
    value.update(schema_version=19,compatibility_tag=TAG)
    value['height']['rate_m_s']=.12
    value['height_profile']={'type':'quintic rest-to-rest segments','full_6cm_duration_s':1.,
        'reversal':'complete current bounded segment, then latest queued goal; no low-body movement',
        'fault':'immediate freeze of applied height, discard segment',
        'peak_6cm_speed_mps':.1125,'lie_down_enabled':False,'jump_enabled':False}
    return value


@configclass
class MotionAgileSkillsEnvCfg(MotionResponsiveSkillsEnvCfg):
    checkpoint_compatibility_tag=TAG
    motion_contract=agile_contract()

    def __post_init__(self):
        super().__post_init__()
        self.motion_commands=dict(self.motion_commands,limits=LIMITS,height_rate_m_s=.12)
        self.motion_contract=agile_contract()


class MotionAgileSkillsEnv(MotionResponsiveSkillsEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.skills=SkillSupervisor(self.num_envs,self.device,
            SkillConfig(nominal_height_m=cfg.base_height_target,maximum_drop_m=.06),request_validator=valid_request)
        self.motion=SmoothHeightCommandState(self.num_envs,self.device,MotionCommandConfig(**cfg.motion_commands))

    def _set_supervised_request(self,request):
        self.motion.freeze_height.copy_(self.skills.mode==SkillMode.FAULT)
        self.motion.set_request(request)

    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,
            self.reference_config,blend=self.motion.blend,height_delta=self.motion.applied[:,3]-self.cfg.base_height_target)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=(q.flatten(1),error,stance);self._reference_tick=self.common_step_counter
        return self._reference_cache

    def _support_weights(self):
        weights=support_weights(self.motion.phase,self.motion.blend,stance_fraction(self.motion.applied[:,:3])[:,None],
            self.cfg.reference_parameters['support_feedback'].get('transition'),twist=self.motion.applied[:,:3])
        return torch.where((self.motion.applied[:,0].abs()>.5)[:,None],weights,super()._support_weights())
