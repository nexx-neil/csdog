import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.trot_policy_routing import blend_actions

class RoutingTests(unittest.TestCase):
 def test_old_domain_is_bitwise_old_and_fast_domain_is_learned(self):
  obs=torch.zeros(5,76);obs[:,9]=torch.tensor([-.6,.3,.6,.66,.8]);old=torch.ones(5,12)*.2;new=torch.ones(5,12)*.8
  result=blend_actions(old,new,obs)
  self.assertTrue(torch.equal(result[:3],old[:3]));self.assertTrue(torch.allclose(result[3],torch.ones(12)*.5));self.assertTrue(torch.allclose(result[4],new[4]))
 def test_blend_has_no_action_jump_at_boundaries(self):
  for speed,expected in [(.6,.2),(.72,.8)]:
   obs=torch.zeros(3,76,dtype=torch.float64);obs[:,9]=torch.tensor([speed-1e-6,speed,speed+1e-6],dtype=torch.float64)
   result=blend_actions(torch.full((3,12),.2,dtype=torch.float64),torch.full((3,12),.8,dtype=torch.float64),obs)
   self.assertLess(float((result[2]-result[0]).abs().max()),1e-9);self.assertAlmostEqual(float(result[1,0]),expected,places=12)
 def test_wrong_observation_layout_rejected(self):
  with self.assertRaises(ValueError):blend_actions(torch.zeros(1,12),torch.zeros(1,12),torch.zeros(1,74))
if __name__=='__main__':unittest.main()
