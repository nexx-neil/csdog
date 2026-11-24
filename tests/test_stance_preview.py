import unittest
from types import SimpleNamespace
import torch
from csdog_motion.stance_preview import reachable_stance_forecast

class StancePreviewTests(unittest.TestCase):
    def setUp(self):self.cfg=SimpleNamespace(solve_tolerance_m=.00005,joint_reserve_rad=.03)
    def test_preferred_feasible_forecast_is_bitwise_preserved(self):
        e=torch.zeros(1,2,3,4);m=torch.full_like(e,.04);keep=torch.ones_like(e,dtype=torch.bool)
        ne,nm,use=reachable_stance_forecast(e,m,e+.00001,m+.05,keep,self.cfg)
        self.assertTrue(torch.equal(ne,e));self.assertTrue(torch.equal(nm,m));self.assertFalse(use.any())
    def test_reachable_endpoint_removes_conflicting_stance_constraint_only(self):
        e=torch.full((1,2,3,4),.001);m=torch.zeros_like(e);ee=torch.zeros_like(e);em=torch.full_like(e,.04);keep=torch.zeros_like(e,dtype=torch.bool);keep[0,0,0,0]=True
        ne,nm,use=reachable_stance_forecast(e,m,ee,em,keep,self.cfg)
        self.assertTrue(torch.equal(use,keep));self.assertEqual(float(ne[keep].max()),0.);self.assertTrue(torch.equal(ne[~keep],e[~keep]));self.assertTrue(torch.equal(nm[~keep],m[~keep]))
    def test_unreachable_or_insufficient_margin_endpoint_remains_rejected(self):
        e=torch.tensor([[[[.001,.001,.001,.001]]]]);m=torch.zeros_like(e);keep=torch.ones_like(e,dtype=torch.bool)
        for ee,em in [(torch.full_like(e,.001),torch.full_like(e,.04)),(torch.zeros_like(e),torch.full_like(e,.02))]:
            ne,nm,use=reachable_stance_forecast(e,m,ee,em,keep,self.cfg);self.assertFalse(use.any());self.assertTrue(torch.equal(ne,e));self.assertTrue(torch.equal(nm,m))
    def test_future_liftoff_cannot_reuse_current_contact(self):
        e=torch.full((1,1,3,4),.001);m=torch.zeros_like(e);ee=torch.zeros_like(e);em=torch.full_like(e,.04);keep=torch.ones_like(e,dtype=torch.bool);keep[:,:,1:]=False
        ne,nm,use=reachable_stance_forecast(e,m,ee,em,keep,self.cfg);self.assertTrue(use[:,:,0].all());self.assertFalse(use[:,:,1:].any());self.assertTrue(torch.equal(ne[:,:,1:],e[:,:,1:]))
