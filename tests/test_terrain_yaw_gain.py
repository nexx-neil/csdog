import unittest
import torch
from csdog_motion.terrain_yaw_gain import TerrainYawIntegral,YAW
from csdog_motion.yaw_integral import YawIntegral

class TerrainYawGainTests(unittest.TestCase):
    def test_backward_is_bitwise_original_and_turn_remains_bounded(self):
        old=YawIntegral(3,config=YAW);new=TerrainYawIntegral(3,config=YAW)
        cmd=torch.tensor([[-.25,0,0],[0,0,.3],[0,0,-.3]]);actual=torch.tensor([.04,.1,-.1]);active=torch.ones(3,dtype=torch.bool)
        for _ in range(200):
            a=old.tick(.02,cmd,cmd,actual,torch.zeros(3),active);b=new.tick(.02,cmd,cmd,actual,torch.zeros(3),active)
            self.assertEqual(float(a[0]),float(b[0]));self.assertLessEqual(float(b.abs().max()),.600001)
        new.tick(.02,cmd,torch.zeros_like(cmd),actual,torch.zeros(3),active)
        self.assertTrue(torch.equal(new.moment,torch.zeros_like(new.moment)))
