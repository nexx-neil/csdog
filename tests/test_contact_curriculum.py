import unittest
import torch
from csdog_motion.contact_curriculum import activation,additional_slide_reward,CommandReplay


class ContactCurriculumTests(unittest.TestCase):
    def test_cost_is_inactive_for_flat_or_non_backward_and_bounded(self):
        twist=torch.tensor([[-.25,0,0],[.25,0,0],[0,.2,0],[-.25,0,0],[-.225,0,0]])
        g=activation(twist,torch.tensor([.02,.02,.02,0.,.02]))
        torch.testing.assert_close(g,torch.tensor([1.,0,0,0,.5]))
        native=torch.full((5,),-.001)
        r=additional_slide_reward(native,g)
        torch.testing.assert_close(r,torch.tensor([-.059,0,0,0,-.0295]))
        self.assertTrue(torch.all(r<=0))

    def test_additive_cost_uses_pre_reset_native_value(self):
        native=torch.tensor([-.002,-.004])
        cost=additional_slide_reward(native,torch.ones(2))
        torch.testing.assert_close(native+cost,native*60)
        with self.assertRaises(ValueError):additional_slide_reward(native,torch.ones(2),native_weight=.5)

    def test_reset_stops_commands_and_replay_stays_in_single_axis_bounds(self):
        class Env:
            num_envs=80;device='cpu';step_dt=.02;terrain_columns=torch.arange(80)%8
            def set_motion_request(self,value):self.request=value.clone()
        env=Env();replay=CommandReplay(env)
        for _ in range(30):replay.request()
        self.assertTrue((env.request.abs()<=torch.tensor([.25,.2,.3])).all())
        self.assertTrue(((env.request.abs()>0).sum(1)<=1).all())
        self.assertGreater(replay.targeted_bouts,0)
        replay.on_dones(torch.ones(80));self.assertEqual(int(replay.current.count_nonzero()),0)
        replay.reset();self.assertTrue(torch.all(replay.remaining==.5))
