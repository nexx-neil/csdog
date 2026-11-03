"""Read-only 500Hz validation of raw force + full collision-mesh clearance.

No hysteresis, merged gaps, or discarded sensor data. Integer physical ticks,
not policy samples, determine continuous 60ms flight qualifications.
"""
import torch
from ..spot_v2.contacts import ContactState
from .events import advance_air_ticks

CONTACT_VERSION='v6.1-raw-500hz-events-1'
class PhysicalEvents:
    def __init__(self,b):
        self.b=b;self.raw=ContactState(b);self.original=b.scene.update
        shape=(b.num_envs,4);device=b.device
        self.air_ticks=torch.zeros(shape,device=device,dtype=torch.long)
        self.ready=torch.zeros(shape,device=device,dtype=torch.bool)
        self.flight_ticks=torch.zeros_like(self.air_ticks)
        self.previous_contact=torch.zeros(shape,device=device,dtype=torch.bool)
        self.begin_control();b.scene.update=self.update
    def begin_control(self):
        self.event_ticks=torch.zeros_like(self.air_ticks)
        self.landings=torch.zeros_like(self.ready)
        self.strict_ticks=torch.zeros_like(self.air_ticks)
        self.switches=torch.zeros_like(self.air_ticks)
        self.support_n=torch.zeros_like(self.air_ticks)
        self.slip_sum=torch.zeros_like(self.air_ticks,dtype=torch.float)
    def update(self,dt):
        self.original(dt)
        with torch.inference_mode():
            self.raw.key=None;s=self.raw.update()
            reset=(self.b.episode_length_buf<=1)[:,None]
            self.air_ticks.masked_fill_(reset,0);self.flight_ticks.masked_fill_(reset,0);self.ready.masked_fill_(reset,False)
            strict=(~s.contact)&(s.clearance>.015)&(s.raw_force<1.)&(~s.shin)
            self.air_ticks,ended=advance_air_ticks(self.air_ticks,strict)
            self.event_ticks=torch.maximum(self.event_ticks,ended)
            self.ready|=(ended>=30)&(ended<=300)
            self.flight_ticks=torch.where(~s.contact,self.flight_ticks+1,0)
            self.ready&=(self.flight_ticks<=300)
            self.landings|=self.ready&s.contact&(~s.shin)
            self.ready&=~s.contact
            self.strict_ticks+=strict.long()
            self.switches+=(s.contact!=self.previous_contact).long()*(~reset)
            self.previous_contact=s.contact.clone()
            self.support_n+=s.contact.long()
            self.slip_sum+=s.velocity[:,:,:2].norm(dim=-1)*s.contact
    def snapshot(self):
        return dict(physics_event_ticks=self.event_ticks,physics_strict_ticks=self.strict_ticks,
            physics_contact_switches=self.switches,physics_support_n=self.support_n,
            physics_slip_sum=self.slip_sum)

def physical_events(b):
    if not hasattr(b,'_v61_physical_events'):b._v61_physical_events=PhysicalEvents(b)
    return b._v61_physical_events
