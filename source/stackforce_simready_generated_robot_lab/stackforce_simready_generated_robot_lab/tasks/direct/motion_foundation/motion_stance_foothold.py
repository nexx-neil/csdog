"""Independent support-frame ablation; preserve v36 and accepted daily entries."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse,quat_mul
from csdog_motion.stance_foothold import TAG,FootholdMemory,contract
from csdog_motion.workspace_height_preview import predict_applied_heights
from csdog_motion.workspace_height_priority import select_height
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from csdog_motion.reachable_clearance import allocate
from .motion_contact_tick_preview import MotionContactTickEnvCfg,MotionContactTickEnv
from .motion_terrain_turn import MotionTerrainTurnEnv

@configclass
class MotionStanceFootholdEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)

class MotionStanceFootholdEnv(MotionContactTickEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.patch=FootholdMemory(self.num_envs,self.device)
        self.patch_peak_count=0;self.patch_env_leg_steps=0;self.patch_force_disagreement_n=0.
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
    def _plan_height(self):
        c=self.height_coordinator;d=self.contact_datum;r=self._robot.data;n=self.num_envs
        candidates=torch.linspace(-c.cfg.maximum_offset_m,c.cfg.maximum_offset_m,c.cfg.candidates,device=self.device);candidates[len(candidates)//2]=0.;k=len(candidates);targets=[]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        flow=quat_apply(r.root_quat_w,torch.cat((self.motion.applied[:,:2],torch.zeros(n,1,device=self.device)),1))
        for tau in c.cfg.preview_seconds:
            phase=torch.remainder(self.motion.phase+tau/self.reference_config.period_s,1.)
            target,_=adaptive_reference(phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
            world=quat_apply(quat,target.reshape(-1,3)).reshape(n,4,3)
            theta=self.motion.applied[:,2]*tau;co=torch.cos(theta)[:,None];si=torch.sin(theta)[:,None];x,y=world[:,:,0].clone(),world[:,:,1].clone();world[:,:,0]=co*x-si*y;world[:,:,1]=si*x+co*y
            world+=r.root_pos_w[:,None]+tau*flow[:,None]
            delta=torch.zeros_like(target);delta[:,:,:2],ground=self._patch_projection(world,tau);delta[:,:,2]=ground-(d.value+tau*d.velocity)[:,None]
            projected=target+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            keep=self.patch.continuing(self.motion.phase,tau,self.reference_config.period_s,self.reference_config.stance_fraction)
            yawq=torch.zeros(n,4,device=self.device);yawq[:,0]=torch.cos(theta/2);yawq[:,3]=torch.sin(theta/2)
            futureq=quat_mul(yawq,r.root_quat_w)[:,None].expand(-1,4,-1).reshape(-1,4)
            goal_root=r.root_pos_w+tau*flow;goal_root[:,2]=self.cfg.base_height_target+d.value+tau*d.velocity
            anchored=quat_apply_inverse(futureq,(self.patch.xyz-goal_root[:,None]).reshape(-1,3)).reshape(n,4,3)
            targets.append(torch.where(keep[:,:,None],anchored,projected))
        target=torch.stack(targets,1);t=target.shape[1]
        v=torch.zeros(n,4,3,device=self.device);v[:,:,2]=1;direction=quat_apply_inverse(quat,v.reshape(-1,3)).reshape(n,4,3)
        predicted=predict_applied_heights(c,candidates,self.step_dt)
        projected=target[:,None]-predicted[:,:,:,None,None]*direction[:,None,None]
        q,e=self.reference_model.solve(projected.reshape(n*k*t,4,3),iterations=18);margin=torch.minimum(q-self.reference_model.lower,self.reference_model.upper-q).amin(2)
        goal,good=select_height(e.reshape(n,k,t,4),margin.reshape(n,k,t,4),candidates,c.goal,c.cfg)
        c.goal.copy_(goal);self.height_preview_no_common_plan+=int((~good).sum())
    def _reference(self):
        if not hasattr(self,'patch'):return super()._reference()
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        r=self._robot.data;n=self.num_envs
        base,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
        scan=self.height_scanner.data.ray_hits_w[:,:,2];extra=(scan.amax(1)-scan.amin(1)-.002).clamp(0,.01)
        full=extra_swing_clearance(base,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend);lift=full[:,:,2]-base[:,:,2]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        def target(scale):
            value=full.clone();value[:,:,2]-=lift*(1-scale)
            world=quat_apply(quat,value.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
            delta=torch.zeros_like(value);delta[:,:,:2],ground=self._patch_projection(world);delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
            projected=value+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            anchored=quat_apply_inverse(quat,(self.patch.xyz-r.root_pos_w[:,None]).reshape(-1,3)).reshape(n,4,3)
            return torch.where(self.patch.active[:,:,None],anchored,projected)
        q,error=self.reference_model.solve(target(torch.ones_like(lift)),iterations=18)
        q,error,scale,adjusted=allocate(self.reference_model,target,q,error,lift)
        self.clearance_scale=scale;self.clearance_adjusted_foot_steps=getattr(self,'clearance_adjusted_foot_steps',0)+int(adjusted.sum())
        self.desired_swing_clearance=full[:,:,2]-self.reference_nominal[None,:,2]-lift*(1-scale)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
