"""Isolated reference change; do not alter any previous task or saved policy."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from csdog_motion.reachable_clearance import TAG,contract,allocate
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from .motion_scanned_rough import MotionScannedRoughEnvCfg,MotionScannedRoughEnv


@configclass
class MotionReachableRoughEnvCfg(MotionScannedRoughEnvCfg):
    def __post_init__(self):
        super().__post_init__()
        self.checkpoint_compatibility_tag=TAG
        self.motion_contract=contract(self.motion_contract)


class MotionReachableRoughEnv(MotionScannedRoughEnv):
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        q,error,stance=super()._reference()
        if not self.cfg.sensor_reference_enabled:return q,error,stance
        base,_=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
        scan=self.height_scanner.data.ray_hits_w[:,:,2];extra=(scan.amax(1)-scan.amin(1)-.002).clamp(0,.01)
        full=extra_swing_clearance(base,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend)
        lift=full[:,:,2]-base[:,:,2]
        r=self._robot.data;quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        def target(scale):
            value=full.clone();value[:,:,2]-=lift*(1-scale)
            world=quat_apply(quat,value.reshape(-1,3)).reshape(-1,4,3)+r.root_pos_w[:,None]
            ground=self._rays(world);delta=torch.zeros_like(value);delta[:,:,2]=ground-self._surfaces()[:,0:1]
            return value+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(-1,4,3)
        new,error,scale,active=allocate(self.reference_model,target,q.reshape(-1,4,3),error,lift)
        self.clearance_scale=scale
        self.clearance_adjusted_foot_steps=getattr(self,'clearance_adjusted_foot_steps',0)+int(active.sum())
        self.desired_swing_clearance-=lift*(1-scale)
        self._reference_cache=new.flatten(1),error,stance
        return self._reference_cache
