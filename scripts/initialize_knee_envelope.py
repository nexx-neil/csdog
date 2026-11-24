#!/usr/bin/env python3
"""Explicitly fork foundation weights into a changed, experimental action contract."""
import argparse
import json
from pathlib import Path
import types
import torch

from csdog_motion.action_bounds import ENVELOPE_TAG, envelope_contract
from csdog_motion.contracts import FOUNDATION_TAG, JOINT_NAMES, contract, contract_hash
from csdog_motion.training import validate_checkpoint, file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    target_metadata = Path(str(args.output) + ".metadata.json")
    if args.output.exists() or target_metadata.exists():
        parser.error("Refusing to overwrite initialization")
    cfg = types.SimpleNamespace(checkpoint_compatibility_tag=FOUNDATION_TAG,
                                actuated_joint_names=JOINT_NAMES, motion_contract=contract())
    metadata = validate_checkpoint(args.source, cfg, policy_only=True)
    if metadata.get("checkpoint_sha256") != file_hash(args.source):
        raise ValueError("Parent hash mismatch")
    data = torch.load(args.source, map_location="cpu", weights_only=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": data["model_state_dict"], "iter": 0,
                "infos": {"initialization_parent": str(args.source.resolve())}}, args.output)
    interface = envelope_contract()
    target_metadata.write_text(json.dumps({
        "schema_version": 2, "task": "CSDog-Motion-Envelope-Direct-v0",
        "checkpoint_sha256": file_hash(args.output), "checkpoint_compatibility_tag": ENVELOPE_TAG,
        "actuated_joint_names": JOINT_NAMES, "observations": 54, "actions": 12,
        "initialization_only": True, "parent_checkpoint": str(args.source.resolve()),
        "parent_sha256": file_hash(args.source), "motion_contract": interface,
        "motion_contract_sha256": contract_hash(interface),
        "migration": "identical actor/critic tensors; discard optimizer; knee target bound .35->.42rad; behavior intentionally changes at clipping; not function-preserving",
    }, indent=2) + "\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
