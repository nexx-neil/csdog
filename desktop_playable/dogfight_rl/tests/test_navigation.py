
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from dogfight_v0.battle.types import Pose2D, VelocityCommand
from dogfight_v0.navigation.simple_navigation import SimpleNavigation


def test_navigation_uses_velocity_contract_and_approaches(core):
    agent = core["agents"]["dog_a"]
    agent.reset(Pose2D(-4.0, -4.0, 0.0))
    navigation = SimpleNavigation(core["config"])
    navigation.set_goal("dog_a", (-2.0, -4.0))
    start = agent.get_pose().x
    for _ in range(40):
        command = navigation.compute_command(agent, 0.05)
        assert isinstance(command, VelocityCommand)
        agent.set_velocity_command(command)
        agent.update(0.05)
    assert agent.get_pose().x > start

