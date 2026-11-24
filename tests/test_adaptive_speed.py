import sys,unittest,itertools
from pathlib import Path
from types import SimpleNamespace
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.adaptive_speed import stance_fraction,adaptive_reference,valid_request,fast_cases
from csdog_motion.residual_learning import learning_profile
from csdog_motion.clean_gait import clean_foot_reference
from csdog_motion.trajectory import TrajectoryConfig,LegKinematics
from csdog_motion.calibration import ASSET
from csdog_motion.support_feedback import support_weights
from csdog_motion.support_transfer import BACKWARD_TRANSITION

class AdaptiveSpeedTests(unittest.TestCase):
 def test_domain_and_frozen_cases(self):
  for case in fast_cases():self.assertTrue(valid_request(torch.tensor([p[1] for p in case['profile']])).all())
  self.assertFalse(valid_request(torch.tensor([[.6,.4,.8],[.61,0,0],[0,0,float('nan')]])).any())
 def test_legacy_references_and_shares_are_bitwise_equal(self):
  data=learning_profile();nom=torch.tensor([data['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64);cfg=TrajectoryConfig(**data['trajectory'])
  cmds=torch.tensor(list(itertools.product((-.4,0,.4),(-.3,0,.3),(-.4,0,.4)))+[[.5,0,0],[-.5,0,0],[0,.35,0],[0,0,.6]],dtype=torch.float64)
  for phase in (.0,.49,.51,.54,.55,.58,.8,.999):
   p=torch.full((len(cmds),),phase,dtype=torch.float64);b=torch.ones_like(p)
   old,om=clean_foot_reference(p,cmds,nom,cfg,b);new,nm=adaptive_reference(p,cmds,nom,cfg,b)
   self.assertTrue(torch.equal(old,new));self.assertTrue(torch.equal(om,nm))
   self.assertTrue(torch.equal(support_weights(p,b,.55,BACKWARD_TRANSITION,cmds),support_weights(p,b,stance_fraction(cmds)[:,None],BACKWARD_TRANSITION,cmds)))
 def test_float32_inactive_branch_retains_scalar_reference_exactly(self):
  d=learning_profile();nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')]);cfg=TrajectoryConfig(**d['trajectory']);p=torch.arange(400)/400
  for vx in (-.5,-.4,0.,.4,.5):
   cmd=torch.tensor([[vx,0.,0.]]).expand(400,-1)
   old,om=clean_foot_reference(p,cmd,nom,cfg,torch.ones(400));new,nm=adaptive_reference(p,cmd,nom,cfg,torch.ones(400))
   self.assertTrue(torch.equal(old,new));self.assertTrue(torch.equal(om,nm))
 def test_high_speed_trajectory_and_shared_support_timing_are_bounded(self):
  d=learning_profile();m=LegKinematics(ASSET/'robot_sim.urdf',d['nominal_joint_positions_rad'],offset_bound=.5,dtype=torch.float64);nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64);cfg=TrajectoryConfig(**d['trajectory'])
  phase=torch.arange(400,dtype=torch.float64)/400
  for vx in (-.6,-.575,-.55,-.525,.525,.55,.575,.6):
   cmd=torch.tensor([[vx,0,0]],dtype=torch.float64).expand(400,-1);foot,mask=adaptive_reference(phase,cmd,nom,cfg,torch.ones_like(phase));q,error=m.solve(foot,iterations=18)
   self.assertLess(float(error.max()),.001);self.assertLess(float((q.roll(-1,0)-q).abs().max()/(cfg.period_s/400)),7.8)
   shares=support_weights(phase,torch.ones_like(phase),stance_fraction(cmd)[:,None],BACKWARD_TRANSITION,cmd)
   self.assertTrue(((shares>=0)&(shares<=1)).all());self.assertGreater(float(shares.sum(1).min()),.9)

if __name__=='__main__':unittest.main()
