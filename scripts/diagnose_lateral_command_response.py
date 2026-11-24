#!/usr/bin/env python3
"""Paired closed-loop speed sweep, no gradient updates or configuration tuning."""
import argparse
import json
from pathlib import Path
import traceback
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--control", type=Path, required=True)
parser.add_argument("--candidate", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--record-reward-terms", action="store_true")
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.output.exists():
    parser.error("Refusing to overwrite diagnostic")
app = AppLauncher(args)

import gymnasium as gym
import torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_env_cfg import MotionFoundationEnvCfg
from csdog_motion.training import validate_checkpoint, file_hash


def main():
    speeds = [0.0, 0.1, 0.2, 0.3, -0.1, -0.2, -0.3]
    n = len(speeds)
    cfg = MotionFoundationEnvCfg()
    cfg.scene.num_envs = 2 * n
    cfg.seed = 42
    cfg.sim.device = args.device
    cfg.periodic_commands = False
    cfg.record_reward_terms = args.record_reward_terms
    cfg.episode_length_s = 25.0
    cfg.command_ranges = {key: (0.0, 0.0) for key in cfg.command_ranges}
    paths = [args.control, args.candidate]
    for path in paths:
        validate_checkpoint(path, cfg, policy_only=True)
    env = gym.make("CSDog-Motion-Foundation-Direct-v0", cfg=cfg)
    raw = env.unwrapped
    try:
        observation, _ = env.reset()
        policies = []
        for path in paths:
            policy = ActorCritic(TensorDict({"policy": observation["policy"][:n]}, batch_size=[n]),
                                 {"policy": ["policy"], "critic": ["policy"]}, 12,
                                 actor_hidden_dims=[256, 256, 128], critic_hidden_dims=[256, 256, 128], activation="elu")
            policy.load_state_dict(torch.load(path, map_location=raw.device, weights_only=True)["model_state_dict"])
            policies.append(policy.to(raw.device).eval())
        commands = torch.zeros(2 * n, 3, device=raw.device)
        commands[:, 1] = torch.tensor(speeds * 2, device=raw.device)
        velocity_sum = torch.zeros(2 * n, 3, device=raw.device)
        error_square = torch.zeros_like(velocity_sum)
        tilt_square = torch.zeros(2 * n, device=raw.device)
        failures = torch.zeros(2 * n, device=raw.device)
        samples = 0
        term_sums = {key: torch.zeros(2 * n, device=raw.device) for key in cfg.reward_scales}
        with torch.inference_mode():
            for step in range(1000):
                raw.set_motion_request(commands)
                observation = raw._get_observations()
                actions = torch.cat([policy.act_inference(TensorDict(
                    {"policy": observation["policy"][i*n:(i+1)*n]}, batch_size=[n]))
                    for i, policy in enumerate(policies)])
                observation, reward, terminated, truncated, _ = env.step(actions)
                velocity = torch.cat((raw._robot.data.root_lin_vel_b[:, :2], raw._robot.data.root_ang_vel_b[:, 2:3]), dim=1)
                failures += terminated
                if not all(torch.isfinite(value).all() for value in (actions, observation["policy"], velocity, reward)):
                    raise RuntimeError("Nonfinite diagnostic state")
                if step >= 100:
                    if args.record_reward_terms:
                        for key, value in raw.last_reward_terms.items():
                            term_sums[key] += value
                    velocity_sum += velocity
                    error_square += (velocity - commands).square()
                    tilt_square += torch.acos((-raw._robot.data.projected_gravity_b[:, 2]).clamp(-1, 1)).square()
                    samples += 1
        result = {"scope": "paired nominal-reset inference sweep; one trajectory per command, not robustness certification",
                  "seed": 42, "simulation_seconds": 20.0, "steady_start_s": 2.0,
                  "gradient_updates": 0, "groups": {}}
        for i, name in enumerate(("control", "candidate")):
            values = []
            for j, speed in enumerate(speeds):
                index = i * n + j
                values.append({"requested_vy_mps": speed,
                               "mean_actual_vx_vy_yaw": (velocity_sum[index] / samples).tolist(),
                               "steady_rmse_vx_vy_yaw": (error_square[index] / samples).sqrt().tolist(),
                               "tilt_rms_deg": float((tilt_square[index] / samples).sqrt() * 180 / torch.pi),
                               "unexpected_terminations": int(failures[index])})
                if args.record_reward_terms:
                    values[-1]["mean_scaled_reward_terms_per_second"] = {key: float(value[index] / samples / raw.step_dt) for key, value in term_sums.items()}
            result["groups"][name] = {"checkpoint": str(paths[i].resolve()), "sha256": file_hash(paths[i]), "cases": values}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        for name, group in result["groups"].items():
            print(name)
            for item in group["cases"]:
                print(item["requested_vy_mps"], item["mean_actual_vx_vy_yaw"], item["unexpected_terminations"])
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
