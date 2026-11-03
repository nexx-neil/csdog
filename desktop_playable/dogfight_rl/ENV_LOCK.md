# DOGFIGHT RL GOLDEN ENVIRONMENT — DO NOT UPGRADE

| Component | Locked version |
| --- | --- |
| Ubuntu | 22.04.5 LTS |
| NVIDIA driver | 580.159.03 |
| Python | 3.11.16 |
| PyTorch | 2.7.0+cu128 |
| Torchvision | 0.22.0+cu128 |
| PyTorch CUDA runtime | 12.8 |
| Isaac Sim | 5.1.0.0 |
| Isaac Lab | v2.3.2 |
| Isaac Lab commit | `37ddf626871758333d6ed89cf64ad702aef127d0` |
| RSL-RL | 3.1.2 |

Do not run these against the production `dogfight` environment:

```bash
pip install -U torch torchvision isaacsim rsl-rl-lib
pip install --upgrade ...
conda update --all
conda upgrade --all
git pull  # inside ~/robot_projects/IsaacLab
```

Do not upgrade Isaac Sim, Isaac Lab, PyTorch, CUDA runtime, or reinstall the NVIDIA driver unless the user explicitly says: **“我要升级 Dogfight 环境”**.

`KNOWN_UPSTREAM_METADATA_CONFLICT`: Isaac Sim 5.1 pins FastAPI 0.115.7 while Isaac Lab v2.3.2 pins Starlette 0.49.1. Do not change either package merely to silence `pip check`.

Before every formal training run, use `./run_training.sh`; it aborts when the golden environment differs from this lock.
