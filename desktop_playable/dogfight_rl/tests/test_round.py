
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.agents.locomotion_interface import LocomotionInterface
from dogfight_v0.agents.proxy_agent import ProxyAgent


def test_health_death_and_reset(core):
    health = HealthSystem(core["config"].max_health)
    health.reset(list(core["agents"]))
    health.apply_damage("dog_b", core["config"].max_health)
    assert not health.is_alive("dog_b")
    health.reset(list(core["agents"]))
    assert all(health.is_alive(agent_id) for agent_id in core["agents"])


def test_proxy_satisfies_replaceable_agent_contract():
    proxy = ProxyAgent("future_real_dog", "/World/Agents/future_real_dog")
    assert isinstance(proxy, AgentInterface)

    class FutureLocomotionAdapter:
        def reset(self): pass
        def set_command(self, command): self.command = command
        def compute_action(self, observation): return [0.0] * 12
        def step(self, dt): pass

    assert isinstance(FutureLocomotionAdapter(), LocomotionInterface)
