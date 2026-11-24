"""Separate flat running-support reference and residual-learning task."""
import torch
from isaaclab.utils import configclass
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.trot_course import TAG,TrotCommands,contract,valid_request,reference,duty,sample_commands
from csdog_motion.support_feedback import support_weights
from .motion_yaw import MotionYawEnvCfg,MotionYawEnv
from .motion_reference import MotionReferenceEnv

@configclass
class MotionTrotEnvCfg(MotionYawEnvCfg):
    checkpoint_compatibility_tag=TAG
    residual_training_enabled=True
    def __post_init__(self):
        super().__post_init__()
        self.motion_commands=dict(self.motion_commands,limits=(.8,.4,.8))
        self.motion_contract=contract(self.motion_contract,training=True)

class MotionTrotEnv(MotionYawEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs)
        self.motion=TrotCommands(self.num_envs,self.device,MotionCommandConfig(**cfg.motion_commands))
    def set_motion_request(self,request,env_ids=None):
        twist=torch.as_tensor(request,device=self.device).reshape(-1,torch.as_tensor(request).shape[-1])[:,:3]
        if not valid_request(twist).all():raise ValueError('Trot extension is forward-only; old mixed/axis limits retained')
        MotionReferenceEnv.set_motion_request(self,request,env_ids)
    def _sample_commands(self,env_ids):
        if self.motion is None:return super()._sample_commands(env_ids)
        self.motion.set_request(sample_commands(len(env_ids),self.device),env_ids)
        low,high=self.cfg.command_resampling_interval_s
        self._command_remaining[env_ids]=torch.empty(len(env_ids),device=self.device).uniform_(low,high)
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        target,stance=reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
    def _support_weights(self):
        twist=self.motion.applied[:,:3]
        weights=support_weights(self.motion.phase,self.motion.blend,duty(twist)[:,None],self.cfg.reference_parameters['support_feedback'].get('transition'),twist=twist)
        return torch.where((twist[:,0]>.6)[:,None],weights,super()._support_weights())
