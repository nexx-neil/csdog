from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from shared.paths import load_project_yaml

import hashlib
import os
from pathlib import Path
from typing import Any

from dogfight_v0.agents.dog_a_locomotion_adapter import DogALocomotionAdapter
from dogfight_v0.agents.real_dog_agent import RealDogAgent
from dogfight_v0.config.battle_cfg import BattleConfig


PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
DEFAULT_TASK_CONFIG = PROJECT_ROOT / "02_training" / "configs" / "back_gait_primitive_recovery.yaml"
DEFAULT_CHECKPOINT = PROJECT_ROOT / "02_training/logs" / "back_gait_primitive_recovery" / "model_final.pt"
DEFAULT_CHECKPOINT_SHA256 = "c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058"


def create_dog_a_agent(
    config: BattleConfig,
    *,
    device: str = "cuda:0",
    task_config_path: str | Path = DEFAULT_TASK_CONFIG,
    checkpoint_path: str | Path = DEFAULT_CHECKPOINT,
    episode_length_s: float = 300.0,
) -> tuple[RealDogAgent, Any]:
    """Construct the real Dog A. Call only after Isaac Sim AppLauncher starts."""
    import yaml

    task_config_path = Path(task_config_path).resolve()
    checkpoint_path = Path(checkpoint_path).resolve()
    if not task_config_path.is_file() or not checkpoint_path.is_file():
        raise FileNotFoundError(f"Dog A config/checkpoint missing: {task_config_path}, {checkpoint_path}")
    if checkpoint_path == DEFAULT_CHECKPOINT.resolve():
        actual_hash = hashlib.sha256(checkpoint_path.read_bytes()).hexdigest()
        if actual_hash != DEFAULT_CHECKPOINT_SHA256:
            raise RuntimeError(
                f"authoritative Dog A checkpoint hash mismatch: {actual_hash}"
            )
    os.environ["DOG_A_LOCOMOTION_TASK_CFG"] = str(task_config_path)
    os.environ["DOG_A_ENABLE_CONTACT_SENSOR"] = "1"

    from shared.policy import create_environment
    raw = load_project_yaml(task_config_path.read_text(encoding="utf-8"))
    environment = create_environment(task_config_path, device, episode_length_s)
    adapter = DogALocomotionAdapter.from_checkpoint(environment, checkpoint_path, raw, config)
    agent = RealDogAgent(environment._robot, adapter, config)
    return agent, environment
