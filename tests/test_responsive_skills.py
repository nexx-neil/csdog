"""Domain and physical-workspace checks for the new keyboard/crouch interface."""
import itertools
from pathlib import Path
import sys
import unittest
import torch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab'))
from csdog_motion.teleop import keyboard_twist
from csdog_motion.speed_learning import valid_speed_request
from csdog_motion.calibration import ASSET
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics


class ResponsiveTests(unittest.TestCase):
    def test_every_keyboard_combination_respects_measured_command_domain(self):
        for mode in ('normal','fast'):
            commands=[keyboard_twist({key for key,on in zip('WSADQE',bits) if on},mode)
                      for bits in itertools.product((False,True),repeat=6)]
            self.assertTrue(valid_speed_request(torch.tensor(commands)).all())
        self.assertEqual(keyboard_twist({'Q'},'fast'),[0.,0.,.6])
        self.assertEqual(keyboard_twist({'E'},'fast'),[0.,0.,-.6])
        self.assertEqual(keyboard_twist({'W'},'fast'),[.5,0.,0.])
        self.assertEqual(keyboard_twist({'W','Q'},'fast'),[.4,0.,.4])
        self.assertEqual(keyboard_twist({'W','S','Q'},'fast'),[0.,0.,.6])

    def test_deeper_crouch_path_has_real_ik_and_joint_speed_reserve(self):
        data=learning_profile();model=LegKinematics(ASSET/'robot_sim.urdf',data['nominal_joint_positions_rad'],offset_bound=.5,dtype=torch.float64)
        nominal=torch.tensor([data['nominal_sole_positions_body_m'][leg] for leg in ('lr','lf','rf','rr')],dtype=torch.float64)
        drops=torch.linspace(0,.06,51,dtype=torch.float64)
        target=nominal[None].expand(51,-1,-1).clone();target[:,:,2]+=drops[:,None]
        q,error=model.solve(target,iterations=18)
        self.assertLess(float(error.max()),.00001)
        self.assertGreater(float(torch.minimum(q-model.lower,model.upper-q).min()),.04)
        # 0.06m/s at 50Hz: the same 1.2mm height increments as the live task.
        self.assertLess(float((q[1:]-q[:-1]).abs().max()/.02),1.)

if __name__=='__main__':unittest.main()
