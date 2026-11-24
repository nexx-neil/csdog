#!/usr/bin/env python3
"""Paired command-distribution experiment with identical budgets and expanded regression."""
import argparse
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256/model_final.pt"
REFERENCE = ROOT / "outputs/motion_foundation/lesson05_lateral_grid_reference.json"


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_command(profile, stamp):
    name = f"lesson05_{stamp}_{profile}20"
    command = [sys.executable, str(ROOT / "scripts/rsl_rl/train.py"),
               "--task", "CSDog-Motion-Foundation-Direct-v0", "--resume_path", str(PARENT),
               "--policy_only_resume", "--num_envs", "256", "--max_iterations", "20",
               "--segment_iterations", "5", "--resume_learning_rate", "1e-5",
               "--lr_bounds", "1e-6", "1e-5", "--validation_reference", str(REFERENCE),
               "--seed", "42", "--device", "cuda:0", "--headless", "--run_name", name,
               "agent.num_steps_per_env=128", "agent.algorithm.learning_rate=0.00001",
               "env.tracking_ang_vel_std=0.25", "env.reward_scales.contact_schedule=2.0",
               f"env.command_curriculum={profile}"]
    return name, command


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    metadata = json.loads(Path(str(PARENT) + ".metadata.json").read_text())
    if digest(PARENT) != metadata["checkpoint_sha256"]:
        raise RuntimeError("Parent hash mismatch")
    reference = json.loads(REFERENCE.read_text())
    if not reference.get("complete") or len(reference["cases"]) != 18 or reference.get("protocol_name") != "lateral_grid":
        raise RuntimeError("Missing expanded reference")
    if reference["checkpoint_sha256"] != digest(PARENT) or reference["screen_status"] != "PASS":
        raise RuntimeError("Reference parent mismatch or failed screening")
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    result = {"experiment": "lesson05_sampling_distribution", "parent": str(PARENT),
              "parent_sha256": digest(PARENT), "reference": str(REFERENCE),
              "reference_sha256": digest(REFERENCE), "seed": 42,
              "maximum_updates_per_arm": 20, "regression_every_updates": 5,
              "only_intervention": "training command distribution", "arms": {}}
    for profile in ("legacy", "balanced_lateral_v1"):
        name, command = make_command(profile, stamp)
        result["arms"][profile] = {"run_name": name, "command": command, "status": "NOT_RUN"}
    if args.check_only:
        print(json.dumps(result, indent=2))
        print("Preflight PASS. No training started.")
        return 0
    folder = ROOT / "outputs/motion_foundation" / f"lesson05_ab_{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    manifest = folder / "experiment.json"
    save = lambda: manifest.write_text(json.dumps(result, indent=2) + "\n")
    save()
    print(f"Manifest: {manifest}", flush=True)
    for profile, arm in result["arms"].items():
        if digest(PARENT) != result["parent_sha256"] or digest(REFERENCE) != result["reference_sha256"]:
            raise RuntimeError("Paired inputs changed")
        log = folder / f"{profile}.log"
        arm.update(status="RUNNING", terminal_log=str(log))
        save()
        print(f"Starting {profile}; log: {log}", flush=True)
        with log.open("w") as stream:
            process = subprocess.Popen(arm["command"], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            try:
                code = process.wait()
            except BaseException:
                os.killpg(process.pid, signal.SIGTERM)
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    os.killpg(process.pid, signal.SIGKILL)
                    process.wait()
                arm["status"] = "INTERRUPTED"
                save()
                raise
        arm["returncode"] = code
        runs = list((ROOT / "logs/rsl_rl/csdog_motion_foundation").glob(f"*_{arm['run_name']}"))
        arm["status"] = "REJECTED_OR_RUNTIME_ERROR"
        if len(runs) == 1:
            run = runs[0]
            arm["run_directory"] = str(run)
            arm["segments"] = []
            for report in sorted(run.glob("validation_*.json")):
                value = json.loads(report.read_text())
                updates = int(report.stem.split("_")[-1])
                segment = run / f"segment_{updates:04d}.pt"
                if digest(segment) != value["checkpoint_sha256"]:
                    raise RuntimeError("Evaluated segment hash mismatch")
                arm["segments"].append({"updates": updates, "report": str(report), "gate": value["regression_gate"]})
            if (code == 0 and [v["updates"] for v in arm["segments"]] == [5, 10, 15, 20]
                    and all(v["gate"]["status"] == "PASS" for v in arm["segments"])):
                final = run / "model_final.pt"
                data = json.loads(Path(str(final) + ".metadata.json").read_text())
                if digest(final) == data["checkpoint_sha256"] and data["updates_in_this_run"] == 20:
                    arm.update(status="TRAIN_AND_REGRESSION_PASS", checkpoint=str(final))
        save()
        print(f"Finished {profile}: {arm['status']}", flush=True)
    print(f"Experiment complete: {manifest}", flush=True)
    return 0 if all(arm["status"] == "TRAIN_AND_REGRESSION_PASS" for arm in result["arms"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
