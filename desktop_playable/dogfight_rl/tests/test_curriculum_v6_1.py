import copy,json
from pathlib import Path
import pytest
from dogfight.locomotion.curriculum_v6_1.supervisor import Supervisor,score,protocol,SEEDS,SCORE_VERSION,assess
from test_curriculum_v6 import summary

@pytest.fixture
def options():
    o=json.loads((Path(__file__).parents[1]/'configs/locomotion/curriculum_v6/default.json').read_text())
    o['contact_validated']=True;o['weights']['gait_guide']=.3
    return o

def panel(**kw):
    s=summary(**kw)
    for r in s['rows']:r['velocity']=[r['speed_xy'],0.,0.]
    s.update(full=True,seeds=SEEDS,seconds=12,contact_version='v6-raw');return s

def test_continuous_slip_and_no_stationary_exploit(options):
    t=options['thresholds']
    assert score(panel(slip=.15),0,t)-score(panel(slip=.3),0,t)>.08
    assert score(panel(ratio=0,gait=0,slip=0),0,t)<score(panel(ratio=1,gait=0,slip=.3),0,t)
    assert score(panel(ratio=-1,slip=0),0,t)<score(panel(ratio=1,slip=.3),0,t)
    assert not all(assess(panel(slip=.081),0,t).values())

def test_candidate_control_and_rejection_ranked(tmp_path,options):
    s=Supervisor(tmp_path,options);s.observe(panel(gait=0,slip=.3),'anchor')
    s.state['candidate']=dict(arm='control',evaluation_seeds=SEEDS,protocol=protocol(panel()),anchor='anchor',anchor_score=s.state['best_score'],start_update=0,diagnosis='SLIDING_REWARD_EXPLOIT',before={k:copy.deepcopy(s.state[k]) for k in ['weights','ppo','distribution','speed_range','substage']})
    s.state['total_updates']=500
    assert s.observe(panel(gait=0,slip=.15),'control')['action']=='candidate_adjust'
    assert s.state['best_checkpoint']=='control'
    s.state['total_updates']=1000
    result=s.observe(panel(gait=0,slip=.2),'adjusted')
    assert result['action']=='rollback' and result['checkpoint']=='control'
    assert s.state['best_checkpoint']=='control'
    assert len(s.state['rankings'])==3

def test_incomparable_candidate_fails(tmp_path,options):
    s=Supervisor(tmp_path,options);s.state['candidate']=dict(protocol=protocol(panel()))
    bad=panel();bad['seeds']=[1]
    with pytest.raises(RuntimeError,match='PROTOCOL'):s.observe(bad,'bad')

def test_failed_swing_not_repeated(tmp_path,options):
    s=Supervisor(tmp_path,options);s.state['candidate']={}
    old=s.state['weights']['swing']
    assert s.adjust('SLIDING_REWARD_EXPLOIT',panel(gait=0))=='continuous_swing:1.5'
    assert s.state['weights']['swing']==old
    s.state['failed_factors'].append('continuous_swing:1.5')
    before=copy.deepcopy(s.state['weights'])
    with pytest.raises(RuntimeError,match='REPEAT'):s.adjust('SLIDING_REWARD_EXPLOIT',panel(gait=0))
    assert s.state['weights']==before

def test_version_reset_preserves_legacy(tmp_path,options):
    s=Supervisor(tmp_path,options,dict(stage=0,best_checkpoint='old',best_score=99,best_summary=None,history=[]))
    assert s.state['best_score']==-1e6 and s.state['legacy_best']['best_checkpoint']=='old'

def test_rank_pointer_after_stage_switch(tmp_path,options):
    s=Supervisor(tmp_path,options)
    for i in range(3):result=s.observe(panel(),str(i))
    assert result['action']=='advance'
    entries=s.state['rankings'];winner=max(entries,key=lambda x:score(x['summary'],1,options['thresholds']))
    assert s.state['best_checkpoint']==winner['checkpoint']

def test_guidance_rejects_hover_shin_and_standing():
    import torch
    from dogfight.locomotion.curriculum_v6_1.rewards import guidance
    shape=(1,4);height=torch.full(shape,.03);zero=torch.zeros(shape);shin=torch.zeros(shape,dtype=torch.bool)
    contact=torch.tensor([[True,False,False,True]]);air=torch.full(shape,.1);travel=torch.full(shape,.05);velocity=torch.full(shape,.2)
    def calc(**kw):
        args=dict(clearance=height,raw_force=zero,shin=shin,contact=contact,air=air,excursion=travel,relative_v=velocity,progress=torch.ones(1));args.update(kw);return guidance(**args)
    assert calc().item()>0
    assert calc(progress=torch.zeros(1)).item()==0
    assert calc(contact=torch.zeros_like(contact)).item()==0
    assert calc(excursion=zero).item()==0
    assert calc(shin=torch.ones_like(shin)).item()==0
    assert calc(raw_force=torch.full(shape,2.)).item()==0
    assert calc(air=torch.full(shape,.02)).item()==0
    assert calc(air=torch.full(shape,.04)).item()==0

