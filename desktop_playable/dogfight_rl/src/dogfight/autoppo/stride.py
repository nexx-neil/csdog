"""V6.3 physical kernel with fixed landing window and auditable rejection events.

Acceptance constants remain 40ms support, 15mm/60ms strict air, 20mm placement,
60ms landing, <=80N impact, <=0.08m/s slip and >=2 supports throughout flight.
Reward rates still integrate once through Isaac Lab's RewardManager.
"""
import torch
from ..locomotion.curriculum_v6_3.stride import Stride as LegacyStride
from ..locomotion.curriculum_v6_3.stride import Observer as LegacyObserver
from .gait_audit import REASONS

PROTOCOL = 'autoppo-500hz-fixed-landing-v2'

class Stride(LegacyStride):
    def __init__(self,n,device='cpu'):
        super().__init__(n,device)
        shape=(n,4)
        self.previous_flight=torch.zeros(shape,device=device)
        self.candidate_active=torch.zeros(shape,device=device,dtype=torch.bool)
        self.flight_armed=torch.zeros_like(self.candidate_active)
        self.flight_support_failure=torch.zeros_like(self.candidate_active)
        self.flight_shin_failure=torch.zeros_like(self.candidate_active)
        self.flight_peak_clearance=torch.zeros(shape,device=device)
        self.landing_pending=torch.zeros_like(self.candidate_active)
        self.candidate_count=torch.zeros(shape,device=device)
        self.rejected_count=torch.zeros(shape,device=device)
        self.reason_count=torch.zeros((*shape,len(REASONS)),device=device)
        self.latest_reasons=torch.zeros(shape,device=device,dtype=torch.int16)
        self.latest_candidates=torch.zeros(shape,device=device,dtype=torch.bool)
        self.latest_cycles=torch.zeros(shape,device=device,dtype=torch.bool)
    def begin_control(self):
        super().begin_control()
        for k in ['candidate_count','rejected_count','reason_count']:getattr(self,k).zero_()
    def reject(self,mask,reasons):
        mask=mask&self.candidate_active
        self.rejected_count+=mask
        for name,value in reasons.items():
            self.reason_count[:,:,REASONS.index(name)]+=mask&value
            self.latest_reasons|=(mask&value).to(torch.int16)*(1<<REASONS.index(name))
        missing=mask&(self.latest_reasons==0)
        self.reason_count[:,:,REASONS.index('OTHER')]+=missing
        self.latest_reasons|=missing.to(torch.int16)*(1<<REASONS.index('OTHER'))
        self.candidate_active&=~mask
        self.landing_pending&=~mask
    def update(self,dt,contact,clearance,raw_force,shin,x,slip,command,body_v,tilt,force,reset):
        # Do not let reset generate a synthetic touchdown or clear a different
        # environment's candidate. Report an in-progress reset before clearing.
        self.latest_reasons.zero_();self.latest_cycles.zero_()
        resetting=self.candidate_active&reset[:,None]
        self.reset(reset)
        # Arm from the completed previous support interval before processing
        # its falling edge. V6.3 accidentally required an extra physical tick.
        self.armed|=self.previous&(self.stance>=.04-1e-6)
        lift=(~contact)&self.previous
        land=contact&~self.previous
        armed=self.armed|((contact&~shin)&(self.stance>=.04-1e-6))
        self.candidate_active|=lift
        self.flight_armed=torch.where(lift,armed,self.flight_armed)
        self.landing_pending&=~lift
        self.candidate_count+=lift
        self.latest_candidates=lift.clone()
        old_pending=self.pending.clone()
        active_before=self.candidate_active.clone()
        old_flight=self.flight.clone()
        old_maxair=self.max_air.clone()
        inflight=self.candidate_active&~self.landing_pending
        self.flight_support_failure=torch.where(lift,False,self.flight_support_failure)
        self.flight_shin_failure=torch.where(lift,False,self.flight_shin_failure)
        self.flight_peak_clearance=torch.where(lift,0.,self.flight_peak_clearance)
        self.flight_support_failure|=inflight&~contact&((contact&~shin).sum(-1)<2)[:,None]
        self.flight_shin_failure|=inflight&shin
        self.flight_peak_clearance=torch.where(inflight,torch.maximum(self.flight_peak_clearance,clearance),self.flight_peak_clearance)
        excursion=(x-self.origin)*command[:,None].sign()
        support=contact&~shin
        supports=support.sum(-1)
        progress=(body_v*command.sign()/command.abs().clamp_min(.04)).clamp(0,1)
        quality=(command.abs()>.04)&(progress>.25)&(tilt<.35)
        reason={
            'INSUFFICIENT_SUPPORT': self.flight_support_failure|((supports<2)[:,None].expand_as(contact)),
            'INSUFFICIENT_SWING_HEIGHT': self.flight_peak_clearance<=.015,
            'SWING_DURATION_TOO_SHORT': old_maxair<.06-1e-6,
            'NO_FORWARD_FOOT_DISPLACEMENT': excursion<=.02,
            'INVALID_TOUCHDOWN': ~self.flight_armed|(old_flight>.6+1e-6)|(force>=80)|~quality[:,None],
            'SHANK_GROUND_CONTACT': self.flight_shin_failure,
        }
        old_cycles=self.stride_count.clone()
        super().update(dt,contact,clearance,raw_force,shin,x,slip,command,body_v,tilt,force,torch.zeros_like(reset))
        # Legacy code can revive a bad landing after later slip dilution. Freeze
        # the decision at the first complete 60ms window; no later revival.
        due=self.pending&(self.stance>=.06-1e-6)&active_before
        bad_slip=due&(self.slip_integral/self.stance_time.clamp_min(dt)>.08)
        self.reject(bad_slip,{'EXCESSIVE_STANCE_SLIP':bad_slip})
        bad_quality=due&~quality[:,None]
        self.reject(bad_quality,{'INVALID_TOUCHDOWN':bad_quality})
        self.pending&=~(bad_slip|bad_quality)
        aborted=old_pending&~support&active_before&~land
        self.reject(aborted,{'CONTACT_CHATTER':aborted,'INVALID_TOUCHDOWN':aborted,'SHANK_GROUND_CONTACT':shin})
        invalid_land=land&active_before&~self.pending&~bad_slip
        self.reject(invalid_land,reason)
        self.landing_pending|=land&self.pending&self.candidate_active
        timeout=(self.flight>.6+1e-6)&self.candidate_active&~self.landing_pending
        self.reject(timeout,{'INVALID_TOUCHDOWN':timeout,'SWING_DURATION_TOO_SHORT':self.max_air<.06-1e-6,
                             'INSUFFICIENT_SUPPORT':~self.valid_flight,'SHANK_GROUND_CONTACT':shin})
        completed=self.counted&self.candidate_active&self.landing_pending
        self.candidate_active&=~completed
        self.landing_pending&=~completed
        self.latest_cycles=self.stride_count>old_cycles
        self.rejected_count+=resetting
        self.reason_count[:,:,REASONS.index('STATE_MACHINE_RESET')]+=resetting
        self.latest_reasons|=resetting.to(torch.int16)*(1<<REASONS.index('STATE_MACHINE_RESET'))

