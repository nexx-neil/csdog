import sys,unittest
from pathlib import Path
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.smooth_height import HeightSegments,SmoothHeightCommandState
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.terrain_course import course_height,START,RUN,RISE,END
from csdog_motion.adaptive_speed import valid_request
from csdog_motion.teleop import keyboard_twist

class SmoothHeightTests(unittest.TestCase):
 def test_six_cm_segment_has_zero_endpoint_derivatives_and_bounded_velocity(self):
  p=HeightSegments(1,.37);ids=torch.tensor([0]);values=[];vel=[]
  for _ in range(50):values.append(float(p.tick(.02,ids,torch.tensor([.31]),torch.tensor([False]))[0]));vel.append(float(p.velocity[0]))
  self.assertAlmostEqual(values[-1],.31,places=6);self.assertTrue(all(a>=b for a,b in zip(values,values[1:])));self.assertLess(max(abs(v) for v in vel),.113)
  self.assertEqual(float(p.velocity[0]),0.);self.assertEqual(float(p.acceleration[0]),0.)
 def test_reversal_waits_for_zero_velocity_and_stays_in_height_envelope(self):
  p=HeightSegments(1,.37);ids=torch.tensor([0]);values=[]
  for step in range(110):
   goal=.31 if step<20 else .37
   values.append(float(p.tick(.02,ids,torch.tensor([goal]),torch.tensor([False]))[0]))
   if step==49:self.assertEqual(float(p.velocity[0]),0.)
  self.assertGreaterEqual(min(values),.31-1e-6);self.assertLessEqual(max(values),.37+1e-6);self.assertAlmostEqual(values[-1],.37,places=6)
 def test_fault_freezes_executed_height_and_reset_discards_pending_trajectory(self):
  cfg=MotionCommandConfig(nominal_height_m=.37,height_min_m=.31,height_max_m=.37,height_rate_m_s=.12)
  m=SmoothHeightCommandState(2,config=cfg);m.set_request([0.,0.,0.,.31]);contacts=torch.ones(2,4,dtype=torch.bool)
  for _ in range(20):m.tick(.02,foot_contact=contacts)
  h=m.applied[:,3].clone();m.freeze_height[:]=True
  for _ in range(30):m.tick(.02,foot_contact=contacts)
  self.assertTrue(torch.equal(m.applied[:,3],h));m.reset();self.assertFalse(m.height_segments.active.any());self.assertFalse(m.freeze_height.any())
 def test_agile_keyboard_does_not_enable_rejected_fast_backward_or_high_mixed_commands(self):
  import itertools
  commands=[keyboard_twist({k for k,b in zip('WSADQE',bits) if b},'agile') for bits in itertools.product((0,1),repeat=6)]
  self.assertTrue(valid_request(torch.tensor(commands)).all());self.assertEqual(keyboard_twist({'S'},'agile'),[-.5,0.,0.]);self.assertEqual(keyboard_twist({'Q'},'agile'),[0.,0.,.8]);self.assertEqual(keyboard_twist({'W','Q'},'agile'),[.4,0.,.4])

class CourseTests(unittest.TestCase):
 def test_hill_surface_has_correct_rise_plateau_descent_and_finite_width(self):
  x=torch.tensor([0.,START,START+RUN,START+RUN+.3,END,END+.2]);case=torch.full_like(x,3,dtype=torch.long)
  torch.testing.assert_close(course_height(x,case),torch.tensor([0.,0.,RISE,RISE,0.,0.]))
  self.assertEqual(float(course_height(torch.tensor([1.5]),torch.tensor([3]),torch.tensor([.7]))[0]),0.)
 def test_bar_surface_matches_three_1cm_and_2cm_features(self):
  x=torch.tensor([.8,1.6,2.4,.6]);torch.testing.assert_close(course_height(x,torch.full((4,),1)),torch.tensor([.01,.01,.01,0.]));torch.testing.assert_close(course_height(x,torch.full((4,),2)),torch.tensor([.02,.02,.02,0.]))

if __name__=='__main__':unittest.main()

class ChallengeCourseTests(unittest.TestCase):
 def test_challenge_increases_three_independent_difficulties_and_matches_geometry(self):
  from csdog_motion.terrain_course import BASE_COURSE,CHALLENGE_COURSE
  self.assertGreater(CHALLENGE_COURSE.slope_deg,BASE_COURSE.slope_deg);self.assertGreater(CHALLENGE_COURSE.high_bar_m,BASE_COURSE.high_bar_m);self.assertLess(CHALLENGE_COURSE.material_friction,BASE_COURSE.material_friction)
  torch.testing.assert_close(course_height(torch.tensor([START+RUN]),torch.tensor([3]),config=CHALLENGE_COURSE),torch.tensor([CHALLENGE_COURSE.rise_m]))
  torch.testing.assert_close(course_height(torch.tensor([.8]),torch.tensor([2]),config=CHALLENGE_COURSE),torch.tensor([.03]))

class ObstacleClearanceTests(unittest.TestCase):
 def test_extra_lift_keeps_stance_and_stand_unchanged_and_has_zero_boundary_derivatives(self):
  from csdog_motion.terrain_course import extra_swing_clearance
  for boundary in (.55,1.):
   p=torch.tensor([boundary-1e-5,boundary,boundary+1e-5],dtype=torch.float64);target=torch.zeros(3,4,3,dtype=torch.float64);duty=torch.full((3,),.55,dtype=torch.float64);extra=torch.full((3,),.013,dtype=torch.float64)
   out=extra_swing_clearance(target,p,duty,extra,torch.ones(3,dtype=torch.float64));z=out[:,0,2]
   self.assertLess(float(abs((z[2]-z[0])/2e-5)),1e-6);self.assertLess(float(abs((z[2]-2*z[1]+z[0])/1e-10)),.01)
   self.assertTrue(torch.equal(extra_swing_clearance(target,p,duty,extra,torch.zeros(3,dtype=torch.float64)),target))
 def test_45mm_lift_with_bounded_path_commands_has_real_kinematic_and_speed_reserve(self):
  from csdog_motion.terrain_course import extra_swing_clearance
  from csdog_motion.residual_learning import learning_profile
  from csdog_motion.trajectory import LegKinematics,TrajectoryConfig
  from csdog_motion.calibration import ASSET
  from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
  d=learning_profile();m=LegKinematics(ASSET/'robot_sim.urdf',d['nominal_joint_positions_rad'],offset_bound=.5,dtype=torch.float64);nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64);cfg=TrajectoryConfig(**d['trajectory']);p=torch.arange(400,dtype=torch.float64)/400
  for command in ([.25,0.,0.],[.25,.08,.12],[.25,-.08,-.12]):
   cmd=torch.tensor([command],dtype=torch.float64).expand(400,-1);foot,_=adaptive_reference(p,cmd,nom,cfg,torch.ones_like(p));foot=extra_swing_clearance(foot,p,stance_fraction(cmd),torch.full_like(p,.013),torch.ones_like(p));q,e=m.solve(foot,iterations=18)
   self.assertLess(float(e.max()),.001);self.assertLess(float((q.roll(-1,0)-q).abs().max()/(.5/400)),8.)
