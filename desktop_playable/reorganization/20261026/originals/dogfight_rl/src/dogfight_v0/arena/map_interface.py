
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
from typing import Protocol, runtime_checkable

from dogfight_v0.battle.types import Pose2D


@runtime_checkable
class MapInterface(Protocol):
    def load(self) -> None: ...
    def reset(self, seed: int | None = None) -> None: ...
    def get_bounds(self) -> tuple[float, float, float, float]: ...
    def get_spawn_points(self) -> list[Pose2D]: ...
    def get_navigation_data(self) -> object: ...
    def is_position_valid(self, x: float, y: float) -> bool: ...

