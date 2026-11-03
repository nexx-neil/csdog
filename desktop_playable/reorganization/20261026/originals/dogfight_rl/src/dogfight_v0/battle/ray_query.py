from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import sqrt
from typing import Protocol, runtime_checkable

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.arena.test_map import WallSpec
from dogfight_v0.battle.types import RayHit


@runtime_checkable
class RayQueryInterface(Protocol):
    def raycast_closest(self, origin: tuple[float, float, float], direction: tuple[float, float, float], max_distance: float) -> RayHit: ...


def agent_id_from_path(path: str | None, agents: dict[str, AgentInterface]) -> str | None:
    if path is None:
        return None
    for agent_id, agent in agents.items():
        if path == agent.prim_path or path.startswith(agent.prim_path + "/"):
            return agent_id
    return None


class AnalyticRayQuery:
    """Deterministic geometry backend for fast rule tests; Isaac runtime uses PhysX."""

    def __init__(self, walls: list[WallSpec], agents: dict[str, AgentInterface], agent_radius_m: float = 0.4) -> None:
        self.walls = walls
        self.agents = agents
        self.agent_radius_m = agent_radius_m

    def raycast_closest(self, origin: tuple[float, float, float], direction: tuple[float, float, float], max_distance: float) -> RayHit:
        dx, dy, dz = direction
        norm = sqrt(dx * dx + dy * dy + dz * dz)
        if norm <= 1e-12:
            return RayHit(False)
        direction = (dx / norm, dy / norm, dz / norm)
        hits: list[tuple[float, str]] = []
        for wall in self.walls:
            distance = self._ray_aabb(origin, direction, wall)
            if distance is not None and 0.0 <= distance <= max_distance:
                hits.append((distance, wall.path))
        for agent in self.agents.values():
            if not agent.is_alive():
                continue
            p = agent.get_pose()
            distance = self._ray_circle_xy(origin, direction, (p.x, p.y), self.agent_radius_m)
            if distance is not None and 1e-5 <= distance <= max_distance:
                hits.append((distance, agent.prim_path))
        if not hits:
            return RayHit(False)
        distance, path = min(hits, key=lambda item: item[0])
        return RayHit(True, path, distance)

    @staticmethod
    def _ray_circle_xy(origin, direction, center, radius) -> float | None:
        ox, oy = origin[0] - center[0], origin[1] - center[1]
        dx, dy = direction[0], direction[1]
        a = dx * dx + dy * dy
        if a <= 1e-12:
            return None
        b = 2.0 * (ox * dx + oy * dy)
        c = ox * ox + oy * oy - radius * radius
        disc = b * b - 4.0 * a * c
        if disc < 0.0:
            return None
        root = sqrt(disc)
        roots = [value for value in ((-b - root) / (2.0 * a), (-b + root) / (2.0 * a)) if value >= 0.0]
        return min(roots) if roots else None

    @staticmethod
    def _ray_aabb(origin, direction, wall: WallSpec) -> float | None:
        bounds = tuple((c - s / 2.0, c + s / 2.0) for c, s in zip(wall.center, wall.size, strict=True))
        t_min, t_max = 0.0, float("inf")
        for o, d, (lo, hi) in zip(origin, direction, bounds, strict=True):
            if abs(d) < 1e-12:
                if o < lo or o > hi:
                    return None
                continue
            t1, t2 = (lo - o) / d, (hi - o) / d
            t_min, t_max = max(t_min, min(t1, t2)), min(t_max, max(t1, t2))
            if t_min > t_max:
                return None
        return t_min

