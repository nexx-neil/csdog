"""Keep one live runner between segments and stop on any failed/missing validation."""

import json
from pathlib import Path


def require_validation_report(path, checkpoint):
    from .training import file_hash
    report = json.loads(Path(path).read_text())
    if (not report.get("complete") or report.get("checkpoint_sha256") != file_hash(checkpoint)
            or report.get("regression_gate", {}).get("status") != "PASS"):
        raise RuntimeError(f"Segment failed validation: {path}")
    return report


def run_segments(total, segment, learn, save, validate):
    if total < 0 or (total > 0 and segment <= 0):
        raise ValueError("Invalid iteration counts")
    done = 0
    while done < total:
        amount = min(segment, total - done)
        learn(amount, done == 0)
        done += amount
        checkpoint = save(done)
        validate(checkpoint, done)
    return done
