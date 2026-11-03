"""Project paths. No dependency on the caller working directory or simulator."""
from pathlib import Path
import os
ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
ROBOTS = ROOT / "01_robots"
TRAINING = ROOT / "02_training"
BATTLE = ROOT / "03_battle"
ASSETS = ROBOTS / "assets"
LOGS = TRAINING / "logs"
CHECKPOINTS = TRAINING / "checkpoints"
ISAACLAB = Path(os.environ.get("DOGFIGHT_ISAACLAB", str(ROOT.parent / "IsaacLab")))
PYTHON = Path(os.environ.get("DOGFIGHT_PYTHON", str(Path.home() / "miniconda3/envs/dogfight/bin/python")))
def project_path(value):
    path = Path(value).expanduser()
    return path if path.is_absolute() else ROOT / path


def load_project_yaml(stream):
    """Read YAML and anchor project resource paths to ROOT, independent of cwd.

    Only 01_robots/, 02_training/, and 03_battle/ identify project resources.
    Other strings, URLs, system paths, and numeric values retain their meaning.
    """
    import yaml

    def resolve(value):
        if isinstance(value, dict):
            return {key: resolve(item) for key, item in value.items()}
        if isinstance(value, list):
            return [resolve(item) for item in value]
        if isinstance(value, str) and value.startswith(("01_robots/", "02_training/", "03_battle/")):
            return str(project_path(value))
        return value

    return resolve(yaml.safe_load(stream))
