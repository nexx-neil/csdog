"""Pure tensor physical-time state machine. One flight, one touchdown, one stride.

No contact filtering: any contact interrupts strict air; any unload interrupts
stable support. Reward credit is an integral, never a physical-tick event rate.
"""
import torch

class Stride:
    def __init__(self,n,device='cpu'):
        shape=(n,4)
        for k in ['stance','air','max_air','flight','peak','origin','last_x','slip_integral','stance_time','guide','touchdown_credit','stride_credit','stable_credit','slip_cost','strict_time','stable_time','lift_count','swing_count','touchdown_count','stride_count']:
            setattr(self,k,torch.zeros(shape,device=device))
        for k in ['previous','armed','flying','pending','counted','valid_flight']:
            setattr(self,k,torch.zeros(shape,device=device,dtype=torch.bool))
    def reset(self,mask):
        for key,v in list(vars(self).items()):
            if torch.is_tensor(v):
                # Evaluation executes the whole rollout under inference_mode and
                # may rebind recurrence buffers to inference tensors. Clone them
                # back to ordinary mutable storage before a training/reset write.
                if torch.is_inference(v):
                    v=v.clone();setattr(self,key,v)
                v[mask]=0

    def normalize_storage(self):
        for key,v in list(vars(self).items()):
            if torch.is_tensor(v) and torch.is_inference(v):setattr(self,key,v.clone())
    def begin_control(self):
        for k in ['guide','touchdown_credit','stride_credit','stable_credit','slip_cost','strict_time','stable_time','lift_count','swing_count','touchdown_count','stride_count']:
            getattr(self,k).zero_()
    def update(self,dt,contact,clearance,raw_force,shin,x,slip,command,body_v,tilt,force,reset):
        self.reset(reset)
        moving=command.abs()>.04
        progress=(body_v*command.sign()/command.abs().clamp_min(.04)).clamp(0,1)
        quality=moving&(progress>.25)&(tilt<.35)
        support=contact&~shin
        strict=(~contact)&(clearance>.015)&(raw_force<1)&~shin
        real=(~contact)&(clearance>.004)&(raw_force<1)&~shin
        lift=(~contact)&self.previous
        land=contact&(~self.previous)
        self.armed|=support&(self.stance>=.04-1e-6)
        self.origin=torch.where(lift,x,self.origin)
        self.flying=torch.where(lift,self.armed,self.flying)
        self.lift_count+=lift.float()
        self.valid_flight=torch.where(lift,True,self.valid_flight)&~shin
        self.valid_flight&=contact|(support.sum(-1)>=2)[:,None]
        self.peak=torch.where(lift,0.,self.peak)
        self.air=torch.where(strict,self.air+dt,0.)
        self.max_air=torch.where(lift,0.,self.max_air)
        self.max_air=torch.maximum(self.max_air,self.air)
        self.flight=torch.where(~contact,self.flight+dt,0.)
        excursion=(x-self.origin)*command[:,None].sign()
        newpeak=torch.maximum(self.peak,excursion.clamp(0,.06))
        incremental=(newpeak-self.peak).clamp_min(0)/.06
        supports=support.sum(-1)
        safe=quality&(supports>=2)&(supports<=3)
        height=((clearance-.004)/.011).clamp(0,1)
        self.guide+=.04*incremental*height*real*self.flying*(self.flight<=.6)*safe[:,None]
        self.peak=newpeak
        # The previous flight length must be read before landing resets it.
        elapsed_flight=torch.where(land,self.previous_flight,self.flight) if hasattr(self,'previous_flight') else self.flight
        valid=land&self.flying&self.valid_flight&(self.max_air>=.06-1e-6)&(elapsed_flight<=.6+1e-6)&(excursion>.02)&(force<80)&~shin&(quality&(supports>=2))[:,None]
        self.swing_count+=(land&self.flying&(self.max_air>=.06-1e-6)).float()
        self.touchdown_count+=valid.float()
        self.touchdown_credit+=.02*valid*progress[:,None]
        self.pending=torch.where(land,valid,self.pending)&support
        self.counted=torch.where(land,False,self.counted)
        self.stance=torch.where(support,self.stance+dt,0.)
        self.stance_time=torch.where(support,self.stance_time+dt,0.)
        self.slip_integral=torch.where(support,self.slip_integral+slip*dt,0.)
        mean_slip=self.slip_integral/self.stance_time.clamp_min(dt)
        stable=self.pending&(self.stance>=.06-1e-6)&(mean_slip<=.08)&quality[:,None]
        cycle=stable&~self.counted
        self.stride_count+=cycle.float();self.stride_credit+=.12*cycle*progress[:,None]
        self.counted|=cycle
        # Quality guidance is limited to the first 0.3s after a valid landing.
        self.stable_credit+=.3*dt*self.pending*(self.stance<=.3)*torch.exp(-slip/.08)*progress[:,None]
        self.stable_time+=dt*stable
        self.strict_time+=dt*strict
        self.slip_cost+=dt*torch.log1p(slip/.08)*support
        self.armed=torch.where(land,False,self.armed)
        self.flying&=~contact
        self.previous=contact.clone();self.previous_flight=self.flight.clone();self.last_x=x.clone()

class Observer:
    def __init__(self,b):
        from ..curriculum_v6_1.contacts import physical_events
        self.b=b;self.physical=physical_events(b);self.original=b.scene.update
        self.state=Stride(b.num_envs,b.device);self.key=None;self.sign=torch.zeros(b.num_envs,device=b.device)
        b.scene.update=self.update
    def begin_control(self):self.state.begin_control();self.key=self.b.common_step_counter
    def update(self,dt):
        self.original(dt)
        # Environment construction may lazily allocate Isaac Lab state caches.
        # no_grad keeps those tensors mutable for subsequent reset; inference_mode
        # would mark a first-access cache as an immutable inference tensor.
        with torch.no_grad():
            from isaaclab.utils.math import quat_apply_inverse
            b=self.b;s=self.physical.raw;r=b.scene['robot'];c=b.command_manager.get_command('base_velocity')[:,0]
            if self.key!=b.common_step_counter:self.begin_control()
            relative=quat_apply_inverse(r.data.root_quat_w[:,None,:].expand(-1,4,-1),s.tip_position-r.data.root_pos_w[:,None,:])[:,:,0]
            reset=(b.episode_length_buf<=1)|(self.sign!=c.sign());self.sign=c.sign().clone()
            self.state.update(dt,s.contact,s.clearance,s.raw_force,s.shin,relative,s.velocity[:,:,:2].norm(dim=-1),c,r.data.root_lin_vel_b[:,0],r.data.projected_gravity_b[:,:2].norm(dim=-1),s.force,reset)
    def snapshot(self):
        return {k:getattr(self.state,k) for k in ['lift_count','swing_count','touchdown_count','stride_count','strict_time','stable_time']}

def observe(b):
    if not hasattr(b,'_v63_stride'):b._v63_stride=Observer(b)
    return b._v63_stride
