"""Permit a small output correction while retaining frozen gait feature layers."""
import torch
from .anchored_ppo import configure_scan_adapter


def configure_output_adapter(algorithm, coefficient=1.0, action_scale=.1):
    teacher = configure_scan_adapter(algorithm, coefficient, action_scale)
    for parameter in algorithm.policy.actor[-1].parameters():
        parameter.requires_grad_(True)
    algorithm.optimizer = torch.optim.Adam(
        [p for p in algorithm.policy.parameters() if p.requires_grad],
        lr=algorithm.learning_rate)
    return teacher


def preservation_check(policy, teacher):
    final_index = len(policy.actor)-1
    old = teacher.state_dict()
    for name, value in policy.state_dict().items():
        if name.startswith(('critic.', f'actor.{final_index}.')):
            continue
        reference = old[name]
        if name == 'actor.0.weight':
            value, reference = value[:, :76], reference[:, :76]
        if not torch.equal(value, reference):
            raise RuntimeError('Frozen feature parameter changed: '+name)
    return True
