#!/usr/bin/env python3
"""Inference-only action-bound counterfactual, never a compatible policy release."""
import argparse
import json
from pathlib import Path
import traceback
import types
from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--checkpoint", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--profiles", choices=("uniform", "knee"), default="uniform")
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
    profiles = [("original_0.35rad", [1.] * 12), ("probe_0.42rad", [1.2] * 12),
                ("probe_0.50rad", [.5 / .35] * 12)]
    if args.profiles == "knee":
        profiles = [("original_0.35rad", [1.] * 12), ("probe_all_0.42rad", [1.2] * 12),
                    ("probe_knees_0.42rad", [1., 1., 1.2] * 4),
                    ("probe_knees_0.50rad", [1., 1., .5 / .35] * 4)]
    commands = [[0, 0, 0], [.4, 0, 0], [-.4, 0, 0], [0, .3, 0], [0, -.3, 0], [0, 0, .4], [0, 0, -.4]]
    names = ["stand", "forward", "backward", "left", "right", "turn_left", "turn_right"]
    count = len(commands)
    cfg = MotionFoundationEnvCfg()
    cfg.scene.num_envs = len(profiles) * count
    cfg.seed = 42
    cfg.sim.device = args.device
    cfg.periodic_commands = False
    cfg.episode_length_s = 25.0
    cfg.command_ranges = {key: (0., 0.) for key in cfg.command_ranges}
    validate_checkpoint(args.checkpoint, cfg, policy_only=True)
    env = gym.make("CSDog-Motion-Foundation-Direct-v0", cfg=cfg)
    raw = env.unwrapped
    bounds = torch.tensor([p[1] for p in profiles], device=raw.device).repeat_interleave(count, dim=0)

    def diagnostic_pre_step(self, actions):
        self._raw_actions = actions.clone()
        self._actions = torch.maximum(torch.minimum(actions, bounds), -bounds)
        self._pre_step_root_height = self._robot.data.root_pos_w[:, 2] - self._terrain.env_origins[:, 2]
        self._processed_actions = self.cfg.action_scale * self._actions + self._robot.data.default_joint_pos[:, self._actuated_joint_ids]

    raw._pre_physics_step = types.MethodType(diagnostic_pre_step, raw)
    try:
        obs, _ = env.reset()
        policy = ActorCritic(TensorDict(obs, batch_size=[raw.num_envs]), {"policy": ["policy"], "critic": ["policy"]}, 12,
                             actor_hidden_dims=[256, 256, 128], critic_hidden_dims=[256, 256, 128], activation="elu")
        policy.load_state_dict(torch.load(args.checkpoint, map_location=raw.device, weights_only=True)["model_state_dict"])
        policy.to(raw.device).eval()
        request = torch.tensor(commands * len(profiles), device=raw.device)
        velocities, errors, tilts, heights, targets, torques, contacts, clearances, clipping = [[] for _ in range(9)]
        failures = torch.zeros(raw.num_envs, device=raw.device)
        violations = torch.zeros_like(failures)
        with torch.inference_mode():
            for step in range(1000):
                raw.set_motion_request(request)
                obs = raw._get_observations()
                actions = policy.act_inference(TensorDict(obs, batch_size=[raw.num_envs]))
                obs, reward, terminated, truncated, _ = env.step(actions)
                failures += terminated
                limits = raw._robot.data.soft_joint_pos_limits[:, raw._actuated_joint_ids]
                violations += ((raw._processed_actions < limits[..., 0]) | (raw._processed_actions > limits[..., 1])).sum(dim=1)
                velocity = torch.cat((raw._robot.data.root_lin_vel_b[:, :2], raw._robot.data.root_ang_vel_b[:, 2:3]), dim=1)
                if not all(torch.isfinite(x).all() for x in (obs["policy"], actions, velocity, reward)):
                    raise RuntimeError("Nonfinite action-envelope probe")
                if step >= 100:
                    velocities.append(velocity.clone())
                    errors.append((velocity - request).square())
                    tilts.append(torch.acos((-raw._robot.data.projected_gravity_b[:, 2]).clamp(-1, 1)))
                    heights.append((raw._robot.data.root_pos_w[:, 2] - raw._terrain.env_origins[:, 2]).clone())
                    targets.append(raw._processed_actions.clone())
                    torques.append(raw._robot.data.applied_torque[:, raw._actuated_joint_ids].clone())
                    contact = torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[:, raw._foot_ids], dim=-1) > 1.
                    contacts.append(contact)
                    clearances.append(raw._robot.data.body_pos_w[:, raw._robot_foot_ids, 2] - raw._terrain.env_origins[:, 2:3] - .018)
                    clipping.append((actions.abs() >= bounds).float())
        velocity, error, tilt, height, target, torque, contact, clearance, clip = [torch.stack(x) for x in
            (velocities, errors, tilts, heights, targets, torques, contacts, clearances, clipping)]
        result = {"complete": True, "scope": "diagnostic counterfactual only; altered action/previous-action bounds violate the original policy interface; not deployment or training approval",
                  "checkpoint": str(args.checkpoint.resolve()), "checkpoint_sha256": file_hash(args.checkpoint),
                  "seed": 42, "gradient_updates": 0, "simulation_seconds": 20., "steady_start_s": 2.,
                  "physics_urdf_sha256": file_hash(cfg.robot.spawn.asset_path),
                  "physical_joint_limits_unchanged": True, "pd_gains_unchanged": True,
                  "replicas_per_case": 1, "groups": {}}
        for group_index, (name, bound) in enumerate(profiles):
            cases = []
            for i, case in enumerate(names):
                j = group_index * count + i
                cases.append({"name": case, "requested_twist": commands[i],
                              "mean_actual_twist": velocity[:, j].mean(0).tolist(), "steady_rmse": error[:, j].mean(0).sqrt().tolist(),
                              "body_tilt_rms_deg": float(tilt[:, j].square().mean().sqrt() * 180 / torch.pi),
                              "body_height_mean_m": float(height[:, j].mean()), "body_height_std_m": float(height[:, j].std()),
                              "unexpected_terminations": int(failures[j]), "target_limit_violations": int(violations[j]),
                              "joint_target_abs_max_rad": target[:, j].abs().amax(0).tolist(),
                              "per_joint_action_clip_fraction": clip[:, j].mean(0).tolist(),
                              "peak_torque_nm": float(torque[:, j].abs().max()),
                              "torque_limit_fraction": float((torque[:, j].abs() >= 11.99).float().mean()),
                              "foot_contact_duty_factor": contact[:, j].float().mean(0).tolist(),
                              "foot_max_clearance_m": clearance[:, j].amax(0).tolist()})
            result["groups"][name] = {"action_clip": bound, "target_bound_rad": [v * .35 for v in bound], "cases": cases}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        for name, group in result["groups"].items():
            print(name)
            for case in group["cases"]:
                print(case["name"], [round(v, 3) for v in case["mean_actual_twist"]], "tilt", round(case["body_tilt_rms_deg"], 2), "failures", case["unexpected_terminations"])
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
