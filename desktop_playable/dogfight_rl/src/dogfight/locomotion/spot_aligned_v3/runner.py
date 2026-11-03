"""Measurements and checkpoint cadence only; unmodified RSL PPO and Gaussian probabilities."""
from pathlib import Path
import torch
from ..runner import MeasuredRunner,MeasuredWrapper
from ..spot_v2.contacts import contact_state
class Wrapper(MeasuredWrapper):
 def step(self,actions):
  result=super().step(actions);e=self.unwrapped;r=e.scene['robot'];s=contact_state(e);c=s.contact
  row=self.samples[-1]
  row.update(raw_outside_unit_fraction=float((actions.abs()>1).float().mean()),actual_action_clip=0.,slip=float((s.velocity[:,:,:2].norm(dim=-1)*c).sum()/c.sum().clamp_min(1)),
   air_fraction=float(((~c)&(s.clearance>.015)).float().mean()),air_time=float(s.data.current_air_time.mean()),
   diagonal_support=float(((c[:,0]==c[:,3])&(c[:,1]==c[:,2])&(c[:,0]!=c[:,1])).float().mean()),
   torque_rms=float(r.data.applied_torque.square().mean().sqrt()),torque_saturation=float((r.data.applied_torque.abs()>=9.9).float().mean()),
   gait_applicable=float(getattr(e,'_gait_applicable',torch.zeros(e.num_envs,device=e.device)).float().mean()),
   gait_trustworthy=float(getattr(e,'_gait_trustworthy',torch.zeros(e.num_envs,device=e.device)).float().mean()))
  for i,name in enumerate(e.reward_manager.active_terms):row['contribution_'+name]=float(e.reward_manager._step_reward[:,i].mean())
  return result
class Runner(MeasuredRunner):
 def log(self,locs,*a,**kw):
  # Include exploration scale in the same averaging interface.
  for sample in self.env.samples:sample['exploration_std']=float(self.alg.policy.std.mean())
  super().log(locs,*a,**kw)
  if self.budget.completed%30==0:self.save(str(self.output/f'update_{self.budget.completed:04d}.pt'))
 def save(self,path,*a,**kw):
  # Suppress zero-based automatic cadence; explicit checkpoints are at exactly 30 completed updates.
  if Path(path).name.startswith('model_'):return
  return super().save(path,*a,**kw)
