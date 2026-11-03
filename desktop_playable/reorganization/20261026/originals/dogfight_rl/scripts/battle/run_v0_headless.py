#!/usr/bin/env python3
"""Run a bounded headless scripted V0 battle (no training)."""

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "03_battle/source" / "dogfight_v0"))

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--duration", type=float, default=30.0, help="Maximum simulated seconds")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
args.headless = True
# Frozen Isaac Sim 5.1: GPU tensor teleport of standalone kinematic proxies can
# fault. Three V0 proxies use CPU PhysX; future articulations may own GPU adapters.
args.device = "cpu"
app = AppLauncher(args).app

import isaaclab.sim as sim_utils  # noqa: E402
from dogfight_v0.config.battle_cfg import BattleConfig  # noqa: E402
from dogfight_v0.runtime import create_isaac_battle  # noqa: E402


def main() -> int:
    config = BattleConfig()
    sim = sim_utils.SimulationContext(sim_utils.SimulationCfg(
        dt=config.simulation_dt_s, device=args.device, enable_scene_query_support=True
    ))
    battle = create_isaac_battle(sim, PROJECT_ROOT / "03_battle/logs" / "v0", config)
    steps = int(max(0.0, args.duration) / config.simulation_dt_s)
    for _ in range(steps):
        if battle.is_round_over() or not app.is_running():
            break
        battle.step(config.simulation_dt_s)
        sim.step(render=False)
    print(f"[V0] LOG_DIR {battle.logger.log_dir}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    finally:
        app.close(wait_for_replicator=False, skip_cleanup=True)
