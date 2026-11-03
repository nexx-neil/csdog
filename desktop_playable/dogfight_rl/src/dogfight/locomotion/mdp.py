"""New-model command coverage and mesh-tip kinematics; official MDP terms remain imported."""
import torch
from isaaclab.envs.mdp.commands import UniformVelocityCommand, UniformVelocityCommandCfg
from isaaclab.utils import configclass
from isaaclab.utils.math import quat_apply
from .robot_cfg import AUDIT,FEET
class MixedVelocityCommand(UniformVelocityCommand):
 def _resample_command(self, env_ids):
  super()._resample_command(env_ids)
  ids=torch.as_tensor(env_ids,device=self.device);mode=torch.randint(0,5,(len(ids),),device=self.device)
  # 0: stop (20%), 1: pure vx, 2: pure vy, 3: pure yaw, 4: combined.
  self.is_standing_env[ids]=mode==0
  for component in range(3):
   self.vel_command_b[ids[(mode!=4)&(mode!=component+1)],component]=0.
@configclass
class MixedVelocityCommandCfg(UniformVelocityCommandCfg):
 class_type:type=MixedVelocityCommand

def feet_kinematics(env):
 robot=env.scene['robot']
 if not hasattr(env,'_csdog_feet_ids'):
  env._csdog_feet_ids=robot.find_bodies(FEET,preserve_order=True)[0]
  env._csdog_foot_points=torch.tensor([AUDIT['feet_local'][name] for name in FEET],device=env.device)
 ids=env._csdog_feet_ids
 offset=quat_apply(robot.data.body_quat_w[:,ids],env._csdog_foot_points.expand(env.num_envs,-1,-1))
 position=robot.data.body_pos_w[:,ids]+offset
 # body_lin_vel_w is COM velocity in Isaac Lab; use the COM-to-foot lever arm.
 velocity=robot.data.body_com_lin_vel_w[:,ids]+torch.cross(robot.data.body_com_ang_vel_w[:,ids],position-robot.data.body_com_pos_w[:,ids],dim=-1)
 return position,velocity

def foot_clearance(env,target_height=0.035):
 p,v=feet_kinematics(env)
 force=env.scene['contact_forces'].data.net_forces_w[:,env.scene['contact_forces'].find_bodies(FEET,preserve_order=True)[0]]
 swing=force.norm(dim=-1)<1.
 moving=env.command_manager.get_command('base_velocity').norm(dim=-1)>0.05
 return (torch.exp(-((p[:,:,2]-target_height)/0.025)**2)*swing).mean(-1)*moving

def stand_joint_deviation(env):
 robot=env.scene['robot'];stop=env.command_manager.get_command('base_velocity').norm(dim=-1)<0.02
 return (robot.data.joint_pos-robot.data.default_joint_pos).square().sum(-1)*stop

def bad_orientation(env):
 return env.scene['robot'].data.projected_gravity_b[:,2]>-0.65

def foot_slip(env):
 _,velocity=feet_kinematics(env)
 sensor=env.scene['contact_forces'];ids=sensor.find_bodies(FEET,preserve_order=True)[0]
 contact=sensor.data.net_forces_w[:,ids].norm(dim=-1)>1.
 return (velocity[:,:,:2].norm(dim=-1)*contact).sum(-1)
