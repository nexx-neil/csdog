# Copyright (c) 2022-2026, The Isaac Lab Project Developers.
# Independent configuration adapted from official velocity_env_cfg / ANYmal-C Flat; BSD-3-Clause.
import math
import isaaclab.sim as sim_utils
from isaaclab.assets import AssetBaseCfg
from isaaclab.envs import ManagerBasedRLEnvCfg
from isaaclab.scene import InteractiveSceneCfg
from isaaclab.sensors import ContactSensorCfg
from isaaclab.terrains import TerrainImporterCfg
from isaaclab.managers import ObservationGroupCfg as ObsGroup,ObservationTermCfg as ObsTerm,RewardTermCfg as RewTerm,TerminationTermCfg as DoneTerm,EventTermCfg as EventTerm,SceneEntityCfg
from isaaclab.utils import configclass
import isaaclab_tasks.manager_based.locomotion.velocity.mdp as official
import isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp as spot
from .robot_cfg import ROBOT,JOINTS,FEET
from . import mdp
@configclass
class SceneCfg(InteractiveSceneCfg):
 robot=ROBOT
 terrain=TerrainImporterCfg(prim_path='/World/ground',terrain_type='plane',collision_group=-1,
  physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=0.8,dynamic_friction=0.7,restitution=0.,friction_combine_mode='multiply'),
  visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.38,0.40,0.43)))
 contact_forces=ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/.*',history_length=3,track_air_time=True)
 light=AssetBaseCfg(prim_path='/World/light',spawn=sim_utils.DomeLightCfg(intensity=1800.,color=(0.85,0.9,1.)))
@configclass
class CommandsCfg:
 base_velocity=mdp.MixedVelocityCommandCfg(asset_name='robot',resampling_time_range=(3.,5.),rel_standing_envs=0.2,
  heading_command=False,debug_vis=False,ranges=mdp.MixedVelocityCommandCfg.Ranges(lin_vel_x=(-0.35,0.35),lin_vel_y=(-0.22,0.22),ang_vel_z=(-0.5,0.5)))
@configclass
class ActionsCfg:
 joint_pos=official.JointPositionActionCfg(asset_name='robot',joint_names=JOINTS,preserve_order=True,scale=0.25,use_default_offset=True)
@configclass
class PolicyObs(ObsGroup):
 base_ang_vel=ObsTerm(func=official.base_ang_vel,scale=0.25)
 projected_gravity=ObsTerm(func=official.projected_gravity)
 velocity_commands=ObsTerm(func=official.generated_commands,params={'command_name':'base_velocity'})
 joint_pos=ObsTerm(func=official.joint_pos_rel,params={'asset_cfg':SceneEntityCfg('robot',joint_names=JOINTS,preserve_order=True)})
 joint_vel=ObsTerm(func=official.joint_vel_rel,scale=0.05,params={'asset_cfg':SceneEntityCfg('robot',joint_names=JOINTS,preserve_order=True)})
 actions=ObsTerm(func=official.last_action)
 def __post_init__(self):self.enable_corruption=False;self.concatenate_terms=True
@configclass
class CriticObs(PolicyObs):
 base_lin_vel=ObsTerm(func=official.base_lin_vel)
@configclass
class ObservationsCfg:
 policy=PolicyObs()
 critic=CriticObs()
@configclass
class EventsCfg:
 reset_base=EventTerm(func=official.reset_root_state_uniform,mode='reset',params={'pose_range':{'x':(-0.1,0.1),'y':(-0.1,0.1),'yaw':(-math.pi,math.pi)},'velocity_range':{}})
 reset_joints=EventTerm(func=official.reset_joints_by_offset,mode='reset',params={'position_range':(-0.025,0.025),'velocity_range':(0.,0.)})
