# CSDog v2 分阶段门禁

- 总状态：**FAIL**
- Git commit：`6ec43f8961dc7191dc73714ebca2b11727151c54`

| 阶段 | 状态 | 说明 |
|---|---|---|
| `static_urdf` | **FAIL** | Static structure is valid, but simulation/training is blocked until every review_required item has verified provenance. |
| `joint_direction` | **NOT_RUN** | blocked by static_urdf FAIL; planned check: fixed-base joint direction and target tracking |
| `pd_stand_30s` | **NOT_RUN** | blocked by static_urdf FAIL; planned check: 30-second PD standing gate |
| `contact_and_gait` | **NOT_RUN** | blocked by static_urdf FAIL; planned check: contact, slip, swing height, saturation, gait timing |
| `ppo_smoke` | **NOT_RUN** | blocked by static_urdf FAIL; planned check: bounded PPO smoke test only |

失败阶段之后的项目均为 `NOT_RUN`；这不是通过，也不允许启动训练。
