from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import isclose, pi

import torch

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.agents.dog_a_locomotion_adapter import DogALocomotionAdapter, EXPECTED_JOINT_ORDER
from dogfight_v0.agents.locomotion_interface import LocomotionInterface
from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.agents.real_dog_agent import RealDogAgent
from dogfight_v0.arena.spawn_manager import SpawnManager
from dogfight_v0.arena.test_map import TestMap as ArenaMap
from dogfight_v0.battle.battle_manager import BattleManager
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.ray_query import AnalyticRayQuery
from dogfight_v0.battle.scripted_policy import ScriptedBattlePolicy
from dogfight_v0.battle.types import Pose2D, VelocityCommand
from dogfight_v0.battle.visibility_service import VisibilityService
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.config.battle_cfg import BattleConfig
from dogfight_v0.logging.battle_logger import BattleLogger
from dogfight_v0.navigation.simple_navigation import SimpleNavigation


class FakeData:
    def __init__(self) -> None:
        self.root_pos_w = torch.tensor([[0.0, 0.0, 0.145]])
        self.root_quat_w = torch.tensor([[1.0, 0.0, 0.0, 0.0]])
        self.default_joint_pos = torch.zeros((1, 12))
        self.default_joint_vel = torch.zeros((1, 12))


class FakeArticulation:
    device = "cpu"
    joint_names = list(EXPECTED_JOINT_ORDER)

    def __init__(self) -> None:
        self.data = FakeData()
        self.root_velocity = torch.ones((1, 6))
        self.joint_velocity = torch.ones((1, 12))
        self.joint_position = torch.ones((1, 12))

    def write_root_pose_to_sim(self, value, env_ids) -> None:
        self.data.root_pos_w[env_ids] = value[:, :3]
        self.data.root_quat_w[env_ids] = value[:, 3:7]

    def write_root_velocity_to_sim(self, value, env_ids) -> None:
        self.root_velocity[env_ids] = value

    def write_joint_state_to_sim(self, position, velocity, _effort, env_ids) -> None:
        self.joint_position[env_ids] = position
        self.joint_velocity[env_ids] = velocity


class FakeEnvironment:
    device = "cpu"
    num_envs = 1
    step_dt = 1.0 / 60.0
    _command_frame = "body"

    def __init__(self) -> None:
        self._robot = FakeArticulation()
        self._commands = torch.zeros((1, 3))
        self._actions = torch.zeros((1, 12))
        self._previous_actions = torch.zeros((1, 12))
        self._raw_policy_actions = torch.zeros((1, 12))
        self._scaled_policy_actions = torch.zeros((1, 12))
        self._fixed_vx_cmd = None
        self._fixed_vy_cmd = None

    def _get_observations(self):
        observation = torch.zeros((1, 48))
        observation[:, 9:12] = self._commands
        observation[:, 36:48] = self._previous_actions
        return {"policy": observation}

    def reset(self):
        self._robot.data.root_pos_w[:] = torch.tensor([[0.0, 0.0, 0.145]])
        self._robot.data.root_quat_w[:] = torch.tensor([[1.0, 0.0, 0.0, 0.0]])
        return self._get_observations(), {}

    def step(self, action):
        self._actions[:] = action
        self._previous_actions[:] = action
        false = torch.tensor([False])
        return self._get_observations(), torch.zeros(1), false, false, {}


def make_real(config: BattleConfig | None = None):
    config = config or BattleConfig()
    env = FakeEnvironment()
    actor = torch.nn.Sequential(torch.nn.Linear(48, 12))
    torch.nn.init.zeros_(actor[0].weight)
    torch.nn.init.zeros_(actor[0].bias)
    adapter = DogALocomotionAdapter(
        env, actor, config, actor_output_scale=0.5, checkpoint_path="/tmp/model_final.pt"
    )
    return RealDogAgent(env._robot, adapter, config), adapter, env


def test_01_id_and_protocols():
    agent, adapter, _ = make_real()
    assert agent.agent_id == "dog_a"
    assert isinstance(agent, AgentInterface)
    assert isinstance(adapter, LocomotionInterface)


