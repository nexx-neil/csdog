# CSDog v2 进展快照（2026-10-29）

## 已完成

- 关节方向：24/24 PASS（±0.05、±0.10 rad）。
- 30 秒 PD 站立：PASS；无重置、无非足底接触。
- PPO smoke、checkpoint 元数据和 ONNX 导出：PASS。
- 300 轮 x 课程：前进/后退 `±0.30 m/s` 均 0 termination，轴向 RMSE 分别约 0.020/0.041 m/s。
- 续训至 600 轮 x+y、900 轮 x+y+yaw；三个阶段 checkpoint 均保留。

## 900 轮统一评估

`stand`、`lateral_015`、`lateral_030`、`yaw_030` 通过统一阈值。
`forward_015` 与 `forward_030` 的命令轴跟踪通过，但非命令轴耦合失败；
主要表现为约 0.145 m/s 的侧向漂移。因此当前是“方向功能可用的仿真原型”，
不是完成严格解耦与步态优化的最终策略。

## 保留的 checkpoint

- x（300 轮）：`logs/rsl_rl/csdog_v2_locomotion/2026-10-29_11-14-54/model_final.pt`
- x+y（600 轮）：`logs/rsl_rl/csdog_v2_locomotion/2026-10-29_11-18-58_phase_xy/model_final.pt`
- x+y+yaw（900 轮）：`logs/rsl_rl/csdog_v2_locomotion/2026-10-29_11-25-50_phase_xyz/model_final.pt`

训练产物不提交 Git；小型门禁和固定命令 JSON 报告提交。

## 下一轮目标

先查看 900 轮策略的实际动作，再针对前进侧向漂移与步态不对称做奖励/课程调整。
连续力矩、机械硬限位和热保护未知，因此任何 checkpoint 仍禁止直接部署实机。
