"""Two-phase loaded-foot binding and synchronous physics-step contact sampling."""
import copy
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from csdog_motion.adaptive_speed import adaptive_reference
from csdog_motion.post_filter_contacts import TAG,contract,PostFilterMemory,sensor_settings
from .motion_contact_tick_preview import MotionContactTickEnvCfg
from .motion_liftoff_handover import MotionLiftOffEnv

@configclass
class MotionPostFilterEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)
        self.contact_sensor=copy.deepcopy(self.contact_sensor)
        settings=sensor_settings(self.sim.dt,self.contact_sensor.update_period,self.contact_sensor.history_length)
        self.contact_sensor.update_period=settings['update_period'];self.contact_sensor.history_length=settings['history_length']

class MotionPostFilterEnv(MotionLiftOffEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.patch=PostFilterMemory(self.num_envs,self.device,self.patch.cfg)
    def _before_observations(self):
        ready=hasattr(self,'patch')and hasattr(self.patch,'late_bind')
        active=~self._just_reset.clone()if ready else None
        super()._before_observations()
        if not ready or self.patch.late_tick==self.common_step_counter:return
        r=self._robot.data;n=self.num_envs
        base,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        world=quat_apply(quat,base.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
        ground=self._rays(world);delta=torch.zeros_like(base)
        delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
        q,e=self.reference_model.solve(base+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3),iterations=18)
        margin=torch.minimum(q-self.reference_model.lower,self.reference_model.upper-q).amin(2)
        points=torch.stack([s.data.contact_pos_w[:,0,0]for s in self._patch_sensors],1)
        forces=torch.stack([s.data.force_matrix_w[:,0,0]for s in self._patch_sensors],1)
        self.patch_force_disagreement_n=max(self.patch_force_disagreement_n,float((forces-self._contact_sensor.data.net_forces_w[:,self._foot_ids]).norm(dim=-1).max()))
        entered=self.patch.late_bind(self.common_step_counter,stance,points,forces,self._surfaces()[:,1:],r.body_pos_w[:,self._robot_foot_ids],e,margin,active)
        self.patch_env_leg_steps+=int(entered.sum());self.patch_peak_count=max(self.patch_peak_count,int(self.patch.active.sum()))
