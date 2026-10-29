"""Run a bounded zero-action diagnostic for the generated quadruped."""

from __future__ import annotations

import argparse
import json
import math
import traceback
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Measure the generated robot under zero actions.")
parser.add_argument("--task", default="Template-GeneratedRobot-Direct-v0")
parser.add_argument("--duration", type=float, default=10.0, help="Simulation duration in seconds.")
parser.add_argument("--spawn-height", type=float, default=None, help="Override initial base height in meters.")
parser.add_argument("--hip-angle", type=float, default=0.0, help="Joint 1 target for all four legs.")
parser.add_argument(
    "--mirror-hip",
    action="store_true",
    help="Use +hip on right legs and -hip on left legs for a mirrored stance.",
)
parser.add_argument("--thigh-angle", type=float, default=0.0, help="Joint 2 target for all four legs.")
parser.add_argument("--knee-angle", type=float, default=0.0, help="Joint 3 target for all four legs.")
parser.add_argument(
    "--use-configured-pose",
    action="store_true",
    help="Use the environment's per-joint initial pose instead of the three shared angle overrides.",
)
parser.add_argument(
    "--stability-window", type=float, default=5.0, help="Final interval used for steady-state maxima."
)
parser.add_argument("--max-steady-linear-speed", type=float, default=0.05)
parser.add_argument("--max-steady-angular-speed", type=float, default=0.20)
parser.add_argument("--max-torque-limit-fraction", type=float, default=0.95)
parser.add_argument("--contact-force-threshold", type=float, default=1.0)
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--output", type=Path, default=None, help="Optional JSON report path.")
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

from isaaclab_tasks.utils import parse_env_cfg

import stackforce_simready_generated_robot_lab.tasks  # noqa: F401


def tensor_list(value: torch.Tensor) -> list[float]:
    return [round(float(item), 7) for item in value.detach().cpu().flatten()]


