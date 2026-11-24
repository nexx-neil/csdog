#!/usr/bin/env python3
"""Copy weights as an explicit, non-equivalent warm start for calibrated geometry."""
import argparse
import json
from pathlib import Path
import types
import torch
from csdog_motion.calibration import CALIBRATED_TAG, POSTURE_TAG, calibrated_contract, calibrated_data, posture_contract
from csdog_motion.contracts import FOUNDATION_TAG, JOINT_NAMES, contract, contract_hash
from csdog_motion.training import validate_checkpoint, file_hash


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--posture-blend", action="store_true")
    args = parser.parse_args()
    output_metadata = Path(str(args.output) + ".metadata.json")
    if args.output.exists() or output_metadata.exists():
        parser.error("Refusing to overwrite calibrated initialization")
    parent = validate_checkpoint(args.source, types.SimpleNamespace(
        checkpoint_compatibility_tag=FOUNDATION_TAG, actuated_joint_names=JOINT_NAMES, motion_contract=contract()), policy_only=True)
    if parent.get("checkpoint_sha256") != file_hash(args.source):
        raise ValueError("Parent checkpoint hash mismatch")
    data = torch.load(args.source, map_location="cpu", weights_only=True)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": data["model_state_dict"], "iter": 0,
                "infos": {"initialization_parent": str(args.source.resolve())}}, args.output)
    interface = posture_contract() if args.posture_blend else calibrated_contract()
    output_metadata.write_text(json.dumps({
        "schema_version": interface["schema_version"], "task": "CSDog-Motion-Posture-Direct-v0" if args.posture_blend else "CSDog-Motion-Calibrated-Direct-v0",
        "checkpoint_sha256": file_hash(args.output), "checkpoint_compatibility_tag": POSTURE_TAG if args.posture_blend else CALIBRATED_TAG,
        "actuated_joint_names": JOINT_NAMES, "observations": 54, "actions": 12,
        "initialization_only": True, "parent_checkpoint": str(args.source.resolve()),
        "parent_sha256": file_hash(args.source), "motion_contract": interface,
        "motion_contract_sha256": contract_hash(interface),
        "calibration": calibrated_data(),
        "migration": "copy identical actor/critic/std tensors; discard optimizer; declared geometry/nominal-joint/posture semantics intentionally change behavior; requires new evaluation, not function-preserving",
    }, indent=2) + "\n")
    print(args.output.resolve())


if __name__ == "__main__":
    main()
