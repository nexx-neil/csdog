from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import atan2, cos, isfinite, pi, sin
from typing import Any

from dogfight_v0.agents.locomotion_interface import LocomotionInterface
from dogfight_v0.battle.types import Pose2D, VelocityCommand, normalize_angle
from dogfight_v0.config.battle_cfg import BattleConfig


class RealDogAgent:
    """DOGFIGHT-facing Dog A wrapper; low-level details stay in this boundary."""

    _AGENT_ID = "dog_a"
    # Existing Dog A validation identifies articulation +Y as anatomical front.
    _ARTICULATION_YAW_FROM_DOG_YAW = -pi / 2.0

    def __init__(
        self,
        articulation: Any,
        locomotion_adapter: LocomotionInterface,
        config: BattleConfig,
        *,
        prim_path: str = "/World/envs/env_0/Robot",
        environment_index: int = 0,
    ) -> None:
        self.articulation = articulation
        self.locomotion_adapter = locomotion_adapter
        self.config = config
        self._prim_path = prim_path
        self._environment_index = int(environment_index)
        self._alive = True
        self._last_velocity_command = VelocityCommand()

    @property
    def agent_id(self) -> str:
        return self._AGENT_ID

    @property
    def prim_path(self) -> str:
        return self._prim_path

    @property
    def last_velocity_command(self) -> VelocityCommand:
        value = self._last_velocity_command
        return VelocityCommand(value.vx, value.vy, value.yaw_rate)

    def reset(self, pose: Pose2D) -> None:
        import torch

        if not all(isfinite(value) for value in (pose.x, pose.y, pose.yaw)):
            raise ValueError("reset pose must be finite")
        self.locomotion_adapter.reset()
        index = self._environment_index
        env_ids = torch.tensor([index], dtype=torch.long, device=self.articulation.device)
        dog_yaw = normalize_angle(float(pose.yaw))
        articulation_yaw = dog_yaw + self._ARTICULATION_YAW_FROM_DOG_YAW
        half = articulation_yaw / 2.0
        root_pose = torch.tensor(
            [[pose.x, pose.y, self.config.dog_a_root_height_m, cos(half), 0.0, 0.0, sin(half)]],
            dtype=self.articulation.data.root_pos_w.dtype,
            device=self.articulation.device,
        )
        root_velocity = torch.zeros((1, 6), dtype=root_pose.dtype, device=root_pose.device)
        joint_position = self.articulation.data.default_joint_pos[env_ids].clone()
        joint_velocity = torch.zeros_like(joint_position)
        self.articulation.write_root_pose_to_sim(root_pose, env_ids)
        self.articulation.write_root_velocity_to_sim(root_velocity, env_ids)
        self.articulation.write_joint_state_to_sim(joint_position, joint_velocity, None, env_ids)
        self._alive = True
        self._last_velocity_command = VelocityCommand()
        self.locomotion_adapter.set_command(VelocityCommand())

    def get_pose(self) -> Pose2D:
        index = self._environment_index
        position = self.articulation.data.root_pos_w[index]
        quaternion = self.articulation.data.root_quat_w[index]
        w, x, y, z = (float(value) for value in quaternion)
        articulation_yaw = atan2(2.0 * (w * z + x * y), 1.0 - 2.0 * (y * y + z * z))
        dog_yaw = normalize_angle(articulation_yaw - self._ARTICULATION_YAW_FROM_DOG_YAW)
        pose = Pose2D(float(position[0]), float(position[1]), dog_yaw)
        if not all(isfinite(value) for value in (pose.x, pose.y, pose.yaw)):
            raise RuntimeError("Dog A returned a non-finite pose")
        return pose

    def get_forward_vector_world(self) -> tuple[float, float, float]:
        yaw = self.get_pose().yaw
        return cos(yaw), sin(yaw), 0.0

    def get_muzzle_origin_world(self) -> tuple[float, float, float]:
        pose = self.get_pose()
        forward_x, forward_y, _ = self.get_forward_vector_world()
        root_z = float(self.articulation.data.root_pos_w[self._environment_index, 2])
        return (
            pose.x + forward_x * self.config.muzzle_forward_offset_m,
            pose.y + forward_y * self.config.muzzle_forward_offset_m,
            root_z + self.config.muzzle_height_m,
        )

    def set_velocity_command(self, command: VelocityCommand) -> None:
        if not self._alive:
            command = VelocityCommand()
        self.locomotion_adapter.set_command(command)
        self._last_velocity_command = self.locomotion_adapter.command  # type: ignore[attr-defined]

    def stop(self) -> None:
        self.set_velocity_command(VelocityCommand())

    def update(self, dt: float) -> None:
        if self._alive:
            self.locomotion_adapter.step(dt)

    def is_alive(self) -> bool:
        return self._alive

    def set_alive(self, alive: bool) -> None:
        self._alive = bool(alive)
        if not self._alive:
            self.stop()
