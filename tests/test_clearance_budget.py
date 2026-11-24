import unittest
import torch
from csdog_motion.clearance_budget import contract,EXTRA_LIFT_CAP_M
from csdog_motion.calibration import ASSET
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics


class ClearanceBudgetTests(unittest.TestCase):
    def test_recorded_box_target_fits_with_reduced_surplus_without_wider_limits(self):
        profile=learning_profile();m=LegKinematics(ASSET/'robot_sim.urdf',profile['nominal_joint_positions_rad'],offset_bound=.5)
        target=torch.tensor([[[-.23820214,.13946857,-.28607985],[.23011437,.13538355,-.35344955],[.24044637,-.13532206,-.31298622],[-.24853416,-.14063217,-.32654318]]])
        _,old_error=m.solve(target,iterations=82);self.assertGreater(float(old_error.max()),.001)
        target[:,0,2]-=(.01-EXTRA_LIFT_CAP_M)*.95
        q,error=m.solve(target,iterations=18)
        self.assertLess(float(error.max()),.001)
        self.assertTrue(((q>=m.lower)&(q<=m.upper)).all())

    def test_contract_change_is_explicit_and_does_not_mutate_parent(self):
        parent={'schema_version':28,'compatibility_tag':'old','rough_sensing':{'height_grid_rays':99},'limits':[8,12]}
        result=contract(parent)
        self.assertNotEqual(parent['compatibility_tag'],result['compatibility_tag'])
        self.assertNotIn('extra_swing_lift_cap_m',parent['rough_sensing'])
        self.assertEqual(result['limits'],parent['limits'])
