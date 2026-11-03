
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
from typing import Protocol, runtime_checkable

from dogfight_v0.battle.types import VelocityCommand


@runtime_checkable
class LocomotionInterface(Protocol):
    def reset(self) -> None: ...
    def set_command(self, command: VelocityCommand) -> None: ...
    def compute_action(self, observation: object) -> object: ...
    def step(self, dt: float) -> None: ...

