"""Keep nominal support feedback; repair only unreachable loaded stance targets."""
import torch
from .swing_workspace import contract as parent_contract

TAG='csdog_minimum_stance_workspace_obs175_v59'
EPS=.00005
RESERVE=.01
BISECTIONS=8

def repair_stance(model,preferred,measured_endpoint,eligible,q_full,error_full):
    """Smallest feasible fraction toward a measured endpoint on a vertical line.

    The caller constructs endpoints at identical worldXY. Feasible old targets
    remain bitwise unchanged, including near-limit feasible targets. Only a
    loaded, scheduled, remembered stance leg can be repaired. Non-repairable
    targets stay subject to the original rejection path.
    """
    active=eligible&(error_full>EPS)
    weight=torch.zeros_like(error_full)
    if not active.any():return preferred,q_full,error_full,weight,active
    if not torch.isfinite(measured_endpoint[active]).all():
        raise RuntimeError('Nonfinite measured stance endpoint')
    def solve(fraction):
        target=torch.where(active[:,:,None],preferred+fraction[:,:,None]*(measured_endpoint-preferred),preferred)
        q,error=model.solve(target,iterations=18)
        margin=torch.minimum(q-model.lower,model.upper-q).amin(2)
        return target,q,error,(error<=EPS)&(margin>=RESERVE)
    low=torch.zeros_like(weight);high=torch.ones_like(weight)
    target,q,error,good=solve(high)
    if (active&~good).any():
        raise RuntimeError('No reachable loaded stance endpoint with original joint reserve')
    for _ in range(BISECTIONS):
        mid=(low+high)/2
        _,_,_,good=solve(mid)
        high=torch.where(active&good,mid,high)
        low=torch.where(active&~good,mid,low)
    weight=torch.where(active,high,weight)
    target,q,error,good=solve(weight)
    if (active&~good).any():raise RuntimeError('Stance projection lost feasibility')
    return target,torch.where(active[:,:,None],q,q_full),torch.where(active,error,error_full),weight,active

def contract(parent):
    d=parent_contract(parent);d.update(schema_version=59,compatibility_tag=TAG)
    d['measured_contact_patch']['reference']='v56 preferred worldXY/equivalent support height with nominal height feedback; active loaded stance alone may receive minimum vertical workspace correction toward measured foot-center Z; no unconditional XYZ lock'
    d['measured_contact_patch']['forecast']='v56 nominal-height preferred reference, same13 response-aware preview samples; does not assume fullXYZ execution locking'
    d['constrained_swing']['stance']='v59 minimum vertical feasibility projection; separate from swing fallback'
    d['minimum_stance_projection']={'activation':'remembered scheduled stance and preferred IK error>50um; retain feasible legacy q/error bitwise',
        'path':'same held worldXY; interpolate only worldZ toward measured loaded foot-center height',
        'objective':'smallest endpoint fraction satisfying50um IK and10mrad joint reserve',
        'bisections':BISECTIONS,'no_endpoint_solution':'hard reject',
        'preview':'retain nominal support-height feedback in preferred forecast; constrained correction only during execution',
        'continuity':'per-control-step projection; original8rad/s executed target limiter remains; no global C2 or optimal-control claim',
        'learning':'same175 network; zero newPPO; frozen daily27/23 preserved'}
    return d
