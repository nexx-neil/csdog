"""Break equal earliest-infeasibility ties with later response, before posture cost."""
import torch
from .contact_datum import contract as parent_contract
from .workspace_height_preview import TrajectoryHeightConfig
TAG='csdog_contact_datum_lexicographic_preview_obs175_v53'
TIE_TOLERANCE=1e-6

def select_height(error,margin,candidates,previous,cfg=None):
    cfg=cfg or TrajectoryHeightConfig()
    per_time=((error<=cfg.solve_tolerance_m)&(margin>=cfg.joint_reserve_rad)).all(3)
    prefix=per_time.long().cumprod(2).sum(2);full=prefix==error.shape[2]
    cost=candidates.abs()[None]+.25*(candidates[None]-previous[:,None]).abs()
    good_index=torch.where(full,cost,torch.inf).argmin(1)
    eligible=prefix==prefix.amax(1,keepdim=True)
    # Numerical IK noise inside solve tolerance has no violation. Feasible prefix
    # is still judged with the unchanged actual error and reserve requirements.
    violation=(torch.relu(error/cfg.solve_tolerance_m-1.)+torch.relu(cfg.joint_reserve_rad-margin)/.01).amax(3)
    for t in range(error.shape[2]):
        best=torch.where(eligible,violation[:,:,t],torch.inf).amin(1,keepdim=True)
        eligible=eligible&(violation[:,:,t]<=best+TIE_TOLERANCE)
    fallback=torch.where(eligible,cost,torch.inf).argmin(1)
    index=torch.where(full.any(1),good_index,fallback)
    return candidates[index],full.any(1)

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=53,compatibility_tag=TAG)
    d['height']['contact_datum']['preview']='full sensed optional lift as v50; if no candidate satisfies all times, maximize feasible prefix then lexicographically minimize violations at every forecast time before posture cost; saturated equal immediate responses can be distinguished by their later descent; IK error within50um contributes zero violation; original feasibility20mrad and executed guards unchanged'
    d['height']['contact_datum']['fallback_tie_tolerance_normalized']=TIE_TOLERANCE
    return d
