#!/usr/bin/env python3
"""User-run paired experiment: change only yaw tracking width, keep both parents identical."""

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]
PARENT_RUN = ROOT / "logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256"
PARENT = PARENT_RUN / "model_final.pt"
REFERENCE = ROOT / "outputs/motion_foundation/validation/legacy_reference_v2.json"
LOG_ROOT = ROOT / "logs/rsl_rl/csdog_motion_foundation"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def command(arm, stamp):
    width = {"control": "0.25", "yaw_tight": "0.15"}[arm]
    name = f"lesson02_{stamp}_{arm}10_h128_e256"
    return name, [
        sys.executable, str(ROOT / "scripts/rsl_rl/train.py"),
        "--task", "CSDog-Motion-Foundation-Direct-v0",
        "--resume_path", str(PARENT), "--policy_only_resume",
        "--num_envs", "256", "--max_iterations", "10", "--segment_iterations", "5",
        "--resume_learning_rate", "1e-5", "--lr_bounds", "1e-6", "1e-5",
        "--validation_reference", str(REFERENCE), "--seed", "42", "--device", "cuda:0",
        "--headless", "--run_name", name, "agent.num_steps_per_env=128",
        f"env.tracking_ang_vel_std={width}",
    ]


def preflight():
    metadata = json.loads(Path(str(PARENT) + ".metadata.json").read_text())
    if sha256(PARENT) != metadata["checkpoint_sha256"] or metadata["updates_in_this_run"] != 5:
        raise RuntimeError("Lesson 01 parent hash/update count mismatch")
    report = json.loads((PARENT_RUN / "validation_0005.json").read_text())
    if report.get("regression_gate", {}).get("status") != "PASS":
        raise RuntimeError("Lesson 01 parent did not pass regression")
    reference = json.loads(REFERENCE.read_text())
    if not reference.get("complete") or len(reference["cases"]) != 14:
        raise RuntimeError("Missing complete 14-case reference")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true", help="Show verified plan; never start training")
    args = parser.parse_args()
    metadata = preflight()
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    plan = {
        "experiment": "lesson02_yaw_tracking_width_ab", "parent_checkpoint": str(PARENT),
        "parent_sha256": metadata["checkpoint_sha256"],
        "reference": str(REFERENCE), "reference_sha256": sha256(REFERENCE),
        "seed": 42, "maximum_ppo_updates_per_arm": 10, "regression_every_updates": 5,
        "policy_only_resume_for_both": True,
        "independent_arms": "both load the same lesson01 parent; candidate never resumes the control arm",
        "single_experimental_variable": "env.tracking_ang_vel_std: control=0.25, yaw_tight=0.15 rad/s",
        "arms": {},
    }
    for arm in ("control", "yaw_tight"):
        name, invocation = command(arm, stamp)
        plan["arms"][arm] = {"run_name": name, "command": invocation, "status": "NOT_RUN"}
    if args.check_only:
        print(json.dumps(plan, indent=2))
        print("Preflight PASS. No training started.")
        return 0

    folder = ROOT / "outputs/motion_foundation" / f"lesson02_ab_{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    manifest = folder / "experiment.json"

    def save():
        manifest.write_text(json.dumps(plan, indent=2) + "\n")

    print(f"Experiment manifest: {manifest}", flush=True)
    print("Two independent arms, maximum 10 PPO updates each; regression after every 5 updates.", flush=True)
    save()
    for arm, record in plan["arms"].items():
        if sha256(PARENT) != plan["parent_sha256"] or sha256(REFERENCE) != plan["reference_sha256"]:
            raise RuntimeError("Parent or reference changed during the paired experiment")
        log = folder / f"{arm}.log"
        record.update(status="RUNNING", terminal_log=str(log))
        save()
        print(f"\nStarting {arm}; full output: {log}", flush=True)
        with log.open("w") as stream:
            with subprocess.Popen(record["command"], cwd=ROOT, stdout=subprocess.PIPE,
                                  stderr=subprocess.STDOUT, text=True, errors="replace") as process:
                try:
                    for line in process.stdout:
                        print(line, end="", flush=True)
                        stream.write(line)
                    code = process.wait()
                except KeyboardInterrupt:
                    process.terminate()
                    try:
                        process.wait(timeout=15)
                    except subprocess.TimeoutExpired:
                        process.kill()
                        process.wait()
                    record["status"] = "INTERRUPTED"
                    save()
                    raise
        record["returncode"] = code
        matches = list(LOG_ROOT.glob(f"*_{record['run_name']}"))
        if len(matches) == 1:
            run = matches[0]
            record["run_directory"] = str(run)
            reports = sorted(run.glob("validation_*.json"))
            record["validation_reports"] = [str(path) for path in reports]
            final = run / "model_final.pt"
            final_report = run / "validation_0010.json"
            if code == 0 and final.is_file() and final_report.is_file():
                result = json.loads(final_report.read_text())
                final_metadata = json.loads(Path(str(final) + ".metadata.json").read_text())
                passed = (result.get("regression_gate", {}).get("status") == "PASS"
                          and final_metadata.get("updates_in_this_run") == 10
                          and sha256(final) == final_metadata.get("checkpoint_sha256"))
                if passed:
                    record.update(status="TRAIN_AND_REGRESSION_PASS", checkpoint=str(final))
        if record["status"] == "RUNNING":
            record["status"] = "REJECTED_OR_RUNTIME_ERROR"
            print(f"{arm} stopped. Keep its log; the next arm independently reloads lesson01.", flush=True)
        save()
    print(f"\nPaired experiment finished. Share this path: {manifest}", flush=True)
    print("Regression PASS alone does not select a winner; compare yaw errors and retained translation first.", flush=True)
    return 0 if all(x["status"] == "TRAIN_AND_REGRESSION_PASS" for x in plan["arms"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
