"""Native RSL-RL PPO instrumentation, atomic learner snapshots and safe-boundary stops."""
import copy,json,os,random,time,uuid
from pathlib import Path
import numpy as np
import torch
from rsl_rl.runners import OnPolicyRunner
from ..spot_v4.runner import Wrapper as ContactWrapper,GracefulStop
from ..spot_v4.contracts import finite_tree,IDENTITY
from .supervisor import atomic_json

class Wrapper(ContactWrapper):
    def step(self,actions):
        result=super().step(actions);r=self.unwrapped.scene['robot'];limits=r.data.soft_joint_pos_limits
        self.samples[-1]['target_limit_fraction']=float(((r.data.joint_pos_target<limits[:,:,0])|(r.data.joint_pos_target>limits[:,:,1])).float().mean())
        self.samples[-1]['tilt']=float(r.data.projected_gravity_b[:,:2].norm(dim=-1).mean())
        return result

class Runner(OnPolicyRunner):
    def __init__(self,*args,supervisor,**kwargs):
        self.supervisor=supervisor;self.output=supervisor.out;self.stop_requested=None;self.last_ppo={};self.minibatches=[];self.severe_count=0
        super().__init__(*args,**kwargs)
        self.logger_type='tensorboard'
        alg=self.alg;update=alg.update;generator=alg.storage.mini_batch_generator;logprob=alg.policy.get_actions_log_prob
        self.pending=None
        def batches(*a,**kw):
            for batch in generator(*a,**kw):
                self.pending=batch;yield batch
            self.pending=None
        alg.storage.mini_batch_generator=batches
        def measured(actions):
            value=logprob(actions)
            if self.pending is not None:
                mu0,s0=self.pending[6:8]
                with torch.no_grad():
                    mu=alg.policy.action_mean;s=alg.policy.action_std
                    kl=(torch.log(s/s0)+(s0.square()+(mu0-mu).square())/(2*s.square())-.5).sum(-1)
                    self.minibatches.append(float(kl.mean()))
            return value
        alg.policy.get_actions_log_prob=measured
        def measured_update():
            self.before=[p.detach().clone() for p in alg.policy.actor.parameters()]
            result=update()
            if not finite_tree(alg.policy.state_dict()) or not finite_tree(alg.optimizer.state_dict()):raise RuntimeError('NONFINITE_PPO')
            return result
        alg.update=measured_update
    @property
    def total_updates(self):return self.supervisor.state['total_updates']
    def log(self,locs,*a,**kw):
        s=self.supervisor.state;s['total_updates']+=1;s['stage_updates'][s['stage']]+=1;s['environment_steps']+=self.num_steps_per_env*self.env.num_envs
        s['training_seconds']+=locs['collection_time']+locs['learn_time']
        samples=self.env.samples
        row={k:sum(x[k] for x in samples)/len(samples) for k in samples[0]}
        self.last_ppo=dict(kl=sum(self.minibatches)/len(self.minibatches) if self.minibatches else 0.,kl_peak=max(self.minibatches,default=0.),actor_parameter_delta_l2=float(torch.stack([(p-b).square().sum() for p,b in zip(self.alg.policy.actor.parameters(),self.before)]).sum().sqrt()),learning_rate=self.alg.learning_rate,exploration_std=float(self.alg.policy.std.mean()),**{k:float(v) for k,v in locs['loss_dict'].items()})
        self.minibatches=[];row.update(self.last_ppo,total_updates=self.total_updates,stage=s['stage'],environment_steps=s['environment_steps'],training_seconds=s['training_seconds'])
        if not all(np.isfinite(v) for v in row.values()):raise RuntimeError('NONFINITE_METRICS')
        with (self.output/'metrics.jsonl').open('a') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
        if self.writer:
            for k,v in row.items():self.writer.add_scalar(k,v,self.total_updates)
        severe=row['falls']*self.num_steps_per_env>self.env.num_envs*.5 or row['target_limit_fraction']>.5 or row['tilt']>.8 or self.last_ppo['kl']>.3 or float(self.alg.policy.std.min())<.02 or float(self.alg.policy.std.max())>1.
        self.severe_count=self.severe_count+1 if severe else 0
        if self.severe_count>=5:self.stop_requested='PERSISTENT_SEVERE_PHYSICS_OR_PPO'
        self.env.samples.clear()
        if self.total_updates%self.supervisor.options['monitor']['save_interval']==0:
            self.save(str(self.output/f'checkpoint_{self.total_updates:08d}.pt'));self.supervisor.publish()
        if self.stop_requested:raise GracefulStop(self.stop_requested)
    def save(self,path,infos=None):
        path=Path(path)
        if path.name.startswith('model_'):return
        if not finite_tree(self.alg.policy.state_dict()) or not finite_tree(self.alg.optimizer.state_dict()):raise RuntimeError('NONFINITE_CHECKPOINT')
        rng=dict(torch_cpu=torch.get_rng_state(),torch_cuda=torch.cuda.get_rng_state_all(),numpy=np.random.get_state(),python=random.getstate())
        metadata=dict(curriculum_v6=dict(schema=6,identity=IDENTITY,state=copy.deepcopy(self.supervisor.state),options=copy.deepcopy(self.supervisor.options),rng=rng,learning_rate=self.alg.learning_rate,simulation_state_restored=False))
        old=self.current_learning_iteration;self.current_learning_iteration=self.total_updates
        tmp=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
        try:super().save(str(tmp),infos=metadata);os.replace(tmp,path)
        finally:
            self.current_learning_iteration=old
            if tmp.exists():tmp.unlink()
    def restore(self,path,restore_supervisor=True):
        data=torch.load(path,map_location=self.device,weights_only=False)
        meta=(data.get('infos') or {}).get('curriculum_v6')
        if not meta or meta['schema']!=6:raise ValueError('Only full V6 checkpoints are accepted; V4/V5 initialization is prohibited')
        if meta.get('identity')!=IDENTITY:raise ValueError('V6 asset/control/observation identity mismatch')
        if not finite_tree(data):raise ValueError('Nonfinite checkpoint')
        self.load(str(path),load_optimizer=True,map_location=self.device)
        if restore_supervisor:
            self.supervisor.state=copy.deepcopy(meta['state']);self.supervisor.options=copy.deepcopy(meta['options'])
            self.supervisor.state['training_status']='RUNNING'
        self.alg.learning_rate=meta['learning_rate']
        for group in self.alg.optimizer.param_groups:group['lr']=self.alg.learning_rate
        with torch.inference_mode():self.env.reset()
        rng=meta['rng'];torch.set_rng_state(rng['torch_cpu'].cpu());torch.cuda.set_rng_state_all([v.cpu() for v in rng['torch_cuda']]);np.random.set_state(rng['numpy']);random.setstate(rng['python'])
        self.alg.storage.clear();self.current_learning_iteration=self.total_updates
        self.env.samples.clear();self.env.previous=None
        return meta
    def apply(self):
        from .commands import DISTRIBUTIONS
        s=self.supervisor.state;b=self.env.unwrapped
        term=b.command_manager.get_term('base_velocity')
        term.cfg.v6={'distribution':copy.deepcopy(s['distribution'] or DISTRIBUTIONS[s['stage']]),'speed_range':s['speed_range'][:]}
        for name,weight in s['weights'].items():
            cfg=b.reward_manager.get_term_cfg(name);cfg.weight=weight;b.reward_manager.set_term_cfg(name,cfg)
        self.alg.learning_rate=s['ppo']['learning_rate'];self.alg.entropy_coef=s['ppo']['entropy_coef']
        for group in self.alg.optimizer.param_groups:group['lr']=self.alg.learning_rate
        term.time_left[:]=0.
