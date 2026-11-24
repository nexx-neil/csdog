#!/usr/bin/env python3
"""Compare learned policy outputs on the same real simulator observations; inference only."""
import argparse
import json
from pathlib import Path
import traceback

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
if args.output.exists():
    parser.error("Refusing to overwrite audit")
app = AppLauncher(args)

import gymnasium as gym
import torch
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_env_cfg import MotionFoundationEnvCfg
from csdog_motion.training import validate_checkpoint, file_hash


def main():
    root = Path(__file__).resolve().parents[1]
    experiment = json.loads((root / "outputs/motion_foundation/lesson02_ab_20261106_154408_697378/experiment.json").read_text())
    paths = {"parent": Path(experiment["parent_checkpoint"]),
             "control": Path(experiment["arms"]["control"]["checkpoint"]),
             "yaw": Path(experiment["arms"]["yaw_tight"]["checkpoint"]),
             "contact": root / "logs/rsl_rl/csdog_motion_foundation/2026-11-06_16-06-12_lesson03_contact3_h128_e256/model_final.pt"}
    names = ["stand", "forward", "backward", "left", "right", "turn_left", "turn_right"]
    cfg = MotionFoundationEnvCfg()
    cfg.scene.num_envs = len(names)
    cfg.sim.device = args.device
    cfg.seed = 42
    cfg.periodic_commands = False
    cfg.command_ranges = {key: (0.0, 0.0) for key in cfg.command_ranges}
    for path in paths.values():
        validate_checkpoint(path, cfg, policy_only=True)
    env = gym.make("CSDog-Motion-Foundation-Direct-v0", cfg=cfg)
    raw = env.unwrapped
    try:
        obs, _ = env.reset()
        policies = {}
        for name, path in paths.items():
            policy = ActorCritic(TensorDict(obs, batch_size=[raw.num_envs]),
                                 {"policy": ["policy"], "critic": ["policy"]}, 12,
                                 actor_hidden_dims=[256, 256, 128], critic_hidden_dims=[256, 256, 128], activation="elu")
            policy.load_state_dict(torch.load(path, map_location=raw.device, weights_only=True)["model_state_dict"])
            policies[name] = policy.to(raw.device).eval()
        commands = torch.tensor([[0, 0, 0], [.4, 0, 0], [-.4, 0, 0], [0, .3, 0],
                                 [0, -.3, 0], [0, 0, .4], [0, 0, -.4]], device=raw.device)
        observations = []
        terminations = 0
        with torch.inference_mode():
            for step in range(300):
                raw.set_motion_request(commands)
                obs = raw._get_observations()
                if step >= 50 and step % 5 == 0:
                    observations.append(obs["policy"].clone())
                actions = policies["parent"].act_inference(TensorDict(obs, batch_size=[raw.num_envs]))
                obs, reward, terminated, truncated, _ = env.step(actions)
                terminations += int(terminated.sum())
                if not torch.isfinite(obs["policy"]).all() or not torch.isfinite(reward).all():
                    raise RuntimeError("Nonfinite observation/reward")
            data = torch.stack(observations)  # time, case, observation
            flat = data.reshape(-1, 54)
            means = {key: policy.actor(policy.actor_obs_normalizer(flat)).reshape(data.shape[0], len(names), 12)
                     for key, policy in policies.items()}
            result = {
                "scope": "common-state policy-output audit, not per-policy closed-loop capability evaluation",
                "trajectory_policy": str(paths["parent"]), "simulation_seconds": 6.0,
                "samples_per_case": len(observations), "unexpected_terminations": terminations,
                "policy_gradient_updates": 0,
                "checkpoints": {key: {"path": str(path), "sha256": file_hash(path)} for key, path in paths.items()},
                "comparisons": {},
            }
            for candidate, reference in (("control", "parent"), ("yaw", "control"), ("contact", "control")):
                new, old = means[candidate], means[reference]
                new_std = policies[candidate].std
                old_std = policies[reference].std
                kl = (torch.log(new_std / old_std) + (old_std.square() + (old - new).square()) / (2 * new_std.square()) - .5).sum(dim=-1)
                joint_delta = cfg.action_scale * (new.clamp(-cfg.action_clip, cfg.action_clip) - old.clamp(-cfg.action_clip, cfg.action_clip))
                result["comparisons"][f"{candidate}_vs_{reference}"] = {
                    name: {"joint_target_delta_rms_rad": float(joint_delta[:, i].square().mean().sqrt()),
                           "joint_target_delta_max_rad": float(joint_delta[:, i].abs().max()),
                           "raw_action_delta_rms": float((new[:, i] - old[:, i]).square().mean().sqrt()),
                           "mean_gaussian_kl_reference_to_candidate": float(kl[:, i].mean())}
                    for i, name in enumerate(names)}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        torch.save({"observations": data.cpu(), "case_names": names, "sampling_dt_s": .1}, str(args.output) + ".observations.pt")
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result["comparisons"], indent=2))
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
