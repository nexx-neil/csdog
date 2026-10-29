#!/usr/bin/env python3
"""Run the ordered CSDog v2 gates and stop at the first failure.

At present the static gate is executable without Isaac Sim.  Later gates are
listed explicitly and remain NOT_RUN while the physics-readiness gate fails.
This prevents a structurally loadable model from silently entering PPO.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


STAGES = [
    ("static_urdf", "URDF structure, mesh, mass, inertia, limits"),
    ("joint_direction", "fixed-base joint direction and target tracking"),
    ("pd_stand_30s", "30-second PD standing gate"),
    ("contact_and_gait", "contact, slip, swing height, saturation, gait timing"),
    ("ppo_smoke", "bounded PPO smoke test only"),
]


def markdown(report: dict) -> str:
    lines = [
        "# CSDog v2 分阶段门禁",
        "",
        f"- 总状态：**{report['status']}**",
        f"- Git commit：`{report['git_commit']}`",
        "",
        "| 阶段 | 状态 | 说明 |",
        "|---|---|---|",
    ]
    for stage in report["stages"]:
        lines.append(f"| `{stage['name']}` | **{stage['status']}** | {stage['detail']} |")
    lines += ["", "失败阶段之后的项目均为 `NOT_RUN`；这不是通过，也不允许启动训练。", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--json-output", type=Path, required=True)
    parser.add_argument("--markdown-output", type=Path, required=True)
    args = parser.parse_args()
    repo = args.repo.resolve()
    audit_json = repo / "experiments/results/2026-10-29/csdog_v2_static_audit.json"
    audit_md = repo / "experiments/2026-10-29_CSDOG_V2_STATIC_AUDIT.md"
    command = [
        sys.executable, str(repo / "scripts/audit_urdf.py"),
        str(repo / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf"),
        "--expectations", str(repo / "config/csdog_v2_urdf_expectations.json"),
        "--json-output", str(audit_json),
        "--markdown-output", str(audit_md),
    ]
    completed = subprocess.run(command, cwd=repo, check=False)
    static_report = json.loads(audit_json.read_text(encoding="utf-8"))
    static_status = static_report["gate"]["status"]
    stages = [{"name": STAGES[0][0], "status": static_status, "detail": static_report["gate"]["reason"]}]
    for name, detail in STAGES[1:]:
        stages.append({"name": name, "status": "NOT_RUN", "detail": f"blocked by {STAGES[0][0]} FAIL; planned check: {detail}"})
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=repo, capture_output=True, text=True, check=True
    ).stdout.strip()
    report = {
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "status": "FAIL" if static_status == "FAIL" else "INCOMPLETE",
        "stop_on_failure": True,
        "stages": stages,
        "static_audit": str(audit_json),
    }
    args.json_output.parent.mkdir(parents=True, exist_ok=True)
    args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
    args.json_output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.markdown_output.write_text(markdown(report), encoding="utf-8")
    print(json.dumps({"status": report["status"], "failed_stage": "static_urdf"}, ensure_ascii=False))
    return completed.returncode if completed.returncode else (2 if static_status == "FAIL" else 0)


if __name__ == "__main__":
    raise SystemExit(main())
