"""Prioritize earliest reachable preview constraints when one fixed goal cannot satisfy all."""
import torch
from .workspace_height_preview import contract as base_contract,TrajectoryHeightConfig
TAG='csdog_workspace_height_priority_obs175_v36'

def contract(parent):
    d=base_contract(parent);d.update(schema_version=36,compatibility_tag=TAG)
    d['height']['automatic_workspace_preview']['infeasible_forecast_selection']='maximize consecutive feasible preview times from now; then minimize violation at the earliest unmet constraint; a distant larger violation cannot outweigh an earlier constraint; same20mrad preview reserve and executed hard limits'
    return d

def select_height(error,margin,candidates,previous,cfg=None):
    cfg=cfg or TrajectoryHeightConfig()
    per_time=((error<=cfg.solve_tolerance_m)&(margin>=cfg.joint_reserve_rad)).all(3)
    prefix=per_time.long().cumprod(2).sum(2)
    full=prefix==error.shape[2];cost=candidates.abs()[None]+.25*(candidates[None]-previous[:,None]).abs()
    good_score=torch.where(full,cost,torch.inf)
    first_bad=prefix.clamp_max(error.shape[2]-1)
    violation=(error/cfg.solve_tolerance_m+torch.relu(cfg.joint_reserve_rad-margin)/.01).amax(3)
    earliest=violation.gather(2,first_bad[:,:,None]).squeeze(2)
    eligible=prefix==prefix.amax(1,keepdim=True)
    fallback=torch.where(eligible,earliest+.001*cost,torch.inf).argmin(1)
    index=torch.where(full.any(1),good_score.argmin(1),fallback)
    return candidates[index],full.any(1)
