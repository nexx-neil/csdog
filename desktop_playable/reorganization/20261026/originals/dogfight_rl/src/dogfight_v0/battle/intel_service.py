from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.battle.types import IntelRecord


class IntelService:
    def __init__(self, period_s: float) -> None:
        if period_s <= 0.0:
            raise ValueError("Intel period must be positive")
        self.period_s = period_s
        self.reset()

    def reset(self, start_time_s: float = 0.0) -> None:
        self._snapshots: dict[str, dict[str, IntelRecord]] = {}
        self._next_update_s = start_time_s
        self.last_update_s: float | None = None

    def update(self, current_time_s: float, agents: dict[str, AgentInterface]) -> bool:
        if current_time_s + 1e-9 < self._next_update_s:
            return False
        # Schedule from the configured grid, avoiding drift after a long frame.
        while self._next_update_s <= current_time_s + 1e-9:
            self._next_update_s += self.period_s
        records: dict[str, IntelRecord] = {}
        for target_id, target in agents.items():
            pose = target.get_pose()
            records[target_id] = IntelRecord(target_id, pose.x, pose.y, current_time_s, target.is_alive())
        self._snapshots = {
            requester_id: {target_id: record for target_id, record in records.items() if target_id != requester_id}
            for requester_id in agents
        }
        self.last_update_s = current_time_s
        return True

    def get_last_known_position(self, requester_id: str, target_id: str) -> IntelRecord | None:
        return self._snapshots.get(requester_id, {}).get(target_id)

    def get_snapshot_for(self, requester_id: str) -> dict[str, IntelRecord]:
        return dict(self._snapshots.get(requester_id, {}))

