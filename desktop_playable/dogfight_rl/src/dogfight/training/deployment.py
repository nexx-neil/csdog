"""Explicit-spec actor reconstruction; never creates a robot environment."""
from pathlib import Path
from typing import Any
def load_actor(checkpoint_path, task_config, device, *, observation_dimension, action_dimension):
    import torch

    checkpoint_path = Path(checkpoint_path).resolve()
    checkpoint = torch.load(checkpoint_path, map_location="cpu", weights_only=False)
    ppo = task_config["ppo"]
    activation_name = str(ppo["activation"]).lower()
    activations = {"elu": torch.nn.ELU, "relu": torch.nn.ReLU, "tanh": torch.nn.Tanh}
    if activation_name not in activations:
        raise ValueError(f"unsupported actor activation: {activation_name}")
    dimensions = [int(observation_dimension), *map(int, ppo["actor_hidden_dims"]), int(action_dimension)]
    layers: list[Any] = []
    for index, (input_dim, output_dim) in enumerate(zip(dimensions[:-1], dimensions[1:])):
        layers.append(torch.nn.Linear(input_dim, output_dim))
        if index < len(dimensions) - 2:
            layers.append(activations[activation_name]())
    actor = torch.nn.Sequential(*layers)
    actor_state = {
        key.removeprefix("actor."): value
        for key, value in checkpoint["model_state_dict"].items()
        if key.startswith("actor.")
    }
    actor.load_state_dict(actor_state, strict=True)
    actor.to(device).eval()
    infos = checkpoint.get("infos") or {}
    configured_scale = task_config.get("actor_output_scale")
    actor_output_scale = infos.get("actor_output_scale", configured_scale)
    if actor_output_scale is None:
        raise ValueError("actor_output_scale is absent from checkpoint and task config")
    return actor, float(actor_output_scale)
