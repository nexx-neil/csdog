"""Batched command shaping with independent command, gait and episode clocks."""

from dataclasses import dataclass
from enum import IntEnum

import torch


class MotionMode(IntEnum):
    STAND = 0
    START = 1
    MOVE = 2
    STOP = 3


@dataclass(frozen=True)
class MotionCommandConfig:
    limits: tuple = (0.4, 0.3, 0.4)
    acceleration: tuple = (0.8, 0.8, 1.6)
    input_deadband: tuple = (0.01, 0.01, 0.02)
    start_threshold: tuple = (0.02, 0.02, 0.04)
    stop_threshold: tuple = (0.005, 0.005, 0.01)
    gait_period_s: float = 0.5
    clock_runs_in_stand: bool = True
    start_blend_s: float = 0.25
    stop_blend_s: float = 0.5
    nominal_height_m: float = 0.386
    height_min_m: float = 0.386
    height_max_m: float = 0.386
    height_rate_m_s: float = 0.04

    def __post_init__(self):
        for name in ("limits", "acceleration", "input_deadband", "start_threshold", "stop_threshold"):
            values = getattr(self, name)
            if len(values) != 3 or any(not 0 <= float(x) < float("inf") for x in values):
                raise ValueError(f"Invalid {name}")
        if any(x <= 0 for x in self.acceleration) or any(x <= 0 for x in self.limits):
            raise ValueError("Velocity limits and acceleration must be positive")
        if any(a > b for a, b in zip(self.input_deadband, self.start_threshold)):
            raise ValueError("Deadband cannot exceed start threshold")
        if any(a > b for a, b in zip(self.stop_threshold, self.start_threshold)):
            raise ValueError("Stop threshold cannot exceed start threshold")
        if min(self.gait_period_s, self.start_blend_s, self.stop_blend_s, self.height_rate_m_s) <= 0:
            raise ValueError("Time constants and height rate must be positive")
        if not self.height_min_m <= self.nominal_height_m <= self.height_max_m:
            raise ValueError("Nominal height must lie inside the validated height range")


