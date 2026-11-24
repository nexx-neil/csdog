"""Inference-only composition of independently checked trot and quick shallow crouch."""
import torch
from isaaclab.utils import configclass
from csdog_motion.trot_return import contract,period,duty,reference,valid_request
from csdog_motion.quick_crouch import QuickHeightCommands
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.skill_supervisor import SkillSupervisor,SkillConfig
from csdog_motion.support_feedback import support_weights
from .motion_quick_crouch import MotionQuickCrouchEnvCfg,MotionQuickCrouchEnv

TAG='csdog_plateau_trot_quick_skills_obs76_v46'

class QuickReturnCommands(QuickHeightCommands):
    def tick(self,dt,ids=None,foot_contact=None):
        ids=torch.arange(len(self.phase),device=self.device) if ids is None else ids
        super().tick(dt,ids,foot_contact)
        self.phase[ids]=torch.remainder(self.phase[ids]+dt*(1/period(self.applied[ids,:3])-1/self.cfg.gait_period_s),1.)

@configclass
class MotionReturnSkillsEnvCfg(MotionQuickCrouchEnvCfg):
    checkpoint_compatibility_tag=TAG
    def __post_init__(self):
        super().__post_init__()
        self.motion_commands=dict(self.motion_commands,limits=(1.,.4,.8))
        self.motion_contract=contract(self.motion_contract)
        self.motion_contract.update(schema_version=46,compatibility_tag=TAG)
        self.motion_contract['scope']='Independent flat trot + shallow crouch inference; no jump or generic rough terrain claim'

class MotionReturnSkillsEnv(MotionQuickCrouchEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.skills=SkillSupervisor(self.num_envs,self.device,SkillConfig(nominal_height_m=cfg.base_height_target,maximum_drop_m=.06,stable_seconds=.06),request_validator=valid_request)
        self.motion=QuickReturnCommands(self.num_envs,self.device,MotionCommandConfig(**cfg.motion_commands))
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend,height_delta=self.motion.applied[:,3]-self.cfg.base_height_target)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
    def _support_weights(self):
        twist=self.motion.applied[:,:3]
        weights=support_weights(self.motion.phase,self.motion.blend,duty(twist)[:,None],self.cfg.reference_parameters['support_feedback'].get('transition'),twist=twist)
        return torch.where((twist[:,0]>.6)[:,None],weights,super()._support_weights())
