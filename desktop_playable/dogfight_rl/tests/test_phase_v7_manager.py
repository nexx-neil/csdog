from dogfight.autoppo.phase_v7_manager import V7Manager
from dogfight.autoppo.storage import canonical

def metrics(speed=.2,swings=0):
 return dict(actual_speed=speed,fall_fraction=0.,stop_speed=.01,stop_yaw=.01,clearance_peak=[0.]*4,min_swing_per_env=swings,support_slip=.03,phase_match=.5)
def test_no_trend_never_enters_long_training(tmp_path):
 m=V7Manager(tmp_path)
 try:
  t=m.queue('C',1000,source='nonexistent_test_only.pt',rung=1,source_updates=250)
  m.store.db.execute("UPDATE trials SET status='COMPLETE',metrics=?,progress=1000 WHERE id=?",(canonical(metrics()),t))
  assert m.plan_long_candidate() is False
  assert m.store.get('status')=='BLOCKED_NO_SUSTAINED_TREND'
 finally:m.store.close()
def test_stagnation_stops_before_generating_more(tmp_path):
 m=V7Manager(tmp_path)
 try:
  m.store.set('stagnant_candidates',6)
  assert not m.plan_long_candidate()
  assert m.store.get('status')=='BLOCKED_NO_PROGRESS'
  assert not m.store.rows('SELECT id FROM trials')
 finally:m.store.close()

def test_frequency_diagnostic_is_four_equal_budgets_and_stops(tmp_path):
 m=V7Manager(tmp_path)
 try:
  q=metrics(swings=0);q.update(early_swing_q25=15,phase_match=.86,support_slip=.156,shin_rate=0,contact_duty=[.6]*4)
  t=m.queue('D',1000,source='test_only.pt',rung=1,source_updates=250)
  m.store.db.execute("UPDATE trials SET status='COMPLETE',metrics=?,checkpoint='donor_test_only.pt',progress=1000 WHERE id=?",(canonical(q),t))
  rows=m.store.rows('SELECT * FROM trials')
  assert m.diagnostic_frequency_sweep(rows)
  candidates=m.store.rows('SELECT * FROM trials WHERE rung=2')
  import json
  assert len(candidates)==4 and {x['target'] for x in candidates}=={1250}
  assert {x['source'] for x in candidates}=={'donor_test_only.pt'}
  assert {json.loads(x['config'])['options']['frequency'] for x in candidates}=={1.,1.5,2.}
  assert not m.diagnostic_frequency_sweep(rows)
  assert m.store.get('status')=='BLOCKED_DIAGNOSTIC_NO_GAIT'
 finally:m.store.close()
