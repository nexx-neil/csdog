#!/usr/bin/env python3
"""Initialize the 54-input task from a legacy policy, discarding old optimizer moments."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "source/stackforce_simready_generated_robot_lab"))

import torch
from csdog_motion.contracts import (FOUNDATION_TAG, JOINT_NAMES, contract, contract_hash,
                                    migrate_observation_weights)
from csdog_motion.training import file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists() or Path(str(args.output) + ".metadata.json").exists():
        parser.error("Refusing to overwrite an existing checkpoint or metadata")
    source_metadata = json.loads(Path(str(args.source) + ".metadata.json").read_text())
    if source_metadata.get("checkpoint_compatibility_tag") != "csdog_v2_phase_gait_obs_v2_symmetric_soles":
        parser.error("Unsupported source policy contract")
    if source_metadata.get("actuated_joint_names") != JOINT_NAMES:
        parser.error("Source joint order mismatch")
    value = torch.load(args.source, map_location="cpu", weights_only=True)
    weights = migrate_observation_weights(value["model_state_dict"])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": weights, "iter": 0,
                "infos": {"initialization_parent": str(args.source.resolve())}}, args.output)
    interface = contract()
    metadata = {
        "schema_version": 2, "task": "CSDog-Motion-Foundation-Direct-v0",
        "checkpoint_compatibility_tag": FOUNDATION_TAG, "actuated_joint_names": JOINT_NAMES,
        "observations": 54, "actions": 12, "initialization_only": True,
        "parent_checkpoint": str(args.source.resolve()), "parent_sha256": file_hash(args.source),
        "motion_contract": interface, "motion_contract_sha256": contract_hash(interface),
        "migration": "zero-added actor/critic input columns; optimizer discarded; no gradient updates",
    }
    Path(str(args.output) + ".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    print(f"Initialization only: {args.output.resolve()}")


if __name__ == "__main__":
    main()
