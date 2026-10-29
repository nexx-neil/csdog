# CSDog v2 固定命令批量评估

- 状态：**FAIL**
- task：`CSDog-V2-Locomotion-Direct-v0`
- checkpoint：`/home/ni/robot_projects/archive/csdog-runtime-2026-09-17/logs/rsl_rl/csdog_v2_locomotion/2026-10-29_11-25-50_phase_xyz/model_final.pt`
- seed：42

| 命令 | 状态 | 失败检查 |
|---|---|---|
| `stand` | **PASS** | - |
| `forward_015` | **FAIL** | non_commanded_axis_coupling |
| `forward_030` | **FAIL** | non_commanded_axis_coupling |
| `lateral_015` | **PASS** | - |
| `lateral_030` | **PASS** | - |
| `yaw_030` | **PASS** | - |