def test_separate_protocol_cannot_replace_best(tmp_path,options):
    s=Supervisor(tmp_path,options);s.register(panel(slip=.2),'verified')
    different=panel(slip=0);different['seeds']=[1]
    assert not s.register(different,'different_panel')
    assert s.state['best_checkpoint']=='verified'
    assert len(s.state['rankings'])==2

def test_stop_gate_uses_norm_and_absolute_yaw(options):
    p=panel();p['rows'][0].update(speed_xy=.04,yaw=0.,yaw_abs=0.)
    assert not assess(p,0,options['thresholds'])['stop']
    p['rows'][0].update(speed_xy=0.,yaw=-.09,yaw_abs=.09)
    assert not assess(p,0,options['thresholds'])['stop']

def test_gait_regression_cannot_overwrite_verified_pointer(tmp_path,options):
    s=Supervisor(tmp_path,options);p=panel();s.register(p,'walking')
    bad=panel(gait=0,slip=0)
    s.register(bad,'lost_gait')
    assert s.state['best_checkpoint']=='walking'
    ranking=json.loads((tmp_path/'ranking.json').read_text())
    assert ranking['entries'][0]['checkpoint']=='walking'
    assert not ranking['entries'][1]['continuation_safe']

def test_accepted_candidate_registers_and_keeps_parameters(tmp_path,options):
    s=Supervisor(tmp_path,options);s.observe(panel(gait=0,slip=.3),'anchor')
    before={k:copy.deepcopy(s.state[k]) for k in ['weights','ppo','distribution','speed_range','substage']}
    s.state['candidate']=dict(arm='control',protocol=protocol(panel()),anchor='anchor',start_update=0,diagnosis='SLIDING_REWARD_EXPLOIT',before=before)
    s.state['total_updates']=500;s.observe(panel(gait=0,slip=.2),'control')
    s.adjust('SLIDING_REWARD_EXPLOIT',panel(gait=0))
    s.state['total_updates']=1000;s.observe(panel(gait=4,slip=.1),'adjusted')
    assert s.state['best_checkpoint']=='adjusted'
    assert s.state['attempts'][-1]['accepted']
    assert s.state['weights']['gait_guide']==pytest.approx(.45)

def test_invalid_full_data_does_not_rank(tmp_path,options):
    s=Supervisor(tmp_path,options);s.register(panel(),'valid')
    bad=panel();bad['rows'][1]['valid']=False
    assert not s.register(bad,'invalid')
    assert s.state['best_checkpoint']=='valid'

def test_raw_substeps_prevent_policy_aliasing():
    import torch
    from dogfight.locomotion.curriculum_v6_1.events import advance_air_ticks
    raw=torch.ones(120,dtype=torch.bool);raw[5::30]=False
    assert raw[9::10].all()  # Policy samples would incorrectly report continuous air.
    count=torch.zeros(1,dtype=torch.long);qualified=0
    for strict in raw:
        count,ended=advance_air_ticks(count,strict)
        qualified+=int((ended>=30).sum())
    assert qualified==0 and count.item()<30
    count=torch.zeros(1,dtype=torch.long)
    for _ in range(30):count,_=advance_air_ticks(count,torch.tensor([True]))
    count,ended=advance_air_ticks(count,torch.tensor([False]))
    assert ended.item()==30 and count.item()==0

def test_partial_gait_loss_is_not_hidden_by_already_failed_speed_case():
    from dogfight.locomotion.curriculum_v6_1.supervisor import motion_safe
    reference=panel();reference['rows'].append(copy.deepcopy(reference['rows'][1]))
    reference['rows'][-1]['gait_trial_fraction']=0.
    current=copy.deepcopy(reference);current['rows'][1]['gait_trial_fraction']=0.
    assert not motion_safe(current,reference)

def test_contact_diagnostics_select_forward_not_last_backward_case():
    from dogfight.locomotion.curriculum_v6_1.events import diagnostic_indices
    cases=[('stop',[(0,0)]),('forward',[(.18,0)])]+[('unused',[(0,0)])]*12+[('forward',[(.25,0)]),('backward',[(-.25,0)])]
    assert diagnostic_indices(256,cases)==[0,1,2,3,16,17,18,19,224,225,226,227]

def test_completed_landing_requires_directional_foot_excursion():
    import torch
    from dogfight.locomotion.curriculum_v6_1.rewards import landing_motion_gate
    landed=torch.ones(1,4,dtype=torch.bool);progress=torch.ones(1);moving=torch.ones(1,dtype=torch.bool)
    assert landing_motion_gate(landed,torch.zeros(1,4),progress,moving).item()==0
    assert landing_motion_gate(landed,torch.full((1,4),-.03),progress,moving).item()==0
    assert landing_motion_gate(landed,torch.full((1,4),.03),progress,moving).item()==1
    assert landing_motion_gate(landed,torch.full((1,4),.03),torch.zeros(1),moving).item()==0
