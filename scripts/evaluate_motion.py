#!/usr/bin/env python3
"""One simulator launch for grouped fixed/transition-command regression screening."""

import argparse
import importlib
import json
from pathlib import Path
import time
import traceback

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--task", default="CSDog-V2-Teleop-Direct-v0")
parser.add_argument("--checkpoint", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--reference", type=Path)
parser.add_argument("--envs_per_case", type=int, default=4)
parser.add_argument("--steps", type=int, default=1000)
parser.add_argument("--cases", nargs="+")
parser.add_argument("--seed", type=int, default=42)
parser.add_argument("--protocol", choices=("standard", "lateral_grid"), default="standard")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.envs_per_case < 1 or args.steps < 1:
    parser.error("Positive environment and step counts required")
if args.output.exists():
    parser.error("Refusing to overwrite an evaluation report")
app = AppLauncher(args)

import gymnasium as gym
import torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import stackforce_simready_generated_robot_lab.tasks  # noqa
from csdog_motion.evaluation import default_cases, profile_at, protocol_hash, regression_gate
from csdog_motion.training import validate_checkpoint, file_hash
from csdog_motion.action_bounds import action_bounds, executed_actions


def run():
    cases = default_cases(args.protocol)
    if args.cases:
        available = {x["name"] for x in cases}
        if set(args.cases) - available:
            raise ValueError("Unknown evaluation case")
        cases = [x for x in cases if x["name"] in args.cases]
    count = len(cases)
    replicas = args.envs_per_case
    entry = gym.spec(args.task).kwargs["env_cfg_entry_point"]
    module, name = entry.split(":")
    cfg = getattr(importlib.import_module(module), name)()
    cfg.scene.num_envs = count * replicas
    cfg.sim.device = args.device
    cfg.seed = args.seed
    cfg.command_ranges = {key: (0.0, 0.0) for key in cfg.command_ranges}
    if hasattr(cfg, "periodic_commands"):
        cfg.periodic_commands = False
    metadata = validate_checkpoint(args.checkpoint, cfg, policy_only=True)
    env = gym.make(args.task, cfg=cfg)
    raw = env.unwrapped
    bounds = action_bounds(cfg, raw.device)
    try:
        obs, _ = env.reset()
        policy = ActorCritic(TensorDict(obs, batch_size=[raw.num_envs]),
                             {"policy": ["policy"], "critic": ["policy"]}, 12,
                             actor_hidden_dims=[256, 256, 128], critic_hidden_dims=[256, 256, 128], activation="elu")
        data = torch.load(args.checkpoint, map_location=raw.device, weights_only=True)
        policy.load_state_dict(data["model_state_dict"])
        policy.to(raw.device).eval()
        squared = torch.zeros(count, 3, device=raw.device)
        steady_squared = torch.zeros_like(squared)
        actual_sum = torch.zeros_like(squared)
        samples = torch.zeros(count, device=raw.device)
        steady_samples = torch.zeros_like(samples)
        failures = torch.zeros(count, replicas, device=raw.device)
        clipping = torch.zeros(count, device=raw.device)
        limit_violations = torch.zeros_like(clipping)
        finite = torch.ones(count, dtype=torch.bool, device=raw.device)
        height_sum = torch.zeros(count, device=raw.device)
        height_square = torch.zeros_like(height_sum)
        tilt_square = torch.zeros_like(height_sum)
        action_change_square = torch.zeros_like(height_sum)
        duty = torch.zeros(count, 4, device=raw.device)
        clearance_max = torch.zeros_like(duty)
        slip_sum = torch.zeros_like(height_sum)
        contact_samples = torch.zeros_like(height_sum)
        previous_actions = torch.zeros(raw.num_envs, 12, device=raw.device)
        causes = {key: torch.zeros(count, device=raw.device) for key in ("base_contact", "low_height", "tilt", "timeout")}
        requested_log = []
        started = time.monotonic()
        with torch.inference_mode():
            for step in range(args.steps):
                commands, ages = zip(*(profile_at(case["profile"], step * raw.step_dt) for case in cases))
                target = torch.tensor(commands, dtype=torch.float32, device=raw.device).repeat_interleave(replicas, dim=0)
                if hasattr(raw, "set_motion_request"):
                    raw.set_motion_request(target)
                else:
                    raw._commands.copy_(target)
                observation = raw._get_observations()
                actions = policy.act_inference(TensorDict(observation, batch_size=[raw.num_envs]))
                obs, reward, terminated, truncated, _ = env.step(actions)
                velocity = torch.cat((raw._robot.data.root_lin_vel_b[:, :2], raw._robot.data.root_ang_vel_b[:, 2:3]), dim=1)
                error = (velocity - target).reshape(count, replicas, 3)
                squared += error.square().sum(dim=1)
                actual_sum += velocity.reshape(count, replicas, 3).sum(dim=1)
                samples += replicas
                steady = torch.tensor(ages, device=raw.device) >= 1.0
                steady_squared += error.square().sum(dim=1) * steady[:, None]
                steady_samples += steady * replicas
                failures += terminated.reshape(count, replicas)
                height = raw._robot.data.root_pos_w[:, 2] - raw._terrain.env_origins[:, 2]
                height_sum += height.reshape(count, replicas).sum(dim=1)
                height_square += height.square().reshape(count, replicas).sum(dim=1)
                tilt = torch.acos((-raw._robot.data.projected_gravity_b[:, 2]).clamp(-1, 1))
                tilt_square += tilt.square().reshape(count, replicas).sum(dim=1)
                applied_actions = executed_actions(actions, bounds, observation["policy"][:, 52:53] if getattr(cfg, "posture_blend_actions", False) else None)
                action_change_square += (applied_actions - previous_actions).square().reshape(count, replicas, 12).mean(dim=2).sum(dim=1)
                previous_actions.copy_(applied_actions)
                contact = torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:, raw._foot_ids], dim=-1) > 1.0
                duty += contact.reshape(count, replicas, 4).float().sum(dim=1)
                foot_height = raw._robot.data.body_pos_w[:, raw._robot_foot_ids, 2] - raw._terrain.env_origins[:, 2:3] - 0.018
                clearance_max = torch.maximum(clearance_max, foot_height.reshape(count, replicas, 4).amax(dim=1))
                slip = torch.linalg.vector_norm(raw._robot.data.body_lin_vel_w[:, raw._robot_foot_ids, :2], dim=-1)
                slip_sum += (slip * contact).reshape(count, -1).sum(dim=1)
                contact_samples += contact.reshape(count, -1).sum(dim=1)
                clipping += (actions.abs() >= bounds).reshape(count, -1).float().mean(dim=1)
                limits = raw._robot.data.soft_joint_pos_limits[:, raw._actuated_joint_ids]
                targets = raw._processed_actions
                outside = (targets < limits[:, :, 0]) | (targets > limits[:, :, 1])
                limit_violations += outside.reshape(count, -1).sum(dim=1)
                valid = torch.isfinite(obs["policy"]).all(dim=1) & torch.isfinite(velocity).all(dim=1) & torch.isfinite(reward)
                finite &= valid.reshape(count, replicas).all(dim=1)
                for key, values in raw.last_termination_causes.items():
                    causes[key] += values.reshape(count, replicas).sum(dim=1)
                if step == 0 or step % 50 == 0:
                    requested_log.append({"step": step, "requested": list(commands)})
        wall = time.monotonic() - started
        result = {
            "schema_version": 1, "complete": True, "task": args.task,
            "protocol_name": args.protocol,
            "checkpoint": str(args.checkpoint.resolve()), "checkpoint_sha256": file_hash(args.checkpoint),
            "initialization_only": metadata.get("initialization_only", False),
            "protocol_sha256": protocol_hash(cases, args.steps, raw.step_dt, replicas, args.seed),
            "physics_contract": {"urdf_sha256": file_hash(cfg.robot.spawn.asset_path),
                                 "policy_dt": raw.step_dt, "action_scale": cfg.action_scale,
                                 "action_clip": cfg.action_clip, "joints": list(cfg.actuated_joint_names),
                                 "decimation": cfg.decimation, "physics_dt": cfg.sim.dt,
                                 "soft_joint_limit_factor": cfg.robot.soft_joint_pos_limit_factor,
                                 "self_collision": cfg.robot.spawn.self_collision,
                                 "rigid_body_properties": cfg.robot.spawn.rigid_props.to_dict(),
                                 "solver_properties": cfg.robot.spawn.articulation_props.to_dict(),
                                 "actuators": {key: {field: getattr(actuator, field) for field in
                                     ("stiffness", "damping", "effort_limit_sim", "velocity_limit_sim")}
                                     for key, actuator in cfg.robot.actuators.items()}},
            "seed": args.seed, "environments_per_case": replicas,
            "initial_conditions": "nominal reset clones; deterministic screening, not independent robustness trials",
            "simulation_seconds": args.steps * raw.step_dt, "loop_wall_seconds": wall,
            "real_time_factor": args.steps * raw.step_dt / wall,
            "cases": [], "requested_command_trace": requested_log,
        }
        if getattr(cfg, "action_clip_per_joint", None) is not None:
            result["physics_contract"]["action_clip_per_joint"] = list(cfg.action_clip_per_joint)
        if getattr(cfg, "record_nominal_pose_in_physics_contract", False):
            result["physics_contract"]["nominal_joint_positions_rad"] = [cfg.robot.init_state.joint_pos[name] for name in cfg.actuated_joint_names]
        if getattr(cfg, "posture_blend_actions", False):
            result["physics_contract"]["posture_blend_actions"] = True
        for i, case in enumerate(cases):
            result["cases"].append({
                "name": case["name"], "protected": case["protected"], "finite": bool(finite[i]),
                "failures": int(failures[i].sum()), "per_environment_failures": failures[i].int().tolist(),
                "termination_causes": {key: int(value[i]) for key, value in causes.items()},
                "mean_actual_twist": (actual_sum[i] / samples[i]).tolist(),
                "all_rmse": torch.sqrt(squared[i] / samples[i]).tolist(),
                "steady_rmse": torch.sqrt(steady_squared[i] / steady_samples[i].clamp_min(1)).tolist(),
                "steady_samples": int(steady_samples[i]),
                "action_clip_fraction": float(clipping[i] / args.steps),
                "target_limit_violations": int(limit_violations[i]),
                "body_height_mean_m": float(height_sum[i] / samples[i]),
                "body_height_std_m": float(torch.sqrt((height_square[i] / samples[i] - (height_sum[i] / samples[i]).square()).clamp_min(0))),
                "body_tilt_rms_deg": float(torch.sqrt(tilt_square[i] / samples[i]) * 180 / torch.pi),
                "action_change_rms_per_step": float(torch.sqrt(action_change_square[i] / samples[i])),
                "foot_contact_duty_factor": (duty[i] / samples[i]).tolist(),
                "foot_max_clearance_m": clearance_max[i].tolist(),
                "contact_slide_speed_proxy_mps": float(slip_sum[i] / contact_samples[i].clamp_min(1)),
            })
        result["screen_status"] = "PASS" if all(x["finite"] and x["failures"] == 0 and x["target_limit_violations"] == 0 for x in result["cases"]) else "FAIL"
        if args.reference:
            result["regression_gate"] = regression_gate(result, json.loads(args.reference.read_text()))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(f"Evaluation complete: {args.output}")
        for case in result["cases"]:
            print(case["name"], "actual=", [round(x, 3) for x in case["mean_actual_twist"]], "failures=", case["failures"])
        return 2 if args.reference and result["regression_gate"]["status"] != "PASS" else 0
    finally:
        env.close()


try:
    status = run()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
raise SystemExit(status)
