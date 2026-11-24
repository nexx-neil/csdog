import unittest,json
import torch
from csdog_motion.workspace_height import HeightCoordinator,select_height
from csdog_motion.workspace_height_preview import TrajectoryHeightConfig,predict_applied_heights,contract

class TrajectoryPreviewTests(unittest.TestCase):
 def test_planner_height_path_matches_the_real_limited_servo_under_reversal(self):
  cfg=TrajectoryHeightConfig();c=HeightCoordinator(2,cfg=cfg);c.value[:]=torch.tensor([.01,-.01]);c.velocity[:]=torch.tensor([-.04,.04]);goals=torch.tensor([-.025,0.,.025]);pred=predict_applied_heights(c,goals)
  for j,g in enumerate(goals):
   actual=HeightCoordinator(2,cfg=cfg);actual.value.copy_(c.value);actual.velocity.copy_(c.velocity);actual.goal[:]=g
   for step in range(1,14):
    actual.tick(.02,torch.ones(2,dtype=torch.bool))
    if step in [1,3,5,7,9,11,13]:self.assertTrue(torch.equal(actual.value,pred[:,j,[1,3,5,7,9,11,13].index(step)]))
 def test_feasible_final_height_is_not_mistaken_for_feasible_height_during_response(self):
  c=HeightCoordinator(1,cfg=TrajectoryHeightConfig());goals=torch.tensor([0.,.005,.02]);path=predict_applied_heights(c,goals)
  error=torch.zeros(1,3,7,4);margin=torch.ones_like(error)
  # The upcoming foot target needs3mm body offset at80ms.5mm eventual height arrives too late.
  error[:,:,2,:]=torch.relu(.003-path[:,:,2])[:,:,None]
  goal,good=select_height(error,margin,goals,c.goal,c.cfg);self.assertTrue(good[0]);self.assertAlmostEqual(float(goal[0]),.02,places=6)
  d=contract({'height':{},'schema_version':33});self.assertEqual(d,json.loads(json.dumps(d)))
