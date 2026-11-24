"""Observed-command routing: frozen previous actor below0.6, learned actor above0.72."""
import copy,json
from pathlib import Path
import torch
from .trot_course import strength
from .training import file_hash

def blend_actions(old,new,observations):
    if observations.shape[-1]!=76:raise ValueError('Router requires declared76D observation layout')
    # Base layout is lin_vel3/ang_vel3/gravity3/applied_twist3, unchanged in both actors.
    alpha=strength(observations[:,9:12])[:,None]
    return torch.where(alpha==0,old,old+alpha*(new-old))

class RoutedTrotPolicy(torch.nn.Module):
    def __init__(self,new,old):super().__init__();self.new=new;self.old=old
    def act_inference(self,obs):return blend_actions(self.old.act_inference(obs),self.new.act_inference(obs),obs['policy'])

def routing_record(checkpoint):
    path=Path(str(checkpoint)+'.routing.json')
    if not path.exists():return None
    r=json.loads(path.read_text())
    if r['checkpoint_sha256']!=file_hash(checkpoint) or r['old_checkpoint_sha256']!=file_hash(r['old_checkpoint']):raise ValueError('Routed policy source hash mismatch')
    if r['vx_activation_mps']!=[.6,.72] or r['observation_applied_twist_slice']!=[9,12]:raise ValueError('Unknown routing contract')
    return r

def with_saved_routing(policy,checkpoint):
    r=routing_record(checkpoint)
    if r is None:return policy
    old=copy.deepcopy(policy);device=next(policy.parameters()).device;old.load_state_dict(torch.load(r['old_checkpoint'],map_location=device,weights_only=True)['model_state_dict'])
    old.eval();policy.eval();result=RoutedTrotPolicy(policy,old);result.eval();return result
