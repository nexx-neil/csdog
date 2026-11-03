
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from dogfight_v0.arena.spawn_manager import SpawnManager


def test_three_unique_data_driven_spawns(core):
    ids = list(core["agents"])
    result = SpawnManager().assign_spawns(ids, core["map"].get_spawn_points(), seed=7)
    assert set(result) == {"dog_a", "dog_b", "dog_c"}
    assert len({(pose.x, pose.y) for pose in result.values()}) == 3


def test_seed_is_repeatable(core):
    ids = list(core["agents"])
    points = core["map"].get_spawn_points()
    assert SpawnManager().assign_spawns(ids, points, 3) == SpawnManager().assign_spawns(ids, points, 3)

