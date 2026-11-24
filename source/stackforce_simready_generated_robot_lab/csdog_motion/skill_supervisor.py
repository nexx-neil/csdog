"""Guarded flat-ground locomotion/crouch/rise supervisor; no jump or belly contact."""
from dataclasses import dataclass
from enum import IntEnum
import math
import torch
from .speed_learning import valid_speed_request


class SkillMode(IntEnum):
    LOCOMOTION = 0
    BRAKE = 1
    LOWER = 2
    HOLD = 3
    RISE = 4
    SETTLE = 5
    FAULT = 6


class SkillFault(IntEnum):
    NONE = 0
    NONFINITE = 1
    TILT = 2
    CONTACT_LOSS = 3
    TIMEOUT = 4
    LOW_HEIGHT = 5


@dataclass(frozen=True)
class SkillConfig:
    nominal_height_m: float = .37144956
    maximum_drop_m: float = .04
    quiet_linear_mps: float = .03
    quiet_yaw_radps: float = .05
    quiet_blend: float = .001
    stable_seconds: float = .30
    posture_height_tolerance_m: float = .005
    applied_height_tolerance_m: float = .0005
    maximum_tilt_deg: float = 12.
    contact_loss_seconds: float = .20
    brake_timeout_seconds: float = 8.
    posture_timeout_seconds: float = 6.

    def __post_init__(self):
        if not all(math.isfinite(v) and v > 0 for v in vars(self).values()):
            raise ValueError('Skill thresholds must be finite and positive')
        if self.maximum_drop_m >= self.nominal_height_m or self.maximum_tilt_deg >= 90:
            raise ValueError('Invalid posture range')


