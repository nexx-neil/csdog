#!/usr/bin/env python3
"""Run the actual legacy sampler on CPU and compare the new command distribution."""
import argparse
import ast
import json
from pathlib import Path
import types
import torch
import yaml
from csdog_motion.curriculum import sample_lateral_balanced


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = root / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env.py"
    tree = ast.parse(source.read_text())
    method = next(n for c in tree.body if isinstance(c, ast.ClassDef) and c.name == "GeneratedRobotEnv"
                  for n in c.body if isinstance(n, ast.FunctionDef) and n.name == "_sample_commands")
    namespace = {"torch": torch}
    exec(compile(ast.Module(body=[method], type_ignores=[]), str(source), "exec"), namespace)
    class TupleSafeLoader(yaml.SafeLoader):
        pass
    TupleSafeLoader.add_constructor("tag:yaml.org,2002:python/tuple", lambda loader, node: loader.construct_sequence(node))
    cfg = yaml.load((root / "logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-44-15_lesson02_20261106_154408_697378_control10_h128_e256/params/env.yaml").read_text(), Loader=TupleSafeLoader)
    keys = ["command_ranges", "command_sampling", "stand_command_probability", "multi_axis_command_probability", "command_min_magnitude"]
    torch.set_num_threads(1)
    torch.manual_seed(42)
    count = 200000
    env = types.SimpleNamespace(cfg=types.SimpleNamespace(**{key: cfg[key] for key in keys}), device="cpu", _commands=torch.zeros(count, 3))
    namespace["_sample_commands"](env, torch.arange(count))
    alternative, _ = sample_lateral_balanced(count)
    result = {"samples_per_distribution": count, "seed": 42, "meaning": "requested draw frequencies, not physical-time occupancy or independent locomotion trials", "distributions": {}}
    for name, commands in (("legacy", env._commands), ("balanced_lateral_v1", alternative)):
        active = commands.abs() > 1e-6
        y = (active.sum(1) == 1) & active[:, 1]
        stats = {"stand_fraction": float((~active.any(1)).float().mean()),
                 "single_y_fraction": float(y.float().mean()),
                 "combined_fraction": float((active.sum(1) > 1).float().mean()),
                 "pure_left_above_0_25_fraction": float((y & (commands[:, 1] > .25)).float().mean()),
                 "pure_right_0_06_to_0_14_fraction": float((y & (commands[:, 1] < -.06) & (commands[:, 1] > -.14)).float().mean())}
        result["distributions"][name] = stats
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
