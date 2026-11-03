"""Reuse the unchanged V6 model, observations, PD, PPO and directional objectives."""
from ..curriculum_v6.config import build as v6_build
from isaaclab.managers import RewardTermCfg
from .rewards import gait_guide,completed_swing

def build(options,num_envs,seed,device):
    import copy
    legacy=copy.deepcopy(options);legacy['weights'].pop('gait_guide',None)
    cfg,agent=v6_build(legacy,num_envs,seed,device)
    cfg.rewards.gait_guide=RewardTermCfg(func=gait_guide,weight=options['weights'].get('gait_guide',0.))
    if options.get('variant')=='improved':cfg.rewards.swing.func=completed_swing
    agent.experiment_name='csdog_curriculum_ppo_v6_1'
    return cfg,agent
