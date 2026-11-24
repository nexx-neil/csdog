import unittest
import torch
from csdog_motion.trot_return import swing_displacement,reference,period,ReturnCommands
from csdog_motion import trot_course as old
from csdog_motion.commands import MotionCommandConfig
from csdog_motion.trajectory import TrajectoryConfig

class ReturnTests(unittest.TestCase):
    def derivative(self,s):
        p=torch.tensor(s,dtype=torch.float64,requires_grad=True)
        x=swing_displacement(p,1.,.24)
        v=torch.autograd.grad(x,p,create_graph=True)[0]/.24
        a=torch.autograd.grad(v,p)[0]/.24
        return float(x),float(v),float(a)
    def test_exact_endpoint_distance_and_stance_matched_velocity_acceleration(self):
        start=self.derivative(0.);end=self.derivative(1.)
        self.assertAlmostEqual(start[0],0.,places=12);self.assertAlmostEqual(end[0],.16,places=12)
        for item in (start,end):
            self.assertAlmostEqual(item[1],-1.,places=12);self.assertAlmostEqual(item[2],0.,places=12)
    def test_c2_at_both_internal_ramp_boundaries(self):
        for boundary in (.2,.8):
            a,b=self.derivative(boundary-1e-8),self.derivative(boundary+1e-8)
            for x,y in zip(a,b):self.assertLess(abs(x-y),2e-4)
        self.assertAlmostEqual(self.derivative(.5)[1],13/12,places=12)
    def test_old_reference_and_clock_are_exact(self):
        torch.manual_seed(4501);ph=torch.rand(100);tw=torch.rand(100,3)*torch.tensor([1.6,.8,1.6])-torch.tensor([.8,.4,.8]);nom=torch.tensor([[-.24,.14,-.35],[.23,.14,-.35],[.23,-.14,-.35],[-.24,-.14,-.35]])
        args=(ph,tw,nom,TrajectoryConfig(stance_fraction=.55))
        self.assertTrue(all(torch.equal(a,b)for a,b in zip(reference(*args),old.reference(*args))))
        cfg=MotionCommandConfig(limits=(1.,.4,.8));a,b=ReturnCommands(1,config=cfg),old.TrotCommands(1,config=cfg)
        for m in (a,b):m.set_request([.8,0,0]);m.applied[:,0]=.8;m.phase[:]=.2
        for _ in range(100):a.tick(.02);b.tick(.02)
        self.assertTrue(torch.equal(a.phase,b.phase))

if __name__=='__main__':unittest.main()
