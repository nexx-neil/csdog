"""Fallback swing trajectory optimization; retain the old result when feasible."""
import torch
from .reachable_clearance import allocate as legacy_allocate
from .stance_foothold import contract as parent_contract
TAG='csdog_constrained_swing_foothold_obs175_v58'
EPS=.00005
RESERVE=.01
MIN_CLEARANCE_M=.01

def allocate_swing(model,build_sensor,build_total,q_full,error_full,basic_lift,surplus_lift,minimum_scale,safe_clearance,swing):
    """No stance modification or joint/IK relaxation; minimum clearance mandatory."""
    try:
        q,e,scale,changed=legacy_allocate(model,build_sensor,q_full,error_full,surplus_lift)
        if not ((e>EPS)&swing).any():
            if ((e>EPS)&~swing).any():raise RuntimeError('Stance reference infeasible; swing optimization cannot repair it')
            return q,e,basic_lift+surplus_lift*scale,changed,torch.zeros_like(swing)
    except RuntimeError as exc:
        if 'Base foot reference is infeasible; surplus lift cannot repair it' not in str(exc):raise
    total=basic_lift+surplus_lift;active=(error_full>EPS)&swing&(total>1e-6)
    if ((error_full>EPS)&~swing).any():raise RuntimeError('Stance reference infeasible; swing optimization cannot repair it')
    if (active&(minimum_scale>1.)).any():raise RuntimeError('Minimum planned obstacle clearance exceeds full swing target')
    low=torch.where(active,minimum_scale.clamp(0,1),torch.ones_like(total));high=torch.ones_like(total)
    def solve(scale):
        target=build_total(scale);q,e=model.solve(target,iterations=18)
        margin=torch.minimum(q-model.lower,model.upper-q).amin(2)
        good=(e<=EPS)&(margin>=RESERVE)&safe_clearance(target)
        return q,e,good
    q,e,good=solve(low)
    if (active&~good).any():raise RuntimeError('No reachable swing target at minimum planned clearance')
    for _ in range(8):
        mid=(low+high)/2;q,e,good=solve(mid)
        low=torch.where(active&good,mid,low);high=torch.where(active&~good,mid,high)
    q,e,_=solve(low)
    return torch.where(active[:,:,None],q,q_full),torch.where(active,e,error_full),total*low,active,active

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=58,compatibility_tag=TAG)
    d['constrained_swing']={'legacy_first':True,'scope':'new reference design:32mm basic lift becomes preferred maximum, only infeasible swing legs may reduce it; previously failed v56/v57 are retained','minimum_planned_world_clearance_m':MIN_CLEARANCE_M,'minimum_envelope':'10mm times original C2 phase bump and motion blend, zero at touchdown/liftoff','terrain_check':'center plus8 perimeter mesh rays at18mm sphere radius; conservative sampled vertical cylinder proxy, not a complete swept-collision proof','selection':'maximize original swing lift subject to50um IK,10mrad joint reserve and minimum planned actual-world clearance;8 bisections; no solution remains a hard failure','preview':'v57 preferred32mm basic swing forecast retained as conservative envelope; constrained execution fallback does not claim a joint trajectory MPC','stance':'frozen v57 worldXYZ contact anchor, never shortened by swing optimizer','limits_and_acceptance':'unchanged actual joint limits,target offset.5rad,target rate8radps,torque12Nm,executed IK1mm and all quality gates','learning':'same175 network; desired swing-clearance reward follows chosen reference; no new PPO'}
    return d
