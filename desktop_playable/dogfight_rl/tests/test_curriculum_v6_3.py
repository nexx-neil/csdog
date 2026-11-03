"""Timing and adversarial traces for the exact production stride kernel."""
import ast,types
from pathlib import Path
import torch
import pytest
from dogfight.locomotion.curriculum_v6_3.stride import Stride

def trace(mode='good',dt=.002,control=.02,cycles=1):
    s=Stride(1);total=0.;events=0.;touch=0.;rates=[]
    # Three other legs remain loaded; tested leg supports, unloads, moves and lands.
    per=round(.4/dt)
    for k in range(per*cycles):
        t=(k%per)*dt
        c=torch.ones(1,4,dtype=torch.bool);h=torch.zeros(1,4);x=torch.zeros(1,4)
        flight=.08<=t<.2
        if flight:
            c[:,0]=False;h[:,0]=.025;x[:,0]=min(.05,(t-.08)/.12*.05)
        elif t>=.2:x[:,0]=.05
        if mode=='chatter':c[:,0]=k%2==0;h[:,0]=.025;x[:,0]=.05*(k%2)
        if mode=='held' and t>=.08:c[:,0]=False;h[:,0]=.025;x[:,0]=.05
        if mode=='slide':c[:]=True;h.zero_();x.zero_()
        if mode=='wrong':x=-x
        if mode=='short':c[:,0]=not (.08<=t<.1);h[:,0]=.025;x[:,0]=.05 if t>=.1 else 0.
        if mode=='all_air' and flight:c[:]=False;h[:]=.025
        if mode=='shin':shin=~c
        else:shin=torch.zeros_like(c)
        v=torch.tensor([0. if mode=='no_body' else .18]);command=torch.tensor([0. if mode=='stop' else .18])
        slip=torch.full((1,4),.25 if mode in ['sliding_landing','slide'] else .02)
        if k%round(control/dt)==0:s.begin_control()
        s.update(dt,c,h,c.float()*20,shin,x,slip,command,v,torch.zeros(1),c.float()*20,torch.tensor([False]))
        if (k+1)%round(control/dt)==0:
            credit=(s.guide+s.touchdown_credit+s.stride_credit+s.stable_credit).mean().item()
            total+=credit;events+=s.stride_count.sum().item();touch+=s.touchdown_count.sum().item();rates.append(credit/control)
    return total,events,touch,rates

def test_valid_sequence_one_payment():
    reward,count,td,_=trace();assert count==1 and td==1 and .03<reward<.07

def test_substep_invariance():
    results=[trace(dt=dt,control=control) for dt,control in [(.001,.02),(.002,.02),(.004,.02),(.002,.01),(.002,.04)]]
    assert all(r[1:3]==(1,1) for r in results)
    assert max(r[0] for r in results)-min(r[0] for r in results)<.002

@pytest.mark.parametrize('mode',['chatter','held','slide','wrong','short','all_air','shin','no_body','stop'])
def test_no_complete_exploit(mode):
    reward,count,td,_=trace(mode);assert count==0 and td==0
    assert reward<=.0101

def test_sliding_landing_cannot_complete():
    reward,count,td,_=trace('sliding_landing');assert count==0 and td==1

def test_real_reward_manager_compute():
    # Execute the installed method body unchanged, with only its storage fixture mocked.
    path=Path('/home/zxq/robot_projects/IsaacLab/source/isaaclab/isaaclab/managers/reward_manager.py')
    tree=ast.parse(path.read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='RewardManager')
    compute=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='compute')
    ns={'torch':torch};exec(compile(ast.Module(body=[compute],type_ignores=[]),str(path),'exec'),ns)
    for dt in [.01,.02,.04]:
        env=types.SimpleNamespace(credit=torch.tensor([.05]));cfg=types.SimpleNamespace(weight=1.,params={},func=lambda e:e.credit/dt)
        manager=types.SimpleNamespace(_env=env,_term_names=['event'],_term_cfgs=[cfg],_reward_buf=torch.zeros(1),_step_reward=torch.zeros(1,1),_episode_sums={'event':torch.zeros(1)})
        assert ns['compute'](manager,dt).item()==pytest.approx(.05)
        env.credit.zero_();assert ns['compute'](manager,dt).item()==0
        # Continuous rate 2/s integrates once, with no extra dt.
        cfg.func=lambda e:torch.tensor([2.]);assert ns['compute'](manager,dt).item()==pytest.approx(2*dt)
