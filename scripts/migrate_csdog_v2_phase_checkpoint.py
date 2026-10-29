#!/usr/bin/env python3
"""Add two zero-initialized gait-phase inputs to a compatible v2 checkpoint.

The original 48 observations retain their exact columns.  The appended sine
and cosine phase inputs start with zero influence, so the migrated policy has
the same initial behavior and can learn to use the clock during correction.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import torch


TARGET_TASK = "CSDog-V2-Phase-Gait-Direct-v0"
TARGET_COMPATIBILITY_TAG = "csdog_v2_phase_gait_obs_v1"


def pad_input_weight(state: dict, key: str) -> None:
    weight = state[key]
    if weight.ndim != 2 or weight.shape[1] != 48:
        raise ValueError(f"Expected {key} shape (*, 48), got {tuple(weight.shape)}")
    state[key] = torch.cat((weight, torch.zeros_like(weight[:, :2])), dim=1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    checkpoint = torch.load(args.source, map_location="cpu", weights_only=False)
    state = checkpoint.get("model_state_dict")
    if not isinstance(state, dict):
        raise ValueError("Checkpoint has no model_state_dict")
    pad_input_weight(state, "actor.0.weight")
    pad_input_weight(state, "critic.0.weight")

    # The optimizer tensors still have 48-column moments and must not be
    # restored.  Training uses --policy_only_resume for this migrated file.
    checkpoint.pop("optimizer_state_dict", None)
    infos = checkpoint.get("infos") or {}
    checkpoint["infos"] = infos
    infos["phase_observation_migration"] = {
        "source": str(args.source.resolve()),
        "old_observation_count": 48,
        "new_observation_count": 50,
        "appended_observations": ["gait_phase_sin", "gait_phase_cos"],
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save(checkpoint, args.output)

    source_metadata_path = Path(str(args.source) + ".metadata.json")
    source_metadata = (
        json.loads(source_metadata_path.read_text(encoding="utf-8"))
        if source_metadata_path.is_file()
        else {}
    )
    metadata = {
        **source_metadata,
        "task": TARGET_TASK,
        "checkpoint": args.output.name,
        "checkpoint_compatibility_tag": TARGET_COMPATIBILITY_TAG,
        "migration": checkpoint["infos"]["phase_observation_migration"],
    }
    Path(str(args.output) + ".metadata.json").write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"Migrated checkpoint: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
