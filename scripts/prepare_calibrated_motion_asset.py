#!/usr/bin/env python3
"""Restore mesh-derived sole locations and solve nominal joints, not sole translations."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np
from prepare_csdog_v2_sim_urdf import generate
from audit_motion_mechanics import Leg

ROOT = Path(__file__).resolve().parents[1]
ASSET = ROOT / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    folder = args.output_dir.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    output = folder / "robot_sim.urdf"
    profile = ROOT / "config/csdog_v2_hardware_profile.json"
    generate(ASSET / "robot.urdf", output, profile)
    tree = ET.parse(output)
    # One sibling package asset, referencing existing meshes without copying them.
    import os
    for mesh in tree.getroot().findall(".//mesh"):
        mesh.set("filename", os.path.relpath(ASSET / mesh.get("filename"), folder))
    tree.write(output, encoding="utf-8", xml_declaration=True)
    current = ET.parse(ASSET / "robot_sim.urdf").getroot()
    angles, targets, fit = {}, {}, {}
    for name in ("lr", "lf", "rf", "rr"):
        # Preserve the existing nominal body-frame foot placement, then solve
        # joints on the source-derived geometry. This compensates CAD zero
        # poses without inventing unequal contact lever lengths. The settled
        # height is measured separately; PD compliance is not ignored.
        target = Leg(current, name).evaluate(np.zeros(3))[0]
        leg = Leg(tree.getroot(), name)
        q, residual = leg.solve(target, .6, np.zeros(3))
        if residual > 1e-6:
            raise RuntimeError("Nominal pose IK failed")
        angles.update({f"joint_{name}_{i}": float(angle) for i, angle in enumerate(q, 1)})
        targets[name] = target.tolist()
        fit[name] = residual
    value = {"scope": "calibration candidate; standing and locomotion must be independently validated",
             "urdf": str(output), "standing_joint_angles": angles, "nominal_sole_positions_body_m": targets,
             "ik_residual_m": fit, "nominal_pose_rationale": "same foot placement as released zero pose; joints calibrated on original mesh-derived contacts; settled height measured under unchanged PD",
             "parent_current_urdf_sha256": digest(ASSET / "robot_sim.urdf"),
             "source_mesh_urdf_sha256": digest(ASSET / "robot.urdf"),
             "hardware_profile_sha256": digest(profile), "diagnostic_urdf_sha256": digest(output),
             "geometry_basis": "mesh-derived foot centers from versioned profile, not hardware certification"}
    (folder / "calibration.json").write_text(json.dumps(value, indent=2) + "\n")
    print(folder / "calibration.json")


if __name__ == "__main__":
    main()
