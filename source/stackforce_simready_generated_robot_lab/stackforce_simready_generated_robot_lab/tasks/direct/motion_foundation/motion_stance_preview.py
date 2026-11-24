"""Independent v60 forecast; frozen v59 execution and all hard gates retained."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse,quat_mul
from csdog_motion.stance_preview import TAG,contract,reachable_stance_forecast
from csdog_motion.workspace_height_preview import predict_applied_heights
from csdog_motion.workspace_height_priority import select_height
from csdog_motion.adaptive_speed import adaptive_reference
from .motion_contact_tick_preview import MotionContactTickEnvCfg
from .motion_stance_workspace import MotionStanceWorkspaceEnv

@configclass
class MotionStancePreviewEnvCfg(MotionContactTickEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)

class MotionStancePreviewEnv(MotionStanceWorkspaceEnv):
    def _plan_height(self):
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
