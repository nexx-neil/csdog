
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from math import pi

from dogfight_v0.battle.types import Pose2D


def test_fov_los_and_yaw_sign(core):
    a, b = core["agents"]["dog_a"], core["agents"]["dog_b"]
    a.reset(Pose2D(-4.0, -4.0, 0.0))
    b.reset(Pose2D(-2.0, -4.0, pi))
    clear = core["visibility"].observe_target(a, b)
    assert clear.visible and clear.line_of_sight and clear.in_fov
    b.reset(Pose2D(-2.0, -3.0, pi))
    assert core["visibility"].observe_target(a, b).yaw_error_rad > 0.0
    b.reset(Pose2D(-2.0, -4.5, pi))
    assert core["visibility"].observe_target(a, b).yaw_error_rad < 0.0
    b.reset(Pose2D(-5.0, -4.0, pi))
    assert not core["visibility"].observe_target(a, b).in_fov


def test_wall_blocks_los(core):
    a, b = core["agents"]["dog_a"], core["agents"]["dog_b"]
    a.reset(Pose2D(-2.0, 0.0, 0.0))
    b.reset(Pose2D(2.0, 0.0, pi))
    result = core["visibility"].observe_target(a, b)
    assert result.in_fov and not result.line_of_sight and not result.visible

