"""Known-geometry test courses, an oracle diagnostic rather than terrain perception."""
import math
from dataclasses import dataclass
import torch

SLOPE_DEG=5.
START=.7
RUN=.6
PLATEAU=.6
RISE=math.tan(math.radians(SLOPE_DEG))*RUN
END=START+2*RUN+PLATEAU
BAR_CENTERS=(.8,1.6,2.4)
BAR_WIDTH=.1


@dataclass(frozen=True)
class CourseConfig:
    slope_deg: float=5.
    low_bar_m: float=.01
    high_bar_m: float=.02
    speed_mps: float=.2
    material_friction: float=1.

    def __post_init__(self):
        if not all(math.isfinite(v) and v>0 for v in vars(self).values()):raise ValueError('Invalid course parameters')
        if self.slope_deg>15 or self.low_bar_m>self.high_bar_m:raise ValueError('Unsupported course geometry')

    @property
    def rise_m(self):return math.tan(math.radians(self.slope_deg))*RUN


BASE_COURSE=CourseConfig()
CHALLENGE_COURSE=CourseConfig(slope_deg=8.,low_bar_m=.02,high_bar_m=.03,speed_mps=.25,material_friction=.8)


def course_height(x,case,y=None,config=None):
    """Local world-Z surface height. case broadcasts with x; all widths are finite."""
    cfg=config or BASE_COURSE
    up=((x-START)/RUN).clamp(0,1)*cfg.rise_m
    down=((END-x)/RUN).clamp(0,1)*cfg.rise_m
    hill=torch.minimum(up,down)
    bar=torch.zeros_like(x)
    for center in BAR_CENTERS:bar=torch.maximum(bar,((x-center).abs()<=BAR_WIDTH/2).to(x.dtype))
    height=torch.where(case==1,cfg.low_bar_m*bar,torch.zeros_like(x))
    height=torch.where((case==2)|(case==4),cfg.high_bar_m*bar,height)
    height=torch.where(case==3,hill,height)
    return height if y is None else torch.where(y.abs()<=.6,height,torch.zeros_like(height))


def extra_swing_clearance(target,phase,duty,extra_m,blend):
    """Terrain-diagnostic C2 lift; no stance height or actuator bound changes."""
    local=torch.remainder(phase[:,None]+phase.new_tensor([0.,.5,0.,.5]),1.)
    progress=((local-duty[:,None])/(1-duty[:,None])).clamp(0,1)
    bump=64*progress.pow(3)*(1-progress).pow(3)
    result=target.clone()
    result[:,:,2]+=extra_m[:,None]*blend[:,None]*bump
    return result
