# 参数基线与修改记录

本文件只保留当前有效值和重要修改记录。修改参数前先提交当前代码，修改后记录原因、结果和对应实验。

## 当前模型基线

| 项目 | 当前值 | 状态 |
|---|---:|---|
| Link 数量 | 13 | 已静态确认 |
| 主动关节数量 | 12 | 已静态确认 |
| 动作维度 | 12 | 已静态确认 |
| 观测维度 | 48 | 已静态确认 |
| URDF 总质量 | 0.764637 kg | 待与真实设计核对 |
| 仿真步长 | 0.005 s | 自动生成值 |
| Decimation | 4 | 自动生成值 |
| Policy 步长 | 0.02 s | 由前两项得到 |
| Action scale | 0.5 rad | 待站立测试后调整 |
| Stiffness | 20.0 | 模板值，待标定 |
| Damping | 0.5 | 模板值，待标定 |
| Effort limit | 10 N·m | 模板值，待核对电机 |
| Velocity limit | 5 rad/s | 模板值，待核对电机 |
| Spawn height | 1.0 m | 必须修正 |
| Base height target | 0.98 m | 必须修正 |
| Minimum base height | 0.441 m | 必须修正 |

## 默认关节角

角度单位为 rad。`1/2/3` 的实际含义必须在 GUI 逐关节测试后填写。

| 关节 | 当前值 | 验证后数值 | 正角度物理含义 |
|---|---:|---:|---|
| FR1_joint | 0.0 |  |  |
| FR2_joint | 0.0 |  |  |
| FR3_joint | 0.0 |  |  |
| FL1_joint | 0.0 |  |  |
| FL2_joint | 0.0 |  |  |
| FL3_joint | 0.0 |  |  |
| RL1_joint | 0.0 |  |  |
| RL2_joint | 0.0 |  |  |
| RL3_joint | 0.0 |  |  |
| RR1_joint | 0.0 |  |  |
| RR2_joint | 0.0 |  |  |
| RR3_joint | 0.0 |  |  |

## 当前训练参数

| 参数 | 当前值 |
|---|---:|
| num_steps_per_env | 24 |
| max_iterations | 1500 |
| save_interval | 50 |
| learning_rate | 1e-3 |
| gamma | 0.99 |
| lambda | 0.95 |
| clip_param | 0.2 |
| entropy_coef | 0.005 |

在模型标定和站立测试通过以前，不调整 PPO 超参数。

## 修改记录

| 日期 | Git commit | 参数 | 原值 | 新值 | 原因 | 实验与结果 |
|---|---|---|---:|---:|---|---|
| 2026-09-16 | 初始提交 | 建立参数基线 | - | - | 保存自动生成配置 | 尚未运行 Linux 测试 |
