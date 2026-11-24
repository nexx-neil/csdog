# PPO loss adapted from RSL-RL v3.1.2, ETH Zurich and NVIDIA CORPORATION.
# Copyright (c) 2021-2025, ETH Zurich and NVIDIA CORPORATION. All rights reserved.
# SPDX-License-Identifier: BSD-3-Clause
"""Restricted scan-input learning with a frozen teacher in the PPO objective.

Supports the project's feed-forward, fixed-LR, single-GPU PPO configuration.
Teacher loss is applied before the common gradient norm clip, not after a step.
"""
import copy
import types
import torch


def configure_scan_adapter(algorithm, coefficient=1.0, action_scale=.1):
    if coefficient < 0 or action_scale <= 0:
        raise ValueError('Nonnegative teacher coefficient and positive action scale required')
    policy = algorithm.policy
    first = policy.actor[0].weight
    if first.shape[1] != 175 or policy.actor_obs_normalization:
        raise ValueError('Expected unnormalized 76+99 observation columns')
    algorithm.teacher = copy.deepcopy(policy).eval().requires_grad_(False)
    for name, parameter in policy.named_parameters():
        parameter.requires_grad_(name.startswith('critic.'))
    first.requires_grad_(True)
    mask = torch.zeros_like(first)
    mask[:, 76:] = 1
    first.register_hook(lambda gradient: gradient * mask)
    algorithm.teacher_coefficient = coefficient
    algorithm.teacher_action_scale = action_scale
    # Fresh Adam, no momentum or weight decay can move masked legacy columns.
    algorithm.optimizer = torch.optim.Adam(
        [p for p in policy.parameters() if p.requires_grad], lr=algorithm.learning_rate)
    algorithm.update = types.MethodType(anchored_update, algorithm)
    return algorithm.teacher


def preservation_check(policy, teacher):
    """Bitwise proof of all old actor parameters; critic is intentionally trainable."""
    old = teacher.state_dict()
    for name, value in policy.state_dict().items():
        if name.startswith('critic.'):
            continue
        reference = old[name]
        if name == 'actor.0.weight':
            value, reference = value[:, :76], reference[:, :76]
        if not torch.equal(value, reference):
            raise RuntimeError('Frozen actor parameter changed: ' + name)
    return True


def anchored_update(self):
    if self.policy.is_recurrent or self.is_multi_gpu or self.rnd or self.symmetry or self.schedule != 'fixed':
        raise ValueError('Anchored PPO requires feed-forward fixed-LR single-GPU without RND/symmetry')
    totals = dict(value_function=0., surrogate=0., entropy=0., teacher=0., action_deviation=0.)
    batches = self.storage.mini_batch_generator(self.num_mini_batches, self.num_learning_epochs)
    count = 0
    for obs, actions, target_values, advantages, returns, old_logp, old_mu, old_sigma, hidden, masks in batches:
        if self.normalize_advantage_per_mini_batch:
            advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        self.policy.act(obs, masks=masks, hidden_state=hidden[0])
        logp = self.policy.get_actions_log_prob(actions)
        values = self.policy.evaluate(obs, masks=masks, hidden_state=hidden[1])
        mu, entropy = self.policy.action_mean, self.policy.entropy
        ratio = torch.exp(logp - old_logp.squeeze())
        surrogate = torch.maximum(-advantages.squeeze() * ratio,
            -advantages.squeeze() * ratio.clamp(1-self.clip_param, 1+self.clip_param)).mean()
        if self.use_clipped_value_loss:
            clipped = target_values + (values-target_values).clamp(-self.clip_param, self.clip_param)
            value_loss = torch.maximum((values-returns).square(), (clipped-returns).square()).mean()
        else:
            value_loss = (values-returns).square().mean()
        with torch.no_grad():
            target_mu = self.teacher.act_inference(obs)
        deviation = (mu-target_mu).square().mean()
        teacher_loss = deviation / self.teacher_action_scale**2
        loss = surrogate + self.value_loss_coef*value_loss - self.entropy_coef*entropy.mean()
        loss = loss + self.teacher_coefficient*teacher_loss
        self.optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), self.max_grad_norm)
        self.optimizer.step()
        for key, value in [('value_function',value_loss), ('surrogate',surrogate),
                           ('entropy',entropy.mean()), ('teacher',teacher_loss), ('action_deviation',deviation)]:
            totals[key] += value.item()
        count += 1
    if count != self.num_learning_epochs*self.num_mini_batches:
        raise RuntimeError('Unexpected number of PPO minibatches')
    self.storage.clear()
    return {key:value/count for key,value in totals.items()}
