from dogfight.autoppo.phase_v7_search import V7Search,BOUNDS
from dogfight.locomotion.phase_guided_v7.kernel import DEFAULTS

def good():return dict(actual_speed=.2,fall_fraction=0.,stop_speed=.01,stop_yaw=.01,clearance_peak=[.025]*4,min_swing_per_env=8,support_slip=.03,phase_match=.85)
def test_targeted_search_bounds_and_one_change():
    m=good();m['support_slip']=.15
    assert V7Search.diagnose(m)=='SLIP'
    o,decision=V7Search.propose({},m,0)
    assert decision['key']=='slip_weight' and o['slip_weight']>DEFAULTS['slip_weight']
    assert [k for k in DEFAULTS if DEFAULTS[k]!=o[k]]==['slip_weight']
    for i in range(20):
        o,d=V7Search.propose({},m,i);assert BOUNDS[d['key']][0]<=d['after']<=BOUNDS[d['key']][1]
def test_diagnosis_is_physical_not_mean_reward():
    m=good();m['clearance_peak'][0]=0.
    assert V7Search.diagnose(m)=='NO_LIFT'
    m=good();m['actual_speed']=-.1;assert V7Search.diagnose(m)=='WRONG_DIRECTION'
    m=good();m['fall_fraction']=.3;assert V7Search.diagnose(m)=='FALLING'

def test_small_real_four_leg_motion_can_earn_bounded_continuation_only():
    from dogfight.autoppo.phase_v7_search import early_physical_trend
    baseline=dict(support_slip=.327)
    m=good();m.update(early_swing_q25=1,phase_match=.71,support_slip=.267,contact_duty=[.74,.81,.61,.68],shin_rate=0,qualified=False,min_swing_per_env=0)
    assert early_physical_trend(m,baseline)
    assert not m['qualified']  # formal 15mm/60ms/low-slip gate is untouched
    m['early_swing_q25']=0
    assert not early_physical_trend(m,baseline)

def test_new_direction_progress_affects_ranking_and_prior_skills_required():
    from dogfight.autoppo.phase_v7_search import prior_course_safe
    m=good();m['course']=1
    m['rows']=[dict(mode=mode,tracking_ratio=1.,min_swing_per_env=8,qualified=True) for mode in ['forward','stop','transition_stop']]
    m['rows'].append(dict(mode='backward',tracking_ratio=0.,min_swing_per_env=0,qualified=False))
    assert prior_course_safe(m,1)
    low=V7Search.score(m);m['rows'][-1]['tracking_ratio']=.6
    assert V7Search.score(m)>low
    m['rows'][0]['qualified']=False
    assert not prior_course_safe(m,1)
    assert not prior_course_safe({'rows':[]},1)

def test_overspeed_cannot_receive_the_same_ranking_as_correct_speed():
 m=good();best=V7Search.score(m)
 m['actual_speed']=.34
 assert V7Search.score(m)<best-2.
