#!/usr/bin/env python3
"""Offline-only gate: failed geometry is written, then signalled by exit code 2."""
import argparse
import hashlib
import json
from pathlib import Path

from csdog_motion.calibration import ASSET
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.posture_preflight import PostureGeometry
from csdog_motion.residual_learning import learning_profile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--poses", type=Path, help="JSON {'poses': [{label, body_height_m, joint_positions_rad, body_rpy_rad?}]}")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    profile = learning_profile()
    poses = (json.loads(args.poses.read_text())["poses"] if args.poses else [{
        "label": "nominal", "body_height_m": profile["nominal_height_m"],
        "joint_positions_rad": profile["nominal_joint_positions_rad"]}])
    if not poses:
        raise ValueError("No poses to audit")
    model = PostureGeometry(ASSET/"robot_sim.urdf", JOINT_NAMES)
    results = []
    for pose in poses:
        result = model.audit(pose["joint_positions_rad"], pose["body_height_m"], pose.get("body_rpy_rad", (0, 0, 0)))
        result["label"] = pose["label"]
        results.append(result)
    import csdog_motion.posture_preflight as implementation
    inputs = [Path(__file__).resolve(), Path(implementation.__file__), ASSET/"robot_sim.urdf"]
    if args.poses:
        inputs.append(args.poses.resolve())
    report = {"schema": "csdog_offline_posture_preflight_v1", "joint_order": JOINT_NAMES,
        "geometry_pass": all(r["geometry_pass"] for r in results),
        "execution_authorized": False, "training_authorized": False,
        "note": "No simulator was started. A geometric pass never authorizes a contact transition.",
        "input_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}, "poses": results}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n")
    print(f"OFFLINE geometry {'PASS' if report['geometry_pass'] else 'FAIL'}: {args.output.resolve()}")
    return 0 if report["geometry_pass"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
