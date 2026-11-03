from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import atan2, hypot

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.battle.ray_query import RayQueryInterface, agent_id_from_path
from dogfight_v0.battle.types import VisibilityResult, normalize_angle
from dogfight_v0.config.battle_cfg import BattleConfig


class VisibilityService:
    def __init__(self, config: BattleConfig, ray_query: RayQueryInterface, agents: dict[str, AgentInterface]) -> None:
        self.config = config
        self.ray_query = ray_query
        self.agents = agents

    def observe_target(self, observer: AgentInterface, target: AgentInterface) -> VisibilityResult:
        op, tp = observer.get_pose(), target.get_pose()
        dx, dy = tp.x - op.x, tp.y - op.y
        distance = hypot(dx, dy)
        yaw_error = normalize_angle(atan2(dy, dx) - op.yaw) if distance > 1e-12 else 0.0
        in_fov = distance <= self.config.vision_max_range_m and abs(yaw_error) <= self.config.vision_half_fov_rad
        los = False
        if observer.is_alive() and target.is_alive() and in_fov:
            origin = observer.get_muzzle_origin_world()
            target_point = (tp.x, tp.y, self.config.muzzle_height_m)
            vx, vy, vz = (target_point[i] - origin[i] for i in range(3))
            ray_distance = (vx * vx + vy * vy + vz * vz) ** 0.5
            if ray_distance <= 1e-9:
                los = True
            else:
                hit = self.ray_query.raycast_closest(origin, (vx / ray_distance, vy / ray_distance, vz / ray_distance), ray_distance + self.config.agent_hit_radius_m)
                los = not hit.hit or agent_id_from_path(hit.object_path, self.agents) == target.agent_id
        visible = observer.is_alive() and target.is_alive() and in_fov and los
        return VisibilityResult(observer.agent_id, target.agent_id, visible, in_fov, los, distance, yaw_error)

    def observe_all(self, observer: AgentInterface, candidates: list[AgentInterface]) -> list[VisibilityResult]:
        return [self.observe_target(observer, target) for target in candidates if target.agent_id != observer.agent_id]

