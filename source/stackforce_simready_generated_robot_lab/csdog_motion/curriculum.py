"""Command distribution only; no reward, observation or motor-setting changes."""
import torch


def lateral_balanced_bank():
    """45% continuous lateral bands, 15% X, 10% yaw, 10% stand, 20% combinations."""
    rows = [("stand", [0, 0, 0], [0, 0, 0], .10),
            ("forward", [.08, 0, 0], [.4, 0, 0], .075),
            ("backward", [-.4, 0, 0], [-.08, 0, 0], .075),
            ("turn_left", [0, 0, .08], [0, 0, .4], .05),
            ("turn_right", [0, 0, -.4], [0, 0, -.08], .05)]
    for side, sign in (("left", 1), ("right", -1)):
        for name, lo, hi in (("low", .06, .14), ("mid", .14, .22), ("high", .22, .30)):
            lower, upper = sorted((sign * lo, sign * hi))
            rows.append((f"{side}_{name}", [0, lower, 0], [0, upper, 0], .075))
    for name, value in (("forward_turn", [.35, 0, .35]), ("lateral_turn", [0, .22, .35]),
                        ("right_turn", [0, -.22, -.35]), ("diagonal", [.35, .22, 0])):
        rows.append((name, [min(x, .8*x) for x in value], [max(x, .8*x) for x in value], .05))
    return rows


def sample_lateral_balanced(count, device="cpu", generator=None):
    bank = lateral_balanced_bank()
    weights = torch.tensor([row[3] for row in bank], device=device)
    labels = torch.multinomial(weights, count, replacement=True, generator=generator)
    low = torch.tensor([row[1] for row in bank], device=device)[labels]
    high = torch.tensor([row[2] for row in bank], device=device)[labels]
    commands = low + torch.rand((count, 3), device=device, generator=generator) * (high - low)
    return commands, labels
