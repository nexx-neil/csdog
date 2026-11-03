"""Official OnPolicyRunner with observation checks, iteration metrics and time-stop checkpoints.

No PPO algorithm implementation is copied or modified.
"""
import json,time,subprocess,statistics
import torch
from rsl_rl.runners import OnPolicyRunner
from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
class BudgetStop(Exception):pass
class MeasuredWrapper(RslRlVecEnvWrapper):
 def __init__(self,*a,**kw):
  super().__init__(*a,**kw);self.samples=[];self.previous=None
 def step(self,actions):
  if not torch.isfinite(actions).all():raise RuntimeError('nonfinite actions')
  obs,rew,done,extra=super().step(actions)
  if not torch.isfinite(obs['policy']).all() or not torch.isfinite(rew).all():raise RuntimeError('nonfinite observation/reward')
  env=self.unwrapped;r=env.scene['robot'];cmd=env.command_manager.get_command('base_velocity')
  delta=0. if self.previous is None else float((actions-self.previous).square().mean());self.previous=actions.clone()
  timeouts=extra.get('time_outs',torch.zeros_like(done))
  self.samples.append(dict(reward_step=float(rew.mean()),linear_error=float((cmd[:,:2]-r.data.root_lin_vel_b[:,:2]).norm(dim=-1).mean()),
   yaw_error=float((cmd[:,2]-r.data.root_ang_vel_b[:,2]).abs().mean()),falls=int((done.bool()&~timeouts.bool()).sum()),done=int(done.sum()),action_delta_sq=delta,
   command_yaw_abs=float(cmd[:,2].abs().mean()),joint_speed_max=float(r.data.joint_vel.abs().max())))
  return obs,rew,done,extra
class MeasuredRunner(OnPolicyRunner):
 def __init__(self,*a,budget,output,**kw):
  self.budget=budget;self.output=output;super().__init__(*a,**kw)
 def log(self,locs,*a,**kw):
  self.budget.update()
  super().log(locs,*a,**kw)
  samples=self.env.samples
  row={k:sum(s[k] for s in samples)/len(samples) for k in samples[0]}
  row.update(iteration=int(locs['it']),completed_updates=self.budget.completed,elapsed_seconds=time.monotonic()-self.budget.started,
   mean_episode_reward=statistics.mean(locs['rewbuffer']) if locs['rewbuffer'] else None,
   mean_episode_length=statistics.mean(locs['lenbuffer']) if locs['lenbuffer'] else None,
   learning_rate=self.alg.learning_rate,**{str(k):float(v) for k,v in locs['loss_dict'].items()})
  row['policy_entropy']=float(self.alg.policy.entropy.mean())
  try:row['gpu_memory_mib']=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.used','--format=csv,noheader,nounits'],text=True).splitlines()[0])
  except Exception:row['gpu_memory_mib']=None
  with (self.output/'metrics.jsonl').open('a') as f:f.write(json.dumps(row)+'\n')
  if any(not torch.isfinite(p).all() for p in self.alg.policy.parameters()):raise RuntimeError('nonfinite policy parameter')
  self.env.samples.clear()
  if self.budget.expired():
   self.save(str(self.output/'time_limit.pt'));raise BudgetStop('Training wall-time budget reached')
