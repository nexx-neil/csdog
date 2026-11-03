import json
import pytest
from dogfight.locomotion.spot_aligned_v3.budget import Budget

def write_ledger(root,completed=0,seconds=0,status='COMPLETE',name='first'):
 (root/'training_budget.json').write_text(json.dumps(dict(max_updates=230,max_seconds=1200,runs=[dict(name=name,status=status,completed_updates=completed,reserved_updates=120,seconds=seconds)])))

def test_v3_stage_and_total_caps(tmp_path):
 with pytest.raises(RuntimeError):Budget(tmp_path,'first',121)
 write_ledger(tmp_path,completed=225,name='validation')
 with pytest.raises(RuntimeError):Budget(tmp_path,'smoke',6)
 with pytest.raises(RuntimeError):Budget(tmp_path,'second',6)

def test_v3_time_cap_and_interrupted_reservation(tmp_path):
 write_ledger(tmp_path,seconds=1200)
 with pytest.raises(RuntimeError):Budget(tmp_path,'smoke',1)
 write_ledger(tmp_path,status='RUNNING')
 with pytest.raises(RuntimeError):Budget(tmp_path,'smoke',1)

def test_v3_exact_updates_and_separate_ledger(tmp_path):
 b=Budget(tmp_path,'smoke',5)
 for _ in range(5):b.update()
 with pytest.raises(RuntimeError):b.update()
 b.close('COMPLETE')
 d=json.loads((tmp_path/'training_budget.json').read_text())
 assert (d['max_updates'],d['max_seconds'])==(230,1200)
 assert d['runs'][0]['completed_updates']==5
