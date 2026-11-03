
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
from typing import Protocol, runtime_checkable

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.battle.types import VelocityCommand


@runtime_checkable
class NavigationInterface(Protocol):
    def set_goal(self, agent_id: str, target_xy: tuple[float, float]) -> None: ...
    def clear_goal(self, agent_id: str) -> None: ...
    def has_goal(self, agent_id: str) -> bool: ...
    def goal_reached(self, agent_id: str) -> bool: ...
    def compute_command(self, agent: AgentInterface, dt: float) -> VelocityCommand: ...

