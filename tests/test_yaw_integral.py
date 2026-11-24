import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.yaw_integral import YawIntegral,strength,extend_policy_inputs

class YawTests(unittest.TestCase):
 def setUp(self):
  self.c=YawIntegral(2);self.applied=torch.tensor([[0.,0.,.8],[-.6,0.,0.]]);self.request=self.applied.clone();self.actual=torch.tensor([.7,.1]);self.p=torch.tensor([.2,-.4]);self.active=torch.ones(2,dtype=torch.bool)
 def tick(self,n=1):
  for _ in range(n):self.c.tick(.02,self.applied,self.request,self.actual,self.p,self.active)
 def test_persistent_bias_has_bounded_signed_integral(self):
  self.tick(350);torch.testing.assert_close(self.c.integral,torch.tensor([.6,-.6]));self.assertTrue(torch.isfinite(self.c.moment).all())
 def test_new_command_and_inactive_reset_discard_old_bias(self):
  self.tick(100);self.request.neg_();self.tick();self.assertLess(float(self.c.integral.abs().max()),.001)
  self.active[:]=False;self.tick();self.assertTrue((self.c.integral==0).all());self.assertTrue((self.c.filtered_error==0).all())
 def test_outward_integration_freezes_at_total_yaw_limit(self):
  self.p[:]=torch.tensor([2.1,-2.1]);self.tick(100);self.assertTrue((self.c.integral==0).all())
 def test_stop_clears_correction_even_while_applied_twist_is_still_braking(self):
  self.tick(100);self.request.zero_();self.tick(5);self.assertTrue((self.c.integral==0).all());self.assertTrue((self.c.moment==0).all())
 def test_legacy_forward_lateral_low_turn_and_mixed_back_are_inactive(self):
  cmd=torch.tensor([[.6,0,0],[0,.4,0],[0,0,.4],[-.15,0,0],[-.4,.3,0]])
  self.assertTrue((strength(cmd)==0).all());self.assertTrue((strength(torch.tensor([[-.4,0,0],[0,0,.8]]))==1).all())
 def test_subset_reset_and_invalid_sensor_input(self):
  self.tick(20);self.c.reset(torch.tensor([0]));self.assertEqual(float(self.c.integral[0]),0.);self.assertLess(float(self.c.integral[1]),0.)
  self.actual[0]=float('nan')
  with self.assertRaises(ValueError):self.tick()
 def test_explicit_input_extension_preserves_all_old_tensors_and_ignores_new_features_initially(self):
  torch.manual_seed(17);state={'actor.0.weight':torch.randn(4,74),'critic.0.weight':torch.randn(4,74),'actor.0.bias':torch.randn(4)};target={k:(torch.empty(4,76) if k.endswith('weight') else torch.empty_like(v)) for k,v in state.items()};new=extend_policy_inputs(state,target)
  for key in ('actor.0.weight','critic.0.weight'):
   self.assertTrue(torch.equal(new[key][:,:74],state[key]));self.assertTrue((new[key][:,74:]==0).all())
   x=torch.randn(5,76);torch.testing.assert_close(torch.nn.functional.linear(x,new[key]),torch.nn.functional.linear(x[:,:74],state[key]),rtol=1e-5,atol=1e-5)
  self.assertTrue(torch.equal(new['actor.0.bias'],state['actor.0.bias']))
  target['actor.0.bias']=torch.zeros(5)
  with self.assertRaises(ValueError):extend_policy_inputs(state,target)

if __name__=='__main__':unittest.main()

class YawSamplingTests(unittest.TestCase):
 def test_training_keeps_old_exposure_and_rejects_unchecked_fast_combinations(self):
  from csdog_motion.yaw_learning import sample_commands
  from csdog_motion.adaptive_speed import valid_request
  torch.manual_seed(99);cmd,category=sample_commands(20000)
  self.assertTrue(valid_request(cmd).all())
  self.assertLess(abs(float((category<.75).float().mean())-.75),.02)
  fast=category>=.75;self.assertTrue(((cmd[fast].abs()>1e-6).sum(1)==1).all())
  self.assertTrue((cmd[category<.25].abs()<=torch.tensor([.15,.1,.15])+1e-6).all())
