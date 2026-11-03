#!/usr/bin/env python3
"""Read-only health check for the Dogfight RL golden environment."""

from __future__ import annotations

# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))

import platform
import subprocess
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


EXPECTED = {
    "Python": "3.11.16",
    "PyTorch": "2.7.0+cu128",
    "Torchvision": "0.22.0+cu128",
    "Torchaudio": "2.7.0",
    "PyTorch CUDA runtime": "12.8",
    "Isaac Sim": "5.1.0.0",
    "RSL-RL": "3.1.2",
    "Isaac Lab tag": "v2.3.2",
    "Isaac Lab commit": "37ddf626871758333d6ed89cf64ad702aef127d0",
    "GPU": "NVIDIA GeForce RTX 4070 Laptop GPU",
}


def command(*args: str) -> str:
    return subprocess.check_output(args, text=True, stderr=subprocess.STDOUT).strip()


def package(name: str) -> str:
    try:
        return version(name)
    except PackageNotFoundError:
        return "NOT INSTALLED"


def main() -> int:
    failures: list[tuple[str, str, str]] = []

    def check(name: str, detected: str, expected: str) -> None:
        if detected != expected:
            failures.append((name, detected, expected))

    ubuntu = command("lsb_release", "-ds")
    if not ubuntu.startswith("Ubuntu 22.04"):
        failures.append(("Ubuntu major version", ubuntu, "Ubuntu 22.04.x"))

    check("Conda environment", Path(sys.prefix).name, "dogfight")
    check("Python", platform.python_version(), EXPECTED["Python"])

    import torch

    check("PyTorch", torch.__version__, EXPECTED["PyTorch"])
    check("Torchvision", package("torchvision"), EXPECTED["Torchvision"])
    check("Torchaudio", package("torchaudio"), EXPECTED["Torchaudio"])
    check("PyTorch CUDA runtime", str(torch.version.cuda), EXPECTED["PyTorch CUDA runtime"])

    if not torch.cuda.is_available():
        failures.append(("CUDA availability", "False", "True"))
    else:
        check("GPU", torch.cuda.get_device_name(0), EXPECTED["GPU"])

    check("Isaac Sim", package("isaacsim"), EXPECTED["Isaac Sim"])
    check("RSL-RL", package("rsl-rl-lib"), EXPECTED["RSL-RL"])

    from dogfight.common.paths import ISAACLAB
    isaaclab = ISAACLAB
    try:
        check("Isaac Lab tag", command("git", "-C", str(isaaclab), "describe", "--tags", "--exact-match"), EXPECTED["Isaac Lab tag"])
        check("Isaac Lab commit", command("git", "-C", str(isaaclab), "rev-parse", "HEAD"), EXPECTED["Isaac Lab commit"])
        status = command("git", "-C", str(isaaclab), "status", "--porcelain")
        if status:
            failures.append(("Isaac Lab working tree", status, "clean working tree"))
    except (FileNotFoundError, subprocess.CalledProcessError) as error:
        failures.append(("Isaac Lab repository", str(error), "v2.3.2 at golden commit"))

    if failures:
        print("=" * 37)
        print("DOGFIGHT ENVIRONMENT CHECK FAILED")
        print("=" * 37)
        for name, detected, expected in failures:
            print(f"Detected {name}: {detected}")
            print(f"Expected {name}: {expected}")
        print("Environment may have been modified.")
        print("Training aborted.")
        return 1

    print("=" * 39)
    print("DOGFIGHT GOLDEN ENVIRONMENT CHECK PASSED")
    print("=" * 39)
    print("Known note: KNOWN_UPSTREAM_METADATA_CONFLICT (FastAPI / Starlette) is recorded and intentionally not checked as a failure.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
