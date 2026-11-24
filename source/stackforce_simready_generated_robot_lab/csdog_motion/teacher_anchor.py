"""Train actor features under a fixed teacher; keep exploration noise unchanged."""
import copy
import types
import torch
from .anchored_ppo import anchored_update


def configure_teacher_anchor(algorithm, coefficient=1., action_scale=.1):
    if coefficient < 0 or action_scale <= 0:
        raise ValueError('Invalid teacher constraint')
    teacher = copy.deepcopy(algorithm.policy).eval().requires_grad_(False)
    teacher._initial_state = {k:v.detach().clone() for k,v in teacher.state_dict().items()}
    for name, parameter in algorithm.policy.named_parameters():
        parameter.requires_grad_(name not in ('std','log_std'))
    algorithm.teacher = teacher
    algorithm.teacher_coefficient = coefficient
    algorithm.teacher_action_scale = action_scale
    algorithm.optimizer = torch.optim.Adam(
        [p for p in algorithm.policy.parameters() if p.requires_grad], lr=algorithm.learning_rate)
    algorithm.update = types.MethodType(anchored_update,algorithm)
    return teacher


def preservation_check(policy,teacher):
    for name,value in teacher.state_dict().items():
        if not torch.equal(value,teacher._initial_state[name]):
            raise RuntimeError('Frozen teacher changed: '+name)
    for name,parameter in teacher.named_parameters():
        if parameter.requires_grad or parameter.grad is not None:
            raise RuntimeError('Teacher entered gradient graph: '+name)
    for name,value in policy.state_dict().items():
        if name in ('std','log_std') and not torch.equal(value,teacher.state_dict()[name]):
            raise RuntimeError('Exploration noise changed')
    return True
