#!/usr/bin/env python3
"""Run the 15 bounded V0 acceptance smoke tests in one Isaac Sim process."""

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

import argparse
import json
import sys
from math import pi
from pathlib import Path

PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "03_battle/source" / "dogfight_v0"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True
# Deterministic compatibility path for standalone kinematic proxies on Isaac Sim 5.1.
args.device = "cpu"
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from dogfight_v0.battle.intel_service import IntelService  # noqa: E402
from dogfight_v0.battle.types import Pose2D, VelocityCommand  # noqa: E402
from dogfight_v0.config.battle_cfg import BattleConfig  # noqa: E402
from dogfight_v0.navigation.simple_navigation import SimpleNavigation  # noqa: E402
from dogfight_v0.runtime import create_isaac_battle  # noqa: E402


class SmokeRunner:
    def __init__(self, sim, battle, config):
        self.sim, self.battle, self.config = sim, battle, config
        self.results = []

    def run(self, number, name, function):
        try:
            function()
        except Exception as exc:
            self.results.append({"test": number, "name": name, "status": "FAIL", "reason": repr(exc)})
            print(f"TEST {number:02d} FAIL {name}: {exc}", flush=True)
        else:
            self.results.append({"test": number, "name": name, "status": "PASS"})
            print(f"TEST {number:02d} PASS {name}", flush=True)

    def pose(self, agent_id, x, y, yaw):
        self.battle.agents[agent_id].reset(Pose2D(x, y, yaw))

    def sync(self):
        self.sim.step(render=False)
        self.sim.step(render=False)


