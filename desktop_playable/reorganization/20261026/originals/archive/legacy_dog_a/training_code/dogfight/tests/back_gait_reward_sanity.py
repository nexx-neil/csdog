#!/usr/bin/env python3
"""CPU-only algebraic gates for BACK progress, shortfall, STOP, and held-foot cost."""
from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

import torch

from dogfight.tasks.dog_a_locomotion_ppo_smoke_v1.reward_terms import (
    directional_progress_signals,
    excessive_air_time_signal,
    locomotion_shortfall_signal,
)


command = torch.tensor([[0.0, -0.2]] * 4 + [[0.0, 0.0]])
actual = torch.tensor([
    [0.0, 0.0], [0.0, -0.1], [0.0, -0.2], [0.0, 0.1], [0.3, -0.2],
])
speed = torch.linalg.vector_norm(command, dim=1)
progress, ratio = directional_progress_signals(actual, command, 0.08, 1.0)
shortfall = locomotion_shortfall_signal(progress, speed, 0.08, 0.45)

expected_ratio = torch.tensor([0.0, 0.5, 1.0, -0.5, 0.0])
assert torch.allclose(ratio, expected_ratio)
assert shortfall[0] > shortfall[1]
assert shortfall[1] == 0.0
assert shortfall[2] == 0.0
assert shortfall[3] > shortfall[0]
assert progress[4] == 0.0 and ratio[4] == 0.0 and shortfall[4] == 0.0

air_time = torch.tensor([[0.0, 0.0, 0.0, 0.79], [0.0, 0.0, 0.0, 1.0], [0.0, 0.0, 0.0, 5.0]])
air_cost = excessive_air_time_signal(
    air_time, torch.tensor([0.2, 0.2, 0.2]), 0.08, 0.8, 0.8, 4.0,
)
assert air_cost[0] == 0.0
assert torch.isclose(air_cost[1], torch.tensor(0.2))
assert torch.isclose(air_cost[2], torch.tensor(4.0))

print("BACK REWARD SANITY: PASS")
print({"progress_speed": progress.tolist(), "progress_ratio": ratio.tolist(),
       "shortfall": shortfall.tolist(), "single_foot_air_cost": air_cost.tolist()})
