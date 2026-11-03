
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.types import Pose2D


def test_intel_updates_on_period_and_excludes_requester(core):
    service = IntelService(5.0)
    assert service.update(0.0, core["agents"])
    assert set(service.get_snapshot_for("dog_a")) == {"dog_b", "dog_c"}
    assert not service.update(4.999, core["agents"])
    assert service.update(5.0, core["agents"])


def test_intel_is_immutable_snapshot_and_records_dead(core):
    service = IntelService(5.0)
    service.update(0.0, core["agents"])
    old = service.get_last_known_position("dog_a", "dog_b")
    core["agents"]["dog_b"].reset(Pose2D(2.0, 1.0, 0.0))
    core["agents"]["dog_b"].set_alive(False)
    assert not service.update(2.0, core["agents"])
    assert service.get_last_known_position("dog_a", "dog_b") == old
    service.update(5.0, core["agents"])
    current = service.get_last_known_position("dog_a", "dog_b")
    assert (current.x, current.y, current.timestamp_s, current.alive) == (2.0, 1.0, 5.0, False)

