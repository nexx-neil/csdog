"""Independent budget boundaries for the newly authorized experiment."""
import json
import pytest
from dogfight.locomotion.spot_v2.budget import Budget

def test_spot_budget_does_not_read_old_ledger(tmp_path):
 b=Budget(tmp_path,'smoke',5)
 for _ in range(5):b.update()
 with pytest.raises(RuntimeError):b.update()
 b.close('COMPLETE')
 d=json.loads((tmp_path/'training_budget.json').read_text())
 assert d['max_updates']==320 and d['max_seconds']==1800
 assert d['runs'][0]['completed_updates']==5

def test_spot_cumulative_update_limit(tmp_path):
 (tmp_path/'training_budget.json').write_text(json.dumps(dict(max_updates=320,max_seconds=1800,runs=[dict(status='COMPLETE',completed_updates=305,reserved_updates=305,seconds=100)])))
 with pytest.raises(RuntimeError):Budget(tmp_path,'over_limit',16)

def test_spot_cumulative_time_limit(tmp_path):
 (tmp_path/'training_budget.json').write_text(json.dumps(dict(max_updates=320,max_seconds=1800,runs=[dict(status='COMPLETE',completed_updates=1,reserved_updates=1,seconds=1800)])))
 with pytest.raises(RuntimeError):Budget(tmp_path,'over_time',1)
