"""Preview the reachable measured vertical endpoint used by stance repair."""
import torch
from .stance_workspace import contract as parent_contract

TAG='csdog_consistent_stance_preview_obs175_v60'

def reachable_stance_forecast(error,margin,endpoint_error,endpoint_margin,continuing,cfg):
    preferred_good=(error<=cfg.solve_tolerance_m)&(margin>=cfg.joint_reserve_rad)
    endpoint_good=(endpoint_error<=cfg.solve_tolerance_m)&(endpoint_margin>=cfg.joint_reserve_rad)
    use=~preferred_good&continuing&endpoint_good
    return torch.where(use,endpoint_error,error),torch.where(use,endpoint_margin,margin),use

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=60,compatibility_tag=TAG)
    d['minimum_stance_projection']['preview']='candidate-specific preferred target first; while a measured foothold continues, an otherwise infeasible preferred stance may use feasibility of its same-worldXY measured-Z endpoint; original preview error/margin limits unchanged; execution still chooses minimum correction'
    d['measured_contact_patch']['forecast']=d['minimum_stance_projection']['preview']
    d['stance_endpoint_preview']={'no_endpoint_after_liftoff':True,'endpoint_requires_original_preview_margin':True,'no_invented_contact_for_support_forces':True,'support_height_definition_unchanged':True,'no_global_stability_claim':True}
    return d
