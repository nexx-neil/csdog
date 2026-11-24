#!/usr/bin/env python3
"""Read-only URDF/action-envelope audit; IK is a geometric probe, not a gait controller."""
import argparse
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation

ROOT = Path(__file__).resolve().parents[1]
URDF = ROOT / "source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot_sim.urdf"
LEGS = ("lr", "lf", "rf", "rr")


class Leg:
    def __init__(self, tree, name):
        joints = [tree.find(f"joint[@name='joint_{name}_{i}']") for i in (1, 2, 3)]
        self.origins = [np.fromstring(j.find("origin").get("xyz"), sep=" ") for j in joints]
        self.rotations = [Rotation.from_euler("xyz", np.fromstring(j.find("origin").get("rpy", "0 0 0"), sep=" ")).as_matrix() for j in joints]
        self.axes = [np.fromstring(j.find("axis").get("xyz"), sep=" ") for j in joints]
        self.axes = [axis / np.linalg.norm(axis) for axis in self.axes]
        fixed = tree.find(f"joint[@name='joint_link_{name}_sole_fixed']")
        self.sole = np.fromstring(fixed.find("origin").get("xyz"), sep=" ")

    def evaluate(self, q):
        position, rotation = np.zeros(3), np.eye(3)
        pivots, axes = [], []
        for angle, origin, local_rotation, axis in zip(q, self.origins, self.rotations, self.axes):
            position = position + rotation @ origin
            rotation = rotation @ local_rotation
            pivots.append(position.copy())
            axes.append(rotation @ axis)
            rotation = rotation @ Rotation.from_rotvec(axis * angle).as_matrix()
        foot = position + rotation @ self.sole
        jacobian = np.stack([np.cross(axis, foot - pivot) for axis, pivot in zip(axes, pivots)], axis=1)
        return foot, jacobian, np.array(pivots)

    def solve(self, target, bound, initial):
        result = least_squares(lambda q: self.evaluate(q)[0] - target,
                               np.clip(initial, -bound + 1e-8, bound - 1e-8),
                               jac=lambda q: self.evaluate(q)[1], bounds=(-bound, bound),
                               ftol=1e-10, xtol=1e-10, gtol=1e-10, max_nfev=80)
        return result.x, float(np.linalg.norm(result.fun))


def run(output):
    if output.exists():
        raise FileExistsError(output)
    tree = ET.parse(URDF).getroot()
    legs = {name: Leg(tree, name) for name in LEGS}
    result = {"scope": "static free-space FK/IK; ignores contact, collision, balance, torque, tracking dynamics; not proof of an executable gait",
              "urdf": str(URDF), "urdf_sha256": hashlib.sha256(URDF.read_bytes()).hexdigest(),
              "action_joint_offset_bound_rad": .35, "reflection": {}, "trajectory_probes": []}
    rng = np.random.default_rng(42)
    reflection = np.array([1., -1., 1.])
    for left, right in (("lf", "rf"), ("lr", "rr")):
        # Current joint axes require all three joint coordinates to change sign.
        # This tests that proposed map, rather than assuming it is a model symmetry.
        foot_error, knee_error = [], []
        for q in rng.uniform(-.35, .35, (1000, 3)):
            p, _, pivots = legs[left].evaluate(q)
            reflected_p, _, reflected_pivots = legs[right].evaluate(-q)
            foot_error.append(np.linalg.norm(reflected_p - p * reflection))
            knee_error.append(np.linalg.norm(reflected_pivots[-1] - pivots[-1] * reflection))
        p0 = legs[left].evaluate(np.zeros(3))[0]
        p1 = legs[right].evaluate(np.zeros(3))[0]
        result["reflection"][f"{left}_{right}"] = {
            "nominal_sole_reflection_error_m": float(np.linalg.norm(p1 - p0 * reflection)),
            "sampled_sole_reflection_rms_m": float(np.sqrt(np.mean(np.square(foot_error)))),
            "sampled_sole_reflection_max_m": float(max(foot_error)),
            "sampled_knee_reflection_rms_m": float(np.sqrt(np.mean(np.square(knee_error)))),
            "naive_joint_swap_is_exact_symmetry": bool(max(foot_error) < 1e-6)}
    # Prescribed flat, level-body trot: stance follows -v-omega cross r;
    # swing returns with zero endpoint lift and sin^2 clearance. It is only a
    # workspace probe. Ground reaction / acceleration is not solved by IK.
    commands = {"forward": (.4, 0, 0), "backward": (-.4, 0, 0),
                "left": (0, .3, 0), "right": (0, -.3, 0),
                "turn_left": (0, 0, .4), "turn_right": (0, 0, -.4)}
    for height_mode in ("exported_zero_pose", "level_base_0.386m"):
        for name, command in commands.items():
            entry = {"case": name, "command": command, "height_mode": height_mode, "legs": {}}
            for leg_name, leg in legs.items():
                nominal = leg.evaluate(np.zeros(3))[0]
                if height_mode == "level_base_0.386m":
                    nominal[2] = .018 - .386
                vx, vy, yaw = command
                body_velocity = np.array([vx - yaw * nominal[1], vy + yaw * nominal[0]])
                targets = []
                for phase in np.arange(50) / 50:
                    target = nominal.copy()
                    if phase < .5:
                        target[:2] += (.5 - phase * 2) * .25 * body_velocity
                    else:
                        progress = (phase - .5) * 2
                        # Smooth return: same endpoints, no instantaneous lift.
                        target[:2] += (-.5 + 3 * progress**2 - 2 * progress**3) * .25 * body_velocity
                        target[2] += .032 * np.sin(np.pi * progress)**2
                    targets.append(target)
                fits = {}
                for bound in (.35, .50):
                    initial = np.zeros(3)
                    solutions, errors = [], []
                    for target in targets:
                        initial, error = leg.solve(target, bound, initial)
                        solutions.append(initial.copy())
                        errors.append(error)
                    fits[str(bound)] = {"max_position_residual_m": max(errors),
                                       "rms_position_residual_m": float(np.sqrt(np.mean(np.square(errors)))),
                                       "samples_over_2mm": int(np.count_nonzero(np.array(errors) > .002)),
                                       "max_abs_joint_rad": np.max(np.abs(solutions), axis=0).tolist()}
                entry["legs"][leg_name] = fits
            result["trajectory_probes"].append(entry)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result["reflection"], indent=2))
    for item in result["trajectory_probes"]:
        print(item["height_mode"], item["case"], {leg: round(v["0.35"]["max_position_residual_m"] * 1000, 2) for leg, v in item["legs"].items()})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    run(parser.parse_args().output)
