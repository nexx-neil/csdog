"""Tests operate on the production physical kernel, including the installed dt code."""
import torch
from dogfight.autoppo.stride import Stride
from dogfight.autoppo.gait_audit import REASONS
from test_curriculum_v6_3 import test_real_reward_manager_compute

def run(mode='good',dt=.002,control=.02,kernel=Stride,leg=0,stance_s=.08):
    s=kernel(1);counts=torch.zeros(4);rejected=torch.zeros(4,len(REASONS));credit=0
    for k in range(round(.8/dt)):
        t=k*dt;start=stance_s;end=start+.12;c=torch.ones(1,4,dtype=torch.bool);h=torch.zeros(1,4);x=torch.zeros(1,4)
        if start<=t<end:c[:,leg]=False;h[:,leg]=.025;x[:,leg]=min(.05,(t-start)/.12*.05)
        if t>=end:x[:,leg]=.05
        if mode=='all_air' and start<=t<start+.1:c[:]=False;h[:]=.025
        if mode=='chatter':c[:,leg]=k%2==0;h[:,leg]=.025;x[:,leg]=.05*(k%2)
        if mode=='held' and t>=start:c[:,leg]=False;h[:,leg]=.025;x[:,leg]=.05
        if mode=='wrong':x=-x
        if mode=='no_displacement':x.zero_()
        v=torch.tensor([0. if mode=='stationary' else .18])
        slip=torch.full((1,4),.02)
        if mode=='slip_dilution' and end<=t<end+.07:slip[:,leg]=.2
        if k%round(control/dt)==0:s.begin_control()
        reset=torch.tensor([mode=='reset' and abs(t-(start+.07))<dt/2])
        s.update(dt,c,h,c.float()*20,torch.zeros_like(c),x,slip,torch.tensor([.18]),v,torch.zeros(1),c.float()*20,reset)
        if (k+1)%round(control/dt)==0:
            counts+=s.stride_count[0]
            if hasattr(s,'reason_count'):rejected+=s.reason_count[0]
            credit+=(s.guide+s.stride_credit+s.touchdown_credit+s.stable_credit).mean().item()
    return counts,rejected,credit

def test_good_once():
    counts,rejected,credit=run();assert counts.tolist()==[1,0,0,0];assert rejected.sum()==0;assert credit>0

def test_no_late_slip_dilution():
    counts,rejected,_=run('slip_dilution');assert counts.sum()==0
    assert rejected[0,REASONS.index('EXCESSIVE_STANCE_SLIP')]==1

def test_time_invariance():
    a=[run(dt=d,control=c) for d,c in [(.001,.02),(.002,.02),(.004,.02),(.002,.04)]]
    assert all(x[0].sum()==1 for x in a)
    assert max(x[2] for x in a)-min(x[2] for x in a)<.002

def test_rejections_and_anti_exploit():
    for mode,reason in [('all_air','INSUFFICIENT_SUPPORT'),('wrong','NO_FORWARD_FOOT_DISPLACEMENT'),
                        ('no_displacement','NO_FORWARD_FOOT_DISPLACEMENT'),('held','INVALID_TOUCHDOWN'),
                        ('chatter','SWING_DURATION_TOO_SHORT'),('reset','STATE_MACHINE_RESET')]:
        count,rejected,credit=run(mode);assert count.sum()==0,mode
        assert rejected[:,REASONS.index(reason)].sum()>0,mode
    assert run('stationary')[0].sum()==0


def test_same_trace_old_bug_new_fix():
    from dogfight.locomotion.curriculum_v6_3.stride import Stride as Old
    assert run('slip_dilution',kernel=Old)[0].sum()==1
    assert run('slip_dilution')[0].sum()==0


def test_actual_new_event_rate_and_slip_integral():
    from types import SimpleNamespace
    from dogfight.autoppo import rewards
    for dt in [.01,.02,.04]:
        s=Stride(1);s.stride_credit[0,0]=.12;s.slip_cost[:]=dt*torch.log1p(torch.tensor(.16/.08))
        env=SimpleNamespace(step_dt=dt,_autoppo_stride=SimpleNamespace(state=s))
        assert abs(float(rewards.gait(env,2)*dt)-.03)<1e-6
        assert abs(float(rewards.support_slip(env)*dt)-float(s.slip_cost.mean()))<1e-6
        s.begin_control();assert float(rewards.gait(env,2))==0


def test_each_leg_independent():
    for leg in range(4):
        counts,rejections,_=run(leg=leg)
        assert counts[leg]==1 and counts.sum()==1
        assert rejections.sum()==0


def test_exact_40ms_support_edge_is_not_42ms():
    from dogfight.locomotion.curriculum_v6_3.stride import Stride as Old
    assert run(stance_s=.04,kernel=Old)[0].sum()==0
    assert run(stance_s=.04)[0].sum()==1
