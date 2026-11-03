from __future__ import annotations


from collections.abc import Callable
from math import cos, sin

from dogfight_v0.battle.types import Pose2D, VelocityCommand, normalize_angle


class ProxyAgent:
    """Kinematic V0 agent implementing the same velocity contract as future dogs."""

    def __init__(
        self,
        agent_id: str,
        prim_path: str,
        muzzle_height_m: float = 0.45,
        muzzle_forward_offset_m: float = 0.55,
        pose_writer: Callable[[str, Pose2D], None] | None = None,
        position_validator: Callable[[float, float], bool] | None = None,
    ) -> None:
        self._agent_id = agent_id
        self._prim_path = prim_path
        self._pose = Pose2D(0.0, 0.0, 0.0)
        self._command = VelocityCommand()
        self._alive = True
        self._muzzle_height_m = muzzle_height_m
        self._muzzle_forward_offset_m = muzzle_forward_offset_m
        self._pose_writer = pose_writer
        self._position_validator = position_validator

    @property
    def agent_id(self) -> str:
        return self._agent_id

    @property
    def prim_path(self) -> str:
        return self._prim_path

    @property
    def last_velocity_command(self) -> VelocityCommand:
        c = self._command
        return VelocityCommand(c.vx, c.vy, c.yaw_rate)

    def reset(self, pose: Pose2D) -> None:
        self._pose = Pose2D(pose.x, pose.y, normalize_angle(pose.yaw))
        self._alive = True
        self.stop()
        self._sync_pose()

    def get_pose(self) -> Pose2D:
        p = self._pose
        return Pose2D(p.x, p.y, p.yaw)

    def get_forward_vector_world(self) -> tuple[float, float, float]:
        return cos(self._pose.yaw), sin(self._pose.yaw), 0.0

    def get_muzzle_origin_world(self) -> tuple[float, float, float]:
        fx, fy, _ = self.get_forward_vector_world()
        return (
            self._pose.x + fx * self._muzzle_forward_offset_m,
            self._pose.y + fy * self._muzzle_forward_offset_m,
            self._muzzle_height_m,
        )

    def set_velocity_command(self, command: VelocityCommand) -> None:
        self._command = command if self._alive else VelocityCommand()

    def stop(self) -> None:
        self._command = VelocityCommand()

    def update(self, dt: float) -> None:
        if not self._alive or dt <= 0.0:
            return
        p, c = self._pose, self._command
        new_yaw = normalize_angle(p.yaw + c.yaw_rate * dt)
        dx = (cos(p.yaw) * c.vx - sin(p.yaw) * c.vy) * dt
        dy = (sin(p.yaw) * c.vx + cos(p.yaw) * c.vy) * dt
        new_x, new_y = p.x + dx, p.y + dy
        if self._position_validator is None or self._position_validator(new_x, new_y):
            self._pose = Pose2D(new_x, new_y, new_yaw)
        else:
            self._pose = Pose2D(p.x, p.y, new_yaw)
        self._sync_pose()

    def is_alive(self) -> bool:
        return self._alive

    def set_alive(self, alive: bool) -> None:
        self._alive = alive
        if not alive:
            self.stop()

    def _sync_pose(self) -> None:
        if self._pose_writer is not None:
            self._pose_writer(self._prim_path, self._pose)

