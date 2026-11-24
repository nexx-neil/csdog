# CSDog v2 分阶段门禁

- 总状态：**INCOMPLETE**
- Git commit：`446e451657f9f78ecdcffe4b76a191b1f28e2522`

| 阶段 | 状态 | 说明 |
|---|---|---|
| `static_urdf` | **PASS** | Static simulation gate passed; hardware deployment remains separately gated. |
| `joint_direction` | **PASS** | evidence: experiments/results/2026-10-29/csdog_v2_joint_directions_005.json, experiments/results/2026-10-29/csdog_v2_joint_directions_010.json |
| `pd_stand_30s` | **PASS** | evidence: experiments/results/2026-10-29/csdog_v2_pd_stand_30s.json |
| `contact_and_gait` | **NOT_RUN** | awaiting ordered execution; planned check: contact, slip, swing height, saturation, gait timing |
| `ppo_smoke` | **NOT_RUN** | blocked by an earlier gate; planned check: bounded PPO smoke test only |

已完成阶段均有机器可读证据；下一阶段仍须显式执行，不能把 smoke 当成行为通过。