class Observer(LegacyObserver):
    def __init__(self,b):
        super().__init__(b)
        self.state=Stride(b.num_envs,b.device)
        self.record_events=False;self.events=[]
    def update(self,dt):
        self.original(dt)
        with torch.no_grad():
            from isaaclab.utils.math import quat_apply_inverse
            b=self.b;s=self.physical.raw;r=b.scene['robot']
            cmd=b.command_manager.get_command('base_velocity')
            turn=(cmd[:,0].abs()<=.04)&(cmd[:,2].abs()>.04)
            c=torch.where(turn,cmd[:,2],cmd[:,0])
            if self.key!=b.common_step_counter:self.begin_control()
            relative=quat_apply_inverse(r.data.root_quat_w[:,None,:].expand(-1,4,-1),s.tip_position-r.data.root_pos_w[:,None,:])
            if not hasattr(self,'turn_mode'):
                self.turn_mode=torch.zeros_like(turn)
                self.tangent=torch.zeros_like(relative[:,:,:2])
            reset=(b.episode_length_buf<=1)|(self.sign!=c.sign())|(self.turn_mode!=turn)
            self.sign=c.sign().clone();self.turn_mode=turn.clone()
            # Fixed body-frame tangents at the command/reset boundary. Using
            # instantaneous radial tangents would dot to zero identically.
            radial=relative[:,:,:2]
            tangent=torch.stack((-radial[:,:,1],radial[:,:,0]),-1)/radial.norm(dim=-1,keepdim=True).clamp_min(.05)
            self.tangent=torch.where(reset[:,None,None],tangent,self.tangent)
            placement=torch.where(turn[:,None],(radial*self.tangent).sum(-1),relative[:,:,0])
            velocity=torch.where(turn,r.data.root_ang_vel_b[:,2],r.data.root_lin_vel_b[:,0])
            self.state.update(dt,s.contact,s.clearance,s.raw_force,s.shin,placement,s.velocity[:,:,:2].norm(dim=-1),c,velocity,r.data.projected_gravity_b[:,:2].norm(dim=-1),s.force,reset)
            if self.record_events:
                self.events.append(torch.stack((self.state.latest_candidates.to(torch.int16),self.state.latest_reasons,self.state.latest_cycles.to(torch.int16)),-1).clone())
    def snapshot(self):
        return dict(super().snapshot(),candidate_count=self.state.candidate_count,
                    rejected_count=self.state.rejected_count,reason_count=self.state.reason_count)

def observe(b):
    if not hasattr(b,'_autoppo_stride'):b._autoppo_stride=Observer(b)
    return b._autoppo_stride
