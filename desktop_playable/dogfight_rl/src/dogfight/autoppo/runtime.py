"""Native Isaac Lab/RSL-RL adapter; import only after AppLauncher."""
import copy
from isaaclab.managers import RewardTermCfg
from ..locomotion.curriculum_v6_1.config import build as base_build
from ..locomotion.curriculum_v6_1.runner import Wrapper as BaseWrapper
from ..locomotion.curriculum_v6.runner import Runner as BaseRunner
from .stride import observe
from . import rewards

EXTRA=('swing_credit','touchdown_credit','stride_credit','support_quality','physical_slip','stop_feedback')

def build(options,num_envs,seed,device):
    base=copy.deepcopy(options)
    for key in EXTRA:base['weights'].pop(key,None)
    # Legacy policy-rate swing and the historical V6.2 run-local signal are
    # disabled; keep the same task, action, observations and physical interface.
    base.update(variant='control')
    base['weights'].update(gait_guide=0.,swing=0.)
    cfg,agent=base_build(base,num_envs,seed,device)
    cfg.rewards.gait_guide.func=lambda env:rewards.gait(env,0)
    for i,name in enumerate(EXTRA[:4]):
        setattr(cfg.rewards,name,RewardTermCfg(func=rewards.gait,weight=options['weights'][name],params={'index':i}))
    cfg.rewards.physical_slip=RewardTermCfg(func=rewards.support_slip,weight=options['weights']['physical_slip'])
    cfg.rewards.stop_feedback=RewardTermCfg(func=rewards.stop_feedback,weight=options['weights']['stop_feedback'])
    for name in ['learning_rate','entropy_coef','clip_param','lam']:
        if name in options['ppo']:setattr(agent.algorithm,name,options['ppo'][name])
    return cfg,agent

class Wrapper(BaseWrapper):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw);self.stride=observe(self.unwrapped)
    def step(self,a):
        self.stride.begin_control();result=super().step(a)
        self.samples[-1]['complete_stride_count']=float(self.stride.state.stride_count.sum())
        return result

class Runner(BaseRunner):
    def apply(self):
        super().apply()
        for name in ['clip_param','lam']:
            if name in self.supervisor.state['ppo']:setattr(self.alg,name,self.supervisor.state['ppo'][name])
    def restore(self,path,restore_supervisor=True):
        result=super().restore(path,restore_supervisor)
        import torch
        self.env.stride.state.reset(torch.ones(self.env.num_envs,device=self.device,dtype=torch.bool))
        return result
