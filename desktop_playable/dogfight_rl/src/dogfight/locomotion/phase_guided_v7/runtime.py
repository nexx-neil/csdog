"""V7 phase timing, unchanged twelve-joint PD action interface, geometric contact."""
import torch,json
from pathlib import Path
from isaaclab.utils import configclass
from isaaclab.managers import ObservationTermCfg,RewardTermCfg,EventTermCfg
from ..curriculum_v6.config import EnvCfg as BaseEnv,PPOCfg,CurriculumCommand
from ..spot_aligned_v3.config import PolicyObs
from ..spot_v2.contacts import ContactState
from ..robot_cfg import FEET,ROOT
from .kernel import Clock,DEFAULTS,terms

def clock(env):
    if not hasattr(env,'_v7_clock'):env._v7_clock=Clock(env.num_envs,env.device)
    return env._v7_clock
class PhaseCommand(CurriculumCommand):
    def compute(self,dt):
        # Reward at s[t+1] uses phase seen by action a[t]. Advance after reward,
        # before command resampling and observation of s[t+1].
        active_command=torch.where((self._env.episode_length_buf>0)[:,None],self.vel_command_b,0.)
        clock(self._env).advance(dt,active_command,self._env.cfg.v7['frequency'])
        super().compute(dt)
def phase_obs(env):return clock(env).observation()
def reset_clock(env,env_ids):clock(env).reset(env_ids)
@configclass
class PhaseObs(PolicyObs):
    phase=ObservationTermCfg(func=phase_obs)
@configclass
class PhaseObservations:
    policy=PhaseObs();critic=PhaseObs()
class Contacts(ContactState):
    def __init__(self,env):
        super().__init__(env)
        if env.cfg.v7['collision']=='sole':
            m=json.loads((ROOT/'runs/locomotion/csdog_phase_guided_ppo_v7/collision_geometry.json').read_text())
            self.vertices=[torch.tensor(m['legs'][k]['sole_vertices'],device=env.device,dtype=torch.float) for k in ('lf','rf','lr','rr')]

def contacts(env):
    if not hasattr(env,'_v7_contacts'):env._v7_contacts=Contacts(env)
    return env._v7_contacts.update()
def reward(env,name):
    key=env.common_step_counter
    if getattr(env,'_v7_reward_key',None)==key:return env._v7_rewards[name]
    s=contacts(env);d=env.scene['robot'].data
    if not hasattr(env,'_v7_air'):env._v7_air=torch.zeros_like(s.clearance)
    env._v7_air[env.episode_length_buf<=1]=0.
    env._v7_air=torch.where(s.contact,0.,env._v7_air+env.step_dt)
    v=terms(clock(env).phase,env.command_manager.get_command('base_velocity'),d.root_lin_vel_b,d.root_ang_vel_b[:,2],s.contact,s.clearance,s.shin,s.velocity[:,:,:2].norm(dim=-1),env.cfg.v7,env._v7_air)
    env._v7_reward_key=key;env._v7_rewards=v
    return v[name]
def action_amplitude(env):return env.action_manager.action.square().mean(-1)
def stopped_joints(env):
    d=env.scene['robot'].data;stop=env.command_manager.get_command('base_velocity').norm(dim=-1)<=.04
    return stop*(d.joint_vel.square().mean(-1)+2*(d.joint_pos-d.default_joint_pos).square().mean(-1))
def build(options,num_envs=128,seed=42,device='cuda:0'):
    o=dict(DEFAULTS,**options);cfg=BaseEnv();cfg.v7=o
    cfg.scene.num_envs=num_envs;cfg.seed=seed;cfg.sim.device=device
    cfg.observations=PhaseObservations() if o.get('phase',True) else cfg.observations
    cfg.commands.base_velocity.class_type=PhaseCommand
    cfg.commands.base_velocity.v6={'distribution':{'forward':1-o['stop_fraction'],'stop':o['stop_fraction']},'speed_range':[.12,.25]}
    if o.get('stage',0):
        from ..curriculum_v6.commands import DISTRIBUTIONS
        dist=DISTRIBUTIONS[o['stage']].copy();old=dist['stop'];dist={k:(o['stop_fraction'] if k=='stop' else v*(1-o['stop_fraction'])/(1-old)) for k,v in dist.items()}
        cfg.commands.base_velocity.v6['distribution']=dist
    cfg.events.v7_phase_reset=EventTermCfg(func=reset_clock,mode='reset')
    if o['collision']=='sole':cfg.scene.robot.spawn.usd_path=str(ROOT/'assets/csdog_12dof/collision_sole_candidate/csdog.usda')
    # Remove old swing events; all arms use the same new base objectives.
    cfg.rewards.swing=None;cfg.rewards.slip=None
    weights=dict(progress=o['tracking_weight'],tracking=2.,unwanted=-2.,stop=2.,gait_stance_contact=o['stance_weight'],gait_swing_release=o['release_weight'],height_progress=o['height_weight'],slip=-o['slip_weight'],shin=-2.,wrong_support=-2.,stop_feet=-.5,unsupported=-3.,excess_height=-2.,overdue_air=-6.)
    for name,weight in weights.items():
        if not o.get('phase',True) and name in ('gait_stance_contact','gait_swing_release','height_progress','wrong_support','overdue_air'):weight=0.
        setattr(cfg.rewards,name,RewardTermCfg(func=reward,weight=weight,params={'name':name}))
    cfg.rewards.action_amplitude=RewardTermCfg(func=action_amplitude,weight=-.002)
    cfg.rewards.stopped_joints=RewardTermCfg(func=stopped_joints,weight=-.03)
    agent=PPOCfg();agent.seed=seed;agent.device=device;agent.experiment_name='csdog_phase_guided_ppo_v7'
    agent.policy.init_noise_std=.4;agent.save_interval=50
    agent.algorithm.entropy_coef=o.get('entropy_coef',.0025)
    return cfg,agent
