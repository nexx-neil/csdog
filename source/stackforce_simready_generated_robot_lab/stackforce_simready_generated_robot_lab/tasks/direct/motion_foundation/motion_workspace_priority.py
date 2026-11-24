"""Independent v36 earliest-constraint priority; all prior controller files stay frozen."""
import torch
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from csdog_motion.workspace_height import HeightCoordinator
from csdog_motion.workspace_height_priority import select_height,TAG,contract
from csdog_motion.workspace_height_preview import TrajectoryHeightConfig,predict_applied_heights
from csdog_motion.adaptive_speed import adaptive_reference
from .motion_workspace_height import MotionWorkspaceHeightEnvCfg,MotionWorkspaceHeightEnv

@configclass
class MotionWorkspacePriorityEnvCfg(MotionWorkspaceHeightEnvCfg):
    def __post_init__(self):
        super().__post_init__();self.checkpoint_compatibility_tag=TAG;self.motion_contract=contract(self.motion_contract)

class MotionWorkspacePriorityEnv(MotionWorkspaceHeightEnv):
    def __init__(self,cfg,**kwargs):
        super().__init__(cfg,**kwargs);self.height_coordinator=HeightCoordinator(self.num_envs,self.device,TrajectoryHeightConfig())
    def _plan_height(self):
        c=self.height_coordinator;r=self._robot.data;n=self.num_envs
        candidates=torch.linspace(-c.cfg.maximum_offset_m,c.cfg.maximum_offset_m,c.cfg.candidates,device=self.device);candidates[len(candidates)//2]=0.;k=len(candidates);targets=[]
        quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        flow=quat_apply(r.root_quat_w,torch.cat((self.motion.applied[:,:2],torch.zeros(n,1,device=self.device)),1))
        for tau in c.cfg.preview_seconds:
            phase=torch.remainder(self.motion.phase+tau/self.reference_config.period_s,1.)
            target,_=adaptive_reference(phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,self.motion.blend)
            world=quat_apply(quat,target.reshape(-1,3)).reshape(n,4,3)
            theta=self.motion.applied[:,2]*tau;co=torch.cos(theta)[:,None];si=torch.sin(theta)[:,None];x,y=world[:,:,0].clone(),world[:,:,1].clone();world[:,:,0]=co*x-si*y;world[:,:,1]=si*x+co*y
            world+=r.root_pos_w[:,None]+tau*flow[:,None];root=r.root_pos_w+tau*flow
            delta=torch.zeros_like(target);delta[:,:,2]=self._rays(world)-self._rays(root)[:,0:1]
            targets.append(target+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3))
        target=torch.stack(targets,1);t=target.shape[1]
        v=torch.zeros(n,4,3,device=self.device);v[:,:,2]=1;direction=quat_apply_inverse(quat,v.reshape(-1,3)).reshape(n,4,3)
        predicted=predict_applied_heights(c,candidates,self.step_dt)
        projected=target[:,None]-predicted[:,:,:,None,None]*direction[:,None,None]
        q,e=self.reference_model.solve(projected.reshape(n*k*t,4,3),iterations=18);margin=torch.minimum(q-self.reference_model.lower,self.reference_model.upper-q).amin(2)
        # Current references are protected by the existing executed IK guard;
        # future reserve is predictive, never an extension of physical joint bounds.
        goal,good=select_height(e.reshape(n,k,t,4),margin.reshape(n,k,t,4),candidates,c.goal,c.cfg)
        c.goal.copy_(goal);self.height_preview_no_common_plan+=int((~good).sum())
