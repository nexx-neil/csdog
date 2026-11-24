"""Independent support-frame ablation; preserve v36 and accepted daily entries."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse,quat_mul
from csdog_motion.stance_foothold import FootholdMemory
from csdog_motion.swing_workspace import allocate_swing,MIN_CLEARANCE_M
from csdog_motion.stance_workspace import TAG,contract,repair_stance
from .motion_contact_patch import MotionContactPatchEnv
from csdog_motion.workspace_height_preview import predict_applied_heights
from csdog_motion.workspace_height_priority import select_height
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from csdog_motion.reachable_clearance import allocate
from .motion_contact_tick_preview import MotionContactTickEnvCfg,MotionContactTickEnv
from .motion_terrain_turn import MotionTerrainTurnEnv

@configclass
class MotionStanceWorkspaceEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)

class MotionStanceWorkspaceEnv(MotionContactTickEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.patch=FootholdMemory(self.num_envs,self.device)
        self.patch_peak_count=0;self.patch_env_leg_steps=0;self.patch_force_disagreement_n=0.;self.swing_workspace_leg_steps=0;self.swing_min_clearance_surplus_m=float("inf")
    def _setup_scene(self):
        super()._setup_scene()
        from isaaclab.sensors import ContactSensor,ContactSensorCfg
        self._patch_sensors=[]
        for leg in ('lr','lf','rf','rr'):
            cfg=ContactSensorCfg(prim_path=f'/World/envs/env_.*/Robot/link_{leg}_sole',update_period=0.,track_contact_points=True,filter_prim_paths_expr=[self.cfg.terrain.prim_path+'/terrain/mesh'],max_contact_data_count_per_prim=16)
            sensor=ContactSensor(cfg);self._patch_sensors.append(sensor);self.scene.sensors['patch_'+leg]=sensor
    def _reset_idx(self,env_ids):
        super()._reset_idx(env_ids)
        if hasattr(self,'patch'):self.patch.reset(self._robot._ALL_INDICES if env_ids is None else env_ids)
    def _update_patch(self,active):
        r=self._robot.data;n=self.num_envs
        base,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        world=quat_apply(quat,base.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
        ground=self._rays(world);delta=torch.zeros_like(base);delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
        q,e=self.reference_model.solve(base+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3),iterations=18)
        margin=torch.minimum(q-self.reference_model.lower,self.reference_model.upper-q).amin(2)
        unsafe=(e>.00005)|(margin<self.patch.cfg.minimum_ray_joint_margin_rad)
        points=torch.stack([s.data.contact_pos_w[:,0,0]for s in self._patch_sensors],1)
        forces=torch.stack([s.data.force_matrix_w[:,0,0]for s in self._patch_sensors],1)
        self.patch_force_disagreement_n=max(self.patch_force_disagreement_n,float((forces-self._contact_sensor.data.net_forces_w[:,self._foot_ids]).norm(dim=-1).max()))
        self.patch.update(self.common_step_counter,stance,points,forces,self._surfaces()[:,1:],r.body_pos_w[:,self._robot_foot_ids],unsafe,active,hard_invalid=e>.00005)
        self.patch_peak_count=max(self.patch_peak_count,int(self.patch.active.sum()));self.patch_env_leg_steps+=int(self.patch.active.sum())
    def _patch_projection(self,world,tau=0.):
        keep=self.patch.continuing(self.motion.phase,tau,self.reference_config.period_s,self.reference_config.stance_fraction)
        anchored=world.clone();anchored[:,:,:2]=torch.where(keep[:,:,None],self.patch.xy,world[:,:,:2])
        ground=torch.where(keep,self.patch.height,self._rays(anchored))
        return anchored[:,:,:2]-world[:,:,:2],ground
    def _before_observations(self):
        ready=hasattr(self,'patch');active=~self._just_reset.clone()if ready else None
        if not ready:return super()._before_observations()
        if ready:self.motion.applied[:,3]=self.cfg.base_height_target;self.motion.height_rate.zero_()
        # Parent twist/yaw shaping advances once; avoid the v34 height update here.
        MotionTerrainTurnEnv._before_observations(self)
        if ready:
            d=self.contact_datum;c=self.height_coordinator
            if self._height_tick!=self.common_step_counter:
                self._update_patch(active)
                ground=self._surfaces().clone();ground[:,1:]=torch.where(self.patch.active,self.patch.height,ground[:,1:]);force=self._contact_sensor.data.net_forces_w[:,self._foot_ids,2]
                d.update(ground[:,0],ground[:,1:],force,self.common_step_counter,self.step_dt,active)
                self._plan_height();c.tick(self.step_dt,active);self._height_tick=self.common_step_counter
                self.height_adjustment_env_steps+=int((c.value.abs()>1e-6).sum())
                self.height_peak_offset=max(self.height_peak_offset,float(c.value.abs().max()));self.height_peak_velocity=max(self.height_peak_velocity,float(c.velocity.abs().max()));self.height_peak_acceleration=max(self.height_peak_acceleration,float(c.acceleration.abs().max()))
                self.datum_peak_velocity=max(self.datum_peak_velocity,float(d.velocity.abs().max()));self.datum_peak_acceleration=max(self.datum_peak_acceleration,float(d.acceleration.abs().max()))
            delta=d.value-self._surfaces()[:,0]
            self.datum_peak_root_difference=max(self.datum_peak_root_difference,float(delta.abs().max()))
            self.motion.applied[:,3]=self.cfg.base_height_target+c.value+delta
            self.motion.height_rate.copy_(c.velocity+d.velocity)
    _plan_height=MotionContactPatchEnv._plan_height
    def _reference(self):
        if not hasattr(self,'patch'):return super()._reference()
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        r=self._robot.data;n=self.num_envs
        base,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
        scan=self.height_scanner.data.ray_hits_w[:,:,2];extra=(scan.amax(1)-scan.amin(1)-.002).clamp(0,.01)
        full=extra_swing_clearance(base,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend);lift=full[:,:,2]-base[:,:,2]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        fixed_stance=None
        def target(scale):
            value=full.clone();value[:,:,2]-=lift*(1-scale)
            world=quat_apply(quat,value.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
            delta=torch.zeros_like(value);delta[:,:,:2],ground=self._patch_projection(world);delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
            projected=value+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            return projected if fixed_stance is None else torch.where(self.patch.active[:,:,None],fixed_stance,projected)
        preferred=target(torch.ones_like(lift))
        q,error=self.reference_model.solve(preferred,iterations=18)
        world=quat_apply(quat,preferred.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
        vertical=torch.zeros_like(world);vertical[:,:,2]=self.patch.xyz[:,:,2]-world[:,:,2]
        endpoint=preferred+quat_apply_inverse(quat,vertical.reshape(-1,3)).reshape(n,4,3)
        fixed_stance,q,error,fraction,repaired=repair_stance(self.reference_model,preferred,endpoint,self.patch.active&stance,q,error)
        self.stance_projection_leg_steps=getattr(self,'stance_projection_leg_steps',0)+int(repaired.sum())
        if repaired.any():
            shift=quat_apply(quat,(fixed_stance-preferred).reshape(-1,3)).reshape(n,4,3)[:,:,2]
            self.stance_projection_peak_shift_m=max(getattr(self,'stance_projection_peak_shift_m',0.),float(shift[repaired].abs().max()))
            self.stance_projection_peak_fraction=max(getattr(self,'stance_projection_peak_fraction',0.),float(fraction[repaired].max()))
        basic_lift=base[:,:,2]-self.reference_nominal[None,:,2];total=basic_lift+lift
        local=torch.remainder(self.motion.phase[:,None]+self.motion.phase.new_tensor([0.,.5,0.,.5]),1.)
        progress=((local-self.reference_config.stance_fraction)/(1-self.reference_config.stance_fraction)).clamp(0,1)
        minimum_gap=MIN_CLEARANCE_M*64*progress.pow(3)*(1-progress).pow(3)*self.motion.blend[:,None]
        def total_target(scale):
            # Convert total-lift scale into the old sensor scale algebraically.
            value=full.clone();value[:,:,2]-=total*(1-scale)
            world=quat_apply(quat,value.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
            delta=torch.zeros_like(value);delta[:,:,:2],ground=self._patch_projection(world);delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
            projected=value+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            return projected if fixed_stance is None else torch.where(self.patch.active[:,:,None],fixed_stance,projected)
        # The lower bound is evaluated lazily only after a legacy failure.
        def clearance_geometry(body):
            world=quat_apply(quat,body.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
            angle=torch.arange(8,device=self.device)*torch.pi/4
            offsets=torch.cat((torch.zeros(1,2,device=self.device),.018*torch.stack((torch.cos(angle),torch.sin(angle)),1)),0)
            samples=world[:,:,None,:].expand(-1,-1,9,-1).clone();samples[:,:,:,:2]+=offsets[None,None]
            ground=self._rays(samples.reshape(n,36,3)).reshape(n,4,9).amax(2)
            return world[:,:,2]-.018-ground
        # allocate_swing requests arithmetic on a lower bound, so compute it
        # only when the unchanged old allocator cannot retain its full result.
        try:
            lq,le,ls,la=allocate(self.reference_model,target,q,error,lift)
            legacy_ok=not bool(((le>.00005)&~stance).any())
        except RuntimeError as exc:
            if 'Base foot reference is infeasible; surplus lift cannot repair it' not in str(exc):raise
            legacy_ok=False
        if legacy_ok:
            q,error=lq,le;chosen=basic_lift+lift*ls;adjusted=la;optimized=torch.zeros_like(stance)
        else:
            zero=total_target(torch.zeros_like(total));zero_gap=clearance_geometry(zero)
            vertical=r.root_quat_w.new_zeros(n,4,3);vertical[:,:,2]=1.
            cos_tilt=quat_apply(quat,vertical.reshape(-1,3)).reshape(n,4,3)[:,:,2].clamp_min(.1)
            lower=(minimum_gap-zero_gap).clamp_min(0)/(total.clamp_min(1e-8)*cos_tilt)
            def safe(body):return clearance_geometry(body)>=minimum_gap-1e-6
            q,error,chosen,adjusted,optimized=allocate_swing(self.reference_model,target,total_target,q,error,basic_lift,lift,lower,safe,~stance)
            self.swing_workspace_leg_steps+=int(optimized.sum())
            if optimized.any():
                actual=total_target(chosen/total.clamp_min(1e-8));self.swing_min_clearance_surplus_m=min(self.swing_min_clearance_surplus_m,float((clearance_geometry(actual)-minimum_gap)[optimized].min()))
        self.clearance_scale=chosen/total.clamp_min(1e-8);self.clearance_adjusted_foot_steps=getattr(self,'clearance_adjusted_foot_steps',0)+int(adjusted.sum())
        self.desired_swing_clearance=chosen
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
