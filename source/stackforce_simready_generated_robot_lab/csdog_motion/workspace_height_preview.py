"""Preview the bounded height response itself, rather than a constant final height."""
from dataclasses import dataclass
import torch
from .workspace_height import HeightPlanConfig,contract as base_contract
TAG='csdog_workspace_height_trajectory_obs175_v35'

@dataclass(frozen=True)
class TrajectoryHeightConfig(HeightPlanConfig):
    joint_reserve_rad:float=.02
    preview_seconds:tuple=(0.,.04,.08,.12,.16,.20,.24)
    replanning_steps:int=1

def contract(parent):
    d=base_contract(parent);d.update(schema_version=35,compatibility_tag=TAG)
    d['height']['automatic_workspace_preview'].update(**TrajectoryHeightConfig().__dict__)
    d['height']['automatic_workspace_preview']['preview_seconds']=list(TrajectoryHeightConfig().preview_seconds)
    d['height']['automatic_workspace_preview']['height_prediction']='simulate the same bounded acceleration/velocity height servo for each candidate goal; evaluate each future foot target at its predicted applied height; first .02s update included at time0'
    return d

def predict_applied_heights(state,candidates,dt=.02):
    c=state.cfg;n=len(state.value);k=len(candidates)
    value=state.value[:,None].expand(n,k).clone();vel=state.velocity[:,None].expand(n,k).clone();goal=candidates[None].expand(n,k);snapshots=[]
    indices=[round(t/dt)+1 for t in c.preview_seconds]
    for step in range(1,max(indices)+1):
        acceleration=(c.response_radps**2*(goal-value)-2*c.response_radps*vel).clamp(-c.maximum_acceleration_mps2,c.maximum_acceleration_mps2)
        vel=(vel+dt*acceleration).clamp(-c.maximum_speed_mps,c.maximum_speed_mps)
        value=(value+dt*vel).clamp(-c.maximum_offset_m,c.maximum_offset_m)
        vel=torch.where((value>=c.maximum_offset_m)&(vel>0)|(value<=-c.maximum_offset_m)&(vel<0),0.,vel)
        if step in indices:snapshots.append(value.clone())
    return torch.stack(snapshots,2)
