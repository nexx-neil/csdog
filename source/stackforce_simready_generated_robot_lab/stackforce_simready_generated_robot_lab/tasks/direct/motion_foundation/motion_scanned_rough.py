"""Independent low-speed rough task using actual static-mesh rays, not analytic terrain."""
import copy,torch
from isaaclab.utils import configclass
from isaaclab.sensors import RayCaster,RayCasterCfg,patterns
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from isaaclab.utils.warp import raycast_mesh
from csdog_motion.rough_curriculum import build_rough_cfg
from csdog_motion.rough_sensing import TAG,OBSERVATIONS,relative_scan
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.terrain_course import extra_swing_clearance
from csdog_motion.residual_learning import reward_terms
from .motion_yaw import MotionYawEnvCfg,MotionYawEnv

@configclass
class MotionScannedRoughEnvCfg(MotionYawEnvCfg):
    checkpoint_compatibility_tag=TAG
    observation_space=OBSERVATIONS
    residual_training_enabled=True
    terrain_seed=42
    terrain_row=0
    sensor_reference_enabled=True
    def __post_init__(self):
        super().__post_init__()
        self.terrain=copy.deepcopy(self.terrain)
        self.terrain.terrain_type='generator';self.terrain.terrain_generator=build_rough_cfg('easy',self.terrain_seed)
        self.terrain.max_init_terrain_level=0
        self.motion_commands=dict(self.motion_commands,limits=(.25,.2,.3))
        self.command_resampling_interval_s=(4.,6.)
        self.motion_contract=copy.deepcopy(self.motion_contract)
        self.motion_contract.update(schema_version=28,compatibility_tag=TAG,observations=OBSERVATIONS)
        self.motion_contract['rough_sensing']={'height_grid_rays':99,'resolution_m':.1,'size_m':[1.,.8],'observations':'append99 ground-relative heights/.1m, clipped+-2; missing hits rejected','observation_slice':[76,175],'surface_query':'noiseless vertical simulation rays to same physical static terrain mesh; current root,feet and reference targets','reference':'terrain-aware world-vertical footZ and bounded extra swing lift; no analytical height or world path controller','height_reward_and_support':'relative to ray under root','scope':'first low-speed generated terrain course; not general autonomy','sensor_reference_enabled':self.sensor_reference_enabled}
        self.motion_contract['observation_layout']['ground_relative_scan']=[76,175]
        self.motion_contract['training_command_ranges']={'vx':[-.25,.25],'vy':[-.2,.2],'yaw':[-.3,.3]}
        self.motion_contract['terrain_reward']='same residual terms; actual root/foot height ground-relative, desired clearance excludes ground offset'
        # Replace inherited flat-task descriptions; controller and bounds are unchanged.
        self.motion_contract['height']['reference']='base above actual terrain ray under root'
        self.motion_contract['terrain_support']='static generated easy terrain; noiseless mesh rays; low-speed first course only'
        self.motion_contract['training_replay']={'stand_probability':.15,'moving_axes':'uniform single axis','magnitude_fraction':[.5,1.],'resample_seconds':[4.,6.]}
        self.motion_contract['command_envelope']={'single_axis_limits':[.25,.2,.3],'viewer_commands':[.2,.18,.3],'tested_motion':'single-axis translation followed by simple turn; simultaneous mixed commands unvalidated','limits_are_commands_not_measured_capability':True}
        self.motion_contract['scope']='independent scanned-terrain task; explicit flat-policy input migration, no old optimizer transfer; preserve separate fast flat controller'

