"""Observed yaw-integral experiment, separately identified from 74-D parents."""
import copy
import torch
from isaaclab.utils import configclass
from csdog_motion.yaw_integral import YawIntegral,yaw_contract,YAW_TAG,YAW_SKILLS_TAG
from csdog_motion.support_feedback import transfer_strength
from .motion_adaptive_speed import MotionAdaptiveSpeedEnvCfg,MotionAdaptiveSpeedEnv
from .motion_agile_skills import MotionAgileSkillsEnvCfg,MotionAgileSkillsEnv,agile_contract
from csdog_motion.adaptive_speed import fast_contract


class YawMixin:
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.yaw_control=YawIntegral(self.num_envs,self.device)
        self._yaw_tick=self.common_step_counter

    def _reset_idx(self,env_ids):
        if hasattr(self,'yaw_control'):
            if env_ids is None:env_ids=self._robot._ALL_INDICES
            self.yaw_control.reset(env_ids)
            self._yaw_tick=-1
        super()._reset_idx(env_ids)

    def _before_observations(self):
        active=~self._just_reset.clone() if hasattr(self,'yaw_control') else None
        super()._before_observations()
        if hasattr(self,'yaw_control') and self._yaw_tick!=self.common_step_counter:
            applied=self.motion.applied[:,:3];feedback=self.cfg.reference_parameters['support_feedback']
            transition=feedback['transition'];back=transfer_strength(applied,transition)
            gain=feedback['yaw_gain_nm_s_rad']+(transition['backward_yaw_gain_nm_s_rad']-feedback['yaw_gain_nm_s_rad'])*back
            actual=self._robot.data.root_ang_vel_b[:,2]
            self.yaw_control.tick(self.step_dt,applied,self.motion.request[:,:3],actual,gain*(applied[:,2]-actual),active)
            self._yaw_tick=self.common_step_counter

    def _get_observations(self):
        base=super()._get_observations()['policy']
        if hasattr(self,'yaw_control'):
            state=torch.stack((self.yaw_control.integral/.6,self.yaw_control.filtered_error/.8),1)
        else:state=torch.zeros(self.num_envs,2,device=self.device)
        return {'policy':torch.cat((base,state),1)}

    def _support_parameters(self):
        result=super()._support_parameters()
        if hasattr(self,'yaw_control'):result=dict(result,yaw_extra_moment_nm=self.yaw_control.moment)
        return result


@configclass
class MotionYawEnvCfg(MotionAdaptiveSpeedEnvCfg):
    checkpoint_compatibility_tag=YAW_TAG
    observation_space=76
    motion_contract=yaw_contract(fast_contract())

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=yaw_contract(fast_contract())
        self.reference_parameters=copy.deepcopy(self.reference_parameters)
        self.reference_parameters['support_feedback']['yaw_integral']=self.motion_contract['support_feedback']['yaw_integral']


class MotionYawEnv(YawMixin,MotionAdaptiveSpeedEnv):pass


@configclass
class MotionYawSkillsEnvCfg(MotionAgileSkillsEnvCfg):
    checkpoint_compatibility_tag=YAW_SKILLS_TAG
    observation_space=76
    motion_contract=yaw_contract(agile_contract(),skills=True)

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract=yaw_contract(agile_contract(),skills=True)
        self.reference_parameters=copy.deepcopy(self.reference_parameters)
        self.reference_parameters['support_feedback']['yaw_integral']=self.motion_contract['support_feedback']['yaw_integral']


class MotionYawSkillsEnv(YawMixin,MotionAgileSkillsEnv):pass
