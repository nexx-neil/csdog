#!/usr/bin/env python3
"""Current project entrypoints; historical Dog A is never selected implicitly."""
from pathlib import Path
import argparse
import json
import os
import subprocess
import sys
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from dogfight.common.paths import ROOT, PYTHON, project_path

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", choices=["fsm_battle", "teleop", "train", "evaluate", "play", "battle", "battle-gui", "battle-smoke",
        "hud-smoke", "training-tools-check", "test", "test-legacy", "integrity", "check-environment", "legacy-info",
        "train-a", "validate-a", "gui-a", "train-b", "validate-b", "train-c", "validate-c"])
    parser.add_argument("--dry-run", action="store_true")
    args, rest = parser.parse_known_args()
    if args.task.endswith(("-a", "-b", "-c")):
        parser.error("旧模型入口已归档；本机缺少该历史入口对应的正式配置。请使用 legacy-info 查看历史资料。")
    if args.task == "play":
        rest.append("--video")
    if args.task == "legacy-info":
        print((ROOT.parent / "archive/legacy_dog_a/README.md").read_text())
        return 0
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)
    env.update(PYTHONPATH=str(ROOT / "src"), PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1",
        PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", OMNI_KIT_ACCEPT_EULA="YES", TERM="xterm")
    if not PYTHON.is_file():
        parser.error(f"Frozen Python missing: {PYTHON}")
    for flag in ("--config", "--checkpoint", "--resume", "--output", "--output-dir", "--trajectory", "--video-dir", "--log-dir"):
        for i, value in enumerate(rest):
            if value == flag and i+1 < len(rest):
                rest[i+1] = str(project_path(rest[i+1]))
            elif value.startswith(flag+"="):
                rest[i] = flag+"="+str(project_path(value.split("=",1)[1]))
    for i, value in enumerate(rest):
        for flag in ("--output", "--output-dir", "--trajectory", "--video-dir", "--log-dir"):
            target = rest[i+1] if value == flag and i+1 < len(rest) else value.split("=",1)[1] if value.startswith(flag+"=") else None
            if target and Path(target).exists():
                parser.error(f"refusing to overwrite existing output: {target}")
    if args.task == "fsm_battle":
        rest = ["--config", str(ROOT / "configs/teleop/fsm_battle.yaml")] + rest
    scripts = {"fsm_battle": "teleop/run.py", "teleop": "teleop/run.py", "train": "train/csdog_12dof.py", "evaluate": "evaluate/csdog_12dof.py", "play": "evaluate/csdog_12dof.py",
        "battle": "battle/run_v0_headless.py", "battle-gui": "battle/run_v0_battle_demo.py",
        "battle-smoke": "battle/run_v0_smoke_tests.py", "hud-smoke": "battle/run_v02_hud_smoke_tests.py",
        "training-tools-check": "diagnostics/verify_training_runtime.py",
        "check-environment": "diagnostics/check_environment.py", "integrity": "diagnostics/verify_integrity.py"}
    if args.task in ("test", "test-legacy"):
        target = ROOT / "tests" if args.task == "test" else ROOT.parent / "archive/legacy_dog_a/diagnostics/test_dog_a_interface.py"
        command = [str(PYTHON), "-B", "-m", "pytest", "-q", "-p", "no:cacheprovider", str(target)]
    else:
        command = [str(PYTHON), "-B", str(ROOT / "scripts" / scripts[args.task])]
    command += rest
    print(json.dumps({"command": command, "cwd": str(ROOT), "python": str(PYTHON)}, ensure_ascii=False), flush=True)
    if args.dry_run:
        return 0
    if args.task in ("teleop", "fsm_battle"):
        os.chdir(ROOT)
        os.execvpe(command[0], command, env)
    return subprocess.run(command, env=env, cwd=ROOT).returncode
if __name__ == "__main__":
    raise SystemExit(main())