def main() -> int:
    config = BattleConfig()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(
        dt=config.simulation_dt_s, device=args.device, enable_scene_query_support=True
    ))
    battle = create_isaac_battle(sim, PROJECT_ROOT / "03_battle/logs" / "v0", config, echo=False)
    r = SmokeRunner(sim, battle, config)

    r.run(1, "three proxies load", lambda: (
        len(battle.agents) == 3 and set(battle.agents) == {"dog_a", "dog_b", "dog_c"}
    ) or (_ for _ in ()).throw(AssertionError("canonical proxies missing")))

    def test_independent_move():
        battle.reset(); battle.start_round()
        before = {key: value.get_pose() for key, value in battle.agents.items()}
        battle.agents["dog_a"].set_velocity_command(VelocityCommand(0.5, 0.0, 0.0))
        battle.agents["dog_b"].set_velocity_command(VelocityCommand(0.0, 0.3, 0.0))
        battle.agents["dog_c"].set_velocity_command(VelocityCommand(0.0, 0.0, 0.5))
        for agent in battle.agents.values(): agent.update(0.5)
        after = {key: value.get_pose() for key, value in battle.agents.items()}
        assert after["dog_a"].x != before["dog_a"].x
        assert (after["dog_b"].x, after["dog_b"].y) != (before["dog_b"].x, before["dog_b"].y)
        assert after["dog_c"].yaw != before["dog_c"].yaw
    r.run(2, "independent movement", test_independent_move)

    intel_holder = {}
    def test_intel_period():
        service = IntelService(5.0); service.reset(0.0)
        assert service.update(0.0, battle.agents)
        assert not service.update(4.999, battle.agents)
        assert service.update(5.0, battle.agents)
        assert service.last_update_s == 5.0
        intel_holder["service"] = service
    r.run(3, "intel exact 5s period", test_intel_period)

    def test_intel_stale():
        service = IntelService(5.0); service.update(0.0, battle.agents)
        old = service.get_last_known_position("dog_a", "dog_b")
        p = battle.agents["dog_b"].get_pose(); battle.agents["dog_b"].reset(Pose2D(p.x + 1.0, p.y, p.yaw))
        assert not service.update(2.0, battle.agents)
        assert service.get_last_known_position("dog_a", "dog_b") == old
        assert service.update(5.0, battle.agents)
        assert service.get_last_known_position("dog_a", "dog_b").x == p.x + 1.0
    r.run(4, "intel remains stale between snapshots", test_intel_stale)

    def test_navigation():
        r.pose("dog_a", -4.0, -4.0, 0.0)
        nav = SimpleNavigation(config); nav.set_goal("dog_a", (-2.0, -4.0))
        start = battle.agents["dog_a"].get_pose().x
        for _ in range(30):
            command = nav.compute_command(battle.agents["dog_a"], 0.05)
            battle.agents["dog_a"].set_velocity_command(command); battle.agents["dog_a"].update(0.05)
        assert battle.agents["dog_a"].get_pose().x > start
    r.run(5, "navigation approaches goal", test_navigation)

    def test_fov_out():
        r.pose("dog_a", 0.0, -4.0, 0.0); r.pose("dog_b", -2.0, -4.0, 0.0); r.sync()
        result = battle.visibility.observe_target(battle.agents["dog_a"], battle.agents["dog_b"])
        assert not result.visible and not result.in_fov
    r.run(6, "outside FOV is invisible", test_fov_out)

    def test_visible():
        r.pose("dog_a", -4.0, -4.0, 0.0); r.pose("dog_b", -2.0, -4.0, pi); r.pose("dog_c", 0.0, 3.5, 0.0); r.sync()
        result = battle.visibility.observe_target(battle.agents["dog_a"], battle.agents["dog_b"])
        assert result.visible and result.in_fov and result.line_of_sight
    r.run(7, "inside FOV and clear LOS is visible", test_visible)

    def test_wall_los():
        r.pose("dog_a", -2.0, 0.0, 0.0); r.pose("dog_b", 2.0, 0.0, pi); r.pose("dog_c", 0.0, 4.0, 0.0); r.sync()
        result = battle.visibility.observe_target(battle.agents["dog_a"], battle.agents["dog_b"])
        assert result.in_fov and not result.line_of_sight and not result.visible, result
    r.run(8, "wall blocks LOS", test_wall_los)

    def test_yaw_sign():
        r.pose("dog_a", -4.0, -4.0, 0.0); r.pose("dog_b", -2.0, -3.0, 0.0); r.sync()
        left = battle.visibility.observe_target(battle.agents["dog_a"], battle.agents["dog_b"])
        r.pose("dog_b", -2.0, -4.5, 0.0); r.sync()
        right = battle.visibility.observe_target(battle.agents["dog_a"], battle.agents["dog_b"])
        assert 0.0 < left.yaw_error_rad <= pi and -pi <= right.yaw_error_rad < 0.0
    r.run(9, "yaw error sign and normalization", test_yaw_sign)

    def test_wall_fire():
        battle.health.reset(list(battle.agents)); battle.weapon.reset()
        r.pose("dog_a", -2.0, 0.0, 0.0); r.pose("dog_b", 2.0, 0.0, pi); r.sync()
        before = battle.health.get_health("dog_b")
        result = battle.weapon.fire(battle.agents["dog_a"], battle.agents, 0.0)
        if result.hit and result.hit_agent_id: battle.apply_damage(result.hit_agent_id, result.damage, "dog_a")
        assert result.fired and not result.hit and battle.health.get_health("dog_b") == before, result
        assert result.hit_object_path and "wall_center" in result.hit_object_path, result
    r.run(10, "wall absorbs fire", test_wall_fire)

    shot_holder = {}
    def test_agent_fire():
        battle.health.reset(list(battle.agents)); battle.weapon.reset()
        for agent in battle.agents.values(): agent.set_alive(True)
        r.pose("dog_a", -4.0, -4.0, 0.0); r.pose("dog_b", -2.0, -4.0, pi); r.pose("dog_c", 0.0, 3.5, 0.0); r.sync()
        result = battle.weapon.fire(battle.agents["dog_a"], battle.agents, 10.0)
        assert result.hit and result.hit_agent_id == "dog_b", result
        battle.apply_damage("dog_b", result.damage, "dog_a")
        assert battle.health.get_health("dog_b") == config.max_health - config.weapon_damage
        shot_holder["time"] = 10.0
    r.run(11, "agent hit reduces correct HP", test_agent_fire)

    def test_cooldown():
        blocked = battle.weapon.fire(battle.agents["dog_a"], battle.agents, 10.5)
        ready = battle.weapon.fire(battle.agents["dog_a"], battle.agents, 11.0)
        assert not blocked.fired and ready.fired
    r.run(12, "weapon cooldown", test_cooldown)

    def test_death():
        battle.health.reset(list(battle.agents)); battle.agents["dog_b"].set_alive(True)
        battle.apply_damage("dog_b", config.max_health, "dog_a")
        assert not battle.health.is_alive("dog_b") and not battle.agents["dog_b"].is_alive()
    r.run(13, "HP zero marks dead", test_death)

    def test_winner():
        battle.reset(); battle.start_round()
        battle.apply_damage("dog_b", config.max_health, "dog_a")
        battle.apply_damage("dog_c", config.max_health, "dog_a")
        battle.step(config.simulation_dt_s)
        assert battle.is_round_over() and battle.get_winner() == "dog_a"
    r.run(14, "last survivor wins", test_winner)

    def test_reset():
        battle.reset(); battle.start_round(); r.sync()
        assert not battle.is_round_over() and battle.time_s == 0.0
        assert set(battle.get_alive_agents()) == {"dog_a", "dog_b", "dog_c"}
        battle.step(config.simulation_dt_s); sim.step(render=False)
    r.run(15, "reset without closing Isaac Sim", test_reset)

    summary_path = battle.logger.log_dir / "smoke_summary.json"
    summary_path.write_text(json.dumps(r.results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    failures = [result for result in r.results if result["status"] == "FAIL"]
    print(f"SMOKE_SUMMARY pass={len(r.results)-len(failures)} fail={len(failures)}", flush=True)
    print(f"SMOKE_LOG_DIR {battle.logger.log_dir}", flush=True)
    return 1 if failures else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        app.close(wait_for_replicator=False, skip_cleanup=True)
