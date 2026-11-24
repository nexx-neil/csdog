#!/usr/bin/env python3
"""Thirty-second zero-policy contact/standing probe, with FK cross-check."""
import argparse
import json
from pathlib import Path
import traceback
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--profile", choices=("current", "mesh_zero", "mesh_pose"), required=True)
parser.add_argument("--provenance", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.output.exists():
    parser.error("Refusing to overwrite contact diagnostic")
app = AppLauncher(args)

import gymnasium as gym
import numpy as np
import torch
import xml.etree.ElementTree as ET
import isaaclab.utils.math as math_utils
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_env_cfg import MotionFoundationEnvCfg
from csdog_motion.training import file_hash
from audit_motion_mechanics import Leg


def main():
    provenance = json.loads(args.provenance.read_text())
    cfg = MotionFoundationEnvCfg()
    cfg.scene.num_envs = 8
    cfg.seed = 42
    cfg.sim.device = args.device
    cfg.periodic_commands = False
    cfg.episode_length_s = 40.0
    cfg.command_ranges = {key: (0., 0.) for key in cfg.command_ranges}
    if args.profile != "current":
        if file_hash(provenance["urdf"]) != provenance["diagnostic_urdf_sha256"]:
            raise RuntimeError("Diagnostic asset hash mismatch")
        cfg.robot.spawn.asset_path = provenance["urdf"]
    elif file_hash(cfg.robot.spawn.asset_path) != provenance["parent_current_urdf_sha256"]:
        raise RuntimeError("Current asset changed")
    if args.profile == "mesh_pose":
        cfg.robot.init_state.joint_pos = provenance["standing_joint_angles"]
        cfg.default_joint_angles = provenance["standing_joint_angles"]
    fk = [Leg(ET.parse(cfg.robot.spawn.asset_path).getroot(), name) for name in ("lr", "lf", "rf", "rr")]
    env = gym.make("CSDog-Motion-Foundation-Direct-v0", cfg=cfg)
    raw = env.unwrapped
    try:
        obs, _ = env.reset()
        actions = torch.zeros(raw.num_envs, 12, device=raw.device)
        failures = torch.zeros(raw.num_envs, device=raw.device)
        contact_sum = torch.zeros(raw.num_envs, 4, device=raw.device)
        all_contacts = torch.zeros(raw.num_envs, device=raw.device)
        mean_force = torch.zeros_like(contact_sum)
        height_sum = torch.zeros_like(all_contacts)
        height_square = torch.zeros_like(all_contacts)
        tilt_square = torch.zeros_like(all_contacts)
        max_torque = torch.zeros_like(all_contacts)
        samples = 0
        fk_error = 0.
        with torch.inference_mode():
            for step in range(1500):
                raw.set_motion_request([0., 0., 0.])
                obs, reward, terminated, truncated, _ = env.step(actions)
                failures += terminated
                data = raw._robot.data
                if not torch.isfinite(obs["policy"]).all():
                    raise RuntimeError("Nonfinite standing diagnostic")
                if step in (0, 100, 500, 1000):
                    quaternion = data.root_quat_w[:, None].expand(-1, 4, -1)
                    foot_body = math_utils.quat_apply_inverse(quaternion.reshape(-1, 4),
                        (data.body_pos_w[:, raw._robot_foot_ids] - data.root_pos_w[:, None]).reshape(-1, 3)).reshape(-1, 4, 3).cpu().numpy()
                    q = data.joint_pos[:, raw._actuated_joint_ids].cpu().numpy().reshape(-1, 4, 3)
                    for i in range(raw.num_envs):
                        for j, leg in enumerate(fk):
                            fk_error = max(fk_error, float(np.linalg.norm(foot_body[i, j] - leg.evaluate(q[i, j])[0])))
                if step >= 500:
                    forces = torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:, raw._foot_ids], dim=-1)
                    contact = forces > 5.
                    contact_sum += contact.float()
                    all_contacts += torch.all(contact, dim=1)
                    mean_force += forces
                    height = data.root_pos_w[:, 2] - raw._terrain.env_origins[:, 2]
                    height_sum += height
                    height_square += height.square()
                    tilt_square += torch.acos((-data.projected_gravity_b[:, 2]).clamp(-1, 1)).square()
                    max_torque = torch.maximum(max_torque, data.applied_torque[:, raw._actuated_joint_ids].abs().amax(dim=1))
                    samples += 1
        mean_height = height_sum / samples
        tilt = (tilt_square / samples).sqrt() * 180 / torch.pi
        duty = all_contacts / samples
        passed = (not failures.any() and bool(torch.all(duty >= .99))
                  and bool(torch.all(tilt <= 3.)) and bool(torch.all((mean_height - .386).abs() <= .02))
                  and fk_error < .0001)
        result = {"complete": True, "profile": args.profile, "scope": "30s nominal zero-action PD standing only; not locomotion/hardware validation",
                  "policy_gradient_updates": 0, "num_envs": 8, "nominal_clones_not_independent_trials": True,
                  "simulation_seconds": 30., "statistics_interval_s": [10., 30.],
                  "urdf": cfg.robot.spawn.asset_path, "urdf_sha256": file_hash(cfg.robot.spawn.asset_path),
                  "standing_joint_angles": cfg.robot.init_state.joint_pos,
                  "unexpected_terminations": failures.int().tolist(),
                  "all_four_contact_fraction": duty.tolist(), "per_foot_contact_fraction": (contact_sum / samples).tolist(),
                  "mean_contact_force_n": (mean_force / samples).tolist(),
                  "height_mean_m": mean_height.tolist(),
                  "height_std_m": (height_square / samples - mean_height.square()).clamp_min(0).sqrt().tolist(),
                  "tilt_rms_deg": tilt.tolist(), "peak_torque_after_10s_nm": max_torque.tolist(),
                  "urdf_fk_vs_simulator_max_error_m": fk_error,
                  "standing_screen": "PASS" if passed else "FAIL",
                  "screen_thresholds": {"failures": 0, "all_four_contact_fraction_min": .99,
                                        "tilt_rms_max_deg": 3., "height_error_max_m": .02, "fk_error_max_m": .0001}}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(args.profile, result["standing_screen"], "height", float(mean_height.mean()), "tilt", float(tilt.mean()),
              "four-contact", float(duty.mean()), "FK error", fk_error)
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
