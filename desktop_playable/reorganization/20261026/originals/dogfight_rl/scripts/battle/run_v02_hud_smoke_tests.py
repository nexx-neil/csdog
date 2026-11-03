#!/usr/bin/env python3
"""Bounded GUI smoke tests for the V0.2-A battle HUD (no training)."""

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
from pathlib import Path

PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "03_battle/source" / "dogfight_v0"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = False
args.device = "cpu"
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from dogfight_v0.config.battle_cfg import BattleConfig  # noqa: E402
from dogfight_v0.runtime import create_isaac_battle  # noqa: E402
from dogfight_v0.ui import BattleHUD  # noqa: E402


def main() -> int:
    config = BattleConfig()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(
        dt=config.simulation_dt_s,
        device=args.device,
        enable_scene_query_support=True,
    ))
    battle = create_isaac_battle(sim, PROJECT_ROOT / "03_battle/logs" / "v0", config, echo=False)
    hud = BattleHUD()
    results: list[dict[str, str | int]] = []

    def run(number: int, name: str, fn) -> None:
        try:
            fn()
        except Exception as exc:
            results.append({"test": number, "name": name, "status": "FAIL", "reason": repr(exc)})
            print(f"TEST HUD-{number} FAIL {name}: {exc}", flush=True)
        else:
            results.append({"test": number, "name": name, "status": "PASS"})
            print(f"TEST HUD-{number} PASS {name}", flush=True)

    try:
        hud.build()
        hud.update(battle.get_match_state())
        sim.step(render=True)

        def test_exists():
            assert hud.is_built and hud.window is not None
            assert hud.window.position_y <= BattleHUD.TOP_MARGIN + 1.0
            assert all(hud.get_display_text(agent_id) for agent_id in BattleHUD.AGENT_IDS)
        run(1, "top HUD contains three agents", test_exists)

        def test_initial():
            for agent_id in BattleHUD.AGENT_IDS:
                text = hud.get_display_text(agent_id)
                assert "HP 100 / 100" in text and text.endswith("ALIVE"), text
        run(2, "initial health is 100/100", test_initial)

        def test_damage():
            battle.apply_damage("dog_b", 20.0, "dog_a")
            hud.update(battle.get_match_state())
            assert hud.get_display_text("dog_b") == "DOG B | HP 80 / 100 | ALIVE"
        run(3, "damage updates Dog B to 80", test_damage)

        def test_death():
            battle.apply_damage("dog_c", config.max_health, "dog_a")
            hud.update(battle.get_match_state())
            assert hud.get_display_text("dog_c") == "DOG C | HP 0 / 100 | DEAD"
        run(4, "death displays zero and DEAD", test_death)

        def test_reset():
            battle.reset(); battle.start_round()
            hud.reset(battle.get_match_state())
            for agent_id in BattleHUD.AGENT_IDS:
                text = hud.get_display_text(agent_id)
                assert "HP 100 / 100" in text and text.endswith("ALIVE"), text
        run(5, "round reset restores all health", test_reset)

        def test_truth_source():
            state = battle.get_match_state()
            for agent_id in BattleHUD.AGENT_IDS:
                agent = state["agents"][agent_id]
                expected = BattleHUD.format_agent_status(
                    agent_id, agent["health"], state["max_health"], agent["alive"]
                )
                assert hud.get_display_text(agent_id) == expected
                assert agent["health"] == battle.health.get_health(agent_id)
        run(6, "HUD agrees with BattleManager and HealthSystem", test_truth_source)

        sim.step(render=True)
        summary_path = battle.logger.log_dir / "hud_smoke_summary.json"
        summary_path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        failures = [result for result in results if result["status"] == "FAIL"]
        print(f"HUD_SMOKE_SUMMARY pass={len(results)-len(failures)} fail={len(failures)}", flush=True)
        print(f"HUD_SMOKE_LOG_DIR {battle.logger.log_dir}", flush=True)
        return 1 if failures else 0
    finally:
        hud.destroy()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        app.close(wait_for_replicator=False, skip_cleanup=True)

