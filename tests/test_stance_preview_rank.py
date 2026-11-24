import unittest
from types import SimpleNamespace
import torch
from csdog_motion.stance_preview_rank import reachable_stance_forecast
from csdog_motion.workspace_height_priority import select_height

class PreviewRankTests(unittest.TestCase):
    def setUp(self):self.cfg=SimpleNamespace(solve_tolerance_m=.00005,joint_reserve_rad=.03)
    def test_partial_improvement_preserves_actual_bad_margin_and_not_full_feasibility(self):
        e=torch.full((1,1,1,4),.001);m=torch.zeros_like(e);ee=torch.zeros_like(e);em=torch.full_like(e,.02)
        ne,nm,use=reachable_stance_forecast(e,m,ee,em,torch.ones_like(e,dtype=torch.bool),self.cfg)
        self.assertTrue(use.all());self.assertTrue(torch.equal(nm,em))
        goal,good=select_height(ne,nm,torch.zeros(1),torch.zeros(1),self.cfg);self.assertFalse(good.any())
    def test_worse_measured_endpoint_cannot_replace_preferred(self):
        e=torch.zeros(1,1,1,4);m=torch.full_like(e,.05)
        ne,nm,use=reachable_stance_forecast(e,m,e+.01,m-.04,torch.ones_like(e,dtype=torch.bool),self.cfg)
        self.assertFalse(use.any());self.assertTrue(torch.equal(ne,e));self.assertTrue(torch.equal(nm,m))
    def test_no_continuing_anchor_or_liftoff_preserves_original_constraint(self):
        e=torch.full((1,1,2,4),.001);m=torch.zeros_like(e);keep=torch.ones_like(e,dtype=torch.bool);keep[:,:,1:]=False
        ne,nm,use=reachable_stance_forecast(e,m,e*0,m+.05,keep,self.cfg)
        self.assertTrue(torch.equal(use,keep));self.assertTrue(torch.equal(ne[:,:,1:],e[:,:,1:]));self.assertTrue(torch.equal(nm[:,:,1:],m[:,:,1:]))
    def test_unreachable_endpoint_residual_is_never_zeroed(self):
        e=torch.full((1,1,1,4),.003);ee=e/2;m=torch.zeros_like(e)
        ne,nm,use=reachable_stance_forecast(e,m,ee,m,torch.ones_like(e,dtype=torch.bool),self.cfg)
        self.assertTrue(use.all());self.assertTrue(torch.equal(ne,ee));_,good=select_height(ne,nm,torch.zeros(1),torch.zeros(1),self.cfg);self.assertFalse(good.any())
