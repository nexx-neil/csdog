import unittest,json
from pathlib import Path
import torch
from csdog_motion.workspace_height import select_height as global_select
from csdog_motion.workspace_height_priority import select_height,contract
from csdog_motion.workspace_height_preview import TrajectoryHeightConfig

class PriorityPreviewTests(unittest.TestCase):
 def test_recorded_backward_failure_prefers_immediate_extension_reserve(self):
  d=json.loads((Path(__file__).parent/'fixtures/workspace_priority_preview.json').read_text());e=torch.tensor(d['error']);m=torch.tensor(d['margin']);g=torch.tensor(d['candidates_m']);prev=torch.tensor([d['previous_goal_m']]);cfg=TrajectoryHeightConfig()
  old,_=global_select(e,m,g,prev,cfg);new,_=select_height(e,m,g,prev,cfg)
  self.assertAlmostEqual(float(old[0]),0.,places=6);self.assertGreaterEqual(float(new[0]),.01-1e-6)
 def test_near_constraint_is_not_sacrificed_for_a_larger_distant_violation(self):
  error=torch.zeros(1,2,7,4);margin=torch.ones_like(error);goals=torch.tensor([0.,.02]);previous=torch.zeros(1);cfg=TrajectoryHeightConfig()
  error[0,0,2]=.001;error[0,1,5]=.01
  legacy,_=global_select(error,margin,goals,previous,cfg);new,good=select_height(error,margin,goals,previous,cfg)
  self.assertEqual(float(legacy[0]),0);self.assertAlmostEqual(float(new[0]),.02,places=6);self.assertFalse(good[0])
 def test_feasible_zero_retains_no_adjustment_and_contract_is_json_stable(self):
  e=torch.zeros(2,3,7,4);m=torch.ones_like(e);goal,good=select_height(e,m,torch.tensor([-.02,0.,.02]),torch.zeros(2));self.assertTrue(torch.equal(goal,torch.zeros(2)));self.assertTrue(good.all())
  d=contract({'height':{}});self.assertEqual(d,json.loads(json.dumps(d)))
