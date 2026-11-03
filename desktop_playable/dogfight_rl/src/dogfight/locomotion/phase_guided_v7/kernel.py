"""Pure tensor clock and dense reward kernel. Feet order LF, RF, LR, RR."""
import math
import torch
DEFAULTS=dict(frequency=1.5,clearance_start=.001,clearance_target=.025,stance_weight=1.2,release_weight=.6,height_weight=.8,slip_weight=.2,tracking_weight=4.,stop_fraction=.2,slip_mode='raw')
class Clock:
    def __init__(self,n,device='cpu'):
        self.phase=torch.zeros(n,device=device);self.activity=torch.zeros(n,device=device)
    def reset(self,ids):self.phase[ids]=0.;self.activity[ids]=0.
    def advance(self,dt,command,frequency):
        moving=command.norm(dim=-1)>.04
        self.activity.add_((moving.float()-self.activity)*(1-math.exp(-dt/.15)))
        # Freeze on stop. On restart preserve phase and ramp its angular speed.
        self.phase.add_(2*math.pi*frequency*dt*self.activity*moving).remainder_(2*math.pi)
    def observation(self):return torch.stack((self.phase.sin(),self.phase.cos()),-1)
    def state_dict(self):return dict(phase=self.phase.clone(),activity=self.activity.clone())
    def load_state_dict(self,state):
        self.phase.copy_(state['phase']);self.activity.copy_(state['activity'])
def schedule(phase):
    # Smooth 40ms-scale transition at 1.5Hz, equal diagonal pairs.
    s=.5+.5*torch.tanh(phase.sin()/ .20)
    return torch.stack((1-s,s,s,1-s),-1)
def terms(phase,command,velocity,yaw,contact,clearance,shin,slip,options=None,air_time=None):
    o=dict(DEFAULTS,**(options or {}));moving=command.norm(dim=-1)>.04
    stance=schedule(phase);swing=1-stance
    legal=contact&~shin
    h=((clearance-o['clearance_start'])/(o['clearance_target']-o['clearance_start'])).clamp(0,1)
    release=((clearance-.001)/.006).clamp(0,1)*(~contact)*(~shin)
    # Velocity has a zero stationary baseline, signed direction cost and lateral cost.
    from ..curriculum_v6.rewards import terms as directional
    progress,track,unwanted,stop=directional(command,velocity,yaw)
    # Dense learning starts at zero speed, but stationary phase imitation cannot
    # score near locomotion: all gait bonuses total <=2.6 vs speed contribution ~6.
    quality=(1-velocity[:,1].abs()/.25).clamp(0,1)
    return dict(progress=progress,tracking=track,unwanted=unwanted,stop=stop,
        gait_stance_contact=(stance*legal).sum(-1)/2*moving*quality,
        gait_swing_release=(swing*release).sum(-1)/2*moving*quality,
        height_progress=(swing*h*(~contact)*(~shin)).sum(-1)/2*moving*quality,
        slip=((torch.log1p(slip/.08) if o.get('slip_mode','raw')=='log' else slip)*legal).sum(-1)/legal.sum(-1).clamp_min(1),
        shin=shin.float().mean(-1),
        wrong_support=(swing*legal+stance*(~legal)).mean(-1)*moving,
        stop_feet=(slip.square().mean(-1))*(~moving),
        unsupported=(legal.sum(-1)==0).float()*moving,
        excess_height=((clearance/o['clearance_target']-1).clamp(0,3)).mean(-1),
        overdue_air=torch.zeros_like(progress) if air_time is None else ((air_time-.6/o['frequency'])/(.4/o['frequency'])).clamp(0,1).mean(-1)*moving)
def weighted(values,o=None):
    o=dict(DEFAULTS,**(o or {}))
    weights=dict(progress=o['tracking_weight'],tracking=2.,unwanted=-2.,stop=2.,gait_stance_contact=o['stance_weight'],gait_swing_release=o['release_weight'],height_progress=o['height_weight'],slip=-o['slip_weight'],shin=-2.,wrong_support=-2.,stop_feet=-.5,unsupported=-3.,excess_height=-2.,overdue_air=-6.)
    return sum(values[k]*v for k,v in weights.items())
