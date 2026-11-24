"""Rank true endpoint violations even when no complete preview plan is feasible."""
import torch
from .stance_preview import contract as parent_contract

TAG='csdog_ranked_stance_preview_obs175_v61'

def reachable_stance_forecast(error,margin,endpoint_error,endpoint_margin,continuing,cfg):
    preferred=error/cfg.solve_tolerance_m+torch.relu(cfg.joint_reserve_rad-margin)/.01
    measured=endpoint_error/cfg.solve_tolerance_m+torch.relu(cfg.joint_reserve_rad-endpoint_margin)/.01
    use=continuing&(measured<preferred)
    # Return measured violations as-is. A bad endpoint remains a bad plan;
    # select_height still applies the original complete-plan thresholds.
    return torch.where(use,endpoint_error,error),torch.where(use,endpoint_margin,margin),use

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=61,compatibility_tag=TAG)
    description='while measured stance continues, forecast uses lower true normalized IK/joint-reserve violation of preferred and same-worldXY measured-Z endpoint; partial improvement is available to the unchanged earliest-constraint fallback; bad endpoint is never marked feasible'
    d['minimum_stance_projection']['preview']=description
    d['measured_contact_patch']['forecast']=description
    d['stance_endpoint_preview']['endpoint_requires_original_preview_margin']='complete feasibility still requires original30mrad preview margin; partial endpoint violations may be ranked but are not waived'
    return d
