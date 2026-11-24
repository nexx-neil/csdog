#!/usr/bin/env python3
"""Exercise the physical foundation with zero actions. No policy optimization."""

import argparse
import json
import traceback
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output", type=Path, required=True)
parser.add_argument("--num_envs", type=int, default=64)
AppLauncher.add_app_launcher_args(parser)
args = parser.parse_args()
app = AppLauncher(args)

import gymnasium as gym
import torch
import stackforce_simready_generated_robot_lab.tasks  # noqa
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_env_cfg import MotionFoundationEnvCfg
from csdog_motion.commands import MotionMode
from csdog_motion.training import EpisodeCounterProxy


def main():
    cfg = MotionFoundationEnvCfg()
    cfg.scene.num_envs = args.num_envs
    cfg.sim.device = args.device
    cfg.seed = 42
    cfg.periodic_commands = False
    env = gym.make("CSDog-Motion-Foundation-Direct-v0", cfg=cfg)
    raw = env.unwrapped
    try:
        obs, _ = env.reset()
        assert obs["policy"].shape == (args.num_envs, 54)
        class Proxy(EpisodeCounterProxy):
            pass
        proxy = Proxy()
        proxy.env = env
        before = raw.motion.phase.clone()
        proxy.episode_length_buf = torch.arange(args.num_envs, device=raw.device)
        assert torch.equal(raw.episode_length_buf, torch.arange(args.num_envs, device=raw.device))
        assert torch.equal(raw.motion.phase, before)
        raw.episode_length_buf.zero_()
        requests = torch.zeros(args.num_envs, 3, device=raw.device)
        patterns = requests.new_tensor([[0.08, 0, 0], [0, 0.06, 0], [0, 0, 0.08], [0.2, 0.15, 0.2]])
        groups = torch.arange(args.num_envs, device=raw.device) % 4
        modes = set()
        failures = 0
        finite = True
        raw.set_motion_request(requests)
        for step in range(500):
            if step == 50:
                raw.set_motion_request(patterns[groups])
            elif step in (175, 375):
                raw.set_motion_request(requests)
            elif step == 275:
                raw.set_motion_request(-patterns[groups])
            obs, reward, terminated, truncated, _ = env.step(torch.zeros(args.num_envs, 12, device=raw.device))
            finite &= bool(torch.isfinite(obs["policy"]).all() and torch.isfinite(reward).all())
            failures += int(terminated.sum())
            modes.update(raw.motion.mode.unique().tolist())
            phase = raw.motion.phase.clone()
            raw._get_observations()
            assert torch.equal(phase, raw.motion.phase), "Reading observations advanced the clock twice"
        stopped = bool(torch.all(raw.motion.mode == MotionMode.STAND))
        assert finite and failures == 0 and stopped
        # Check in-episode resampling independently of the external command stream.
        raw._external_commands = False
        raw.cfg.periodic_commands = True
        raw._command_remaining.fill_(0.04)
        original = raw.motion.request.clone()
        for _ in range(10):
            env.step(torch.zeros(args.num_envs, 12, device=raw.device))
        resampled = bool(torch.any(raw.motion.request != original))
        assert resampled
        result = {
            "status": "PASS", "scope": "zero-action PD/interface smoke; not learned locomotion",
            "environments": args.num_envs, "physics_control_steps": 510, "gradient_updates": 0,
            "observation_dimensions": 54, "finite": finite, "unexpected_terminations": failures,
            "episode_counter_proxy_reaches_simulation": True,
            "gait_clock_independent_of_episode_age": True,
            "observation_reads_do_not_advance_time": True,
            "observed_modes": sorted(modes), "settled_into_stand": stopped,
            "in_episode_resampling_observed": resampled,
            "height_range": [raw.motion.cfg.height_min_m, raw.motion.cfg.height_max_m],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2))
    finally:
        env.close()


try:
    main()
except BaseException:
    traceback.print_exc()
    raise
finally:
    app.app.close()
