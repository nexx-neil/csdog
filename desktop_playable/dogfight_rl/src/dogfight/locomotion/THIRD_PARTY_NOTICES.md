# Official training references

Isaac Lab source commit `37ddf626871758333d6ed89cf64ad702aef127d0`, tag `v2.3.2` (local frozen checkout). BSD-3-Clause text is preserved in LICENSE.NVIDIA. No official source files are modified.

- `manager_based/locomotion/velocity/velocity_env_cfg.py`: ManagerBasedRLEnv, scene/command/action/observation/event/reward/termination patterns and imported standard reward functions.
- `config/anymal_c/flat_env_cfg.py` and `agents/rsl_rl_ppo_cfg.py`: plane terrain, orientation penalty, 24-step rollout, actor/critic [128,128,128] ELU, clipped PPO, adaptive KL learning rate, gamma .99 / GAE .95 / epochs 5 / minibatches 4.
- `config/spot/flat_env_cfg.py`, `mdp/rewards.py`: optional diagonal synchronized-foot GaitReward (direct API reuse); optional swing clearance and support-foot slip concepts. Because this model has no separate foot body, clearance/slip are adapted to STL-derived distal points instead of knee-body origins. Gait weight defaults to zero. Gait rewards synchronize LF/RR and RF/LR and anti-synchronize the other pairs, gated on movement. It is a prior, not a controller.
- `scripts/reinforcement_learning/rsl_rl/{train,play}.py`: AppLauncher-before-simulator imports, Gym registration, RslRlVecEnvWrapper, OnPolicyRunner.learn/load and RGB recording flow.

[Versioned source](https://github.com/isaac-sim/IsaacLab/tree/37ddf626871758333d6ed89cf64ad702aef127d0/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity).
[Official Spot training overview](https://developer.nvidia.com/blog/closing-the-sim-to-real-gap-training-spot-quadruped-locomotion-with-nvidia-isaac-lab/).

The robot mass/inertia, stance, actuator parameters, speed range, action scale, foot clearance and weights are independent of Spot/ANYmal physical parameters. PPO itself is imported from frozen RSL-RL 3.1.2 (ETH Zurich/NVIDIA, BSD-3-Clause), never copied or reinstalled.
