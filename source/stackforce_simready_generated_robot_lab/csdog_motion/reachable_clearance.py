"""Allocate surplus lift within existing per-leg workspace; never relax IK/limits."""
import copy
import torch
TAG='csdog_reachable_clearance_obs175_v31'
JOINT_RESERVE_RAD=.01
SOLVE_TOL_M=.00005


def contract(parent):
    value=copy.deepcopy(parent);value.update(schema_version=31,compatibility_tag=TAG)
    value['rough_sensing']['reachable_clearance']={'max_sensor_surplus_m':.01,'joint_reserve_rad':JOINT_RESERVE_RAD,'feasibility_error_m':SOLVE_TOL_M,'bisection_steps':6,'activation':'requested surplus yields IK residual above50um; otherwise retain exact original output','scope':'only surplus lift may shrink per leg; base lift/landing rays/stance targets/limits unchanged; no feasible base target remains a hard failure'}
    return value


def allocate(model,build_target,q_full,error_full,lift):
    margin=torch.minimum(q_full-model.lower,model.upper-q_full).amin(2)
    active=(error_full>SOLVE_TOL_M)&(lift>1e-6)
    if not active.any():return q_full,error_full,torch.ones_like(lift),active
    low=torch.where(active,torch.zeros_like(lift),torch.ones_like(lift));high=torch.ones_like(lift)
    def solve(scale):
        q,e=model.solve(build_target(scale),iterations=18)
        margin=torch.minimum(q-model.lower,model.upper-q).amin(2)
        return q,e,(e<=SOLVE_TOL_M)&(margin>=JOINT_RESERVE_RAD)
    q,e,good=solve(low)
    if (active&~good).any():raise RuntimeError('Base foot reference is infeasible; surplus lift cannot repair it')
    for _ in range(6):
        mid=(low+high)/2;q,e,good=solve(mid)
        low=torch.where(active&good,mid,low);high=torch.where(active&~good,mid,high)
    q,e,_=solve(low)
    # Leave every unaffected leg exactly at the original controller output.
    return torch.where(active[:,:,None],q,q_full),torch.where(active,e,error_full),low,active
