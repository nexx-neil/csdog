"""Meaningful CPU contracts: signs, gate evidence, regression and finite repair budgets."""
import copy,json
from pathlib import Path
import pytest
import torch
from dogfight.locomotion.curriculum_v6.rewards import signed_progress,terms
from dogfight.locomotion.curriculum_v6.supervisor import Supervisor,assess,required,LEGS
ROOT=Path(__file__).resolve().parents[1]
@pytest.fixture
def options():return json.loads((ROOT/'configs/locomotion/curriculum_v6/default.json').read_text())

def summary(stage=0,ratio=.85,gait=4,fall=0.,slip=.01):
    rows=[]
    for name in required(stage):
        stop=name=='stop'
        rows.append(dict(test=name,is_stop=stop,valid=True,fall_rate=fall,speed_xy=0. if stop or name.startswith('yaw') else .18*ratio,yaw=.25 if name.startswith('yaw') else 0.,tilt=.01,lateral_speed=.005,support_slip_speed=slip,tracking_ratios=[] if stop else [ratio],pure_yaw=name.startswith('yaw'),periodic_legs=gait,gait_trial_fraction=1. if gait==4 else 0.,**{leg+'_swing_ratio':.15 if gait else 0. for leg in LEGS}))
    return dict(id='test',rows=rows,num_envs=256,ppo={'kl':.01})

def test_signed_progress():
    cmd=torch.tensor([.2,-.2,.2,-.2,0.,1e-9]);vel=torch.tensor([.1,-.1,-.1,.1,1.,1.])
    assert torch.allclose(signed_progress(cmd,vel),torch.tensor([.5,.5,-.5,-.5,0.,0.]))
    assert torch.isfinite(signed_progress(cmd,vel)).all()

def test_no_static_reward_on_nonzero_tasks():
    cmd=torch.tensor([[.18,0,0],[-.18,0,0],[0,0,.3],[0,0,-.3],[0,0,0]])
    rs=terms(cmd,torch.zeros(5,3),torch.zeros(5))
    assert all(torch.equal(r[:4],torch.zeros(4)) for r in rs)
    assert rs[3][4]==1.
    actual=torch.tensor([[.18,0,0],[-.18,0,0],[0,0,0],[0,0,0],[0,0,0]])
    correct=terms(cmd,actual,torch.tensor([0,0,.3,-.3,0]))
    wrong=terms(cmd,-actual,torch.tensor([0,0,-.3,.3,0]))
    assert (correct[0][:4]>wrong[0][:4]).all()

def test_gate_requires_consecutive_full_evidence(tmp_path,options):
    s=Supervisor(tmp_path,options);good=summary()
    for i in range(2):
        assert s.observe(good,f'c{i}')['action']!='advance'
    assert s.state['stage']==0
    s.observe(summary(ratio=.1),'fail')
    assert s.state['passes']==0
    for i in range(3):decision=s.observe(good,f'd{i}')
    assert decision['action']=='advance' and s.state['stage']==1

def test_no_sliding_or_one_direction_gate(options):
    assert not all(assess(summary(ratio=1.,gait=0,slip=.12),0,options['thresholds']).values())
    bad=summary(2);bad['rows'][-1]['tracking_ratios']=[-.8]
    assert not assess(bad,2,options['thresholds'])['yaw_negative']

def test_regression_preserves_rejected_evidence(tmp_path,options):
    s=Supervisor(tmp_path,options);s.observe(summary(),'good')
    result=s.observe(summary(ratio=.1),'rejected')
    assert result['action']=='rollback' and result['checkpoint']=='good'
    assert s.state['best_checkpoint']=='good'
    assert s.state['history'][-1]['rejected_checkpoint']=='rejected'

def test_finite_repair_and_equal_budget(tmp_path,options):
    options['monitor']['stagnant_windows']=2;options['monitor']['max_repairs']=1
    s=Supervisor(tmp_path,options);bad=summary(ratio=0.,gait=0)
    s.observe(bad,'anchor');s.observe(bad,'flat1');d=s.observe(bad,'flat2')
    assert d['action']=='candidate_control'
    s.state['total_updates']=499
    assert s.observe(bad,'not_yet')['action']=='continue'
    s.state['total_updates']=500
    assert s.observe(bad,'control')['action']=='candidate_adjust'
    s.state['total_updates']=1000
    assert s.observe(bad,'adjusted')['action']=='rollback'
    s.observe(bad,'flat3');d=s.observe(bad,'flat4')
    assert d['action']=='blocked' and s.state['training_status']=='BLOCKED_NEEDS_REDESIGN'

def test_supervisor_resume_preserves_history(tmp_path,options):
    s=Supervisor(tmp_path,options);s.observe(summary(ratio=0,gait=0),'a');s.event('TEST_EVENT')
    restored=Supervisor(tmp_path,options,json.loads(json.dumps(s.state)))
    assert restored.state==s.state

def test_light_never_promotes_and_stage_retains_anchor(tmp_path,options):
    s=Supervisor(tmp_path,options);good=summary();good['full']=False
    for _ in range(10):assert s.observe(good,'light')['action']=='continue'
    assert s.state['passes']==0 and s.state['full_windows']==0
    good['full']=True
    for i in range(3):s.observe(good,f'anchor{i}')
    assert s.state['stage']==1 and s.state['best_summary'] is not None
    assert s.state['best_checkpoint']=='anchor2'

def test_safe_repairs_change_one_factor_and_preserve_hardware(tmp_path,options):
    s=Supervisor(tmp_path,options);s.state['repairs']=1;before=copy.deepcopy(s.state)
    s.adjust('STANDING_LOCAL_OPTIMUM',summary())
    changed=[k for k in options['weights'] if s.state['weights'][k]!=before['weights'][k]]
    assert set(changed)=={'smoothness','posture','acceleration'}
    for k in ['limits','collision','termination','slip']:assert s.state['weights'][k]==before['weights'][k]
    s.adjust('PPO_UPDATE_TOO_LARGE',summary())
    assert s.state['ppo']['learning_rate']==5e-5
    s.adjust('SLIDING_REWARD_EXPLOIT',summary())
    assert s.state['weights']['swing']==.3
    bad=summary();bad['rows'][1]['tracking_ratios']=[-.5]
    s.adjust('WRONG_DIRECTION',bad)
    assert s.state['distribution']['forward']>.85
    assert sum(s.state['distribution'].values())==pytest.approx(1.)

def test_stop_cannot_hide_opposite_yaw_oscillation(options):
    s=summary();s['rows'][0]['yaw']=0.;s['rows'][0]['yaw_abs']=.3
    assert not assess(s,0,options['thresholds'])['stop']
