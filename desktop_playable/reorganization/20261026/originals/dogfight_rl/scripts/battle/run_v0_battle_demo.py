#!/usr/bin/env python3
"""Run the visual three-proxy FFA battle demo (no training, no fake damage)."""

from __future__ import annotations

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
from math import radians
from pathlib import Path


PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "03_battle/source" / "dogfight_v0"))

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--duration", type=float, default=120.0, help="Total active battle time in seconds")
parser.add_argument("--seed", type=int, default=42, help="Deterministic first-round spawn seed")
parser.add_argument("--auto-reset", action="store_true", help="Start another round after the result hold")
parser.add_argument("--result-hold", type=float, default=4.0, help="Seconds to hold each final result")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
# Standalone kinematic V0 proxies use the frozen environment's stable CPU PhysX path.
args.device = "cpu"
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from dogfight_v0.arena.test_map import TestMap  # noqa: E402
from dogfight_v0.battle.types import Pose2D  # noqa: E402
from dogfight_v0.config.battle_cfg import BattleConfig  # noqa: E402
from dogfight_v0.runtime import create_isaac_battle  # noqa: E402
from dogfight_v0.ui import BattleHUD  # noqa: E402


AGENT_IDS = ("dog_a", "dog_b", "dog_c")


class DemoTestMap(TestMap):
    """The production TestMap geometry with a demo-friendly open triangle."""

    def get_spawn_points(self) -> list[Pose2D]:
        return [
            Pose2D(-4.0, -3.0, 0.0),
            Pose2D(4.0, -3.0, radians(180.0)),
            Pose2D(0.0, -4.2, radians(163.3)),
        ]


def demo_config() -> BattleConfig:
    """Demo-only tuning; production ``BattleConfig`` defaults remain unchanged."""
    return BattleConfig(
        max_health=100.0,
        weapon_damage=20.0,
        weapon_cooldown_s=0.9,
        weapon_range_m=22.0,
        vision_max_range_m=22.0,
        # A focused cone avoids edge-of-LOS target thrashing in the triangular
        # spawn, while the tight fire gate keeps the forward ray on the proxy.
        vision_half_fov_rad=radians(28.0),
        aim_tolerance_rad=radians(1.0),
        round_time_limit_s=90.0,
        intel_period_s=5.0,
    )


def new_round_summary(round_number: int) -> dict:
    result = {
        "round": round_number,
        "winner": None,
        "duration": 0.0,
        "completed": False,
        "final_health": {agent_id: 100.0 for agent_id in AGENT_IDS},
    }
    for agent_id in AGENT_IDS:
        result[f"{agent_id}_damage_dealt"] = 0.0
        result[f"{agent_id}_hits"] = 0
    return result


def health_snapshot(battle) -> dict[str, float]:
    return {agent_id: battle.health.get_health(agent_id) for agent_id in AGENT_IDS}


