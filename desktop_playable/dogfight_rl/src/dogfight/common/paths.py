"""Authoritative paths; importing this module never starts the simulator."""
from pathlib import Path
import os
ROOT = Path(__file__).resolve().parents[3]
WORKSPACE = ROOT.parent
MODEL = WORKSPACE / "model"
ASSETS = ROOT / "assets"
CONFIGS = ROOT / "configs"
LOGS = ROOT / "runs"
CHECKPOINTS = LOGS / "locomotion"
ISAACLAB = Path(os.environ.get("DOGFIGHT_ISAACLAB", str(WORKSPACE / "IsaacLab")))
PYTHON = Path(os.environ.get("DOGFIGHT_PYTHON", str(Path.home() / "miniconda3/envs/dogfight/bin/python")))
def project_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path

def load_project_yaml(stream):
    """Resolve explicit project resources; reject retired layout references."""
    import yaml
    def resolve(value):
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if isinstance(value, str):
            if value.startswith(("01_robots/", "02_training/", "03_battle/")):
                raise ValueError("Archived layout resource is not a current project resource: " + value)
            if value.startswith("model/"):
                return str(WORKSPACE / value)
            if value.startswith(("assets/", "configs/", "runs/")):
                return str(project_path(value))
        return value
    return resolve(yaml.safe_load(stream))
