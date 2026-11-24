#!/usr/bin/env python3
"""Quarantined paired control-envelope experiment; source budget and gates recorded."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

from csdog_motion.training import file_hash

ROOT = Path(__file__).resolve().parents[1]
PARENT = ROOT / "logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256/model_final.pt"
INITIALIZATION = ROOT / "outputs/motion_foundation/initialization/lesson06_knee042.pt"
REFERENCES = {"original": ROOT / "outputs/motion_foundation/lesson05_lateral_grid_reference.json",
              "knee042": ROOT / "outputs/motion_foundation/lesson06_knee042_reference18.json"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    sources = {str(p.relative_to(ROOT)): file_hash(p) for folder in ("source", "scripts") for p in sorted((ROOT / folder).rglob("*.py"))}
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    result = {"experiment": "lesson06_action_envelope", "maximum_updates_per_arm": 100,
              "regression_every_updates": 20, "seed": 42,
              "only_intervention": "joint target clipping; knees .35->.42rad, others .35rad",
              "scope": "quarantined development; self-reference PASS does not erase original-baseline regressions",
              "source_files_sha256": sources, "arms": {}}
    for name in ("original", "knee042"):
        checkpoint = PARENT if name == "original" else INITIALIZATION
        reference = REFERENCES[name]
        value = json.loads(reference.read_text())
        metadata = json.loads(Path(str(checkpoint) + ".metadata.json").read_text())
        if metadata["checkpoint_sha256"] != file_hash(checkpoint) or value["checkpoint_sha256"] != file_hash(checkpoint):
            raise RuntimeError("Input checkpoint/reference hash mismatch")
        if not value.get("complete") or len(value["cases"]) != 18 or value["screen_status"] != "PASS":
            raise RuntimeError("Incomplete/failed 18-case reference")
        task = "CSDog-Motion-Foundation-Direct-v0" if name == "original" else "CSDog-Motion-Envelope-Direct-v0"
        run_name = f"lesson06_{stamp}_{name}100"
        command = [sys.executable, str(ROOT / "scripts/rsl_rl/train.py"), "--task", task,
                   "--resume_path", str(checkpoint), "--policy_only_resume", "--num_envs", "256",
                   "--max_iterations", "100", "--segment_iterations", "20", "--resume_learning_rate", "1e-5",
                   "--lr_bounds", "1e-6", "1e-5", "--validation_reference", str(reference),
                   "--seed", "42", "--device", "cuda:0", "--headless", "--run_name", run_name,
                   "agent.num_steps_per_env=128", "agent.algorithm.learning_rate=0.00001"]
        result["arms"][name] = {"task": task, "run_name": run_name, "parent": str(checkpoint),
                               "parent_sha256": file_hash(checkpoint), "reference": str(reference),
                               "reference_sha256": file_hash(reference), "command": command, "status": "NOT_RUN"}
    if args.check_only:
        print(json.dumps(result, indent=2))
        print("Preflight PASS; no training")
        return 0
    folder = ROOT / "outputs/motion_foundation" / f"lesson06_ab_{stamp}"
    folder.mkdir(parents=True, exist_ok=False)
    manifest = folder / "experiment.json"
    save = lambda: manifest.write_text(json.dumps(result, indent=2) + "\n")
    save()
    print(f"Manifest: {manifest}", flush=True)
    for name, arm in result["arms"].items():
        current = {str(p.relative_to(ROOT)): file_hash(p) for f in ("source", "scripts") for p in sorted((ROOT / f).rglob("*.py"))}
        if current != sources or file_hash(arm["parent"]) != arm["parent_sha256"] or file_hash(arm["reference"]) != arm["reference_sha256"]:
            raise RuntimeError("Paired inputs/source changed")
        log = folder / f"{name}.log"
        arm.update(status="RUNNING", terminal_log=str(log))
        save()
        print(f"Starting {name}; log: {log}", flush=True)
        with log.open("w") as stream:
            process = subprocess.Popen(arm["command"], cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT, start_new_session=True)
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
        arm.update(returncode=code, status="REJECTED_OR_RUNTIME_ERROR", segments=[])
        experiment_name = "csdog_motion_foundation" if name == "original" else "csdog_motion_envelope"
        runs = list((ROOT / "logs/rsl_rl" / experiment_name).glob(f"*_{arm['run_name']}"))
        if len(runs) == 1:
            run = runs[0]
            arm["run_directory"] = str(run)
            for report in sorted(run.glob("validation_*.json")):
                value = json.loads(report.read_text())
                done = int(report.stem.split("_")[-1])
                segment = run / f"segment_{done:04d}.pt"
                if file_hash(segment) != value["checkpoint_sha256"]:
                    raise RuntimeError("Evaluated segment hash mismatch")
                arm["segments"].append({"updates": done, "checkpoint": str(segment), "report": str(report),
                                        "gate": value["regression_gate"]})
            final = run / "model_final.pt"
            if code == 0 and final.is_file():
                metadata = json.loads(Path(str(final) + ".metadata.json").read_text())
                if (metadata["checkpoint_sha256"] == file_hash(final) and metadata["updates_in_this_run"] == 100
                        and [v["updates"] for v in arm["segments"]] == [20, 40, 60, 80, 100]
                        and all(v["gate"]["status"] == "PASS" for v in arm["segments"])):
                    arm.update(status="TRAIN_AND_SELF_REGRESSION_PASS", checkpoint=str(final))
        save()
        print(f"Finished {name}: {arm['status']}", flush=True)
    print(f"Experiment complete: {manifest}", flush=True)
    return 0 if all(v["status"] == "TRAIN_AND_SELF_REGRESSION_PASS" for v in result["arms"].values()) else 2


if __name__ == "__main__":
    raise SystemExit(main())