class MotionScannedRoughEnv(MotionYawEnv):
    def _setup_scene(self):
        super()._setup_scene()
        cfg=RayCasterCfg(prim_path='/World/envs/env_.*/Robot/base',update_period=.02,
            offset=RayCasterCfg.OffsetCfg(pos=(0.,0.,1.)),ray_alignment='yaw',
            pattern_cfg=patterns.GridPatternCfg(resolution=.1,size=(1.,.8)),mesh_prim_paths=[self.cfg.terrain.prim_path],max_distance=3.,debug_vis=False)
        self.height_scanner=RayCaster(cfg);self.scene.sensors['height_scanner']=self.height_scanner
        # Deterministic row for the first curriculum; one of8 columns per environment.
        self.terrain_columns=torch.arange(self.num_envs,device=self.device)%8
        self._terrain.env_origins[:]=self._terrain.terrain_origins[self.cfg.terrain_row,self.terrain_columns]
        self._surface_tick=-1
    def _rays(self,positions):
        if positions.ndim==2:positions=positions[:,None,:]
        starts=positions.clone();starts[:,:,2]=self._robot.data.root_pos_w[:,None,2]+1.
        directions=torch.zeros_like(starts);directions[:,:,2]=-1.
        hits=raycast_mesh(starts,directions,mesh=RayCaster.meshes[self.cfg.terrain.prim_path],max_dist=3.)[0]
        if not torch.isfinite(hits).all():raise RuntimeError('Terrain query missed physical mesh')
        return hits[:,:,2]
    def _surfaces(self):
        if self._surface_tick!=self.common_step_counter:
            r=self._robot.data;p=torch.cat((r.root_pos_w[:,None],r.body_pos_w[:,self._robot_foot_ids]),1)
            self._surface_cache=self._rays(p);self._surface_tick=self.common_step_counter
        return self._surface_cache
    def _reset_idx(self,env_ids):
        super()._reset_idx(env_ids);self._surface_tick=-1;self._reference_tick=-1
    def _support_height(self):return self._robot.data.root_pos_w[:,2]-self._surfaces()[:,0]
    def _foot_clearance(self):return self._robot.data.body_pos_w[:,self._robot_foot_ids,2]-.018-self._surfaces()[:,1:]
    def _get_observations(self):
        base=super()._get_observations()['policy'];scan=self.height_scanner.data.ray_hits_w[:,:,2]
        return {'policy':torch.cat((base,relative_scan(scan,self._surfaces()[:,0])),1)}
    def _reference(self):
        if self._reference_tick==self.common_step_counter:return self._reference_cache
        r=self._robot.data;target,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
        if self.cfg.sensor_reference_enabled:
            scan=self.height_scanner.data.ray_hits_w[:,:,2];spread=scan.amax(1)-scan.amin(1)
            extra=(spread-.002).clamp(0,.01)
            target=extra_swing_clearance(target,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend)
        self.desired_swing_clearance=target[:,:,2]-self.reference_nominal[None,:,2]
        if self.cfg.sensor_reference_enabled:
            quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
            world=quat_apply(quat,target.reshape(-1,3)).reshape(-1,4,3)+r.root_pos_w[:,None]
            ground=self._rays(world);delta=torch.zeros_like(target);delta[:,:,2]=ground-self._surfaces()[:,0:1]
            target+=quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(-1,4,3)
        q,error=self.reference_model.solve(target,iterations=18)
        self._reference_cache=q.flatten(1),error,stance;self._reference_tick=self.common_step_counter
        return self._reference_cache
    def _sample_commands(self,env_ids):
        if self.motion is None:return super()._sample_commands(env_ids)
        if not self.cfg.periodic_commands or self._external_commands:
            self.motion.set_request([0.,0.,0.],env_ids);self._command_remaining[env_ids]=1e6;return
        cmd=torch.zeros(len(env_ids),3,device=self.device);axes=torch.randint(0,3,(len(env_ids),),device=self.device)
        scales=cmd.new_tensor([.25,.2,.3]);mag=torch.empty(len(env_ids),device=self.device).uniform_(.5,1.);sign=torch.where(torch.rand(len(env_ids),device=self.device)<.5,-1.,1.)
        cmd[torch.arange(len(env_ids),device=self.device),axes]=scales[axes]*mag*sign
        cmd[torch.rand(len(env_ids),device=self.device)<.15]=0
        self.motion.set_request(cmd,env_ids);low,high=self.cfg.command_resampling_interval_s
        self._command_remaining[env_ids]=torch.empty(len(env_ids),device=self.device).uniform_(low,high)
    def _get_dones(self):
        # Same contact/tilt rules as parent; ground-relative height and tile boundary.
        r=self._robot.data;grace=self.episode_length_buf>self._termination_grace_steps
        force=self._contact_sensor.data.net_forces_w_history[:,:,self._termination_body_ids]
        contact=(torch.linalg.vector_norm(force,dim=-1).amax(1)>self.cfg.termination_contact_force_threshold).any(1)
        fallen=(r.projected_gravity_b[:,2]>self.cfg.fallen_projected_gravity_z)&grace
        self._fallen_fail_buf*=fallen.float();self._fallen_fail_buf+=fallen.float()
        low=self._support_height()<self.cfg.min_base_height
        edge=(r.root_pos_w[:,:2]-self._terrain.env_origins[:,:2]).abs().amax(1)>2.65
        term=((contact|low|edge)&grace)|(self._fallen_fail_buf>self._fallen_termination_steps)
        return term,self.episode_length_buf>=self.max_episode_length-1
    def _get_rewards(self):
        r=self._robot.data;quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
        body=quat_apply_inverse(quat,(r.body_pos_w[:,self._robot_foot_ids]-r.root_pos_w[:,None]).reshape(-1,3)).reshape(-1,4,3)
        ref,_=self.reference_model.fk(self.reference_q.reshape(-1,4,3));forces=torch.linalg.vector_norm(self._contact_sensor.data.net_forces_w[:,self._foot_ids],dim=-1);weight=self.cfg.reference_parameters['support_feedback']['mass_kg']*9.81
        terms=reward_terms({'twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1),'command':self._commands,'stance':self.reference_stance,'blend':self.motion.blend,'foot_body':body,'reference_foot':ref,'contacts':forces>1.,'clearance':self._foot_clearance(),'desired_clearance':self.desired_swing_clearance,'force_over_weight':forces/weight,'height':self._support_height(),'height_command':self.motion.applied[:,3],'gravity':r.projected_gravity_b,'angular_xy':r.root_ang_vel_b[:,:2],'vertical_velocity':r.root_lin_vel_w[:,2],'foot_world_velocity':r.body_lin_vel_w[:,self._robot_foot_ids],'torque':r.applied_torque[:,self._actuated_joint_ids],'joint_acceleration':r.joint_acc[:,self._actuated_joint_ids],'target':self._processed_actions,'previous_target':self.previous_joint_targets,'residual':self.last_residual_actions,'raw_action':self._raw_actions,'target_box_clip':self.target_box_limited,'terminated':self.reset_terminated})
        total=torch.zeros(self.num_envs,device=self.device);self.last_reward_terms={}
        for name,value in terms.items():
            scaled=value*self.cfg.reward_scales[name]*self.step_dt;total+=scaled;self._episode_sums[name]+=scaled;self.last_reward_terms[name]=scaled.detach()
        return total
