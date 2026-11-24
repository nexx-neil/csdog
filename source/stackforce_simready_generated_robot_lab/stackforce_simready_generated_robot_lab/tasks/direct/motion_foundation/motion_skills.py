"""Nontrainable guarded locomotion/crouch/rise task on the v11 controller."""
import torch
from isaaclab.utils import configclass
from csdog_motion.clean_gait import clean_foot_reference, clean_learning_contract
from csdog_motion.skill_supervisor import SkillConfig, SkillSupervisor
from .motion_clean import MotionCleanEnv, MotionCleanEnvCfg

SKILLS_TAG = 'csdog_guarded_crouch_rise_diagnostic_obs74_v12'
BACKWARD_SKILLS_TAG = 'csdog_backward_guarded_crouch_rise_diagnostic_obs74_v15'


def skills_contract(backward=False):
    from csdog_motion.support_transfer import transfer_contract
    value = transfer_contract(backward=True) if backward else clean_learning_contract()
    value.update(schema_version=15 if backward else 12, compatibility_tag=BACKWARD_SKILLS_TAG if backward else SKILLS_TAG)
    value['height'] = dict(value['height'], range_m=[.33144956, .37144956], rate_m_s=.02)
    value['skill_supervisor'] = {'states':['LOCOMOTION','BRAKE','LOWER','HOLD','RISE','SETTLE','FAULT'],
        'limits':vars(SkillConfig()), 'residual':'gait-blend remains zero during posture changes',
        'command_interface':'request_twist queues a rise before motion; request_crouch brakes before lowering; request_stand rises and stays',
        'fault':'latching stop and freeze applied height; explicit reset required', 'scope':'flat ground only; crouch, not belly-contact lie-down; no jump'}
    value['terrain_support'] = 'flat only; bounded stationary height actuation; no terrain sensing'
    return value


@configclass
class MotionSkillsEnvCfg(MotionCleanEnvCfg):
    checkpoint_compatibility_tag = SKILLS_TAG
    motion_contract = skills_contract()
    residual_training_enabled = False
    training_enabled = False
    periodic_commands = False
    training_block_reason = 'Guarded skills are inference/diagnostic only; no posture-learning reward is defined'

    def __post_init__(self):
        super().__post_init__()
        self.motion_contract = skills_contract()
        self.motion_commands = dict(self.motion_commands, height_min_m=self.base_height_target-.04,
                                    height_max_m=self.base_height_target, height_rate_m_s=.02)
        self.command_ranges = {key:(0.,0.) for key in self.command_ranges}


class MotionSkillsEnv(MotionCleanEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg, **kwargs)
        self.skills = SkillSupervisor(self.num_envs, self.device, SkillConfig(nominal_height_m=cfg.base_height_target))
        self._skill_tick = -1
        self._external_commands = True

    def set_motion_request(self, request, env_ids=None):
        value = torch.as_tensor(request)
        if value.shape[-1] != 3:
            raise ValueError('Use request_crouch/drop or request_stand for guarded height changes')
        self.skills.request_twist(request, env_ids)
        self._external_commands = True

    def request_crouch(self, drop_m=.04, env_ids=None):
        self.skills.request_crouch(drop_m, env_ids)

    def request_stand(self, env_ids=None):
        self.skills.request_stand(env_ids)

    def _sample_commands(self, env_ids):
        self._commands[env_ids] = 0
        if self.motion is not None:
            self.motion.set_request([0.,0.,0.], env_ids)
            self._command_remaining[env_ids] = 1e6

    def _reset_idx(self, env_ids):
        if hasattr(self, 'skills'):
            self.skills.reset(env_ids)
            self._skill_tick = -1
        super()._reset_idx(env_ids)

    def _before_observations(self):
        if hasattr(self, 'skills') and self._skill_tick != self.common_step_counter:
            robot = self._robot.data
            contacts = torch.linalg.vector_norm(self._contact_sensor.data.net_forces_w[:,self._foot_ids],dim=-1)>1.
            twist = torch.cat((robot.root_lin_vel_b[:,:2],robot.root_ang_vel_b[:,2:3]),1)
            tilt = torch.acos((-robot.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi
            request = self.skills.tick(self.step_dt, twist=twist, tilt_deg=tilt, contacts=contacts,
                blend=self.motion.blend, applied_height=self.motion.applied[:,3],
                actual_height=robot.root_pos_w[:,2]-self._terrain.env_origins[:,2], active=~self._just_reset)
            self._set_supervised_request(request)
            self._skill_tick = self.common_step_counter
        super()._before_observations()

    def _set_supervised_request(self,request):
        self.motion.set_request(request)

    def _reference(self):
        if self._reference_tick == self.common_step_counter:
            return self._reference_cache
        target, stance = clean_foot_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,
            self.reference_config,blend=self.motion.blend,height_delta=self.motion.applied[:,3]-self.cfg.base_height_target)
        q, error = self.reference_model.solve(target,iterations=18)
        self._reference_cache = (q.flatten(1),error,stance)
        self._reference_tick = self.common_step_counter
        return self._reference_cache

    def _pre_physics_step(self, actions):
        if ((self.motion.applied[:,3] < self.cfg.base_height_target-.0005) & (self.motion.blend > .001)).any():
            raise RuntimeError('Supervisor invariant violated: locomotion blend while lowered')
        super()._pre_physics_step(actions)

    def _get_rewards(self):
        # Existing flat-gait clearance rewards do not define posture learning.
        return torch.zeros(self.num_envs,device=self.device)


@configclass
class MotionBackwardSkillsEnvCfg(MotionSkillsEnvCfg):
    checkpoint_compatibility_tag = BACKWARD_SKILLS_TAG
    motion_contract = skills_contract(backward=True)

    def __post_init__(self):
        super().__post_init__()
        from csdog_motion.support_transfer import BACKWARD_TRANSITION
        self.reference_parameters['support_feedback']['transition'] = dict(BACKWARD_TRANSITION)
        self.motion_contract = skills_contract(backward=True)