def main() -> None:
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=1, use_fabric=True)
    env_cfg.seed = args_cli.seed
    env_cfg.visual_disable_resets = True
    env_cfg.command_ranges = {
        "lin_vel_x": (0.0, 0.0),
        "lin_vel_y": (0.0, 0.0),
        "ang_vel_yaw": (0.0, 0.0),
    }
    if args_cli.spawn_height is not None:
        env_cfg.robot.init_state.pos = (0.0, 0.0, args_cli.spawn_height)
    if args_cli.use_configured_pose:
        pose = dict(env_cfg.robot.init_state.joint_pos)
    else:
        pose = {}
        for leg in ("FR", "FL", "RL", "RR"):
            hip_sign = -1.0 if args_cli.mirror_hip and leg in ("FL", "RL") else 1.0
            pose[f"{leg}1_joint"] = hip_sign * args_cli.hip_angle
            pose[f"{leg}2_joint"] = args_cli.thigh_angle
            pose[f"{leg}3_joint"] = args_cli.knee_angle
        env_cfg.robot.init_state.joint_pos = pose
        env_cfg.default_joint_angles = pose.copy()

    env = gym.make(args_cli.task, cfg=env_cfg)
    unwrapped = env.unwrapped
    env.reset()

    robot = unwrapped._robot
    contact_sensor = unwrapped._contact_sensor
    joint_ids = unwrapped._actuated_joint_ids
    step_dt = float(unwrapped.step_dt)
    num_steps = max(1, math.ceil(args_cli.duration / step_dt))
    stability_steps = min(num_steps, max(1, math.ceil(args_cli.stability_window / step_dt)))
    actions = torch.zeros(env.action_space.shape, device=unwrapped.device)

    start_height = robot.data.root_pos_w[0, 2] - unwrapped._terrain.env_origins[0, 2]
    min_height = start_height.clone()
    max_height = start_height.clone()
    max_abs_joint_vel = torch.zeros(len(joint_ids), device=unwrapped.device)
    max_abs_torque = torch.zeros(len(joint_ids), device=unwrapped.device)
    max_contact_force = torch.zeros(len(contact_sensor.body_names), device=unwrapped.device)
    stable_min_height = torch.tensor(float("inf"), device=unwrapped.device)
    stable_max_height = torch.tensor(float("-inf"), device=unwrapped.device)
    stable_max_root_linear_speed = torch.tensor(0.0, device=unwrapped.device)
    stable_max_root_angular_speed = torch.tensor(0.0, device=unwrapped.device)
    stable_max_abs_joint_vel = torch.zeros(len(joint_ids), device=unwrapped.device)
    stable_max_abs_torque = torch.zeros(len(joint_ids), device=unwrapped.device)
    reset_count = 0
    finite = True

    with torch.inference_mode():
        for step in range(num_steps):
            _, _, terminated, truncated, _ = env.step(actions)
            reset_count += int(torch.count_nonzero(terminated | truncated).item())

            height = robot.data.root_pos_w[0, 2] - unwrapped._terrain.env_origins[0, 2]
            min_height = torch.minimum(min_height, height)
            max_height = torch.maximum(max_height, height)
            max_abs_joint_vel = torch.maximum(
                max_abs_joint_vel, torch.abs(robot.data.joint_vel[0, joint_ids])
            )
            max_abs_torque = torch.maximum(
                max_abs_torque, torch.abs(robot.data.applied_torque[0, joint_ids])
            )
            body_force = torch.linalg.vector_norm(contact_sensor.data.net_forces_w[0], dim=-1)
            max_contact_force = torch.maximum(max_contact_force, body_force)

            if step >= num_steps - stability_steps:
                stable_min_height = torch.minimum(stable_min_height, height)
                stable_max_height = torch.maximum(stable_max_height, height)
                stable_max_root_linear_speed = torch.maximum(
                    stable_max_root_linear_speed, torch.linalg.vector_norm(robot.data.root_lin_vel_b[0])
                )
                stable_max_root_angular_speed = torch.maximum(
                    stable_max_root_angular_speed, torch.linalg.vector_norm(robot.data.root_ang_vel_b[0])
                )
                stable_max_abs_joint_vel = torch.maximum(
                    stable_max_abs_joint_vel, torch.abs(robot.data.joint_vel[0, joint_ids])
                )
                stable_max_abs_torque = torch.maximum(
                    stable_max_abs_torque, torch.abs(robot.data.applied_torque[0, joint_ids])
                )

            finite = finite and all(
                torch.isfinite(value).all().item()
                for value in (
                    robot.data.root_pos_w,
                    robot.data.root_quat_w,
                    robot.data.joint_pos,
                    robot.data.joint_vel,
                    robot.data.applied_torque,
                    contact_sensor.data.net_forces_w,
                )
            )

    final_height = robot.data.root_pos_w[0, 2] - unwrapped._terrain.env_origins[0, 2]
    final_contact_force = torch.linalg.vector_norm(contact_sensor.data.net_forces_w[0], dim=-1)
    effort_limits = robot.data.joint_effort_limits[0, joint_ids]
    stable_torque_fraction = stable_max_abs_torque / torch.clamp(effort_limits, min=1.0e-9)
    foot_names = set(unwrapped.cfg.foot_link_names)
    undesired_final_contacts = {
        name: round(float(force), 7)
        for name, force in zip(contact_sensor.body_names, final_contact_force, strict=True)
        if name not in foot_names and float(force) > args_cli.contact_force_threshold
    }
    checks = {
        "duration_at_least_30s": args_cli.duration >= 30.0,
        "finite": finite,
        "no_automatic_resets": reset_count == 0,
        "height_above_termination_threshold": float(min_height) >= float(unwrapped.cfg.min_base_height),
        "steady_linear_speed": float(stable_max_root_linear_speed) <= args_cli.max_steady_linear_speed,
        "steady_angular_speed": float(stable_max_root_angular_speed) <= args_cli.max_steady_angular_speed,
        "no_sustained_torque_saturation": bool(
            torch.all(stable_torque_fraction <= args_cli.max_torque_limit_fraction).item()
        ),
        "no_final_undesired_contact": not undesired_final_contacts,
    }
    report = {
        "schema_version": 1,
        "gate": {
            "status": "PASS" if all(checks.values()) else "FAIL",
            "checks": checks,
        },
        "task": args_cli.task,
        "seed": args_cli.seed,
        "duration_s": args_cli.duration,
        "step_dt_s": step_dt,
        "steps": num_steps,
        "finite": finite,
        "automatic_resets": reset_count,
        "actuated_joint_names": [robot.joint_names[int(index)] for index in joint_ids],
        "articulation_body_names": list(robot.body_names),
        "contact_sensor_body_names": list(contact_sensor.body_names),
        "configured_pose_rad": pose,
        "root_height_m": {
            "start": round(float(start_height), 7),
            "minimum": round(float(min_height), 7),
            "maximum": round(float(max_height), 7),
            "final": round(float(final_height), 7),
        },
        "projected_gravity_final": tensor_list(robot.data.projected_gravity_b[0]),
        "joint_position_final_rad": tensor_list(robot.data.joint_pos[0, joint_ids]),
        "joint_velocity_final_rad_s": tensor_list(robot.data.joint_vel[0, joint_ids]),
        "max_abs_joint_velocity_rad_s": tensor_list(max_abs_joint_vel),
        "max_abs_applied_torque_nm": tensor_list(max_abs_torque),
        "joint_effort_limit_nm": tensor_list(effort_limits),
        "steady_state": {
            "window_s": min(args_cli.duration, args_cli.stability_window),
            "root_height_min_m": round(float(stable_min_height), 7),
            "root_height_max_m": round(float(stable_max_height), 7),
            "max_root_linear_speed_m_s": round(float(stable_max_root_linear_speed), 7),
            "max_root_angular_speed_rad_s": round(float(stable_max_root_angular_speed), 7),
            "max_abs_joint_velocity_rad_s": tensor_list(stable_max_abs_joint_vel),
            "max_abs_applied_torque_nm": tensor_list(stable_max_abs_torque),
            "max_torque_limit_fraction": tensor_list(stable_torque_fraction),
        },
        "undesired_final_contacts_above_threshold_n": undesired_final_contacts,
        "max_contact_force_n": {
            name: value
            for name, value in zip(contact_sensor.body_names, tensor_list(max_contact_force), strict=True)
        },
        "final_contact_force_n": {
            name: value
            for name, value in zip(contact_sensor.body_names, tensor_list(final_contact_force), strict=True)
        },
    }

    rendered = json.dumps(report, indent=2, ensure_ascii=True)
    print("ZERO_POSE_DIAGNOSTIC_BEGIN")
    print(rendered)
    print("ZERO_POSE_DIAGNOSTIC_END")
    if args_cli.output is not None:
        args_cli.output.parent.mkdir(parents=True, exist_ok=True)
        args_cli.output.write_text(rendered + "\n", encoding="utf-8")

    env.close()


if __name__ == "__main__":
    try:
        main()
    except BaseException:
        traceback.print_exc()
        raise
    finally:
        simulation_app.close()
