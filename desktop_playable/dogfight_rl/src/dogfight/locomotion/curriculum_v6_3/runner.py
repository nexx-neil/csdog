"""Exact learner restoration with explicitly versioned supervisor migration."""
import copy
from ..curriculum_v6.runner import Runner as BaseRunner,GracefulStop
from ..curriculum_v6_1.runner import Wrapper as BaseWrapper
from .stride import observe
from .supervisor import Supervisor,atomic_json

class Wrapper(BaseWrapper):
    def __init__(self,*a,**kw):
        super().__init__(*a,**kw)
        from early_swing_signal import install_signal
        self.early=install_signal(self.unwrapped);self.stride=observe(self.unwrapped)
    def step(self,a):
        self.stride.begin_control();self.early.begin_control();result=super().step(a)
        self.samples[-1]['complete_stride_count']=float(self.stride.state.stride_count.sum())
        return result

class Runner(BaseRunner):
    def restore(self,path,restore_supervisor=True):
        import torch,random,numpy as np
        desired=copy.deepcopy(self.supervisor.options)
        saved=torch.load(path,map_location='cpu',weights_only=False)['infos']['curriculum_v6']
        rng=saved['rng'];torch.set_rng_state(rng['torch_cpu']);torch.cuda.set_rng_state_all(rng['torch_cuda']);np.random.set_state(rng['numpy']);random.setstate(rng['python'])
        meta=super().restore(path,restore_supervisor)
        if restore_supervisor:
            if meta['options'].get('schema')!=6.3:
                state=self.supervisor.state
                state.update(candidate=None,passes=0,repairs=0,full_windows=0,last_improvement=0,training_status='RUNNING',best_checkpoint=None,best_summary=None,best_score=-1e6,rankings=[],ranking_protocol=None,ranking_reference=None)
                state['weights']=copy.deepcopy(desired['weights']);state['ppo']=copy.deepcopy(desired['ppo']);state['distribution']=None
                self.supervisor.__init__(self.output,desired,state)
                self.supervisor.event('V63_FULL_LEARNER_MIGRATION',checkpoint=str(path),optimizer='exact restored',physics_reset=True)
            else:self.supervisor.__init__(self.output,self.supervisor.options,self.supervisor.state)
        self.env.stride.state.reset(torch.ones(self.env.num_envs,device=self.device,dtype=torch.bool))
        return meta
    def log(self,locs,*args,**kwargs):
        super().log(locs,*args,**kwargs)
        if self.total_updates%25==0:self.supervisor.publish()
    def apply(self):
        super().apply()
        b=self.env.unwrapped
        atomic_json(self.output/'ACTIVE_TRAINING_CONFIG.json',dict(update=self.total_updates,stage=self.supervisor.state['stage'],weights={k:b.reward_manager.get_term_cfg(k).weight for k in b.reward_manager.active_terms},commands=b.command_manager.get_term('base_velocity').cfg.v6,ppo=self.supervisor.state['ppo']))