def test_02_pose_is_finite_rad_and_reset_exact():
    agent, _, _ = make_real()
    agent.reset(Pose2D(1.25, -2.5, 0.4))
    pose = agent.get_pose()
    assert isclose(pose.x, 1.25) and isclose(pose.y, -2.5)
    assert isclose(pose.yaw, 0.4, abs_tol=1.0e-6)
    assert -pi <= pose.yaw <= pi


def test_03_forward_yaw_zero_is_world_positive_x():
    agent, _, _ = make_real()
    agent.reset(Pose2D(0.0, 0.0, 0.0))
    forward = agent.get_forward_vector_world()
    assert isclose(forward[0], 1.0, abs_tol=1.0e-6)
    assert isclose(forward[1], 0.0, abs_tol=1.0e-6)
    assert forward[2] == 0.0


def test_04_forward_command_maps_to_trained_policy_forward():
    agent, adapter, _ = make_real()
    agent.set_velocity_command(VelocityCommand(0.2, 0.0, 0.0))
    assert adapter.policy_command == (0.0, 0.2, 0.0)
    adapter.compute_action()


def test_05_positive_lateral_is_left_and_maps_to_policy_negative_x():
    agent, adapter, _ = make_real()
    agent.set_velocity_command(VelocityCommand(0.0, 0.3, 0.0))
    assert adapter.policy_command == (-0.3, 0.0, 0.0)


def test_06_positive_yaw_preserves_counterclockwise_sign():
    agent, adapter, _ = make_real()
    agent.set_velocity_command(VelocityCommand(0.0, 0.0, 0.7))
    assert adapter.policy_command == (0.0, 0.0, 0.7)


def test_07_clamp_and_stop_are_velocity_commands_only():
    config = BattleConfig(max_vx=0.2, max_vy=0.3, max_yaw_rate=0.4)
    agent, adapter, _ = make_real(config)
    agent.set_velocity_command(VelocityCommand(9.0, -9.0, 9.0))
    assert adapter.command == VelocityCommand(0.2, -0.3, 0.4)
    agent.stop()
    assert adapter.command == VelocityCommand()
    assert adapter.policy_command == (0.0, 0.0, 0.0)


def test_08_reset_clears_velocity_command_action_and_policy_state():
    agent, adapter, env = make_real()
    agent.set_velocity_command(VelocityCommand(0.2, 0.1, 0.3))
    agent.update(env.step_dt)
    before = adapter.policy_reset_count
    agent.reset(Pose2D(-1.0, 2.0, -0.5))
    assert adapter.policy_reset_count == before + 1
    assert agent.last_velocity_command == VelocityCommand()
    assert adapter.command == VelocityCommand()
    assert torch.count_nonzero(env._previous_actions) == 0
    assert torch.count_nonzero(env._robot.root_velocity) == 0
    assert torch.count_nonzero(env._robot.joint_velocity) == 0
    assert torch.equal(env._robot.joint_position, env._robot.data.default_joint_pos)


def test_09_battle_manager_accepts_real_dog_a_and_two_proxies(tmp_path):
    config = BattleConfig()
    arena = ArenaMap()
    dog_a, _, _ = make_real(config)
    agents = {
        "dog_a": dog_a,
        "dog_b": ProxyAgent("dog_b", "/World/Agents/dog_b"),
        "dog_c": ProxyAgent("dog_c", "/World/Agents/dog_c"),
    }
    query = AnalyticRayQuery(arena.walls, agents, config.agent_hit_radius_m)
    manager = BattleManager(
        config, arena, SpawnManager(), agents, SimpleNavigation(config),
        IntelService(config.intel_period_s), VisibilityService(config, query, agents),
        WeaponService(config, query), HealthSystem(config.max_health),
        {name: ScriptedBattlePolicy(config) for name in agents}, BattleLogger(tmp_path, echo=False),
    )
    manager.reset(seed=7)
    manager.start_round()
    assert manager.agents["dog_a"] is dog_a
    assert set(manager.agents) == {"dog_a", "dog_b", "dog_c"}
