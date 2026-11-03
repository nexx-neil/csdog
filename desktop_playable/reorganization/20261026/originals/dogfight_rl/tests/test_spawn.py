
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
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

