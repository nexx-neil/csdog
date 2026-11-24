import unittest
import torch
from csdog_motion.contact_patch import measured_patch,PatchMemory

class PatchTests(unittest.TestCase):
    def setUp(self):
        self.p=torch.zeros(1,4,3);self.p[:,:,2]=.1150586307
        self.f=torch.zeros_like(self.p);self.f[:,:,0]=9.6627073;self.f[:,:,2]=8.3144312
        self.r=torch.full((1,4),.08808636665);self.xyz=self.p.clone();self.xyz[:,:,0]=7.61406755;self.xyz[:,:,2]=.128677085
        self.stance=torch.ones(1,4,dtype=torch.bool);self.env=torch.ones(1,dtype=torch.bool)
    def test_recorded_edge_uses_sphere_normal_geometry(self):
        h,valid=measured_patch(self.p,self.f,self.r)
        expected=.1150586307+.018*8.3144312/(9.6627073**2+8.3144312**2)**.5-.018
        self.assertTrue(valid.all());self.assertAlmostEqual(float(h[0,0]),expected,places=7)
        self.assertGreater(float(h[0,0]-self.r[0,0]),.02)
    def test_flat_contact_retains_ray_bitwise(self):
        p=torch.zeros_like(self.p);f=torch.zeros_like(self.f);f[:,:,2]=10.;r=torch.zeros_like(self.r)
        h,valid=measured_patch(p,f,r);self.assertFalse(valid.any());self.assertTrue(torch.equal(h,r))
    def test_missing_or_unloaded_contact_never_fabricates_support(self):
        self.p[0,0]=float('nan');self.f[0,1]=0.;self.f[0,2,2]=-10.
        h,valid=measured_patch(self.p,self.f,self.r)
        self.assertEqual(valid.tolist(),[[False,False,False,True]]);self.assertTrue(torch.isfinite(h).all())
    def test_safe_ray_reference_does_not_activate(self):
        m=PatchMemory(1);m.update(0,self.stance,self.p,self.f,self.r,self.xyz,torch.zeros_like(self.stance),self.env)
        self.assertFalse(m.active.any())
    def test_world_foothold_persists_through_force_loss_then_releases_at_liftoff(self):
        m=PatchMemory(1);m.update(0,self.stance,self.p,self.f,self.r,self.xyz,self.stance,self.env);xy=m.xy.clone();h=m.height.clone()
        m.update(1,self.stance,self.p,self.f*0,self.r-.03,self.xyz+1,self.stance,self.env)
        self.assertTrue(torch.equal(xy,m.xy));self.assertTrue(torch.equal(h,m.height));self.assertTrue(m.active.all())
        m.update(2,~self.stance,self.p,self.f,self.r,self.xyz,self.stance,self.env);self.assertFalse(m.active.any())
    def test_repeated_observation_is_idempotent_and_subset_reset_is_local(self):
        m=PatchMemory(2);p=self.p.expand(2,-1,-1);f=self.f.expand(2,-1,-1);r=self.r.expand(2,-1);xyz=self.xyz.expand(2,-1,-1);s=self.stance.expand(2,-1);env=self.env.expand(2)
        m.update(0,s,p,f,r,xyz,s,env);before=m.xy.clone();m.update(0,~s,p,f,r,xyz+1,s,env);self.assertTrue(torch.equal(m.xy,before));self.assertTrue(m.active.all())
        m.reset(torch.tensor([0]));self.assertFalse(m.active[0].any());self.assertTrue(m.active[1].all())
    def test_anchor_cannot_reappear_after_future_liftoff(self):
        m=PatchMemory(1);m.active[:]=True;phase=torch.tensor([.52])
        self.assertEqual(m.continuing(phase,0.,.5,.55).tolist(),[[True,True,True,True]])
        self.assertEqual(m.continuing(phase,.24,.5,.55).tolist(),[[False,True,False,True]])
    def test_world_translation_shifts_height_without_changing_validity(self):
        h,v=measured_patch(self.p,self.f,self.r);p=self.p.clone();p[:,:,2]+=3;other,valid=measured_patch(p,self.f,self.r+3)
        self.assertTrue(torch.equal(v,valid));self.assertTrue(torch.allclose(other,h+3,atol=5e-7))
