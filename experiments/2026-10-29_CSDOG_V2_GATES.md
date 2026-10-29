# CSDog v2 分阶段门禁

- 总状态：**INCOMPLETE**
- Git commit：`24e953977fa39167fb9996550d21a207823f317d`

| 阶段 | 状态 | 说明 |
|---|---|---|
| `static_urdf` | **PASS** | Static simulation gate passed; hardware deployment remains separately gated. |
| `joint_direction` | **NOT_RUN** | awaiting ordered execution after static gate PASS; planned check: fixed-base joint direction and target tracking |
| `pd_stand_30s` | **NOT_RUN** | awaiting ordered execution after static gate PASS; planned check: 30-second PD standing gate |
| `contact_and_gait` | **NOT_RUN** | awaiting ordered execution after static gate PASS; planned check: contact, slip, swing height, saturation, gait timing |
| `ppo_smoke` | **NOT_RUN** | awaiting ordered execution after static gate PASS; planned check: bounded PPO smoke test only |

静态仿真门禁已通过；其余阶段仍须按顺序显式执行和记录，不能跳过。
