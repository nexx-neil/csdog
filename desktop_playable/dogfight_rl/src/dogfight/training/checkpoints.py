"""Run provenance and explicit policy identity for training and evaluation."""
from pathlib import Path
import hashlib
import json

def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            digest.update(block)
    return digest.hexdigest()

def create_run(path, *, model_id, observation_definition, action_definition, config_paths, source_checkpoint=None):
    """Create a fresh run with immutable source hashes; never overwrite a run."""
    configs = [{"path": str(Path(p).resolve()), "sha256": sha256(p)} for p in config_paths]
    source = None if source_checkpoint is None else {"path": str(Path(source_checkpoint).resolve()), "sha256": sha256(source_checkpoint)}
    if not model_id or not observation_definition or not action_definition or not configs:
        raise ValueError("model, observation/action definitions and configuration provenance are required")
    path = Path(path)
    path.mkdir(parents=True, exist_ok=False)
    (path / "run_manifest.json").write_text(json.dumps(dict(model_id=model_id,
        observation_definition=observation_definition, action_definition=action_definition,
        configs=configs, source_checkpoint=source), indent=2)+"\n")
    return path

def validate_policy_identity(manifest, *, model_id, observation_definition, action_definition):
    """Tensor dimensions alone do not establish compatible model semantics."""
    expected = dict(model_id=model_id, observation_definition=observation_definition, action_definition=action_definition)
    if any(manifest.get(key) != value for key, value in expected.items()):
        raise ValueError("Checkpoint model/observation/action identity mismatch")
