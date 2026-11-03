import math
import torch
from dogfight.locomotion.phase_guided_v7.kernel import Clock,schedule,terms,weighted

def rollout(case):
    phase=torch.linspace(0,8*math.pi,800);n=len(phase)
    cmd=torch.zeros(n,3);cmd[:,0]=.2
    vel=cmd.clone();yaw=torch.zeros(n);stance=schedule(phase)>.5
    contact=stance.clone();height=(~contact)*.025;shin=torch.zeros_like(contact);slip=torch.zeros(n,4)
    if case=='ground':contact[:]=True;height[:]=0;slip[:]=.2
    if case=='in_place':vel[:]=0
    if case=='two_frozen':contact[:]=torch.tensor([0,1,1,0],dtype=torch.bool);height=(~contact)*.025
    if case=='all_air':contact[:]=False;height[:]=.025
    if case in ('hanging','hanging_target'):contact[:,0]=False;height[:,0]=.025 if case=='hanging_target' else .10
    if case=='chatter':contact=contact^(torch.arange(n)[:,None]%2==0);height[:]=.0005
    if case=='shin':shin[:]=True;contact[:]=True;height[:]=0
    if case=='wrong':vel[:,0]=-.2
    if case=='spin':vel[:]=0;yaw[:]=.4
    if case=='stop_steps':cmd[:]=0;slip[:]=.25;vel[:]=0
    air=torch.zeros(n,4)
    for i in range(1,n):air[i]=torch.where(contact[i],0.,air[i-1]+4/(799*1.5))
    v=terms(phase,cmd,vel,yaw,contact,height,shin,slip,air_time=air)
    return weighted(v).mean().item(),v

def test_exploit_ranking():
    ideal,_=rollout('ideal')
    for case in ['ground','in_place','two_frozen','all_air','hanging','hanging_target','chatter','shin','wrong','spin','stop_steps']:
        value,v=rollout(case)
        assert value<ideal*.8,(case,value,ideal)
        assert all(torch.isfinite(x).all() for x in v.values())

def test_gradual_height_and_no_stance_payment():
    n=20;p=torch.full((n,),math.pi/2);c=torch.tensor([[.2,0,0.]]).repeat(n,1);ct=schedule(p)>.5
    h=torch.linspace(.001,.025,n)[:,None].expand(-1,4)
    v=terms(p,c,c,torch.zeros(n),ct,h,torch.zeros_like(ct),torch.zeros(n,4))
    assert torch.all(torch.diff(v['height_progress'])>0)
    all_ground=terms(p,c,c,torch.zeros(n),torch.ones_like(ct),h,torch.zeros_like(ct),torch.zeros(n,4))
    assert all_ground['height_progress'].sum()==0

def test_clock_stop_restart_independent_reset_checkpoint():
    clock=Clock(3);command=torch.tensor([[.2,0,0],[0,0,0],[.2,0,0.]])
    for _ in range(20):clock.advance(.02,command,1.5)
    assert clock.phase[1]==0 and clock.phase[0]>0
    old=clock.phase.clone();clock.reset([0]);assert clock.phase[0]==0 and clock.phase[2]==old[2]
    saved=clock.state_dict();other=Clock(3);other.load_state_dict(saved)
    assert torch.equal(clock.observation(),other.observation())
    command.zero_();old=clock.phase.clone()
    for _ in range(30):clock.advance(.02,command,1.5)
    assert torch.equal(clock.phase,old)
    command[2,0]=.2;clock.advance(.02,command,1.5)
    assert 0<(clock.phase[2]-old[2])<2*math.pi*1.5*.02*.3

def test_diagonal_and_smooth_transition():
    p=torch.linspace(0,2*math.pi,101);s=schedule(p)
    assert torch.equal(s[:,0],s[:,3]) and torch.equal(s[:,1],s[:,2])
    assert torch.allclose(s.sum(-1),torch.full((101,),2.))
    assert schedule(torch.tensor([math.pi/2]))[0,1]>.99
    assert schedule(torch.tensor([3*math.pi/2]))[0,0]>.99

def test_slip_normalization_only_prices_real_support():
 p=torch.tensor([1.]);cmd=torch.tensor([[.2,0,0.]])
 ct=torch.tensor([[True,False,True,False]]);h=(~ct)*.025;bad=torch.zeros_like(ct)
 slip=torch.tensor([[.16,100.,.16,100.]])
 raw=terms(p,cmd,cmd,torch.zeros(1),ct,h,bad,slip)
 normalized=terms(p,cmd,cmd,torch.zeros(1),ct,h,bad,slip,{'slip_mode':'log'})
 assert torch.allclose(raw['slip'],torch.tensor([.16]))
 assert torch.allclose(normalized['slip'],torch.log1p(torch.tensor([2.])))
 for key in raw:
  if key!='slip':assert torch.equal(raw[key],normalized[key])
