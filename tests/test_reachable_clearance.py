import unittest
import torch
from csdog_motion.reachable_clearance import allocate
from csdog_motion.calibration import ASSET
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics


class ReachableTests(unittest.TestCase):
    def test_recorded_failure_is_replanned_and_other_legs_are_bitwise_preserved(self):
        p=learning_profile();m=LegKinematics(ASSET/'robot_sim.urdf',p['nominal_joint_positions_rad'],offset_bound=.5)
        full=torch.tensor([[[-.23820214,.13946857,-.28607985],[.23011437,.13538355,-.35344955],[.24044637,-.13532206,-.31298622],[-.24853416,-.14063217,-.32654318]]]);lift=torch.tensor([[.0095,0.,.0095,0.]])
        q,e=m.solve(full,iterations=18)
        def target(scale):
            result=full.clone();result[:,:,2]-=lift*(1-scale);return result
        new,error,scale,active=allocate(m,target,q,e,lift)
        self.assertLess(float(error.max()),.001)
        self.assertTrue(torch.equal(new[~active],q[~active]))
        self.assertLess(float(scale[0,0]),1.)
        self.assertTrue(((new>=m.lower)&(new<=m.upper)).all())
        bad=full.clone();bad[:,:,2]+=.2
        bq,be=m.solve(bad,iterations=18)
        with self.assertRaises(RuntimeError):allocate(m,lambda s:bad,bq,be,torch.ones_like(lift)*.01)
