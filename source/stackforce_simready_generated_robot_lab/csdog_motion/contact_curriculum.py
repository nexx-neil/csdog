"""External training curriculum/reward adapter; inference task stays unchanged."""
import torch

PROFILE = {
    'name':'backward_terrain_contact_v1',
    'initial_stand_s':.5,
    'stairs_columns':[4,5],
    'stairs_backward_probability':.75,
    'stairs_backward_speed_mps':[.22,.25],
    'stairs_backward_hold_s':[7.5,9.],
    'other_commands':'original single-axis ranges;15% stand;4-6s holds',
    'native_slide_weight':-.5,
    'effective_slide_weight':-30.,
    'activation':'C2 backward speed .20-.25m/s times C2 measured scan spread .002-.012m',
    'reward_timing':'reuse native pre-reset stance_slide term, at every .02s control step',
    'scope':'external training commands and additive reward only; no inference controller/limits changes',
}


def smoothstep(x):
    s=x.clamp(0,1)
    return s.pow(3)*(10+s*(-15+6*s))


def activation(applied_twist, scan_spread):
    return smoothstep((-applied_twist[:,0]-.20)/.05)*smoothstep((scan_spread-.002)/.01)


def additional_slide_reward(native_scaled_term, gate, native_weight=-.5, effective_weight=-30.):
    if native_weight>=0 or effective_weight>native_weight:
        raise ValueError('Expected stronger negative slide penalty')
    return native_scaled_term * (effective_weight/native_weight-1.) * gate


class CommandReplay:
    """Long stair backward bouts, plus broad replay; never controls world position."""
    def __init__(self, env):
        self.env=env
        self.current=torch.zeros(env.num_envs,3,device=env.device)
        self.remaining=torch.full((env.num_envs,),.5,device=env.device)
        self.targeted_bouts=0
        self.total_bouts=0

    def reset(self):
        self.current.zero_();self.remaining.fill_(.5)

    def request(self):
        self.remaining-=self.env.step_dt
        ids=torch.where(self.remaining<=0)[0]
        if len(ids):
            n=len(ids);cmd=torch.zeros(n,3,device=self.env.device)
            axes=torch.randint(0,3,(n,),device=self.env.device)
            mag=torch.empty(n,device=self.env.device).uniform_(.5,1.)
            sign=torch.where(torch.rand(n,device=self.env.device)<.5,-1.,1.)
            cmd[torch.arange(n,device=self.env.device),axes]=cmd.new_tensor([.25,.2,.3])[axes]*mag*sign
            cmd[torch.rand(n,device=self.env.device)<.15]=0
            hold=torch.empty(n,device=self.env.device).uniform_(4.,6.)
            cols=self.env.terrain_columns[ids]
            targeted=((cols==4)|(cols==5))&(torch.rand(n,device=self.env.device)<.75)
            count=int(targeted.sum())
            cmd[targeted]=0
            cmd[targeted,0]=-torch.empty(count,device=self.env.device).uniform_(.22,.25)
            hold[targeted]=torch.empty(count,device=self.env.device).uniform_(7.5,9.)
            self.current[ids]=cmd;self.remaining[ids]=hold
            self.targeted_bouts+=count;self.total_bouts+=n
        self.env.set_motion_request(self.current)

    def on_dones(self,dones):
        ids=torch.where(dones.bool())[0]
        self.current[ids]=0;self.remaining[ids]=.5
