"""Explicit per-joint control bounds; the original scalar contract stays unchanged."""
import torch

ENVELOPE_TAG = "csdog_motion_foundation_flat_obs54_knee042_v2"
KNEE_CLIP = (1., 1., 1.2) * 4


def action_bounds(cfg, device):
    values = getattr(cfg, "action_clip_per_joint", None)
    if values is None:
        values = [cfg.action_clip] * cfg.action_space
    bound = torch.as_tensor(values, device=device, dtype=torch.float32)
    if bound.shape != (cfg.action_space,) or not torch.isfinite(bound).all() or not torch.all(bound > 0):
        raise ValueError("Expected one finite positive action bound per joint")
    return bound


def clip_actions(actions, bounds):
    return torch.maximum(torch.minimum(actions, bounds), -bounds)


def executed_actions(actions, bounds, blend=None):
    value = clip_actions(actions, bounds)
    return value if blend is None else value * blend


def envelope_contract():
    from .contracts import contract
    value = contract()
    value["schema_version"] = 2
    value["compatibility_tag"] = ENVELOPE_TAG
    value["action"]["clip_per_joint"] = list(KNEE_CLIP)
    value["action"]["clip"] = "per-joint; see clip_per_joint in the declared joint order"
    return value
