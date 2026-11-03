# Dogfight RL environment

Generated on 2026-09-13 for reproducibility across Dog A and Dog B machines.

## Locked stack

| Component | Version / value |
| --- | --- |
| Ubuntu | 22.04.5 LTS |
| Kernel | 6.8.0-124-generic |
| NVIDIA driver | 580.159.03 |
| GPU | NVIDIA GeForce RTX 4070 Laptop GPU, 8188 MiB |
| Python | 3.11.16 (`dogfight` Conda environment) |
| PyTorch | 2.7.0+cu128 |
| PyTorch CUDA runtime | 12.8 |
| Isaac Sim | 5.1.0.0 (package form of 5.1.0) |
| Isaac Lab tag | v2.3.2 |
| Isaac Lab commit | 37ddf626871758333d6ed89cf64ad702aef127d0 |
| Isaac Lab core package | 0.54.2 |
| Isaac Lab RL package | 0.4.7 |
| RSL-RL | rsl-rl-lib 3.1.2 |

## Machine capacity

- Physical RAM: 16 GiB
- Swap: 32 GiB (`/swapfile`)
- Training baseline: `--headless --num_envs 256`
- Do not install a system CUDA Toolkit solely for this project. `nvcc` is intentionally absent.

## Validated tests

- PyTorch CUDA test: passed; CUDA available and RTX 4070 Laptop GPU detected.
- Isaac Sim / Isaac Lab PhysX smoke test: passed; reset and ten GPU PhysX steps completed.
- RSL-RL PPO smoke test: passed; `Isaac-Velocity-Rough-Anymal-C-v0`, headless, 256 environments, one iteration (6,144 steps). The dependency-regression run measured approximately 4,511 steps/s.

## Running Isaac Lab on this machine

The login shell contains ROS/Gazebo library paths. Do **not** use those paths for Isaac Sim. Run Isaac Lab with both inherited variables removed, for example:

```bash
cd ~/robot_projects/IsaacLab
env -u PYTHONPATH -u LD_LIBRARY_PATH \
  OMNI_KIT_ACCEPT_EULA=YES \
  conda run --no-capture-output -n dogfight \
  bash ./isaaclab.sh --python scripts/reinforcement_learning/rsl_rl/train.py \
  --task Isaac-Velocity-Rough-Anymal-C-v0 --headless --num_envs 256
```

Increase the number of environments gradually (512, then 1024 only if RAM and VRAM remain healthy). Do not enable RGB cameras or high-quality RTX rendering during locomotion training.

## Shared conventions

- Coordinates: X forward, Y left, Z up.
- Units: m, kg, s, rad.
- Low-level command interface: `vx`, `vy`, `yaw_rate`.
- Locomotion observation baseline: `base_lin_vel`, `base_ang_vel`, `projected_gravity`, `velocity_commands`, `joint_pos`, `joint_vel`, `previous_action`.
- Locomotion action: 12 joint position targets.

## Package metadata note

`pip check` has one remaining upstream metadata conflict: Isaac Lab v2.3.2 pins `starlette==0.49.1`, while Isaac Sim 5.1 pins `fastapi==0.115.7`, whose declared range is `starlette<0.46.0`. Both are exact requirements from the selected NVIDIA releases and cannot be simultaneously satisfied by pip. GPU simulation and the PPO smoke tests pass with the locked stack above; do not replace Isaac Sim or Isaac Lab versions to silence this metadata-only conflict.

## Snapshots

The matching raw environment snapshots are in `~/dogfight_env_info/`:

- `nvidia.txt`
- `system.txt`
- `conda.txt`
- `pip_freeze.txt`
- `pytorch.txt`
- `isaaclab_commit.txt`
