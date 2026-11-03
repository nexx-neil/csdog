"""Small, device-agnostic reward kernels for Dog A foot gait shaping."""
from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

import torch


def foot_slip_signal(contact: torch.Tensor, foot_horizontal_velocity: torch.Tensor) -> torch.Tensor:
    """Return sum(contact * ||v_foot,xy||^2) across the four feet."""
    slip_speed_sq = foot_horizontal_velocity.square().sum(dim=-1)
    return (contact.to(slip_speed_sq.dtype) * slip_speed_sq).sum(dim=-1)


def swing_clearance_signal(
    contact: torch.Tensor,
    foot_height: torch.Tensor,
    current_air_time: torch.Tensor,
    vx_command: torch.Tensor,
    target_height: float,
    sigma: float,
    command_threshold: float,
    max_reward_air_time: float,
) -> torch.Tensor:
    """Bounded clearance score available only during a normal swing window."""
    moving = vx_command.abs() > command_threshold
    swing = (~contact) & (current_air_time <= max_reward_air_time)
    score = torch.exp(-0.5 * ((foot_height - target_height) / sigma).square())
    return (score * swing.to(score.dtype)).mean(dim=-1) * moving.to(score.dtype)


def long_air_time_signal(
    current_air_time: torch.Tensor,
    threshold: float,
    ramp_time: float,
) -> torch.Tensor:
    """Return a bounded per-step cost once any foot exceeds normal swing time."""
    excess = torch.clamp((current_air_time - threshold) / ramp_time, min=0.0, max=1.0)
    return excess.mean(dim=-1)


def excessive_air_time_signal(
    current_air_time: torch.Tensor,
    command_speed: torch.Tensor,
    command_threshold: float,
    moving_threshold_s: float,
    stationary_threshold_s: float,
    max_excess_s: float,
) -> torch.Tensor:
    """Growing air-time cost with separate moving and STOP grace periods."""
    moving = command_speed > command_threshold
    threshold = torch.where(
        moving, current_air_time.new_full(command_speed.shape, moving_threshold_s),
        current_air_time.new_full(command_speed.shape, stationary_threshold_s),
    )
    excess = torch.clamp(current_air_time - threshold[:, None], min=0.0, max=max_excess_s)
    # A mean would dilute one pathological held-up foot by four.  The maximum
    # makes any individual foot beyond the grace period increasingly costly.
    return excess.max(dim=-1).values


def directional_progress_signals(
    actual_velocity_xy: torch.Tensor,
    command_xy: torch.Tensor,
    command_threshold: float,
    ratio_clip: float,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Return signed progress speed and normalized ratio; both are zero for STOP."""
    command_speed = torch.linalg.vector_norm(command_xy, dim=-1)
    moving = command_speed > command_threshold
    command_direction = command_xy / command_speed.clamp(min=1.0e-6)[:, None]
    progress = (actual_velocity_xy * command_direction).sum(dim=-1)
    progress = progress * moving.to(progress.dtype)
    ratio = progress / command_speed.clamp(min=1.0e-6)
    ratio = torch.clamp(ratio, min=-ratio_clip, max=ratio_clip) * moving.to(progress.dtype)
    return progress, ratio


def locomotion_shortfall_signal(
    progress_speed: torch.Tensor,
    command_speed: torch.Tensor,
    command_threshold: float,
    min_progress_ratio: float,
) -> torch.Tensor:
    """Return missing along-command speed below a deliberately partial target.

    Requiring only a fraction of command speed preserves a gradient for gait
    exploration instead of demanding instantaneous perfect tracking. STOP is
    excluded explicitly.
    """
    moving = command_speed > command_threshold
    required_progress = min_progress_ratio * command_speed
    shortfall = torch.clamp(required_progress - progress_speed, min=0.0)
    return shortfall * moving.to(shortfall.dtype)


def stationary_stance_signal(
    contact: torch.Tensor,
    vx_command: torch.Tensor,
    command_threshold: float,
) -> torch.Tensor:
    """Reward four-foot stance only for a near-zero X command."""
    stationary = vx_command.abs() < command_threshold
    four_feet = contact.all(dim=-1)
    return four_feet.to(torch.float32) * stationary.to(torch.float32)


def stationary_action_signal(
    actions: torch.Tensor,
    vx_command: torch.Tensor,
    command_threshold: float,
) -> torch.Tensor:
    """Penalize squared action magnitude only for a near-zero X command."""
    stationary = vx_command.abs() < command_threshold
    return actions.square().mean(dim=-1) * stationary.to(actions.dtype)


def foot_air_time_signal(
    first_contact: torch.Tensor,
    last_air_time: torch.Tensor,
    vx_command: torch.Tensor,
    target_air_time: float,
    sigma: float,
    command_threshold: float,
    step_dt: float,
) -> torch.Tensor:
    """Bounded touchdown event score; holding a foot in air produces no reward."""
    moving = vx_command.abs() > command_threshold
    score = torch.exp(-0.5 * ((last_air_time - target_air_time) / sigma).square())
    # Reward kernels are rates integrated by step_dt in the environment.  Dividing
    # a one-step touchdown event by step_dt makes its integrated bonus independent
    # of control frequency.
    return (
        (score * first_contact.to(score.dtype)).mean(dim=-1)
        * moving.to(score.dtype)
        / step_dt
    )
