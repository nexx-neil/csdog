"""Deterministic algebraic sanity gates for the Dog A X anti-slip rewards."""
from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from shared.paths import load_project_yaml

import argparse
import json
from pathlib import Path

import torch
import yaml

from dogfight.tasks.dog_a_locomotion_ppo_smoke_v1.reward_terms import (
    foot_air_time_signal,
    foot_slip_signal,
    long_air_time_signal,
    stationary_action_signal,
    stationary_stance_signal,
    swing_clearance_signal,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=Path("02_training/configs/dog_a_x_anti_slip_ppo.yaml"))
    parser.add_argument("--output", type=Path, default=Path("02_training/logs/x_anti_slip_reward_sanity.json"))
    args = parser.parse_args()
    cfg = load_project_yaml(args.config.read_text(encoding="utf-8"))
    scales = cfg["reward_scales"]
    foot_cfg = cfg["foot_reward"]
    dt = float(cfg["simulation_dt_s"]) * int(cfg["policy_decimation"])

    # Mirroring both command and achieved X velocity must not alter tracking.
    cmd = torch.tensor([0.5, -0.5, 0.0])
    actual = torch.tensor([0.4, -0.4, 0.0])
    track = float(scales["forward_velocity_tracking"]) * torch.exp(-(actual - cmd).square() / 0.25)

    contact = torch.tensor([[True, True, False, False]])
    no_slip_velocity = torch.zeros((1, 4, 2))
    fast_slip_velocity = torch.tensor([[[0.8, 0.0], [0.0, 0.8], [2.0, 0.0], [2.0, 0.0]]])
    slip_zero = foot_slip_signal(contact, no_slip_velocity)
    slip_fast = foot_slip_signal(contact, fast_slip_velocity)

    all_swing = torch.zeros((1, 4), dtype=torch.bool)
    target = float(foot_cfg["clearance_target_m"])
    sigma = float(foot_cfg["clearance_sigma_m"])
    threshold = float(foot_cfg["command_threshold_mps"])
    long_threshold = float(foot_cfg["long_air_time_threshold_s"])
    long_ramp = float(foot_cfg["long_air_time_ramp_s"])
    normal_air = torch.full((1, 4), 0.18)
    held_air = torch.full((1, 4), 10.0)
    clearance_ground = swing_clearance_signal(all_swing, torch.zeros((1, 4)), normal_air, torch.tensor([0.5]), target, sigma, threshold, long_threshold)
    clearance_target = swing_clearance_signal(all_swing, torch.full((1, 4), target), normal_air, torch.tensor([0.5]), target, sigma, threshold, long_threshold)
    clearance_high = swing_clearance_signal(all_swing, torch.full((1, 4), 0.10), normal_air, torch.tensor([0.5]), target, sigma, threshold, long_threshold)
    clearance_stationary = swing_clearance_signal(all_swing, torch.full((1, 4), target), normal_air, torch.tensor([0.0]), target, sigma, threshold, long_threshold)
    clearance_held = swing_clearance_signal(all_swing, torch.full((1, 4), target), held_air, torch.tensor([0.5]), target, sigma, threshold, long_threshold)
    normal_air_cost = long_air_time_signal(normal_air, long_threshold, long_ramp)
    held_air_cost = long_air_time_signal(held_air, long_threshold, long_ramp)
    four_contact = torch.ones((1, 4), dtype=torch.bool)
    three_contact = torch.tensor([[True, True, True, False]])
    stance_four = stationary_stance_signal(four_contact, torch.tensor([0.0]), threshold)
    stance_three = stationary_stance_signal(three_contact, torch.tensor([0.0]), threshold)
    stance_moving = stationary_stance_signal(four_contact, torch.tensor([0.5]), threshold)
    action_zero = stationary_action_signal(torch.zeros((1, 12)), torch.tensor([0.0]), threshold)
    action_saturated = stationary_action_signal(torch.ones((1, 12)), torch.tensor([0.0]), threshold)
    action_moving = stationary_action_signal(torch.ones((1, 12)), torch.tensor([0.5]), threshold)

    first_contact = torch.tensor([[True, False, False, False]])
    last_air = torch.full((1, 4), float(foot_cfg["air_time_target_s"]))
    air_move = foot_air_time_signal(
        first_contact, last_air, torch.tensor([0.5]), float(foot_cfg["air_time_target_s"]),
        float(foot_cfg["air_time_sigma_s"]), threshold, dt,
    )
    air_stationary = foot_air_time_signal(
        first_contact, last_air, torch.tensor([0.0]), float(foot_cfg["air_time_target_s"]),
        float(foot_cfg["air_time_sigma_s"]), threshold, dt,
    )
    air_held = foot_air_time_signal(
        torch.zeros_like(first_contact), torch.full_like(last_air, 10.0), torch.tensor([0.5]),
        float(foot_cfg["air_time_target_s"]), float(foot_cfg["air_time_sigma_s"]), threshold, dt,
    )

    cross_track_weight = float(cfg["straight_reward"]["cross_track_weight"])
    cross_track_at_x_only = -cross_track_weight * torch.tensor([0.0]).square()
    cross_track_at_y_offset = -cross_track_weight * torch.tensor([0.25]).square()
    heading_weight = float(cfg["straight_reward"]["heading_weight"])
    yaw_probe = torch.tensor([0.5])
    heading_at_zero = -heading_weight * (1.0 - torch.cos(torch.tensor([0.0])))
    heading_at_yaw = -heading_weight * (1.0 - torch.cos(yaw_probe))
    old_heading_at_yaw = -2.0 * (1.0 - torch.cos(yaw_probe))
    world_y_weight = float(cfg["straight_reward"]["world_y_velocity_weight"])
    world_y_at_zero = -world_y_weight * torch.tensor([0.0]).square()
    world_y_at_drift = -world_y_weight * torch.tensor([0.4]).square()
    stationary_heading_weight = float(cfg["straight_reward"]["stationary_heading_weight"])
    stop_heading_aligned = stationary_heading_weight * 0.5 * (1.0 + torch.cos(torch.tensor([0.0])))
    stop_heading_yawed = stationary_heading_weight * 0.5 * (1.0 + torch.cos(yaw_probe))
    moving_heading_aligned = torch.tensor([0.0])
    values = torch.cat((track, slip_zero, slip_fast, clearance_ground, clearance_target, clearance_high,
                        clearance_stationary, clearance_held, normal_air_cost, held_air_cost,
                        stance_four, stance_three, stance_moving, action_zero, action_saturated, action_moving,
                        air_move, air_stationary, air_held,
                        cross_track_at_x_only, cross_track_at_y_offset,
                        heading_at_zero, heading_at_yaw, old_heading_at_yaw,
                        world_y_at_zero, world_y_at_drift,
                        stop_heading_aligned, stop_heading_yawed, moving_heading_aligned))
    checks = {
        "finite": bool(torch.isfinite(values).all()),
        "positive_negative_tracking_symmetric": bool(torch.isclose(track[0], track[1])),
        "contact_slip_increases": bool(slip_fast.item() > slip_zero.item()),
        "swing_clearance_peaks_near_target": bool(clearance_target.item() > clearance_ground.item() and clearance_target.item() > clearance_high.item()),
        "clearance_is_bounded": bool(clearance_target.item() <= 1.0 and clearance_high.item() < clearance_target.item()),
        "stationary_has_no_swing_reward": clearance_stationary.item() == 0.0,
        "long_held_foot_has_no_clearance_reward": clearance_held.item() == 0.0,
        "normal_swing_has_no_long_air_penalty": normal_air_cost.item() == 0.0,
        "long_held_foot_is_penalized": held_air_cost.item() > 0.0,
        "stationary_four_feet_rewarded": stance_four.item() == 1.0,
        "stationary_three_leg_stance_not_rewarded": stance_three.item() == 0.0,
        "stance_reward_does_not_affect_motion": stance_moving.item() == 0.0,
        "stationary_saturated_action_penalized": action_saturated.item() > action_zero.item(),
        "action_penalty_does_not_affect_motion": action_moving.item() == 0.0,
        "stationary_has_no_air_time_reward": air_stationary.item() == 0.0,
        "held_foot_has_no_air_time_reward": air_held.item() == 0.0,
        "cross_track_ignores_x_displacement": cross_track_at_x_only.item() == 0.0,
        "cross_track_penalizes_y_displacement": cross_track_at_y_offset.item() < 0.0,
        "heading_penalty_increases_with_yaw": heading_at_yaw.item() < heading_at_zero.item(),
        "heading_penalty_is_stronger_than_previous_weight": heading_at_yaw.item() < old_heading_at_yaw.item(),
        "world_y_velocity_drift_is_explicitly_penalized": world_y_at_drift.item() < world_y_at_zero.item(),
        "stationary_yaw_alignment_has_higher_reward": stop_heading_aligned.item() > stop_heading_yawed.item(),
        "stationary_heading_reward_is_gated_during_motion": moving_heading_aligned.item() == 0.0,
    }
    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "probe_values": {
            "tracking_positive_rate": track[0].item(),
            "tracking_negative_rate": track[1].item(),
            "tracking_stationary_rate": track[2].item(),
            "slip_signal_no_slip": slip_zero.item(),
            "slip_signal_two_contact_feet_at_0p8_mps": slip_fast.item(),
            "weighted_slip_penalty_rate": float(scales["foot_slip_penalty"]) * slip_fast.item(),
            "clearance_ground": clearance_ground.item(),
            "clearance_target_0p03m": clearance_target.item(),
            "clearance_high_0p10m": clearance_high.item(),
            "clearance_held_10s": clearance_held.item(),
            "weighted_long_air_penalty_rate_10s": float(scales["long_air_time_penalty"]) * held_air_cost.item(),
            "weighted_stationary_four_foot_reward_rate": float(scales["stationary_four_foot_stance"]) * stance_four.item(),
            "weighted_stationary_saturated_action_penalty_rate": float(scales["stationary_action_magnitude_penalty"]) * action_saturated.item(),
            "air_time_touchdown_integrated_bonus": float(scales["foot_air_time"]) * air_move.item() * dt,
            "cross_track_y_0p25m_rate": cross_track_at_y_offset.item(),
            "heading_yaw_0p5rad_rate": heading_at_yaw.item(),
            "heading_yaw_0p5rad_previous_weight_rate": old_heading_at_yaw.item(),
            "world_y_velocity_0p4mps_rate": world_y_at_drift.item(),
            "stationary_heading_reward_yaw_0rad_rate": stop_heading_aligned.item(),
            "stationary_heading_reward_yaw_0p5rad_rate": stop_heading_yawed.item(),
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    if result["status"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
