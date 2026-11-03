#!/usr/bin/env python3
"""Run the visible scripted V0 arena; close the Isaac window to stop."""

# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--duration", type=float, default=120.0, help="Maximum simulated seconds")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = False
# See run_v0_headless.py: this applies only to lightweight V0 proxy rigid bodies.
args.device = "cpu"
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from dogfight_v0.config.battle_cfg import BattleConfig  # noqa: E402
from dogfight_v0.runtime import create_isaac_battle  # noqa: E402
from dogfight_v0.ui import BattleHUD  # noqa: E402


def main() -> int:
    config = BattleConfig()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(
        dt=config.simulation_dt_s, device=args.device, enable_scene_query_support=True
    ))
    battle = create_isaac_battle(sim, PROJECT_ROOT / "runs/battle" / "v0", config)
    hud = BattleHUD()
    hud.build()
    hud.update(battle.get_match_state())
    try:
        steps = int(max(0.0, args.duration) / config.simulation_dt_s)
        for _ in range(steps):
            if not app.is_running():
                break
            if battle.is_round_over():
                battle.reset()
                battle.start_round()
            battle.step(config.simulation_dt_s)
            hud.update(battle.get_match_state())
            sim.step(render=True)
        print(f"[V0] LOG_DIR {battle.logger.log_dir}")
    finally:
        hud.destroy()
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        app.close(wait_for_replicator=False, skip_cleanup=True)
