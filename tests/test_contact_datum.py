import unittest
import torch
from csdog_motion.contact_datum import ContactDatum,measured_goal

class DatumTests(unittest.TestCase):
    def test_recorded_support_mismatch_uses_touching_feet_only(self):
        root=torch.tensor([-.0211778879]);feet=torch.tensor([[1.,-.0172801018,1.,.0244138241]])
        goal,good=measured_goal(root,feet,torch.tensor([[0.,10.,0.,10.]]))
        self.assertTrue(good.all());self.assertAlmostEqual(float(goal-root),.024744749,places=7)
    def test_contact_loss_retains_goal_and_offset_bound_does_not_change_measurements(self):
        d=ContactDatum(1);r=torch.tensor([0.]);f=torch.ones(1,4);before=f.clone()
        d.update(r,f,torch.ones(1,4)*10,0,.02,torch.tensor([True]));self.assertAlmostEqual(float(d.goal),.03,places=7)
        d.update(r,f,torch.zeros(1,4),1,.02,torch.tensor([True]));self.assertAlmostEqual(float(d.goal),.03,places=7);self.assertTrue(torch.equal(f,before))
    def test_bounded_world_filter_idempotence_and_subset_reset(self):
        d=ContactDatum(2);r=torch.tensor([3.,-2.]);f=r[:,None].expand(2,4)+.025;force=torch.ones(2,4)*10;active=torch.ones(2,dtype=torch.bool)
        for tick in range(100):
            d.update(r,f,force,tick,.02,active)
            self.assertLessEqual(float(d.velocity.abs().max()),.080001);self.assertLessEqual(float(d.acceleration.abs().max()),.40001)
            previous=d.value.clone();d.update(r,f,force,tick,.02,active);self.assertTrue(torch.equal(previous,d.value))
        self.assertTrue(torch.allclose(d.value,r+.025,atol=2e-5));old=d.value[1].clone();d.reset(torch.tensor([0]));d.update(r,f,force,99,.02,active)
        self.assertAlmostEqual(float(d.value[0]),3.,places=7);self.assertTrue(torch.equal(old,d.value[1]))
    def test_same_world_datum_cancels_discontinuous_root_ground_in_force_error(self):
        root_z=torch.tensor([.37]);datum=torch.tensor([.01]);nom=.37;auto=.005
        errors=[]
        for ground in [-.025,.025]:
            measured=root_z-ground;target=nom+auto+datum-ground;errors.append(target-measured)
        self.assertTrue(torch.allclose(errors[0],errors[1],atol=1e-7))
if __name__=='__main__':unittest.main()
