
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
from dogfight_v0.agents.locomotion_interface import LocomotionInterface
from dogfight_v0.agents.real_locomotion_adapter import MockRealLocomotionAdapter, RealLocomotionAdapter
from dogfight_v0.battle.types import VelocityCommand


def test_mock_locomotion_adapter_obeys_velocity_contract_without_policy():
    adapter = MockRealLocomotionAdapter()
    command = VelocityCommand(1.0, -0.2, 0.4)
    adapter.set_command(command)
    adapter.step(0.02)
    assert adapter.command == command
    assert adapter.compute_action(None) == [0.0] * 12
    assert adapter.step_count == 1
    assert isinstance(adapter, LocomotionInterface)


def test_base_real_locomotion_requires_concrete_robot_implementation():
    import pytest

    adapter = RealLocomotionAdapter()
    with pytest.raises(NotImplementedError):
        adapter.compute_action(None)
    with pytest.raises(NotImplementedError):
        adapter.step(0.02)
