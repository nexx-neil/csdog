"""Unmodified RSL PPO, with finite checks, exact counters, safe-boundary interruption and atomic saves."""
from pathlib import Path
import json,time,os,uuid,random
import numpy as np
import torch
from rsl_rl.runners import OnPolicyRunner
from ..spot_aligned_v3.runner import Wrapper as V3Wrapper
from ..spot_v2.contacts import contact_state
from .contracts import finite_tree
class GracefulStop(Exception):pass
class Wrapper(V3Wrapper):
 def step(self,actions):
  result=super().step(actions);s=contact_state(self.unwrapped)
  for j,leg in enumerate(['LF','RF','LR','RR']):
   self.samples[-1][leg+'_swing_ratio']=float(((~s.contact[:,j])&(s.clearance[:,j]>.015)).float().mean())
  return result
class Runner(OnPolicyRunner):
 def __init__(self,*args,output,requested,base_updates=0,save_interval=50,validation_budget=None,max_seconds=None,**kwargs):
  self.output=Path(output);self.requested=requested;self.base_updates=base_updates;self.session_updates=0;self.save_every=save_interval;self.validation_budget=validation_budget
  self.started=time.monotonic();self.max_seconds=max_seconds;self.stop_requested=None
  super().__init__(*args,**kwargs)
 @property
 def total_updates(self):return self.base_updates+self.session_updates
 def log(self,locs,*args,**kwargs):
  self.session_updates+=1
  if self.validation_budget is not None:
   budget=json.loads(self.validation_budget.read_text());budget['completed_updates']+=1
   if budget['completed_updates']>5:raise RuntimeError('Repair-session 5-update validation cap exceeded')
   budget['runs'][-1]['completed_updates']=self.session_updates;self.validation_budget.write_text(json.dumps(budget,indent=2))
  super().log(locs,*args,**kwargs)
  if not finite_tree(self.alg.policy.state_dict()):raise RuntimeError('Non-finite policy parameters')
  samples=self.env.samples;row={k:sum(x[k] for x in samples)/len(samples) for k in samples[0]}
  row.update(mean_episode_reward=float(np.mean(locs['rewbuffer'])) if locs['rewbuffer'] else None,mean_episode_length=float(np.mean(locs['lenbuffer'])) if locs['lenbuffer'] else None,session_updates=self.session_updates,total_updates=self.total_updates,learning_rate=self.alg.learning_rate,exploration_std=float(self.alg.policy.std.mean()),elapsed_seconds=time.monotonic()-self.started,**{k:float(v) for k,v in locs['loss_dict'].items()})
  with (self.output/'metrics.jsonl').open('a') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
  self.env.samples.clear()
  self._progress(row)
  if self.session_updates%self.save_every==0:self.save(str(self.output/f'checkpoint_{self.total_updates:06d}.pt'))
  if self.max_seconds is not None and time.monotonic()-self.started>=self.max_seconds:self.stop_requested='max_seconds'
  if self.stop_requested:raise GracefulStop(self.stop_requested)
 def _progress(self,row):
  p=self.output/'progress.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(row,indent=2));os.replace(tmp,p)
 def save(self,path,infos=None):
  path=Path(path)
  if path.name.startswith('model_'):return
  if path.exists():raise FileExistsError(f'Refusing checkpoint overwrite: {path}')
  if not finite_tree(self.alg.policy.state_dict()) or not finite_tree(self.alg.optimizer.state_dict()):raise RuntimeError('Refusing non-finite checkpoint')
  rng=dict(torch_cpu=torch.get_rng_state(),torch_cuda=torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],numpy=np.random.get_state(),python=random.getstate())
  metadata={'spot_v4':dict(completed_updates=self.total_updates,session_updates=self.session_updates,base_updates=self.base_updates,requested_updates=self.requested,learning_rate=self.alg.learning_rate,rng=rng,simulation_state_restored=False)}
  temporary=path.with_name('.'+path.name+'.'+uuid.uuid4().hex+'.tmp')
  try:
   super().save(str(temporary),infos=metadata)
   os.replace(temporary,path)
  finally:
   if temporary.exists():temporary.unlink()