def write_summary(path: Path, duration_s: float, seed: int, rounds: list[dict]) -> None:
    payload = {
        "seed": seed,
        "duration": round(duration_s, 3),
        "round_count": len(rounds),
        "rounds": rounds,
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def emit_new_events(battle, cursor: int, current: dict) -> int:
    """Mirror authoritative battle events to concise Demo console output/statistics."""
    events = battle.logger.events
    for event in events[cursor:]:
        kind, data = event.event_type, event.data
        if kind == "ROUND_START":
            print(f"[DEMO] ROUND_START round={current['round']} seed={args.seed + current['round'] - 1}", flush=True)
        elif kind == "INTEL_UPDATE":
            print(f"[DEMO] INTEL_UPDATE t={event.timestamp_s:.1f}", flush=True)
        elif kind == "TARGET_SELECTED":
            print(f"[DEMO] {event.agent_id} target={event.target_id}", flush=True)
        elif kind == "TARGET_VISIBLE":
            print(
                f"[DEMO] TARGET_VISIBLE observer={event.agent_id} target={event.target_id} "
                f"distance={data['distance_m']:.2f} yaw_error={data['yaw_error_rad']:.3f}",
                flush=True,
            )
        elif kind == "SHOT_FIRED":
            print(f"[DEMO] FIRE shooter={event.agent_id}", flush=True)
        elif kind == "SHOT_HIT":
            current[f"{event.agent_id}_hits"] += 1
        elif kind == "DAMAGE":
            shooter = event.target_id
            if shooter in AGENT_IDS:
                current[f"{shooter}_damage_dealt"] += float(data["amount"])
            print(
                f"[DEMO] HIT shooter={shooter} target={event.agent_id} "
                f"damage={data['amount']:g} remaining_hp={data['health']:g}",
                flush=True,
            )
        elif kind == "DEATH":
            print(f"[DEMO] DEATH {event.agent_id}", flush=True)
        elif kind == "ROUND_END":
            winner = data.get("winner")
            if winner is None:
                print("[DEMO] DRAW", flush=True)
            current["winner"] = winner
            current["duration"] = round(event.timestamp_s, 3)
            current["completed"] = True
            current["final_health"] = health_snapshot(battle)
        elif kind == "WINNER":
            print(f"[DEMO] WINNER {event.agent_id}", flush=True)
    return len(events)


def hold_result(sim, hud: BattleHUD | None, battle, seconds: float, dt: float) -> None:
    for _ in range(int(max(0.0, seconds) / dt)):
        if not app.is_running():
            break
        if hud is not None:
            hud.update(battle.get_match_state())
        sim.step(render=not args.headless)


def main() -> int:
    if args.duration <= 0.0:
        parser.error("--duration must be positive")
    if args.result_hold < 0.0:
        parser.error("--result-hold cannot be negative")

    config = demo_config()
    sim = sim_utils.SimulationContext(
        sim_utils.SimulationCfg(
            dt=config.simulation_dt_s,
            device=args.device,
            enable_scene_query_support=True,
        )
    )
    battle = create_isaac_battle(
        sim,
        PROJECT_ROOT / "03_battle/logs" / "v0" / "battle_demo",
        config,
        echo=False,
        seed=args.seed,
        arena_map=DemoTestMap(),
    )
    hud = None if args.headless else BattleHUD()
    if hud is not None:
        hud.build()
        hud.update(battle.get_match_state())

    summary_path = battle.logger.log_dir / "demo_summary.json"
    rounds = [new_round_summary(1)]
    current = rounds[-1]
    event_cursor = emit_new_events(battle, 0, current)
    elapsed_active_s = 0.0

    try:
        while elapsed_active_s + 1e-9 < args.duration and app.is_running():
            battle.step(config.simulation_dt_s)
            elapsed_active_s += config.simulation_dt_s
            event_cursor = emit_new_events(battle, event_cursor, current)
            if hud is not None:
                hud.update(battle.get_match_state())
            sim.step(render=not args.headless)

            if battle.is_round_over():
                write_summary(summary_path, elapsed_active_s, args.seed, rounds)
                hold_result(sim, hud, battle, args.result_hold, config.simulation_dt_s)
                if not args.auto_reset or elapsed_active_s + 1e-9 >= args.duration or not app.is_running():
                    break
                round_number = len(rounds) + 1
                battle.reset(seed=args.seed + round_number - 1)
                battle.start_round()
                current = new_round_summary(round_number)
                rounds.append(current)
                event_cursor = emit_new_events(battle, event_cursor, current)
                if hud is not None:
                    hud.reset(battle.get_match_state())
                print(f"[DEMO] RESET round={round_number} hp={health_snapshot(battle)}", flush=True)

        if not current["completed"]:
            current["duration"] = round(battle.time_s, 3)
            current["final_health"] = health_snapshot(battle)
        write_summary(summary_path, elapsed_active_s, args.seed, rounds)
        print(f"[DEMO] LOG_DIR {battle.logger.log_dir}", flush=True)
        print(f"[DEMO] SUMMARY {summary_path}", flush=True)
        return 0
    finally:
        if hud is not None:
            hud.destroy()


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        app.close(wait_for_replicator=False, skip_cleanup=True)
