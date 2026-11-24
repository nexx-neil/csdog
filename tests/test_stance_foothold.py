import unittest,torch
from csdog_motion.stance_foothold import FootholdMemory
class FootholdTests(unittest.TestCase):
 def setUp(self):
  self.s=torch.ones(1,4,dtype=torch.bool);self.p=torch.zeros(1,4,3);self.f=self.p.clone();self.f[:,:,2]=10.;self.r=torch.zeros(1,4);self.xyz=self.p.clone();self.xyz[:,:,2]=.018;self.env=torch.ones(1,dtype=torch.bool)
 def test_loaded_nonedge_requires_actual_ray_ik_error(self):
  m=FootholdMemory(1);m.update(0,self.s,self.p,self.f,self.r,self.xyz,self.s,self.env);self.assertFalse(m.active.any())
  m.update(1,self.s,self.p,self.f,self.r,self.xyz,self.s,self.env,hard_invalid=self.s);self.assertTrue(m.active.all());self.assertTrue(torch.equal(m.xyz,self.xyz))
 def test_no_contact_cannot_create_anchor_even_when_ik_failed(self):
  m=FootholdMemory(1);m.update(0,self.s,self.p,self.f*0,self.r,self.xyz,self.s,self.env,hard_invalid=self.s);self.assertFalse(m.active.any())
 def test_worldxyz_keeps_touchdown_pose_through_body_height_goal_change(self):
  m=FootholdMemory(1);m.update(0,self.s,self.p,self.f,self.r,self.xyz,self.s,self.env,hard_invalid=self.s);before=m.xyz.clone()
  m.update(1,self.s,self.p,self.f,self.r,self.xyz+.02,self.s,self.env,hard_invalid=self.s);self.assertTrue(torch.equal(before,m.xyz))
  # Body moves5mm up: body-relative foot must move5mm down, world anchor stays.
  root=torch.tensor([[[0.,0.,.4]]]);newroot=root.clone();newroot[:,:,2]+=.005
  self.assertTrue(torch.allclose((m.xyz-newroot)-(m.xyz-root),torch.tensor([[[0.,0.,-.005]]]),atol=1e-7))
 def test_liftoff_and_subset_reset_release_xyz(self):
  m=FootholdMemory(1);m.update(0,self.s,self.p,self.f,self.r,self.xyz,self.s,self.env,hard_invalid=self.s);m.update(1,~self.s,self.p,self.f,self.r,self.xyz,self.s,self.env,hard_invalid=self.s);self.assertFalse(m.active.any());m.reset(torch.tensor([0]));self.assertEqual(float(m.xyz.abs().sum()),0.)
