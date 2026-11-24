import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.rough_sensing import relative_scan,extend_inputs,OBSERVATIONS
class SensingTests(unittest.TestCase):
 def test_scan_is_invariant_to_world_height_and_rejects_misses(self):
  h=torch.linspace(-.05,.05,99)[None].repeat(2,1);z=torch.tensor([1.,-2.]);a=relative_scan(h+z[:,None],z);b=relative_scan(h+z[:,None]+4,z+4);torch.testing.assert_close(a,b,atol=3e-6,rtol=1e-5)
  h[0,0]=float('inf')
  with self.assertRaises(ValueError):relative_scan(h,z)
 def test_migration_copies_old_columns_and_zeroes_only_new_inputs(self):
  state={'actor.0.weight':torch.randn(8,76),'critic.0.weight':torch.randn(8,76),'actor.0.bias':torch.randn(8)};target={k:torch.empty(8,OBSERVATIONS) if 'weight' in k else torch.empty(8) for k in state};r=extend_inputs(state,target)
  obs=torch.randn(4,76);scan=torch.randn(4,99)
  for k in ['actor.0.weight','critic.0.weight']:
   self.assertTrue(torch.equal(r[k][:,:76],state[k]));self.assertEqual(float(r[k][:,76:].abs().sum()),0.);torch.testing.assert_close(obs@state[k].T,torch.cat((obs,scan),1)@r[k].T)
  self.assertTrue(torch.equal(r['actor.0.bias'],state['actor.0.bias']))
if __name__=='__main__':unittest.main()
