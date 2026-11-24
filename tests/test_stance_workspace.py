import unittest
import json
from pathlib import Path
import torch
from csdog_motion.stance_workspace import repair_stance,EPS
from csdog_motion.trajectory import LegKinematics
from csdog_motion.calibration import ASSET

class BoxLeg:
    def __init__(self):
        self.lower=torch.full((4,3),-1.);self.upper=torch.ones(4,3)
    def solve(self,target,**kwargs):
        q=torch.maximum(torch.minimum(target,self.upper),self.lower)
        return q,(q-target).norm(dim=-1)

class StanceWorkspaceTests(unittest.TestCase):
    def case(self):
        m=BoxLeg();p=torch.zeros(1,4,3);p[0,0,2]=-1.02
        endpoint=p.clone();endpoint[0,0,2]=-.97
        eligible=torch.tensor([[True,False,False,False]])
        q,e=m.solve(p)
        return m,p,endpoint,eligible,q,e
    def test_reachable_reference_and_other_legs_are_bitwise_preserved(self):
        m,p,b,mask,q,e=self.case();p[0,0,2]=-.95;q,e=m.solve(p)
        r=repair_stance(m,p,b,mask,q,e)
        self.assertTrue(torch.equal(r[0],p));self.assertTrue(torch.equal(r[1],q));self.assertTrue(torch.equal(r[2],e));self.assertFalse(r[-1].any())
    def test_projection_retains_more_support_feedback_than_full_lock(self):
        m,p,b,mask,q,e=self.case();r=repair_stance(m,p,b,mask,q,e)
        self.assertTrue(r[-1][0,0]);self.assertGreater(float(r[3][0,0]),.59);self.assertLess(float(r[3][0,0]),.61)
        self.assertLessEqual(float(r[2].max()),EPS);self.assertGreaterEqual(float((r[1]-m.lower)[0,0].min()),.01-1e-7)
        self.assertTrue(torch.equal(r[0][~mask],p[~mask]));self.assertTrue(torch.equal(r[1][~mask],q[~mask]));self.assertTrue(torch.equal(r[0][:,:,:2],p[:,:,:2]))
    def test_no_measured_loaded_stance_cannot_be_repaired(self):
        m,p,b,mask,q,e=self.case();r=repair_stance(m,p,b,~mask&False,q,e)
        self.assertTrue(torch.equal(r[1],q));self.assertGreater(float(r[2].max()),EPS)
    def test_unreachable_measured_endpoint_is_a_hard_failure(self):
        m,p,b,mask,q,e=self.case();b[0,0,2]=-1.01
        with self.assertRaisesRegex(RuntimeError,'No reachable loaded stance'):repair_stance(m,p,b,mask,q,e)
    def test_endpoint_without_joint_reserve_is_rejected(self):
        m,p,b,mask,q,e=self.case();b[0,0,2]=-.995
        with self.assertRaisesRegex(RuntimeError,'original joint reserve'):repair_stance(m,p,b,mask,q,e)
    def test_nonfinite_loaded_endpoint_is_rejected(self):
        m,p,b,mask,q,e=self.case();b[0,0,2]=float('nan')
        with self.assertRaisesRegex(RuntimeError,'Nonfinite'):repair_stance(m,p,b,mask,q,e)
    def test_recorded_compound_stance_failure_keeps_most_nominal_height_feedback(self):
        fixture=json.loads((Path(__file__).parent/'fixtures/stance_support_18979.json').read_text())
        m=LegKinematics(ASSET/'robot_sim.urdf',fixture['nominal'],offset_bound=.5)
        self.assertTrue(torch.allclose(m.lower,torch.tensor(fixture['lower']),atol=1e-7))
        self.assertTrue(torch.allclose(m.upper,torch.tensor(fixture['upper']),atol=1e-7))
        preferred=torch.tensor(fixture['preferred']);endpoint=torch.tensor(fixture['endpoint']);q,e=m.solve(preferred,iterations=18)
        self.assertGreater(float(e[0,0]),.001)
        mask=torch.tensor([[True,False,False,False]])
        result=repair_stance(m,preferred,endpoint,mask,q,e)
        self.assertLess(float(result[2].max()),EPS)
        self.assertLess(float(result[3][0,0]),.3)
        self.assertGreaterEqual(float(torch.minimum(result[1]-m.lower,m.upper-result[1])[mask].min()),.01-1e-7)
        self.assertTrue(torch.equal(result[1][~mask],q[~mask]))