class SkillSupervisor:
    def __init__(self, count, device='cpu', config=None, request_validator=None):
        self.cfg = config or SkillConfig()
        self.request_validator = request_validator or valid_speed_request
        self.device = torch.device(device)
        self.mode = torch.zeros(count, dtype=torch.long, device=device)
        self.fault = torch.zeros_like(self.mode)
        self.requested_twist = torch.zeros(count, 3, device=device)
        self.desired_height = torch.full((count,), self.cfg.nominal_height_m, device=device)
        self.mode_age = torch.zeros(count, device=device)
        self.stable_time = torch.zeros_like(self.mode_age)
        self.contact_loss_time = torch.zeros_like(self.mode_age)

    def _ids(self, ids):
        return torch.arange(len(self.mode), device=self.device) if ids is None else torch.as_tensor(ids, dtype=torch.long, device=self.device)

    def request_twist(self, twist, ids=None):
        ids = self._ids(ids)
        value = torch.as_tensor(twist, dtype=self.requested_twist.dtype, device=self.device)
        if value.ndim == 1:
            value = value[None]
        if value.shape not in ((1, 3), (len(ids), 3)) or not self.request_validator(value).all():
            raise ValueError('Use the validated mixed box or single-axis speed extension')
        value = value.expand(len(ids), -1)
        self.requested_twist[ids] = value
        # A new move request queues an orderly rise; zero twist alone preserves crouch.
        moving = value.abs().amax(1) > 1e-6
        self.desired_height[ids[moving]] = self.cfg.nominal_height_m

    def request_crouch(self, drop_m=.04, ids=None):
        ids = self._ids(ids)
        drop = torch.as_tensor(drop_m, dtype=self.desired_height.dtype, device=self.device)
        if drop.ndim > 1 or drop.numel() not in (1, len(ids)) or not torch.isfinite(drop).all():
            raise ValueError('One finite posture drop per requested environment required')
        if ((drop < 0) | (drop > self.cfg.maximum_drop_m + 1e-6)).any():
            raise ValueError('Posture drop exceeds validated range')
        self.desired_height[ids] = self.cfg.nominal_height_m - drop.reshape(-1).expand(len(ids))
        self.requested_twist[ids] = 0

    def request_stand(self, ids=None):
        self.request_crouch(0., ids)

    def reset(self, ids=None):
        ids = self._ids(ids)
        for value in (self.mode, self.fault, self.mode_age, self.stable_time, self.contact_loss_time):
            value[ids] = 0
        self.requested_twist[ids] = 0
        self.desired_height[ids] = self.cfg.nominal_height_m

    def tick(self, dt, *, twist, tilt_deg, contacts, blend, applied_height, actual_height, active=None):
        if not math.isfinite(dt) or not 0 < dt <= .1:
            raise ValueError('Skill clock requires a positive step no larger than100ms')
        n = len(self.mode)
        if twist.shape != (n, 3) or contacts.shape != (n, 4) or any(v.shape != (n,) for v in (tilt_deg, blend, applied_height, actual_height)):
            raise ValueError('Skill sensor shape mismatch')
        active = torch.ones(n, dtype=torch.bool, device=self.device) if active is None else active
        entry = self.mode.clone()
        self.mode_age += active.float() * dt
        finite = torch.isfinite(twist).all(1) & torch.isfinite(tilt_deg) & torch.isfinite(blend) & torch.isfinite(applied_height) & torch.isfinite(actual_height)
        all_contact = contacts.bool().all(1)
        quiet = (twist[:, :2].abs().amax(1) <= self.cfg.quiet_linear_mps) & (twist[:, 2].abs() <= self.cfg.quiet_yaw_radps)
        quiet &= (blend <= self.cfg.quiet_blend) & all_contact & finite
        self.stable_time = torch.where(active, torch.where(quiet, self.stable_time + dt, 0.), self.stable_time)
        posture = (entry == SkillMode.LOWER) | (entry == SkillMode.HOLD) | (entry == SkillMode.RISE)
        lost = posture & ~all_contact
        self.contact_loss_time = torch.where(active, torch.where(lost, self.contact_loss_time + dt, 0.), self.contact_loss_time)
        timeout = ((entry == SkillMode.BRAKE) & (self.mode_age > self.cfg.brake_timeout_seconds))
        timeout |= ((posture | (entry == SkillMode.SETTLE)) & (entry != SkillMode.HOLD) & (self.mode_age > self.cfg.posture_timeout_seconds))
        bad_height = actual_height < self.cfg.nominal_height_m - self.cfg.maximum_drop_m - .03
        fault_code = torch.zeros_like(self.fault)
        for condition, code in ((timeout, SkillFault.TIMEOUT), (self.contact_loss_time > self.cfg.contact_loss_seconds, SkillFault.CONTACT_LOSS),
                                (bad_height, SkillFault.LOW_HEIGHT), (tilt_deg > self.cfg.maximum_tilt_deg, SkillFault.TILT), (~finite, SkillFault.NONFINITE)):
            fault_code = torch.where(condition, int(code), fault_code)
        new_fault = active & (entry != SkillMode.FAULT) & (fault_code != 0)
        self.fault[new_fault] = fault_code[new_fault]
        self.mode[new_fault] = SkillMode.FAULT
        available = active & (self.mode != SkillMode.FAULT)
        wants_low = self.desired_height < self.cfg.nominal_height_m - 1e-6
        stable = self.stable_time >= self.cfg.stable_seconds - 1e-6
        at_goal = ((applied_height - self.desired_height).abs() <= self.cfg.applied_height_tolerance_m) & ((actual_height - self.desired_height).abs() <= self.cfg.posture_height_tolerance_m)
        at_stand = ((applied_height - self.cfg.nominal_height_m).abs() <= self.cfg.applied_height_tolerance_m) & ((actual_height - self.cfg.nominal_height_m).abs() <= self.cfg.posture_height_tolerance_m)
        next_mode = self.mode.clone()
        transitions = [
            ((entry == SkillMode.LOCOMOTION) & wants_low, SkillMode.BRAKE),
            ((entry == SkillMode.BRAKE) & ~wants_low, SkillMode.LOCOMOTION),
            ((entry == SkillMode.BRAKE) & wants_low & stable, SkillMode.LOWER),
            ((entry == SkillMode.LOWER) & ~wants_low, SkillMode.RISE),
            ((entry == SkillMode.LOWER) & wants_low & at_goal, SkillMode.HOLD),
            ((entry == SkillMode.HOLD) & ~wants_low, SkillMode.RISE),
            ((entry == SkillMode.HOLD) & wants_low & ~at_goal, SkillMode.LOWER),
            ((entry == SkillMode.RISE) & wants_low, SkillMode.LOWER),
            ((entry == SkillMode.RISE) & ~wants_low & at_stand & quiet, SkillMode.SETTLE),
            ((entry == SkillMode.SETTLE) & wants_low, SkillMode.BRAKE),
            ((entry == SkillMode.SETTLE) & ~wants_low & at_stand & stable, SkillMode.LOCOMOTION),
        ]
        for condition, mode in transitions:
            next_mode = torch.where(available & condition, int(mode), next_mode)
        changed = next_mode != self.mode
        self.mode = next_mode
        self.mode_age[changed | new_fault] = 0
        self.stable_time[changed | new_fault] = 0
        output = torch.zeros(n, 4, device=self.device)
        output[:, 3] = self.cfg.nominal_height_m
        moving = self.mode == SkillMode.LOCOMOTION
        output[moving, :3] = self.requested_twist[moving]
        lowering = (self.mode == SkillMode.LOWER) | (self.mode == SkillMode.HOLD)
        output[lowering, 3] = self.desired_height[lowering]
        faulted = self.mode == SkillMode.FAULT
        frozen = torch.nan_to_num(applied_height, nan=self.cfg.nominal_height_m).clamp(self.cfg.nominal_height_m-self.cfg.maximum_drop_m, self.cfg.nominal_height_m)
        output[faulted, 3] = frozen[faulted]
        return output