class MotionCommandState:
    def __init__(self, count, device="cpu", config=None):
        self.cfg = config or MotionCommandConfig()
        self.device = torch.device(device)
        self.request = torch.zeros(count, 4, device=device)
        self.applied = torch.zeros_like(self.request)
        self.request[:, 3] = self.applied[:, 3] = self.cfg.nominal_height_m
        self.mode = torch.zeros(count, dtype=torch.long, device=device)
        self.phase = torch.zeros(count, device=device)
        self.blend = torch.zeros(count, device=device)
        self.height_rate = torch.zeros(count, device=device)
        self.command_age = torch.zeros(count, device=device)
        self._limits = torch.tensor(self.cfg.limits, device=device)
        self._acceleration = torch.tensor(self.cfg.acceleration, device=device)
        self._deadband = torch.tensor(self.cfg.input_deadband, device=device)
        self._start = torch.tensor(self.cfg.start_threshold, device=device)
        self._stop = torch.tensor(self.cfg.stop_threshold, device=device)

    def reset(self, ids):
        self.request[ids] = 0
        self.applied[ids] = 0
        self.request[ids, 3] = self.cfg.nominal_height_m
        self.applied[ids, 3] = self.cfg.nominal_height_m
        for value in (self.mode, self.phase, self.blend, self.height_rate, self.command_age):
            value[ids] = 0

    def set_request(self, value, ids=None):
        ids = slice(None) if ids is None else ids
        value = torch.as_tensor(value, dtype=self.applied.dtype, device=self.device)
        if value.ndim == 1:
            value = value.unsqueeze(0)
        if value.shape[-1] not in (3, 4) or not torch.isfinite(value).all():
            raise ValueError("Motion request must contain finite vx/vy/yaw, optionally height")
        if value.shape[-1] == 4:
            h = value[..., 3]
            if torch.any((h < self.cfg.height_min_m - 1e-6) | (h > self.cfg.height_max_m + 1e-6)):
                raise ValueError("Height request exceeds this task's validated range")
            self.request[ids, 3] = h
        twist = torch.maximum(torch.minimum(value[..., :3], self._limits), -self._limits)
        threshold = torch.where((self.mode[ids] == MotionMode.STAND)[:, None], self._start, self._deadband)
        self.request[ids, :3] = torch.where(torch.abs(twist) < threshold, 0.0, twist)
        self.command_age[ids] = 0

    def tick(self, dt, ids=None, foot_contacts=None):
        if not dt > 0:
            raise ValueError("dt must be positive")
        ids = torch.arange(len(self.mode), device=self.device) if ids is None else ids
        old = self.applied[ids].clone()
        delta = self.request[ids, :3] - old[:, :3]
        bound = self._acceleration * dt
        self.applied[ids, :3] = old[:, :3] + torch.maximum(torch.minimum(delta, bound), -bound)
        dh = (self.request[ids, 3] - old[:, 3]).clamp(-self.cfg.height_rate_m_s * dt, self.cfg.height_rate_m_s * dt)
        self.applied[ids, 3] += dh
        self.height_rate[ids] = dh / dt
        previous_mode = self.mode[ids]
        requested = torch.abs(self.request[ids, :3])
        # Hysteresis uses per-axis units; low but nonzero commands are never called stand.
        enter = torch.any(requested >= self._start, dim=1)
        keep = torch.any(requested > self._deadband, dim=1)
        wants_move = torch.where(previous_mode == MotionMode.STAND, enter, keep)
        quiet = torch.all(torch.abs(self.applied[ids, :3]) <= self._stop, dim=1)
        active_clock = (previous_mode != MotionMode.STAND) | wants_move
        if self.cfg.clock_runs_in_stand:
            active_clock = torch.ones_like(active_clock)
        advance = self.phase[ids] + active_clock.float() * dt / self.cfg.gait_period_s
        wrapped = advance >= 1.0
        self.phase[ids] = torch.remainder(advance, 1.0)
        change = torch.where(wants_move, dt / self.cfg.start_blend_s, -dt / self.cfg.stop_blend_s)
        self.blend[ids] = (self.blend[ids] + change).clamp(0, 1)
        contacts_ready = torch.ones_like(quiet) if foot_contacts is None else torch.all(foot_contacts[ids], dim=1)
        landed = (~wants_move) & quiet & (self.blend[ids] <= 1e-6) & contacts_ready
        standing = (landed & wrapped) | ((previous_mode == MotionMode.STAND) & ~wants_move & quiet)
        mode = torch.where(wants_move, MotionMode.START, MotionMode.STOP)
        mode = torch.where(wants_move & (self.blend[ids] >= 1 - 1e-6), MotionMode.MOVE, mode)
        self.mode[ids] = torch.where(standing, MotionMode.STAND, mode)
        if not self.cfg.clock_runs_in_stand:
            self.phase[ids] = torch.where(standing, 0.0, self.phase[ids])
        self.command_age[ids] += dt

    def extras(self):
        return torch.stack((self.applied[:, 3] - self.cfg.nominal_height_m,
                            self.height_rate, self.blend, (self.mode == MotionMode.STAND).float()), dim=1)

    def gait_targets(self, clearance_m=0.032):
        offsets = self.phase.new_tensor([0.0, 0.5, 0.0, 0.5])
        phase = torch.remainder(self.phase[:, None] + offsets, 1.0)
        swing = phase >= 0.5
        swing_progress = ((phase - 0.5) * 2).clamp(0, 1)
        clearance = clearance_m * torch.sin(torch.pi * swing_progress).square() * self.blend[:, None]
        contact = torch.where(swing, 1 - self.blend[:, None], 1.0)
        return contact, clearance


def foot_velocity_body(twist, nominal_foot_xy):
    """Stationary stance feet in a yawing/translating body: -v - omega cross r."""
    xy = torch.as_tensor(nominal_foot_xy, device=twist.device, dtype=twist.dtype)
    rotational = torch.stack((-xy[:, 1], xy[:, 0]), dim=1)
    return -twist[:, None, :2] - twist[:, None, 2:3] * rotational[None]
