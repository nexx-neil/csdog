"""Faster pure-turn integral response; original backward correction stays exact."""
import torch
from .terrain_control import contract as base_contract,YAW
from .yaw_integral import YawIntegral,strength
TAG='csdog_reachable_terrain_turn_obs175_v33'


def contract(parent):
    value=base_contract(parent);value.update(schema_version=33,compatibility_tag=TAG)
    value['support_feedback']['yaw_integral']['terrain_pure_turn_extra_integral_gain_nm_rad']=2.4
    value['support_feedback']['yaw_integral']['terrain_pure_turn_scope']='additional integration only for requested pure-turn activation; original backward integration exact; same.6Nm integral and2Nm total caps'
    return value


class TerrainYawIntegral(YawIntegral):
    def tick(self,dt,applied,requested,actual_yaw,p_moment,active):
        super().tick(dt,applied,requested,actual_yaw,p_moment,active)
        s=((applied[:,2].abs()-.1)/.2).clamp(0,1)
        turn=s.pow(3)*(10+s*(-15+6*s))
        turn*=1-(applied[:,0].abs()/.4+applied[:,1].abs()/.3).clamp(0,1)
        enabled=strength(applied,self.cfg)*(requested.abs().amax(1)>1e-6)
        increment=2.4*self.filtered_error*dt*turn*(requested.abs().amax(1)>1e-6)
        total=p_moment+self.integral*enabled
        blocked=((total>=2.)&(increment>0))|((total<=-2.)&(increment<0))|~active
        increment=torch.where(blocked,0.,increment)
        self.integral=(self.integral+increment).clamp(-self.cfg.maximum_moment_nm,self.cfg.maximum_moment_nm)
        self.moment=self.integral*enabled
        return self.moment
