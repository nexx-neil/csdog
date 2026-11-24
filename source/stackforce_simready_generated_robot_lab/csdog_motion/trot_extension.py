"""Independent flat forward-speed proposal; preserve the accepted <=.8 branch."""
import copy
from types import SimpleNamespace
import torch
from . import trot_course as previous
from .clean_gait import clean_foot_reference

TAG = 'csdog_forward_trot_extension_obs76_v37'
MAX_FORWARD = 1.0

def strength(twist):
    s = ((twist[:, 0] - .8) / .2).clamp(0, 1)
    value = (s.pow(3) * (10 + s * (-15 + 6 * s))).clamp(0, 1)
    return torch.where(twist[:, 0] >= MAX_FORWARD, torch.ones_like(value), value)

def period(twist):
    return previous.period(twist) - .04 * strength(twist)

def duty(twist):
    return previous.duty(twist) - .08 * strength(twist)

def valid_request(twist):
    extension = (twist[:, 0] >= 0) & (twist[:, 0] <= MAX_FORWARD + 1e-6) & (twist[:, 1:].abs() <= 1e-6).all(1)
    return torch.isfinite(twist).all(1) & (previous.valid_request(twist) | extension)

def reference(phase, twist, nominal, config, blend=None, height_delta=None):
    old, old_stance = previous.reference(phase, twist, nominal, config, blend, height_delta)
    cfg = SimpleNamespace(period_s=period(twist)[:, None], stance_fraction=duty(twist)[:, None], clearance_m=config.clearance_m)
    new, stance = clean_foot_reference(phase, twist, nominal, cfg, blend, height_delta)
    active = twist[:, 0] > .8
    return torch.where(active[:, None, None], new, old), torch.where(active[:, None], stance, old_stance)

class ExtensionCommands(previous.TrotCommands):
    def tick(self, dt, ids=None, foot_contacts=None):
        ids = torch.arange(len(self.phase), device=self.device) if ids is None else ids
        super().tick(dt, ids, foot_contacts)
        extra = dt * (1 / period(self.applied[ids, :3]) - 1 / previous.period(self.applied[ids, :3]))
        self.phase[ids] = torch.remainder(self.phase[ids] + extra, 1.)

def contract(base):
    value = copy.deepcopy(base)
    value.update(schema_version=37, compatibility_tag=TAG)
    value['command_envelope']['forward_single_axis_extension_mps'] = MAX_FORWARD
    value['forward_extension'] = dict(command_range_mps=[.8, MAX_FORWARD], period_s=[.44, .40],
        stance_fraction=[.40, .32], blend='C2 quintic of applied vx .8..1.0; exact old branch <=.8',
        terrain='flat only', actuator_limits_unchanged=True, physical_validation_required=True,
        explanation='Shorter stance reduces return-stroke peak speed; shortening period alone does not.',
        learning_replay='20% .65...8, 80% .8..1.0; no claim of old-domain single-actor preservation')
    return value

def sample_commands(count, device):
    cmd = torch.zeros(count, 3, device=device)
    cat = torch.rand(count, device=device)
    cmd[:, 0] = torch.where(cat < .2, .65 + .15 * torch.rand(count, device=device), .8 + .2 * torch.rand(count, device=device))
    return cmd

def cases(holdout=False):
    speeds = [.83, .88, .94, .98] if holdout else [.8, .85, .9, .95, 1.0]
    out = [dict(name='stand', profile=[[20., [0, 0, 0]]], protected=True)]
    out += [dict(name=f'forward_{s:.2f}', profile=[[20., [s, 0, 0]]], protected=True) for s in speeds]
    high = speeds[-1]
    out += [dict(name='fast_stop', profile=[[2.3, [0, 0, 0]], [10.7, [high, 0, 0]], [20., [0, 0, 0]]], protected=False),
            dict(name='fast_to_turn', profile=[[7.7, [high, 0, 0]], [13.3, [0, 0, -.8]], [20., [0, -.4, 0]]], protected=False),
            dict(name='fast_reverse', profile=[[7.3, [high, 0, 0]], [13.7, [-.5, 0, 0]], [20., [0, 0, 0]]], protected=False)]
    return out
