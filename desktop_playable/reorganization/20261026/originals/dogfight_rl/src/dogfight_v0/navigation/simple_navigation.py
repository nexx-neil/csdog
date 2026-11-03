from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import atan2, cos, hypot, sin

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.battle.types import VelocityCommand, normalize_angle
from dogfight_v0.config.battle_cfg import BattleConfig


def _clamp(value: float, limit: float) -> float:
    return max(-limit, min(limit, value))


class SimpleNavigation:
    """Direct target seeking; replaceable by graph/NavMesh navigation."""

    def __init__(self, config: BattleConfig) -> None:
        self._config = config
        self._goals: dict[str, tuple[float, float]] = {}
        self._reached: dict[str, bool] = {}

    def set_goal(self, agent_id: str, target_xy: tuple[float, float]) -> None:
        self._goals[agent_id] = (float(target_xy[0]), float(target_xy[1]))
        self._reached[agent_id] = False

    def clear_goal(self, agent_id: str) -> None:
        self._goals.pop(agent_id, None)
        self._reached.pop(agent_id, None)

    def has_goal(self, agent_id: str) -> bool:
        return agent_id in self._goals

    def goal_reached(self, agent_id: str) -> bool:
        return self._reached.get(agent_id, False)

    def get_goal(self, agent_id: str) -> tuple[float, float] | None:
        return self._goals.get(agent_id)

    def reset(self) -> None:
        self._goals.clear()
        self._reached.clear()

    def compute_command(self, agent: AgentInterface, dt: float) -> VelocityCommand:
        del dt
        goal = self._goals.get(agent.agent_id)
        if goal is None or not agent.is_alive():
            return VelocityCommand()
        pose = agent.get_pose()
        dx, dy = goal[0] - pose.x, goal[1] - pose.y
        distance = hypot(dx, dy)
        if distance <= self._config.goal_reached_tolerance_m:
            self._reached[agent.agent_id] = True
            return VelocityCommand()
        self._reached[agent.agent_id] = False
        yaw_error = normalize_angle(atan2(dy, dx) - pose.yaw)
        forward = cos(yaw_error) * min(self._config.max_vx, distance)
        lateral = sin(yaw_error) * min(self._config.max_vy, distance)
        # Reduce translation while facing away; this keeps proxy motion stable.
        alignment = max(0.0, cos(yaw_error))
        return VelocityCommand(
            vx=_clamp(forward * alignment, self._config.max_vx),
            vy=_clamp(lateral * 0.5, self._config.max_vy),
            yaw_rate=_clamp(2.0 * yaw_error, self._config.max_yaw_rate),
        )

