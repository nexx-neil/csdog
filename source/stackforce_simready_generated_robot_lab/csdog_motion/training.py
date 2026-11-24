"""Training-state checks shared by launchers; no simulator import side effects."""

import hashlib
import json
from pathlib import Path
import random
import subprocess
import types

import numpy as np
import torch


class EpisodeCounterProxy:
    @property
    def episode_length_buf(self):
        return self.env.unwrapped.episode_length_buf

    @episode_length_buf.setter
    def episode_length_buf(self, value):
        target = self.env.unwrapped.episode_length_buf
        if value.shape != target.shape or value.device != target.device:
            raise ValueError("Episode counters must preserve shape and device")
        target.copy_(value)


def sync_learning_rate(algorithm, requested=None):
    groups = algorithm.optimizer.param_groups
    rates = [float(g["lr"]) for g in groups]
    if requested is None and any(abs(x - rates[0]) > 1e-15 for x in rates):
        raise ValueError("Multiple optimizer learning rates need an explicit synchronization policy")
    rate = rates[0] if requested is None else float(requested)
    if not 0 < rate < float("inf"):
        raise ValueError("Learning rate must be finite and positive")
    algorithm.learning_rate = rate
    for group in groups:
        group["lr"] = rate
    return rate


def bound_learning_rate(algorithm, minimum, maximum):
    if not 0 < minimum <= maximum:
        raise ValueError("Invalid learning-rate bounds")
    audit = {"optimizer_steps": 0, "minimum_actual_lr": None, "maximum_actual_lr": None}

    def before_step(optimizer, args, kwargs):
        rates = []
        for group in optimizer.param_groups:
            group["lr"] = min(max(float(group["lr"]), minimum), maximum)
            rates.append(group["lr"])
        algorithm.learning_rate = rates[0]
        audit["optimizer_steps"] += 1
        audit["minimum_actual_lr"] = min(rates + ([audit["minimum_actual_lr"]] if audit["minimum_actual_lr"] is not None else []))
        audit["maximum_actual_lr"] = max(rates + ([audit["maximum_actual_lr"]] if audit["maximum_actual_lr"] is not None else []))

    handle = algorithm.optimizer.register_step_pre_hook(before_step)
    sync_learning_rate(algorithm, min(max(algorithm.learning_rate, minimum), maximum))
    return audit, handle


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_checkpoint(path, cfg, *, policy_only=False):
    path = Path(path)
    metadata = Path(str(path) + ".metadata.json")
    if not metadata.is_file():
        metadata = path.parent / "model_final.pt.metadata.json"
    if not metadata.is_file():
        raise ValueError(f"Missing checkpoint compatibility metadata: {path}")
    value = json.loads(metadata.read_text())
    if value.get("checkpoint_compatibility_tag") != cfg.checkpoint_compatibility_tag:
        raise ValueError("Checkpoint observation/action contract does not match the task; migrate explicitly")
    if value.get("actuated_joint_names") != list(cfg.actuated_joint_names):
        raise ValueError("Checkpoint joint order mismatch")
    if hasattr(cfg, "motion_contract") and value.get("motion_contract") != cfg.motion_contract:
        raise ValueError("Checkpoint motion semantics differ from the task contract")
    if value.get("initialization_only", False) and not policy_only:
        raise ValueError("Migrated initialization requires --policy_only_resume; old optimizer moments are incompatible")
    return value


def install_checkpoint_records(runner, env_cfg, task, *, parent=None, lr_audit=None, resume_semantics=None):
    """Write metadata at every periodic save; record RNG, not a false exact-state resume claim."""
    original = runner.save
    count = {"updates_in_this_run": 0}
    update = runner.alg.update
    root = Path(__file__).resolve().parents[3]
    sources = {str(path.relative_to(root)): file_hash(path)
               for folder in ("source", "scripts") for path in sorted((root / folder).rglob("*.py"))}
    revision = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)

    def counted_update():
        result = update()
        count["updates_in_this_run"] += 1
        return result

    runner.alg.update = counted_update

    def save(self, path, infos=None):
        original(path, infos)
        metadata = {
            "schema_version": 2, "task": task,
            "checkpoint_sha256": file_hash(path),
            "checkpoint_compatibility_tag": env_cfg.checkpoint_compatibility_tag,
            "actuated_joint_names": list(env_cfg.actuated_joint_names),
            "observations": env_cfg.observation_space, "actions": env_cfg.action_space,
            "updates_in_this_run": count["updates_in_this_run"],
            "parent_checkpoint": str(parent) if parent else None,
            "parent_sha256": file_hash(parent) if parent else None,
            "optimizer_lrs": [float(g["lr"]) for g in runner.alg.optimizer.param_groups],
            "algorithm_learning_rate": float(runner.alg.learning_rate),
            "actual_lr_audit": lr_audit, "initialization_only": False,
            "seed": getattr(env_cfg, "seed", None),
            "source_base_commit": revision.stdout.strip() if revision.returncode == 0 else None,
            "source_files_sha256": sources,
            "resume_semantics": resume_semantics or "weights/optimizer restored; RNG recorded only, not auto-restored; physical environment restarts explicitly",
        }
        if hasattr(env_cfg, "motion_contract"):
            from .contracts import contract_hash
            metadata["motion_contract"] = env_cfg.motion_contract
            metadata["motion_contract_sha256"] = contract_hash(env_cfg.motion_contract)
            metadata["motion_commands"] = env_cfg.motion_commands
        Path(str(path) + ".metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
        numpy_state = np.random.get_state()
        state = {
            "python_random": random.getstate(),
            "numpy_random": (numpy_state[0], numpy_state[1].tolist(), *numpy_state[2:]),
            "torch_cpu": torch.get_rng_state(),
            "torch_cuda": torch.cuda.get_rng_state_all() if torch.cuda.is_available() else [],
            "environment_state_restored": False,
        }
        torch.save(state, str(path) + ".rng.pt")

    runner.save = types.MethodType(save, runner)
    return count
