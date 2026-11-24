import unittest,torch
from csdog_motion.swing_workspace import allocate_swing
class ToyLeg:
 def __init__(self):
  self.lower=torch.full((4,3),-1.);self.upper=torch.ones(4,3);self.upper[:,2]=.05
 def solve(self,target,**kwargs):
  q=target.clone();q[:,:,2]=target[:,:,2].clamp_max(.03);return q,(target-q).norm(dim=-1)
class SwingTests(unittest.TestCase):
 def setup_case(self,full=.042,basic=.032):
  m=ToyLeg();b=torch.full((1,4),basic);s=torch.full((1,4),full-basic)
  def build(height):
   t=torch.zeros(1,4,3);t[:,:,2]=height;return t
  sensor=lambda scale:build(b+s*scale);total=lambda scale:build((b+s)*scale);q,e=m.solve(total(torch.ones(1,4)))
  return m,b,s,sensor,total,q,e
 def test_feasible_legacy_is_retained_exactly(self):
  m,b,s,sen,tot,q,e=self.setup_case(.025,.02);result=allocate_swing(m,sen,tot,q,e,b,s,torch.zeros_like(b),lambda t:torch.ones_like(b,dtype=torch.bool),torch.ones_like(b,dtype=torch.bool))
  self.assertTrue(torch.equal(result[0],q));self.assertTrue(torch.equal(result[1],e));self.assertFalse(result[-1].any());self.assertTrue(torch.equal(result[2],b+s))
 def test_infeasible_basic_lift_can_shorten_with_clearance_and_reserve(self):
  m,b,s,sen,tot,q,e=self.setup_case();r=allocate_swing(m,sen,tot,q,e,b,s,torch.full_like(b,.01/.042),lambda t:t[:,:,2]>=.01-1e-6,torch.ones_like(b,dtype=torch.bool))
  self.assertTrue(r[-1].all());self.assertTrue((r[1]<=.00005).all());self.assertTrue((r[2]>=.01).all());self.assertTrue((r[2]<.032).all());self.assertTrue((m.upper-r[0]).amin(2).ge(.01).all())
 def test_unreachable_minimum_clearance_is_a_hard_failure(self):
  m,b,s,sen,tot,q,e=self.setup_case()
  with self.assertRaisesRegex(RuntimeError,'minimum planned clearance'):allocate_swing(m,sen,tot,q,e,b,s,torch.full_like(b,.036/.042),lambda t:t[:,:,2]>=.036,torch.ones_like(b,dtype=torch.bool))
 def test_cannot_modify_infeasible_stance(self):
  m,b,s,sen,tot,q,e=self.setup_case()
  with self.assertRaisesRegex(RuntimeError,'Stance reference'):allocate_swing(m,sen,tot,q,e,b,s,torch.zeros_like(b),lambda t:torch.ones_like(b,dtype=torch.bool),torch.zeros_like(b,dtype=torch.bool))
 def test_clearance_geometry_veto_cannot_be_bypassed(self):
  m,b,s,sen,tot,q,e=self.setup_case()
  with self.assertRaisesRegex(RuntimeError,'minimum planned clearance'):allocate_swing(m,sen,tot,q,e,b,s,torch.zeros_like(b),lambda t:torch.zeros_like(b,dtype=torch.bool),torch.ones_like(b,dtype=torch.bool))
