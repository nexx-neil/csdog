import unittest,json
from pathlib import Path
import torch
from csdog_motion.workspace_height import HeightCoordinator,HeightPlanConfig,select_height,contract
from csdog_motion.trajectory import LegKinematics
from csdog_motion.calibration import ASSET
from csdog_motion.residual_learning import learning_profile

class WorkspaceHeightTests(unittest.TestCase):
 def test_contract_roundtrips_through_checkpoint_json_without_mutating_parent(self):
  parent={'height':{'nominal_m':.37},'schema_version':33,'compatibility_tag':'parent'}
  before=json.loads(json.dumps(parent));new=contract(parent)
  self.assertEqual(new,json.loads(json.dumps(new)));self.assertEqual(parent,before)
 def test_recorded_opposite_failures_produce_opposite_geometric_height_goals(self):
  r=Path(__file__).resolve().parents[1];p=learning_profile();model=LegKinematics(ASSET/'robot_sim.urdf',p['nominal_joint_positions_rad'],offset_bound=.5)
  grid=torch.linspace(-.03,.03,13);grid[6]=0
  fixtures=json.loads((r/'tests/fixtures/terrain_workspace_targets.json').read_text())
  for kind,sign in [('blocks',-1),('compound',1)]:
   d=fixtures[kind];target=torch.tensor(d['target']);n=len(target);shift=target[:,None].expand(-1,13,-1,-1).clone();shift[:,:,:,2]-=grid[None,:,None]
   q,e=model.solve(shift.reshape(n*13,4,3),iterations=64);margin=torch.minimum(q-model.lower,model.upper-q).amin(2)
   goal,good=select_height(e.reshape(n,13,1,4),margin.reshape(n,13,1,4),grid,torch.zeros(n));self.assertTrue(good.all());self.assertGreaterEqual(float(goal[d['affected_environment']]*sign),.005-1e-7)
 def test_height_motion_is_continuous_bounded_and_repeated_quiet_state_is_exact_zero(self):
  c=HeightCoordinator(2);zero=c.value.clone()
  for _ in range(10):c.tick(.02,torch.ones(2,dtype=torch.bool))
  self.assertTrue(torch.equal(c.value,zero))
  c.goal[:]=torch.tensor([.025,-.025]);last=c.value.clone();lastv=c.velocity.clone()
  for i in range(150):
   if i==60:c.goal.neg_()
   c.tick(.02,torch.ones(2,dtype=torch.bool));self.assertLessEqual(float(c.value.abs().max()),.03);self.assertLessEqual(float((c.value-last).abs().max()/.02),.120001);self.assertLessEqual(float((c.velocity-lastv).abs().max()/.02),.80001);last=c.value.clone();lastv=c.velocity.clone()
  c.reset(torch.tensor([0]));self.assertEqual(float(c.value[0]),0);self.assertEqual(float(c.velocity[0]),0)
