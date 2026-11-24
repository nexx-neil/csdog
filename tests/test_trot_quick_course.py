import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.trot_course import valid_request,reference,period,TrotCommands,sample_commands
from csdog_motion.adaptive_speed import adaptive_reference
from csdog_motion.trajectory import TrajectoryConfig
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.quick_crouch import QuickHeightCommands

class TrotQuickTests(unittest.TestCase):
 def test_old_domain_reference_is_exact(self):
  torch.manual_seed(29);p=torch.rand(160);t=torch.rand(160,3)*torch.tensor([1.2,.8,1.6])-torch.tensor([.6,.4,.8]);nom=torch.tensor([[-.24,.14,-.35],[.23,.14,-.35],[.23,-.14,-.35],[-.24,-.14,-.35]])
  cfg=TrajectoryConfig(stance_fraction=.55);old=adaptive_reference(p,t,nom,cfg);new=reference(p,t,nom,cfg)
  self.assertTrue(torch.equal(old[0],new[0]));self.assertTrue(torch.equal(old[1],new[1]))
 def test_sampling_obeys_declared_domain_and_rejects_mixed_extension(self):
  torch.manual_seed(23);s=sample_commands(6000,'cpu');self.assertTrue(valid_request(s).all());self.assertGreater(int((s[:,0]>.6).sum()),1000)
  self.assertEqual(valid_request(torch.tensor([[.8,0,0],[.8,.01,0],[-.8,0,0],[float('nan'),0,0]])).tolist(),[True,False,False,False])
 def test_clock_matches_period_with_one_tick_and_subsets(self):
  cfg=MotionCommandConfig(limits=(.8,.4,.8));m=TrotCommands(2,config=cfg);m.set_request([.8,0,0]);m.applied[:,0]=.8;m.phase[:]=.2
  m.tick(.02,torch.tensor([0]),torch.ones(2,4,dtype=torch.bool))
  self.assertAlmostEqual(float(m.phase[0]),.2+.02/.44,places=6);self.assertAlmostEqual(float(m.phase[1]),.2,places=6)
 def test_quick_segment_meets_endpoint_and_rate_limit(self):
  cfg=MotionCommandConfig(nominal_height_m=.37,height_min_m=.31,height_max_m=.37,height_rate_m_s=.3);m=QuickHeightCommands(2,config=cfg);m.set_request([0,0,0,.31]);vals=[]
  for _ in range(20):m.tick(.02);vals.append(float(m.applied[0,3]));self.assertLessEqual(float(m.height_rate.abs().max()),.3)
  self.assertAlmostEqual(vals[-1],.31,places=6);self.assertTrue(all(x>=y for x,y in zip(vals,vals[1:])))
  self.assertTrue((m.height_segments.velocity==0).all());self.assertTrue((m.height_segments.acceleration==0).all())
 def test_quick_fault_freeze_discards_pending_goal(self):
  cfg=MotionCommandConfig(nominal_height_m=.37,height_min_m=.31,height_max_m=.37,height_rate_m_s=.3);m=QuickHeightCommands(1,config=cfg);m.set_request([0,0,0,.31])
  for _ in range(8):m.tick(.02)
  h=m.applied[:,3].clone();m.freeze_height[:]=True
  for _ in range(30):m.tick(.02)
  self.assertTrue(torch.equal(h,m.applied[:,3]));m.reset();self.assertFalse(m.height_segments.active.any())

if __name__=='__main__':unittest.main()
