from __future__ import annotations


import random
from typing import Protocol, runtime_checkable

from dogfight_v0.battle.types import Pose2D


@runtime_checkable
class SpawnManagerInterface(Protocol):
    def assign_spawns(self, agent_ids: list[str], spawn_points: list[Pose2D], seed: int | None = None) -> dict[str, Pose2D]: ...
    def respawn(self, agent_id: str) -> Pose2D: ...


class SpawnManager:
    def __init__(self) -> None:
        self._assignments: dict[str, Pose2D] = {}

    def assign_spawns(self, agent_ids: list[str], spawn_points: list[Pose2D], seed: int | None = None) -> dict[str, Pose2D]:
        if len(agent_ids) != 3:
            raise ValueError("Dogfight V0 requires exactly three agents")
        if len(set(agent_ids)) != len(agent_ids) or len(spawn_points) < len(agent_ids):
            raise ValueError("Agent IDs must be unique and enough spawn points must exist")
        points = list(spawn_points)
        if seed is not None:
            random.Random(seed).shuffle(points)
        self._assignments = {
            agent_id: Pose2D(point.x, point.y, point.yaw)
            for agent_id, point in zip(agent_ids, points, strict=True)
        }
        return {key: Pose2D(p.x, p.y, p.yaw) for key, p in self._assignments.items()}

    def respawn(self, agent_id: str) -> Pose2D:
        if agent_id not in self._assignments:
            raise KeyError(f"No spawn assigned for {agent_id}")
        p = self._assignments[agent_id]
        return Pose2D(p.x, p.y, p.yaw)

