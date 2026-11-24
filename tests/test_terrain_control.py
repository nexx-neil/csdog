import unittest
import torch
from csdog_motion.terrain_control import YAW
from csdog_motion.yaw_integral import YawIntegral,strength,YawConfig


class TerrainYawTests(unittest.TestCase):
    def test_moderate_turn_is_enabled_with_original_moment_caps(self):
        commands=torch.tensor([[0.,0.,.3],[0.,0.,-.3],[-.25,0,0]])
        self.assertEqual(float(strength(commands,YawConfig())[0]),0.)
        self.assertEqual(float(strength(commands,YAW)[0]),1.)
        self.assertEqual(float(strength(commands,YAW)[1]),1.)
        self.assertEqual(float(strength(commands,YAW)[2]),float(strength(commands,YawConfig())[2]))
        y=YawIntegral(3,config=YAW)
        for _ in range(1000):y.tick(.02,commands,commands,torch.zeros(3),torch.zeros(3),torch.ones(3,dtype=torch.bool))
        self.assertLessEqual(float(y.moment.abs().max()),.600001)
        y.tick(.02,commands,torch.zeros_like(commands),torch.zeros(3),torch.zeros(3),torch.ones(3,dtype=torch.bool))
        self.assertTrue(torch.equal(y.moment,torch.zeros_like(y.moment)))
