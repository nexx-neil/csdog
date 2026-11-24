"""Independent measured liftoff handover; retain accepted daily controllers."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse,quat_mul
from csdog_motion.liftoff_handover import TAG,contract,LiftOffMemory
from csdog_motion.stance_workspace import repair_stance
from csdog_motion.stance_preview_rank import reachable_stance_forecast
from csdog_motion.swing_workspace import allocate_swing,MIN_CLEARANCE_M
from csdog_motion.reachable_clearance import allocate
from csdog_motion.workspace_height_preview import predict_applied_heights
from csdog_motion.workspace_height_priority import select_height
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from .motion_contact_tick_preview import MotionContactTickEnvCfg
from .motion_stance_preview_rank import MotionStanceRankEnv

@configclass
class MotionLiftOffEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)

class MotionLiftOffEnv(MotionStanceRankEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.handover=LiftOffMemory(self.num_envs,self.device)
    def _reset_idx(self,env_ids):
        super()._reset_idx(env_ids)
        if hasattr(self,'handover'):self.handover.reset(self._robot._ALL_INDICES if env_ids is None else env_ids)
    def _handover_duty(self):
        return torch.where(self.motion.applied[:,0].abs()>.5,stance_fraction(self.motion.applied[:,:3]),torch.full_like(self.motion.phase,self.reference_config.stance_fraction))
    def _plan_height(self):
        if not hasattr(self,'handover'):return super()._plan_height()
        c=self.height_coordinator;d=self.contact_datum;r=self._robot.data;n=self.num_envs
        candidates=torch.linspace(-c.cfg.maximum_offset_m,c.cfg.maximum_offset_m,c.cfg.candidates,device=self.device);candidates[len(candidates)//2]=0.
        k=len(candidates);targets=[];endpoints=[];continuing=[]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        flow=quat_apply(r.root_quat_w,torch.cat((self.motion.applied[:,:2],torch.zeros(n,1,device=self.device)),1))
        vertical=torch.zeros(n,4,3,device=self.device);vertical[:,:,2]=1
        direction=quat_apply_inverse(quat,vertical.reshape(-1,3)).reshape(n,4,3)
        for tau in c.cfg.preview_seconds:
            phase=torch.remainder(self.motion.phase+tau/self.reference_config.period_s,1.)
            target,_=adaptive_reference(phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
            world=quat_apply(quat,target.reshape(-1,3)).reshape(n,4,3)
            theta=self.motion.applied[:,2]*tau;co=torch.cos(theta)[:,None];si=torch.sin(theta)[:,None]
            x,y=world[:,:,0].clone(),world[:,:,1].clone();world[:,:,0]=co*x-si*y;world[:,:,1]=si*x+co*y
            world+=r.root_pos_w[:,None]+tau*flow[:,None]
            delta=torch.zeros_like(target);delta[:,:,:2],ground=self._patch_projection(world,tau);delta[:,:,2]=ground-(d.value+tau*d.velocity)[:,None]
            preferred=target+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            keep=self.patch.continuing(self.motion.phase,tau,self.reference_config.period_s,self.reference_config.stance_fraction)
            yawq=torch.zeros(n,4,device=self.device);yawq[:,0]=torch.cos(theta/2);yawq[:,3]=torch.sin(theta/2)
            futureq=quat_mul(yawq,r.root_quat_w)[:,None].expand(-1,4,-1).reshape(-1,4)
            goal_root=r.root_pos_w+tau*flow;goal_root[:,2]=self.cfg.base_height_target+d.value+tau*d.velocity
            measured=quat_apply_inverse(futureq,(self.patch.xyz-goal_root[:,None]).reshape(-1,3)).reshape(n,4,3)
            carry=self.handover.forecast(self.motion.phase,tau,self.reference_config.period_s,self._handover_duty())
            preferred=preferred+quat_apply_inverse(futureq,carry.reshape(-1,3)).reshape(n,4,3)
            # Preserve preferred worldXY; only forecast the measured-Z endpoint.
            endpoint=preferred+((measured-preferred)*direction).sum(2)[:,:,None]*direction
            targets.append(preferred);endpoints.append(endpoint);continuing.append(keep)
        target=torch.stack(targets,1);endpoint=torch.stack(endpoints,1);keep=torch.stack(continuing,1);t=target.shape[1]
        predicted=predict_applied_heights(c,candidates,self.step_dt)
        shift=predicted[:,:,:,None,None]*direction[:,None,None]
        preferred=target[:,None]-shift
        q,e=self.reference_model.solve(preferred.reshape(n*k*t,4,3),iterations=18)
        margin=torch.minimum(q-self.reference_model.lower,self.reference_model.upper-q).amin(2)
        e=e.reshape(n,k,t,4);margin=margin.reshape(n,k,t,4)
        # No measured foothold: preserve the old forecast exactly.
        if keep.any():
            projected=endpoint[:,None]-shift
            eq,ee=self.reference_model.solve(projected.reshape(n*k*t,4,3),iterations=18)
            em=torch.minimum(eq-self.reference_model.lower,self.reference_model.upper-eq).amin(2)
            e,margin,use=reachable_stance_forecast(e,margin,ee.reshape(n,k,t,4),em.reshape(n,k,t,4),keep[:,None],c.cfg)
            self.stance_endpoint_preview_plans=getattr(self,'stance_endpoint_preview_plans',0)+int(use.sum())
        goal,good=select_height(e,margin,candidates,c.goal,c.cfg)
        c.goal.copy_(goal);self.height_preview_no_common_plan+=int((~good).sum())
    def _reference(self):
        if not hasattr(self,'handover'):return super()._reference()
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        r=self._robot.data;n=self.num_envs
        base,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
        scan=self.height_scanner.data.ray_hits_w[:,:,2];extra=(scan.amax(1)-scan.amin(1)-.002).clamp(0,.01)
        full=extra_swing_clearance(base,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend);lift=full[:,:,2]-base[:,:,2]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        fixed_stance=None;swing_shift=None
        def target(scale):
            value=full.clone();value[:,:,2]-=lift*(1-scale)
            world=quat_apply(quat,value.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
            delta=torch.zeros_like(value);delta[:,:,:2],ground=self._patch_projection(world);delta[:,:,2]=ground-self.contact_datum.value[:,None]-self.height_coordinator.value[:,None]
            projected=value+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3)
            chosen=projected if fixed_stance is None else torch.where(self.patch.active[:,:,None],fixed_stance,projected)
            return chosen if swing_shift is None else chosen+swing_shift
        raw=target(torch.ones_like(lift))
        raw_world=quat_apply(quat,raw.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None]
        shift_world=self.handover.prepare(self.common_step_counter,self.motion.phase,stance,self.patch.active,raw_world,r.body_pos_w[:,self._robot_foot_ids],self._handover_duty())
        swing_shift=quat_apply_inverse(quat,shift_world.reshape(-1,3)).reshape(n,4,3)
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
            chosen=projected if fixed_stance is None else torch.where(self.patch.active[:,:,None],fixed_stance,projected)
            return chosen if swing_shift is None else chosen+swing_shift
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
        self.desired_swing_clearance=chosen+shift_world[:,:,2]
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
