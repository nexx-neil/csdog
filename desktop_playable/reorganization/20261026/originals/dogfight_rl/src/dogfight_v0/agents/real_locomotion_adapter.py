from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from typing import Any

from dogfight_v0.battle.types import VelocityCommand


class RealLocomotionAdapter:
    """Robot-agnostic skeleton from body velocity command to robot action.

    Future Dog A/B/C implementations own their observation construction,
    policy loading, joint ordering, gains, and actuator application. None of
    those details cross this boundary into battle code.
    """

    def __init__(self) -> None:
        self._command = VelocityCommand()

    @property
    def command(self) -> VelocityCommand:
        command = self._command
        return VelocityCommand(command.vx, command.vy, command.yaw_rate)

    def reset(self) -> None:
        self._command = VelocityCommand()

    def set_command(self, command: VelocityCommand) -> None:
        self._command = VelocityCommand(command.vx, command.vy, command.yaw_rate)

    def compute_action(self, observation: Any) -> object:
        del observation
        raise NotImplementedError("A concrete dog locomotion adapter must compute its own actuator action")

    def step(self, dt: float) -> None:
        del dt
        raise NotImplementedError("A concrete dog locomotion adapter must apply its own actuator action")


class MockRealLocomotionAdapter(RealLocomotionAdapter):
    """No-policy mock used to validate integration plumbing without PPO."""

    def __init__(self, action_size: int = 12) -> None:
        super().__init__()
        if action_size <= 0:
            raise ValueError("action_size must be positive")
        self.action_size = action_size
        self.step_count = 0
        self.last_dt = 0.0

    def reset(self) -> None:
        super().reset()
        self.step_count = 0
        self.last_dt = 0.0

    def compute_action(self, observation: Any) -> list[float]:
        del observation
        return [0.0] * self.action_size

    def step(self, dt: float) -> None:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        self.step_count += 1
        self.last_dt = float(dt)