@configclass
class RewardsCfg:
 track_lin_vel_xy_exp=RewTerm(func=official.track_lin_vel_xy_exp,weight=3.,params={'command_name':'base_velocity','std':0.25})
 track_ang_vel_z_exp=RewTerm(func=official.track_ang_vel_z_exp,weight=1.5,params={'command_name':'base_velocity','std':0.35})
 lin_vel_z_l2=RewTerm(func=official.lin_vel_z_l2,weight=-1.)
 ang_vel_xy_l2=RewTerm(func=official.ang_vel_xy_l2,weight=-0.08)
 flat_orientation_l2=RewTerm(func=official.flat_orientation_l2,weight=-2.5)
 dof_torques_l2=RewTerm(func=official.joint_torques_l2,weight=-0.0002)
 dof_acc_l2=RewTerm(func=official.joint_acc_l2,weight=-1e-7)
 action_rate_l2=RewTerm(func=official.action_rate_l2,weight=-0.005)
 undesired_contacts=RewTerm(func=official.undesired_contacts,weight=-1.,params={'sensor_cfg':SceneEntityCfg('contact_forces',body_names=['base','link_.*_hip_.*']),'threshold':2.})
 dof_pos_limits=RewTerm(func=official.joint_pos_limits,weight=-1.)
 stand_deviation=RewTerm(func=mdp.stand_joint_deviation,weight=-0.15)
 gait=RewTerm(func=spot.GaitReward,weight=0.,params={'std':0.05,'max_err':0.2,'velocity_threshold':0.05,
  'synced_feet_pair_names':(('link_lf_knee','link_rr_knee'),('link_rf_knee','link_lr_knee')),
  'asset_cfg':SceneEntityCfg('robot'),'sensor_cfg':SceneEntityCfg('contact_forces')})
 foot_air_time=RewTerm(func=official.feet_air_time,weight=0.,params={'sensor_cfg':SceneEntityCfg('contact_forces',body_names=FEET),'command_name':'base_velocity','threshold':0.15})
 foot_clearance=RewTerm(func=mdp.foot_clearance,weight=0.,params={'target_height':0.035})
 foot_slip=RewTerm(func=mdp.foot_slip,weight=0.)
@configclass
class TerminationsCfg:
 time_out=DoneTerm(func=official.time_out,time_out=True)
 base_contact=DoneTerm(func=official.illegal_contact,params={'sensor_cfg':SceneEntityCfg('contact_forces',body_names='base'),'threshold':8.})
 bad_orientation=DoneTerm(func=mdp.bad_orientation)
@configclass
class CSDogEnvCfg(ManagerBasedRLEnvCfg):
 scene=SceneCfg(num_envs=128,env_spacing=2.5)
 observations=ObservationsCfg();actions=ActionsCfg();commands=CommandsCfg();rewards=RewardsCfg();terminations=TerminationsCfg();events=EventsCfg()
 def __post_init__(self):
  self.decimation=4;self.sim.dt=0.005;self.sim.render_interval=4;self.episode_length_s=8.
  self.scene.contact_forces.update_period=self.sim.dt
  self.sim.physics_material=self.scene.terrain.physics_material
  self.viewer.eye=(1.25,1.25,0.9);self.viewer.lookat=(0.,0.,0.22);self.viewer.origin_type='asset_root';self.viewer.asset_name='robot'
  self.sim.physx.gpu_max_rigid_patch_count=2**18

def configure(cfg,settings):
 cfg.actions.joint_pos.scale=settings.get('action_scale',0.25)
 cfg.rewards.track_lin_vel_xy_exp.weight=settings.get('linear_tracking_weight',3.)
 cfg.rewards.track_ang_vel_z_exp.weight=settings.get('angular_tracking_weight',1.5)
 for flag,term,weight in [('enable_gait_reward','gait',0.3),('enable_foot_air_time_reward','foot_air_time',0.2),('enable_foot_clearance_reward','foot_clearance',0.15),('enable_foot_slip_penalty','foot_slip',-0.15)]:
  getattr(cfg.rewards,term).weight=weight if settings.get(flag,False) else 0.
 if settings.get('no_reset_noise',False):
  cfg.events.reset_joints.params['position_range']=(0.,0.)
  cfg.events.reset_base.params['pose_range']={}
 return cfg
