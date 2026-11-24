import unittest
import numpy as np
from csdog_motion.terrain_library import compound_height,compound_mesh,LEVELS,WALKING_KINDS,SKILL_KINDS,scenario

class TerrainLibraryTests(unittest.TestCase):
 def test_compound_spawn_is_flat_and_ramp_steps_and_rubble_are_real(self):
  p=LEVELS['bridge'];x=np.array([0.,.75,1.,1.24,1.26,1.49,1.51,2.]);h=compound_height(x,np.zeros_like(x),.5,p)
  np.testing.assert_array_equal(h[:2],[0.,0.]);self.assertGreater(h[2],0);self.assertGreater(h[4]-h[3],.024);self.assertGreater(h[6]-h[5],.024);self.assertTrue(np.isfinite(h).all())
 def test_mesh_normals_and_origin_keep_spawn_on_surface(self):
  from types import SimpleNamespace
  mesh,origin=compound_mesh(.5,SimpleNamespace(size=(6.,6.),library_level='bridge'));m=mesh[0]
  np.testing.assert_array_equal(origin,[3.,3.,0.]);self.assertTrue((m.face_normals[:,2]>0).all());self.assertEqual(float(m.vertices[np.linalg.norm(m.vertices[:,:2]-origin[:2],axis=1).argmin(),2]),0.)
 def test_tiers_increase_geometry_and_skill_scenarios_remain_unvalidated(self):
  self.assertEqual(len(set(WALKING_KINDS)),12);self.assertEqual(len(set(SKILL_KINDS)),4)
  for a,b in zip(list(LEVELS.values()),list(LEVELS.values())[1:]):
   self.assertLess(a['slope_deg'],b['slope_deg']);self.assertLess(a['stairs_m'][1],b['stairs_m'][1]);self.assertLess(a['gap_m'][1],b['gap_m'][1])
  s=scenario('bridge','skills',12011,2);self.assertFalse(s['skill_group_robot_execution_enabled']);self.assertFalse(s['policy_trained_for_library'])
  with self.assertRaises(ValueError):scenario('bridge','skills',1,3)
