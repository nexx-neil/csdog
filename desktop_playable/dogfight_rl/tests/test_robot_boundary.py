"""Explicit robot identity/frame parameters prevent old model defaults leaking into new agents."""
from math import isclose
from types import SimpleNamespace
import torch
from dogfight.robots.csdog_12dof import URDF, declared_joint_names
from dogfight_v0.agents.real_dog_agent import RealDogAgent
from dogfight_v0.agents.real_locomotion_adapter import MockRealLocomotionAdapter
from dogfight_v0.battle.types import Pose2D
from dogfight_v0.config.battle_cfg import BattleConfig

class Articulation:
    device = "cpu"
    def __init__(self):
        self.data = SimpleNamespace(root_pos_w=torch.zeros(1, 3), root_quat_w=torch.tensor([[1., 0., 0., 0.]]),
                                    default_joint_pos=torch.zeros(1, 2))
    def write_root_pose_to_sim(self, value, ids):
        self.data.root_pos_w[ids] = value[:, :3]
        self.data.root_quat_w[ids] = value[:, 3:]
    def write_root_velocity_to_sim(self, value, ids):
        assert torch.count_nonzero(value) == 0
    def write_joint_state_to_sim(self, position, velocity, effort, ids):
        assert torch.count_nonzero(velocity) == 0

def test_new_raw_model_has_distinct_joint_identity():
    assert URDF.is_file()
    names = declared_joint_names()
    assert len(names) == 12 and len(set(names)) == 12
    assert set(names) == {f"joint_{leg}_{index}" for leg in ["lf", "lr", "rf", "rr"] for index in [1, 2, 3]}

def test_agent_identity_frame_and_height_are_explicit():
    for identity, height, offset in [("dog_b", 0.6, 0.0), ("dog_c", 0.7, 0.4)]:
        articulation = Articulation()
        agent = RealDogAgent(articulation, MockRealLocomotionAdapter(2), BattleConfig(),
            agent_id=identity, root_height_m=height, articulation_yaw_from_agent_yaw=offset,
            prim_path=f"/World/{identity}")
        agent.reset(Pose2D(1.2, -2.3, 0.8))
        assert agent.agent_id == identity and agent.prim_path == f"/World/{identity}"
        assert isclose(agent.get_pose().yaw, 0.8, abs_tol=1e-6)
        assert isclose(float(articulation.data.root_pos_w[0, 2]), height, abs_tol=1e-6)
