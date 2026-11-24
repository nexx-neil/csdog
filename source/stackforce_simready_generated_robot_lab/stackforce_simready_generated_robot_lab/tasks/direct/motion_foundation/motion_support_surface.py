"""Isolated reference change; do not alter any previous task or saved policy."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from csdog_motion.support_surface import TAG,SupportSurface,contract
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from .motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv


@configclass
class MotionSurfaceRoughEnvCfg(MotionScannedRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.checkpoint_compatibility_tag=TAG
        self.motion_contract=contract(self.motion_contract)


class MotionSurfaceRoughEnv(MotionScannedRoughEnv):
    def _setup_scene(self):
        super()._setup_scene()
        self.support_surface=SupportSurface(self.num_envs,self.device,self.step_dt)

    def _reset_idx(self,env_ids):
        super()._reset_idx(env_ids)
        if hasattr(self,'support_surface'):self.support_surface.reset(env_ids)

    def _support_ground(self):
        raw=self.height_scanner.data.ray_hits_w[:,:,2].mean(1)
        return self.support_surface.update(raw,self.common_step_counter)

    def _support_height(self):
        return self._robot.data.root_pos_w[:,2]-self._support_ground()

    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        r=self._robot.data
        target,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
        if self.cfg.sensor_reference_enabled:
            scan=self.height_scanner.data.ray_hits_w[:,:,2];spread=scan.amax(1)-scan.amin(1)
            extra=(spread-.002).clamp(0,.01)
            target=extra_swing_clearance(target,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend)
        self.desired_swing_clearance=target[:,:,2]-self.reference_nominal[None,:,2]
        if self.cfg.sensor_reference_enabled:
            quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
            world=quat_apply(quat,target.reshape(-1,3)).reshape(-1,4,3)+r.root_pos_w[:,None]
            ground=self._rays(world);delta=torch.zeros_like(target);delta[:,:,2]=ground-self._support_ground()[:,None]
            target+=quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(-1,4,3)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
