"""Independent task derived from official Spot observations, rewards and PPO configuration."""
import copy
import isaaclab.sim as sim
from isaaclab.utils import configclass
from isaaclab.managers import SceneEntityCfg,ObservationTermCfg as ObsTerm
from isaaclab.actuators import DelayedPDActuatorCfg
import isaaclab_tasks.manager_based.locomotion.velocity.mdp as official
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.flat_env_cfg import SpotObservationsCfg,SpotRewardsCfg,SpotCommandsCfg
from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.agents.rsl_rl_ppo_cfg import SpotFlatPPORunnerCfg
from ..env_cfg import CSDogEnvCfg
from ..robot_cfg import JOINTS,FEET,AUDIT
from ..spot_v2.contacts import add_sensors
from . import rewards

@configclass
class PolicyObs(SpotObservationsCfg.PolicyCfg):
 joint_pos=ObsTerm(func=official.joint_pos_rel,params={'asset_cfg':SceneEntityCfg('robot',joint_names=JOINTS,preserve_order=True)})
 joint_vel=ObsTerm(func=official.joint_vel_rel,params={'asset_cfg':SceneEntityCfg('robot',joint_names=JOINTS,preserve_order=True)})
@configclass
class Observations:
 policy=PolicyObs()
 critic=PolicyObs()

@configclass
class AlignedEnvCfg(CSDogEnvCfg):
 observations=Observations()
 rewards=SpotRewardsCfg()
 def __post_init__(self):
  super().__post_init__()
  self.sim.dt=.002;self.decimation=10;self.sim.render_interval=10;self.episode_length_s=20.
  self.scene.contact_forces.update_period=.002
  self.actions.joint_pos.scale=.2
  self.scene.robot.init_state.pos=(0.,0.,.36)
  # Same capability limits, explicit zero-delay PD; no invented CSDog transmission curve.
  self.scene.robot.actuators={'legs':DelayedPDActuatorCfg(joint_names_expr=['joint_.*'],effort_limit=10.,effort_limit_sim=10.,velocity_limit_sim=3.,stiffness=25.,damping=.8,min_delay=0,max_delay=0)}
  self.commands.base_velocity=copy.deepcopy(SpotCommandsCfg().base_velocity)
  self.commands.base_velocity.ranges.lin_vel_x=(-.35,.35)
  self.commands.base_velocity.ranges.lin_vel_y=(-.22,.22)
  self.commands.base_velocity.ranges.ang_vel_z=(-.5,.5)
  self.commands.base_velocity.debug_vis=False
  r=self.rewards
  r.base_linear_velocity.params['std']=.25
  r.base_angular_velocity.params['std']=.5
  r.air_time.func=rewards.air_time_reward;r.air_time.params={'mode_time':.25,'velocity_threshold':.1}
  r.air_time_variance.func=rewards.air_time_variance_penalty;r.air_time_variance.params={}
  r.foot_clearance.func=rewards.foot_clearance_reward
  r.foot_clearance.params={'target_height':.03,'std':.0045,'tanh_mult':2.}
  r.foot_slip.func=rewards.foot_slip_penalty;r.foot_slip.params={'threshold':1.}
  r.gait.func=rewards.DistalGaitReward;r.gait.weight=2.
  r.gait.params.update(std=.1,max_err=.2,velocity_threshold=.1,
    synced_feet_pair_names=(('link_lf_knee','link_rr_knee'),('link_rf_knee','link_lr_knee')))
  r.joint_pos.params['velocity_threshold']=.1
  # Correct CSDog equivalent of Spot h[xy]. Official functions currently take all joint values;
  # retain that exact behavior and record it, rather than assuming asset_cfg slices are used.
  for name in ['joint_acc','joint_vel']:
   getattr(r,name).params['asset_cfg']=SceneEntityCfg('robot',joint_names=[f'joint_{leg}_{j}' for leg in ['lf','rf','lr','rr'] for j in [1,2]],preserve_order=True)
  add_sensors(self)

@configclass
class AlignedPPOCfg(SpotFlatPPORunnerCfg):
 max_iterations=120
 save_interval=30
 experiment_name='csdog_ppo_spot_aligned_v3'
 seed=42
 clip_actions=None
 obs_groups={'policy':['policy'],'critic':['critic']}

def configure(cfg,settings):
 if settings.get('implicit_actuator',False):
  from isaaclab.actuators import ImplicitActuatorCfg
  cfg.scene.robot.actuators={'legs':ImplicitActuatorCfg(joint_names_expr=['joint_.*'],effort_limit_sim=10.,velocity_limit_sim=3.,stiffness=25.,damping=.8)}
 for name,weight in settings.get('reward_weights',{}).items():
  getattr(cfg.rewards,name).weight=float(weight)
 if settings.get('no_reset_noise',False):
  cfg.events.reset_joints.params['position_range']=(0.,0.)
  cfg.events.reset_base.params['pose_range']={}
 return cfg
