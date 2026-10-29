"""Measure each joint's positive and negative motion with the base fixed."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

from isaaclab.app import AppLauncher


parser = argparse.ArgumentParser(description="Diagnose generated quadruped joint mapping and directions.")
parser.add_argument("--task", default="Template-GeneratedRobot-Direct-v0")
parser.add_argument("--delta", type=float, default=0.1, help="Requested joint displacement in radians.")
parser.add_argument("--settle-duration", type=float, default=0.5)
parser.add_argument("--hold-duration", type=float, default=1.0)
parser.add_argument("--output", type=Path, default=None)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import torch

from isaaclab_tasks.utils import parse_env_cfg

import stackforce_simready_generated_robot_lab.tasks  # noqa: F401


def vector(value: torch.Tensor) -> list[float]:
    return [round(float(item), 7) for item in value.detach().cpu().flatten()]


def main() -> None:
    env_cfg = parse_env_cfg(args_cli.task, device=args_cli.device, num_envs=1, use_fabric=True)
    env_cfg.visual_disable_resets = True
    env_cfg.robot.spawn.fix_base = True
    env_cfg.robot.init_state.pos = (0.0, 0.0, 0.5)
    env_cfg.command_ranges = {
        "lin_vel_x": (0.0, 0.0),
        "lin_vel_y": (0.0, 0.0),
        "ang_vel_yaw": (0.0, 0.0),
    }

    env = gym.make(args_cli.task, cfg=env_cfg)
    unwrapped = env.unwrapped
    robot = unwrapped._robot
    joint_ids = [int(index) for index in unwrapped._actuated_joint_ids]
    joint_names = [robot.joint_names[index] for index in joint_ids]
    configured_child_names = getattr(unwrapped.cfg, "joint_child_link_names", None)
    configured_foot_names = getattr(unwrapped.cfg, "joint_foot_link_names", None)
    if configured_child_names is not None and len(configured_child_names) != len(joint_names):
        raise ValueError("joint_child_link_names must match the actuated joint count")
    if configured_foot_names is not None and len(configured_foot_names) != len(joint_names):
        raise ValueError("joint_foot_link_names must match the actuated joint count")
    step_dt = float(unwrapped.step_dt)
    settle_steps = max(1, math.ceil(args_cli.settle_duration / step_dt))
    hold_steps = max(1, math.ceil(args_cli.hold_duration / step_dt))
    zero_actions = torch.zeros(env.action_space.shape, device=unwrapped.device)
    results = []

    with torch.inference_mode():
        for action_index, (joint_id, joint_name) in enumerate(zip(joint_ids, joint_names, strict=True)):
            if configured_child_names is None:
                leg_name = joint_name.removesuffix("_joint")[:2]
                child_name = joint_name.removesuffix("_joint")
                foot_name = f"{leg_name}3"
            else:
                child_name = configured_child_names[action_index]
                foot_name = configured_foot_names[action_index]
            child_id = robot.body_names.index(child_name)
            foot_id = robot.body_names.index(foot_name)

            for direction in (1.0, -1.0):
                env.reset()
                for _ in range(settle_steps):
                    env.step(zero_actions)

                joint_before = robot.data.joint_pos[0, joint_id].clone()
                child_before = robot.data.body_pos_w[0, child_id].clone()
                foot_before = robot.data.body_pos_w[0, foot_id].clone()
                child_com_before = robot.data.body_com_pos_w[0, child_id].clone()
                foot_com_before = robot.data.body_com_pos_w[0, foot_id].clone()
                root_before = robot.data.root_pos_w[0].clone()
                action = zero_actions.clone()
                action[0, action_index] = direction * args_cli.delta / unwrapped.cfg.action_scale
                peak_torque = torch.tensor(0.0, device=unwrapped.device)

                for _ in range(hold_steps):
                    env.step(action)
                    peak_torque = torch.maximum(peak_torque, torch.abs(robot.data.applied_torque[0, joint_id]))

                joint_after = robot.data.joint_pos[0, joint_id]
                measured_delta = float(joint_after - joint_before)
                direction_pass = measured_delta * direction > 0.0 and abs(measured_delta) >= 0.5 * args_cli.delta
                results.append(
                    {
                        "action_index": action_index,
                        "robot_joint_index": joint_id,
                        "joint": joint_name,
                        "requested_delta_rad": round(direction * args_cli.delta, 7),
                        "measured_delta_rad": round(measured_delta, 7),
                        "direction_pass": direction_pass,
                        "direct_child": child_name,
                        "direct_child_displacement_xyz_m": vector(
                            robot.data.body_pos_w[0, child_id] - child_before
                        ),
                        "direct_child_com_displacement_xyz_m": vector(
                            robot.data.body_com_pos_w[0, child_id] - child_com_before
                        ),
                        "foot": foot_name,
                        "foot_displacement_xyz_m": vector(robot.data.body_pos_w[0, foot_id] - foot_before),
                        "foot_com_displacement_xyz_m": vector(
                            robot.data.body_com_pos_w[0, foot_id] - foot_com_before
                        ),
                        "root_displacement_xyz_m": vector(robot.data.root_pos_w[0] - root_before),
                        "peak_abs_torque_nm": round(float(peak_torque), 7),
                    }
                )

    failed_results = [result for result in results if not result["direction_pass"]]
    report = {
        "schema_version": 1,
        "gate": {
            "status": "PASS" if not failed_results else "FAIL",
            "failed_motion_count": len(failed_results),
            "criterion": "measured displacement has requested sign and magnitude >= 50% of request",
        },
        "task": args_cli.task,
        "coordinate_system": {"x": "forward", "y": "left", "z": "up"},
        "base_fixed": True,
        "requested_delta_rad": args_cli.delta,
        "settle_duration_s": args_cli.settle_duration,
        "hold_duration_s": args_cli.hold_duration,
        "joint_order": joint_names,
        "results": results,
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=True)
    print("JOINT_DIRECTION_DIAGNOSTIC_BEGIN")
    print(rendered)
    print("JOINT_DIRECTION_DIAGNOSTIC_END")
    if args_cli.output is not None:
        args_cli.output.parent.mkdir(parents=True, exist_ok=True)
        args_cli.output.write_text(rendered + "\n", encoding="utf-8")

    env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
