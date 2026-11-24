# CSDog v2 固定命令批量评估

- 状态：**FAIL**
- task：`CSDog-V2-Phase-Gait-Direct-v0`
- checkpoint：`/home/ni/robot_projects/archive/csdog-runtime-2026-09-17/logs/rsl_rl/csdog_v2_phase_gait/2026-10-29_14-08-04_symmetric_phase_xyz_coupling100/model_final.pt`
- seed：42

| 命令 | 状态 | 失败检查 |
|---|---|---|
| `stand` | **PASS** | - |
| `forward_015` | **PASS** | - |
| `forward_030` | **PASS** | - |
| `lateral_015` | **FAIL** | action_saturation |
| `lateral_030` | **FAIL** | action_saturation |
| `yaw_030` | **FAIL** | action_saturation, non_commanded_axis_coupling |
