import unittest
import torch
from csdog_motion.trot_bounded import valid_request,cases,CAP
class BoundedTests(unittest.TestCase):
 def test_cap_is_rejected_before_shaping_and_holdout_stays_inside_declared_range(self):
  self.assertEqual(valid_request(torch.tensor([[.95,0,0],[.9501,0,0],[.95,.01,0],[-.5,0,0],[0,.4,0],[0,0,.8]])).tolist(),[True,False,False,True,True,True])
  for holdout in (False,True):
   rows=cases(holdout);values=[v for c in rows for _,v in c['profile']]
   self.assertTrue(valid_request(torch.tensor(values)).all());self.assertEqual(max(v[0]for v in values),CAP)
