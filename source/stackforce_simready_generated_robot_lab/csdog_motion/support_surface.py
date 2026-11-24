"""Idempotent physical-step filter for a measured support-height datum."""
import copy,math
import torch
TAG='csdog_support_surface_obs175_v30'


def contract(parent):
    value=copy.deepcopy(parent);value.update(schema_version=30,compatibility_tag=TAG)
    value['height']['reference']='base above filtered mean of99 physical terrain scan hits'
    value['rough_sensing']['height_reward_and_support']='relative to filtered mean of99 physical terrain scan hits; foot clearance still local ray'
    value['rough_sensing']['support_surface']={'statistic':'mean99 scan hits','filter_tau_s':.1,'update':'once per physical control step; reset only reset environments','reference_delta':'target ray height minus same filtered support datum','extra_swing_lift_cap_m':.01}
    value['terrain_reward']='same residual terms; body height uses measured support surface, foot clearance uses local actual ray'
    return value


class SupportSurface:
    def __init__(self,n,device,dt=.02,tau=.1):
        if dt<=0 or tau<=0:raise ValueError('Positive filter times required')
        self.height=torch.zeros(n,device=device);self.valid=torch.zeros(n,dtype=torch.bool,device=device)
        self.tick=-1;self.alpha=1-math.exp(-dt/tau)

    def reset(self,ids):self.valid[ids]=False

    def update(self,raw,tick):
        if raw.shape!=self.height.shape or not torch.isfinite(raw).all():raise ValueError('Invalid measured surface')
        if tick!=self.tick:
            self.height.copy_(torch.where(self.valid,self.height+self.alpha*(raw-self.height),raw))
            self.valid.fill_(True);self.tick=tick
        elif not self.valid.all():
            self.height[~self.valid]=raw[~self.valid];self.valid.fill_(True)
        return self.height
