
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from math import pi

from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.types import Pose2D


def test_wall_blocks_shot_and_agent_hit_damages(core):
    agents, weapon = core["agents"], core["weapon"]
    agents["dog_a"].reset(Pose2D(-2.0, 0.0, 0.0))
    agents["dog_b"].reset(Pose2D(2.0, 0.0, pi))
    agents["dog_c"].reset(Pose2D(0.0, 4.0, 0.0))
    blocked = weapon.fire(agents["dog_a"], agents, 0.0)
    assert blocked.fired and not blocked.hit and "wall_center" in blocked.hit_object_path
    weapon.reset()
    agents["dog_a"].reset(Pose2D(-4.0, -4.0, 0.0))
    agents["dog_b"].reset(Pose2D(-2.0, -4.0, pi))
    agents["dog_c"].reset(Pose2D(0.0, 4.0, 0.0))
    hit = weapon.fire(agents["dog_a"], agents, 0.0)
    assert hit.hit and hit.hit_agent_id == "dog_b"
    health = HealthSystem(core["config"].max_health); health.reset(list(agents))
    health.apply_damage(hit.hit_agent_id, hit.damage, "dog_a")
    assert health.get_health("dog_b") == core["config"].max_health - core["config"].weapon_damage


def test_cooldown(core):
    agents, weapon = core["agents"], core["weapon"]
    agents["dog_a"].reset(Pose2D(-4.0, -4.0, 0.0))
    agents["dog_b"].reset(Pose2D(-2.0, -4.0, pi))
    assert weapon.fire(agents["dog_a"], agents, 3.0).fired
    assert not weapon.fire(agents["dog_a"], agents, 3.5).fired
    assert weapon.fire(agents["dog_a"], agents, 4.0).fired
