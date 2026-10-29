# CSDog v2 固定命令批量评估

- 状态：**FAIL**
- task：`CSDog-V2-Turn-Style-Direct-v0`
- checkpoint：`/home/ni/robot_projects/archive/csdog-runtime-2026-09-17/logs/rsl_rl/csdog_v2_turn_style/2026-10-29_17-24-35_turn_style_refine50/model_final.pt`
- seed：42

| 命令 | 状态 | 失败检查 |
|---|---|---|
| `stand` | **PASS** | - |
| `forward_015` | **PASS** | - |
| `forward_030` | **FAIL** | non_commanded_axis_coupling |
| `lateral_015` | **FAIL** | action_saturation |
| `lateral_030` | **FAIL** | action_saturation, commanded_axis_tracking |
| `yaw_030` | **FAIL** | action_saturation |
