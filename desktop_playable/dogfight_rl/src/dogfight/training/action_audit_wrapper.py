"""RSL-RL wrapper that preserves pre-clipping actor actions for diagnostics."""
from __future__ import annotations


import torch

from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper


class ActionAuditRslRlVecEnvWrapper(RslRlVecEnvWrapper):
    """Apply a real actor-output scale, then preserve raw/scaled actions for audit."""

    def __init__(self, *args, actor_output_scale: float = 1.0, safety_callback=None, **kwargs):
        if not 0.0 < actor_output_scale <= 1.0:
            raise ValueError("actor_output_scale must be in (0, 1]")
        super().__init__(*args, **kwargs)
        self.actor_output_scale = float(actor_output_scale)
        self._safety_callback = safety_callback

    def step(self, actions: torch.Tensor):
        self.unwrapped._raw_policy_actions = actions.detach().clone()
        scaled_actions = actions * self.actor_output_scale
        self.unwrapped._scaled_policy_actions = scaled_actions.detach().clone()
        result = super().step(scaled_actions)
        if self._safety_callback is not None:
            self._safety_callback(self, actions, scaled_actions, result)
        return result
