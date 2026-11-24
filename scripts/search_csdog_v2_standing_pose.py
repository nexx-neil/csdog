"""Rank symmetric CSDog v2 standing poses in one reproducible Isaac Lab batch.

This is a diagnostic search, not an optimizer and not a training run.  Every
candidate and score component is written to JSON so the selected pose is
auditable.
"""

from __future__ import annotations

import argparse
import itertools
import json
import math
import traceback
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Grid-search a collision-free CSDog v2 standing pose.")
parser.add_argument("--task", default="CSDog-V2-Calibration-Direct-v0")
parser.add_argument("--duration", type=float, default=4.0)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--output", type=Path, required=True)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

from isaaclab_tasks.utils import parse_env_cfg

import stackforce_simready_generated_robot_lab.tasks  # noqa: F401


GRID = (-0.8, 0.0, 0.8)


def main() -> None:
    # Front and rear pitch/knee values are independent; left/right use equal
    # joint coordinates because the URDF axes are mirrored across the body.
    values = list(itertools.product(GRID, GRID, GRID, GRID))
    cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=len(values), use_fabric=True)
    cfg.seed = args_cli.seed
    cfg.visual_disable_resets = True
    cfg.action_scale = 1.0
    cfg.action_clip = 2.0
    cfg.command_ranges = {
        "lin_vel_x": (0.0, 0.0),
        "lin_vel_y": (0.0, 0.0),
        "ang_vel_yaw": (0.0, 0.0),
    }
    env = gym.make(args_cli.task, cfg=cfg)
    unwrapped = env.unwrapped
    robot = unwrapped._robot
    sensor = unwrapped._contact_sensor
    joint_ids = [int(index) for index in unwrapped._actuated_joint_ids]
    joint_names = [robot.joint_names[index] for index in joint_ids]
    name_to_action = {name: index for index, name in enumerate(joint_names)}
    actions = torch.zeros((len(values), len(joint_ids)), device=unwrapped.device)

    candidates = []
    for env_index, (front_hip, front_knee, rear_hip, rear_knee) in enumerate(values):
        pose = {}
        for leg in ("lf", "rf"):
            pose[f"joint_{leg}_1"] = 0.0
            pose[f"joint_{leg}_2"] = front_hip
            pose[f"joint_{leg}_3"] = front_knee
        for leg in ("lr", "rr"):
            pose[f"joint_{leg}_1"] = 0.0
            pose[f"joint_{leg}_2"] = rear_hip
            pose[f"joint_{leg}_3"] = rear_knee
        for name, angle in pose.items():
            actions[env_index, name_to_action[name]] = angle
        candidates.append(pose)

    env.reset()
    # Start each candidate at its commanded pose rather than dropping all 81
    # robots from the exported zero pose.
    joint_state = robot.data.default_joint_pos.clone()
    joint_state[:, joint_ids] = actions
    robot.write_joint_state_to_sim(joint_state, torch.zeros_like(joint_state))

    steps = max(1, math.ceil(args_cli.duration / float(unwrapped.step_dt)))
    peak_torque = torch.zeros_like(actions)
    with torch.inference_mode():
        for _ in range(steps):
            env.step(actions)
            peak_torque = torch.maximum(peak_torque, torch.abs(robot.data.applied_torque[:, joint_ids]))

    body_forces = torch.linalg.vector_norm(sensor.data.net_forces_w, dim=-1)
    body_index = {name: index for index, name in enumerate(sensor.body_names)}
    sole_names = list(cfg.foot_link_names)
    knee_names = [f"link_{leg}_knee" for leg in ("lf", "lr", "rf", "rr")]
    root_speed = torch.linalg.vector_norm(robot.data.root_lin_vel_b, dim=-1)
    root_angular_speed = torch.linalg.vector_norm(robot.data.root_ang_vel_b, dim=-1)
    tilt = torch.linalg.vector_norm(robot.data.projected_gravity_b[:, :2], dim=-1)
    heights = robot.data.root_pos_w[:, 2] - unwrapped._terrain.env_origins[:, 2]
    effort_limits = robot.data.joint_effort_limits[:, joint_ids]
    torque_fraction = peak_torque / torch.clamp(effort_limits, min=1.0e-9)

    results = []
    for index, pose in enumerate(candidates):
        sole_forces = [float(body_forces[index, body_index[name]]) for name in sole_names]
        knee_forces = [float(body_forces[index, body_index[name]]) for name in knee_names]
        missing_feet = sum(force <= 1.0 for force in sole_forces)
        knee_force_sum = sum(knee_forces)
        saturation = float(torch.max(torque_fraction[index]))
        # Hard-contact and missing-foot penalties dominate; posture and motion
        # only rank candidates that already stand on their soles.
        score = (
            100.0 * missing_feet
            + 5.0 * knee_force_sum
            + 50.0 * float(tilt[index])
            + 20.0 * float(root_speed[index])
            + 10.0 * float(root_angular_speed[index])
            + 20.0 * max(0.0, saturation - 0.9)
        )
        results.append(
            {
                "candidate_index": index,
                "score": round(score, 6),
                "pose_rad": pose,
                "root_height_m": round(float(heights[index]), 6),
                "root_speed_m_s": round(float(root_speed[index]), 6),
                "root_angular_speed_rad_s": round(float(root_angular_speed[index]), 6),
                "projected_gravity_xy_norm": round(float(tilt[index]), 6),
                "sole_contact_force_n": dict(zip(sole_names, (round(v, 6) for v in sole_forces), strict=True)),
                "knee_contact_force_n": dict(zip(knee_names, (round(v, 6) for v in knee_forces), strict=True)),
                "missing_sole_contacts": missing_feet,
                "knee_contact_force_sum_n": round(knee_force_sum, 6),
                "max_peak_torque_limit_fraction": round(saturation, 6),
            }
        )

    results.sort(key=lambda item: item["score"])
    report = {
        "schema_version": 1,
        "task": args_cli.task,
        "seed": args_cli.seed,
        "grid_rad": list(GRID),
        "candidate_count": len(results),
        "duration_s": args_cli.duration,
        "selection_rule": "lowest explicit score; sole/knee contact penalties dominate posture and motion",
        "top_candidates": results[:20],
        "all_candidates": results,
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=True)
    args_cli.output.parent.mkdir(parents=True, exist_ok=True)
    args_cli.output.write_text(rendered + "\n", encoding="utf-8")
    print("STANDING_POSE_SEARCH_TOP_BEGIN")
    print(json.dumps(report["top_candidates"][:5], indent=2, ensure_ascii=True))
    print("STANDING_POSE_SEARCH_TOP_END")
    env.close()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
    finally:
        simulation_app.close()
