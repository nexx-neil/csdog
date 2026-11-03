"""Full V6 learner migration with explicit V6.1 supervisor/version boundaries."""
import copy,random
import torch
import numpy as np
from ..curriculum_v6.runner import Runner as V6Runner,Wrapper as V6Wrapper,GracefulStop
from .supervisor import Supervisor,atomic_json
class Wrapper(V6Wrapper):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        from .contacts import physical_events
        self.physical=physical_events(self.unwrapped)
    def step(self,actions):
        self.physical.begin_control()
        result=super().step(actions)
        self.samples[-1]['physics_slip']=float(self.physical.slip_sum.sum()/self.physical.support_n.sum().clamp_min(1))
        self.samples[-1]['physics_air_fraction']=float(self.physical.strict_ticks.float().mean()/10)
        return result
class Runner(V6Runner):
    def log(self,locs,*args,**kwargs):
        super().log(locs,*args,**kwargs)
        if self.total_updates%25==0:self.supervisor.publish()
    def restore(self,path,restore_supervisor=True):
        desired=copy.deepcopy(self.supervisor.options)
        # Reset poses must consume the same saved RNG on both candidate arms.
        envelope=torch.load(path,map_location='cpu',weights_only=False)['infos']['curriculum_v6']
        rng=envelope['rng'];torch.set_rng_state(rng['torch_cpu']);torch.cuda.set_rng_state_all(rng['torch_cuda']);np.random.set_state(rng['numpy']);random.setstate(rng['python'])
        meta=super().restore(path,restore_supervisor)
        if restore_supervisor:
            if meta['options'].get('schema')!=6.1:
                state=self.supervisor.state
                state.update(candidate=None,passes=0,repairs=0,full_windows=0,last_improvement=0,training_status='RUNNING')
                state['weights']=copy.deepcopy(desired['weights']);state['ppo']=copy.deepcopy(desired['ppo'])
                state['distribution']=None
                state['substage']=desired.get('initial_substage','1A')
                self.supervisor.__init__(self.output,desired,state)
                self.supervisor.event('V6_FULL_LEARNER_MIGRATION',checkpoint=str(path),optimizer='restored',actor_critic='restored',exploration='restored',rng='restored',curriculum_stage=state['stage'],physics_reset=True,supervisor_ranking='reset_versioned',reward_variant=desired.get('variant'))
            else:
                self.supervisor.__init__(self.output,self.supervisor.options,self.supervisor.state)
        return meta
    def apply(self):
        super().apply()
        s=self.supervisor.state;b=self.env.unwrapped
        if self.supervisor.options.get('variant')=='improved' and s['stage']==0:
            sub=s['substage'];base=self.supervisor.options['weights']
            weight=0. if sub=='1A' else s['weights'].get('gait_guide',.3)
            cfg=b.reward_manager.get_term_cfg('gait_guide');cfg.weight=weight;b.reward_manager.set_term_cfg('gait_guide',cfg)
            if sub=='1C':
                # Only after all four legs exhibit repeated physical swings.
                for name,factor in [('slip',1.5),('smoothness',1.25)]:
                    cfg=b.reward_manager.get_term_cfg(name);cfg.weight=s['weights'][name]*factor;b.reward_manager.set_term_cfg(name,cfg)
                if s['distribution'] is None:b.command_manager.get_term('base_velocity').cfg.v6['distribution']={'forward':.75,'stop':.25}

        atomic_json(self.output/'ACTIVE_TRAINING_CONFIG.json',dict(update=self.total_updates,stage=s['stage'],substage=s['substage'],variant=self.supervisor.options.get('variant'),weights={name:b.reward_manager.get_term_cfg(name).weight for name in b.reward_manager.active_terms},commands=b.command_manager.get_term('base_velocity').cfg.v6,ppo=s['ppo']))
