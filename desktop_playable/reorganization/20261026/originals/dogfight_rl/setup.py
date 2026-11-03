"""Optional packaging entry point; V0 scripts use PYTHONPATH and do not install it."""

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from setuptools import find_packages, setup

setup(
    name="dogfight_v0",
    version="0.2.0",
    packages=find_packages(),
    python_requires=">=3.11",
    install_requires=[],
)
