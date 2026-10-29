#!/usr/bin/env python3
"""Evaluate one compatible checkpoint on the shared CSDog v2 command matrix."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def assess(metrics: dict, command: dict, thresholds: dict) -> dict[str, bool]:
    command_vector = [command["vx"], command["vy"], command["yaw_rate"]]
    actual = metrics["mean_actual_linear_velocity_body_m_s"][:2] + [metrics["mean_actual_yaw_rate_rad_s"]]
    rmse = metrics["linear_velocity_tracking_rmse_by_axis_m_s"] + [metrics["yaw_rate_tracking_rmse_rad_s"]]
    active = [index for index, value in enumerate(command_vector) if abs(value) > 1.0e-9]
    inactive = [index for index in range(3) if index not in active]
    return {
        "finite": bool(metrics["finite"]),
        "terminations": metrics["total_terminations"] <= thresholds["total_terminations_max"],
        "action_saturation": metrics["action_saturation_fraction"] <= thresholds["action_saturation_fraction_max"],
        "joint_target_limits": metrics["joint_target_outside_soft_limit_fraction"] <= thresholds["joint_target_outside_soft_limit_fraction_max"],
        "joint_position_limits": metrics["joint_position_near_soft_limit_fraction"] <= thresholds["joint_position_near_soft_limit_fraction_max"],
        "torque_saturation": metrics["torque_saturation_fraction_95pct"] <= thresholds["torque_saturation_fraction_95pct_max"],
        "commanded_axis_tracking": all(rmse[index] <= thresholds["commanded_axis_rmse_max"] for index in active),
        "non_commanded_axis_coupling": all(abs(actual[index]) <= thresholds["non_commanded_axis_mean_abs_max"] for index in inactive),
    }


def render_markdown(report: dict) -> str:
    lines = [
        "# CSDog v2 固定命令批量评估",
        "",
        f"- 状态：**{report['status']}**",
        f"- task：`{report['task']}`",
        f"- checkpoint：`{report['checkpoint']}`",
        f"- seed：{report['seed']}",
        "",
        "| 命令 | 状态 | 失败检查 |",
        "|---|---|---|",
    ]
    for result in report["results"]:
        failed = [name for name, passed in result.get("checks", {}).items() if not passed]
        lines.append(f"| `{result['name']}` | **{result['status']}** | {', '.join(failed) or '-'} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--task", required=True)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--matrix", type=Path, default=Path("config/experiments/csdog_v2_abc.json"))
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    matrix = json.loads(args.matrix.read_text(encoding="utf-8"))
    common = matrix["common"]
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results = []
    for command in common["commands"]:
        metrics_path = args.output_dir / f"{command['name']}.json"
        invocation = [
            sys.executable, "scripts/rsl_rl/play.py",
            "--task", args.task,
            "--checkpoint", str(args.checkpoint.resolve()),
            "--seed", str(common["seed"]),
            "--num_envs", str(common["evaluation_num_envs"]),
            "--num_steps", str(common["evaluation_steps_per_env"]),
            "--command", str(command["vx"]), str(command["vy"]), str(command["yaw_rate"]),
            "--metrics-output", str(metrics_path),
            "--headless",
        ]
        if args.dry_run:
            results.append({"name": command["name"], "status": "DRY_RUN", "invocation": invocation})
            continue
        completed = subprocess.run(invocation, check=False)
        if completed.returncode != 0 or not metrics_path.is_file():
            results.append({"name": command["name"], "status": "FAIL", "returncode": completed.returncode})
            break
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        checks = assess(metrics, command, common["evaluation_thresholds"])
        results.append({"name": command["name"], "status": "PASS" if all(checks.values()) else "FAIL", "checks": checks, "metrics": str(metrics_path)})
    if args.dry_run:
        status = "DRY_RUN"
    else:
        status = "PASS" if len(results) == len(common["commands"]) and all(item["status"] == "PASS" for item in results) else "FAIL"
    report = {
        "schema_version": 1,
        "status": status,
        "task": args.task,
        "checkpoint": str(args.checkpoint.resolve()),
        "seed": common["seed"],
        "num_envs": common["evaluation_num_envs"],
        "steps_per_env": common["evaluation_steps_per_env"],
        "thresholds": common["evaluation_thresholds"],
        "results": results,
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_output.write_text(render_markdown(report), encoding="utf-8")
    return 0 if status in {"PASS", "DRY_RUN"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
