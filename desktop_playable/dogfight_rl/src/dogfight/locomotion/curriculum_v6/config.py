"""Independent rewards on the validated CSDog asset/control/sensor interface."""
import torch
from isaaclab.utils import configclass
from isaaclab.managers import RewardTermCfg as Term, SceneEntityCfg
from isaaclab.envs.mdp.commands import UniformVelocityCommand
import isaaclab_tasks.manager_based.locomotion.velocity.mdp as mdp
from ..env_cfg import CSDogEnvCfg
from ..spot_aligned_v3.config import Observations
from ..spot_v2.contacts import add_sensors
from isaaclab.actuators import DelayedPDActuatorCfg
from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg,RslRlPpoActorCriticCfg,RslRlPpoAlgorithmCfg
from . import rewards

from .commands import DISTRIBUTIONS

class CurriculumCommand(UniformVelocityCommand):
    def _resample_command(self,env_ids):
        n=len(env_ids); opts=self.cfg.v6; dist=opts['distribution']; names=list(dist)
        k=torch.multinomial(torch.tensor(list(dist.values()),device=self.device),n,replacement=True)
        v=torch.zeros(n,3,device=self.device)
        for i,name in enumerate(names):
            mask=k==i
            if 'forward' in name or 'backward' in name:
                v[mask,0]=torch.empty(int(mask.sum()),device=self.device).uniform_(*opts['speed_range'])*(1 if 'forward' in name else -1)
            if name.startswith('yaw_') or 'left' in name or 'right' in name:
                sign=1 if name=='yaw_positive' or 'left' in name else -1
                v[mask,2]=torch.empty(int(mask.sum()),device=self.device).uniform_(.2,.45)*sign
        self.vel_command_b[env_ids]=v
        self.is_standing_env[env_ids]=v.norm(dim=-1)<.04

@configclass
class Rewards:
    progress=Term(func=rewards.core,weight=4.,params={'index':0})
    tracking=Term(func=rewards.core,weight=2.,params={'index':1})
    unwanted=Term(func=rewards.core,weight=-1.,params={'index':2})
    stop=Term(func=rewards.core,weight=2.,params={'index':3})
    stability=Term(func=rewards.stability,weight=-1.)
    limits=Term(func=mdp.joint_pos_limits,weight=-5.)
    collision=Term(func=mdp.undesired_contacts,weight=-2.,params={'sensor_cfg':SceneEntityCfg('contact_forces',body_names=['base','link_.*_hip_.*']),'threshold':2.})
    termination=Term(func=mdp.is_terminated,weight=-10.)
    posture=Term(func=rewards.posture,weight=-.02)
    smoothness=Term(func=mdp.action_rate_l2,weight=-.003)
    acceleration=Term(func=mdp.joint_acc_l2,weight=-2e-8)
    torque=Term(func=mdp.joint_torques_l2,weight=-.0001)
    slip=Term(func=rewards.slip,weight=-.15)
    swing=Term(func=rewards.swing,weight=.15)

@configclass
class EnvCfg(CSDogEnvCfg):
    observations=Observations()
    rewards=Rewards()
    def __post_init__(self):
        super().__post_init__()
        self.sim.dt=.002;self.decimation=10;self.sim.render_interval=10;self.episode_length_s=20.
        self.scene.contact_forces.update_period=.002
        self.actions.joint_pos.scale=.2
        self.scene.robot.init_state.pos=(0.,0.,.36)
        self.scene.robot.actuators={'legs':DelayedPDActuatorCfg(joint_names_expr=['joint_.*'],effort_limit=10.,effort_limit_sim=10.,velocity_limit_sim=3.,stiffness=25.,damping=.8,min_delay=0,max_delay=0)}
        self.commands.base_velocity.class_type=CurriculumCommand
        self.commands.base_velocity.heading_command=False
        self.commands.base_velocity.ranges.lin_vel_y=(0.,0.)
        self.commands.base_velocity.resampling_time_range=(3.,5.)
        self.commands.base_velocity.v6={'distribution':DISTRIBUTIONS[0].copy(),'speed_range':[.12,.25]}
        add_sensors(self)

@configclass
class PPOCfg(RslRlOnPolicyRunnerCfg):
    seed=42
    num_steps_per_env=24
    max_iterations=None  # The runner is called in bounded monitoring chunks; no global cap.
    save_interval=100
    experiment_name='csdog_curriculum_ppo_v6'
    obs_groups={'policy':['policy'],'critic':['critic']}
    clip_actions=None
    policy=RslRlPpoActorCriticCfg(init_noise_std=.4,actor_obs_normalization=False,critic_obs_normalization=False,actor_hidden_dims=[512,256,128],critic_hidden_dims=[512,256,128],activation='elu')
    algorithm=RslRlPpoAlgorithmCfg(value_loss_coef=.5,use_clipped_value_loss=True,clip_param=.2,entropy_coef=.0025,num_learning_epochs=5,num_mini_batches=4,learning_rate=1e-4,schedule='fixed',gamma=.99,lam=.95,desired_kl=.01,max_grad_norm=1.)

def build(options,num_envs,seed,device):
    c=EnvCfg();c.scene.num_envs=num_envs;c.seed=seed;c.sim.device=device
    a=PPOCfg();a.seed=seed;a.device=device
    for key in ['learning_rate','schedule','entropy_coef']:setattr(a.algorithm,key,options['ppo'][key])
    a.policy.init_noise_std=options['ppo']['init_noise_std']
    for key,value in options['weights'].items():getattr(c.rewards,key).weight=value
    return c,a
