"""Explicit flat76 to scanned175 observation migration; no optimizer state transfer."""
import torch
SCAN_RAYS=99
OBSERVATIONS=76+SCAN_RAYS
TAG='csdog_scanned_rough_residual_obs175_v28'

def extend_inputs(state,target):
    if state.keys()!=target.keys():raise ValueError('Policy tensor keys differ')
    result={}
    for k,v in state.items():
        if k in ('actor.0.weight','critic.0.weight'):
            if v.shape[1]!=76 or target[k].shape!=(v.shape[0],OBSERVATIONS):raise ValueError('Expected76to175 input migration')
            result[k]=torch.zeros_like(target[k]);result[k][:,:76]=v
        else:
            if v.shape!=target[k].shape:raise ValueError('Unexpected policy shape change')
            result[k]=v.clone()
    return result

def relative_scan(hit_z,root_ground):
    if hit_z.ndim!=2 or hit_z.shape[1]!=SCAN_RAYS or not torch.isfinite(hit_z).all() or not torch.isfinite(root_ground).all():raise ValueError('Missing or invalid terrain ray hits')
    return ((hit_z-root_ground[:,None])/.1).clamp(-2,2)
