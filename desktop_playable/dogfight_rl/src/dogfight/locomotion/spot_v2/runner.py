"""Spot measurements on unmodified RSL PPO; raw Gaussian log-prob remains unchanged."""
import torch
from ..runner import MeasuredWrapper,MeasuredRunner
from .contacts import contact_state
class SpotWrapper(MeasuredWrapper):
 def step(self,actions):
  self.unwrapped._raw_policy_action=actions
  result=super().step(actions)
  e=self.unwrapped;s=contact_state(e);c=s.contact;v=s.velocity[:,:,:2].norm(dim=-1)
  row=self.samples[-1]
  row.update(action_clip=float((actions.abs()>1).float().mean()),slip=float((v*c).sum()/c.sum().clamp_min(1)),air_fraction=float(((~c)&(s.clearance>.015)).float().mean()),
   gait_coordination=float(((c[:,0]==c[:,3])&(c[:,1]==c[:,2])&(c[:,0]!=c[:,1])).float().mean()),shin_fraction=float(s.shin.float().mean()))
  for i,name in enumerate(e.reward_manager.active_terms):row['contribution_'+name]=float(e.reward_manager._step_reward[:,i].mean())
  return result
