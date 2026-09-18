# 实验：Linux 模型门禁与 PPO 冒烟测试

日期：2026-09-17
机器：RTX 4060 Laptop 8GB
Git commit：`30a4f6fbdbf190f012ac466eb0b12ffd16291046`（文档仓库；仿真源码修改尚待纳入 Git）
状态：模型门禁成功；统一三轴 locomotion 尚未通过验收；ONNX 可选导出待修复

## 目标

验证 URDF 静态结构、30 秒零动作站立、12 关节映射、GUI 渲染，以及自定义任务的 PPO/checkpoint 完整链路。

## 关键命令

```bash
python scripts/diagnose_zero_pose.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --duration 30 --stability-window 5 --headless \
  --output zero_pose_30s_calibrated.json

python scripts/diagnose_joint_directions.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --delta 0.1 --headless \
  --output joint_directions_com.json

python scripts/rsl_rl/train.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --headless --num_envs 8 --max_iterations 20 --seed 42

python scripts/rsl_rl/play.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --headless --num_envs 4 --num_steps 500 \
  --checkpoint /home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_13-53-43/model_final.pt

python scripts/rsl_rl/train.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --headless --num_envs 8 --max_iterations 5 --seed 42 \
  --resume --load_run 2026-09-17_13-53-43 \
  --checkpoint model_final.pt --run_name resume_smoke
```

## 结果

- 30 秒站立：PASS；0 reset；无 NaN、非足端接触或 PhysX fatal；
- 稳态 base 高度：0.2011949 m；
- 12 关节 `+-0.1 rad`：映射和方向均已记录；
- GUI：RTX 实时渲染与 Fabric GPU 正常，mesh 完整；
- PPO：20 iterations，3840 timesteps，训练时间 8.45 s；
- 最终 mean reward：约 -7.07；
- checkpoint 保存：PASS；
- 官方 play 加载与 500 步 inference：PASS；
- resume：从 iteration 19 继续至 23，PASS；
- ONNX 自动导出：FAIL（可选功能，不影响训练与推理）。

## 产物

- 站立数据：`/home/ni/robot_projects/csdog/zero_pose_30s_calibrated.json`
- 关节数据：`/home/ni/robot_projects/csdog/joint_directions_com.json`
- GUI 截图：`/home/ni/robot_projects/csdog/zero_agent_calibrated_close_gui.png`
- checkpoint：`/home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_13-53-43/model_final.pt`
- checkpoint SHA256：`a3aafc98960d3dff9108d04fb52028dd1786c5518ee13a33902ddbf994ea8b05`
- resume checkpoint：`/home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_13-55-45_resume_smoke/model_final.pt`

## 结论

模型已经通过进入 locomotion 调试所需的最小门禁。该结果证明训练闭环和 checkpoint 生命周期可用，但不证明当前策略已经学会行走，也不替代真实电机与机械限位数据校准。

## 后续站姿校准

原始全零关节站姿要求策略输出大量饱和动作才能维持站立，因此改为镜像弯腿名义姿态：

```text
FR=(-0.3, 0.9, -1.3)  FL=(+0.3, 0.9, -1.3)
RL=(+0.3, 0.9, -1.3)  RR=(-0.3, 0.9, -1.3)
```

- 出生高度：0.1527 m；
- 目标站高：0.1327 m；
- 最低 termination 高度：0.08 m；
- 30 秒：0 次异常 termination，四足接触，无非足端接触；
- 证据：`/home/ni/robot_projects/csdog/nominal_pose_v7_height_threshold_30s.json`。

## Commanded locomotion v12

v12 从 v11 使用官方 resume 继续训练至累计 iteration 1498。此次新增
3,072,000 transitions，RSL-RL 报告训练时间 214.55 秒；最终 episode length
为 999，过程中无 OOM、NaN、PhysX fatal 或 crash。

Checkpoint：

```text
/home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_16-26-02_commanded_locomotion_v12_axis_decoupling/model_final.pt
```

SHA256：`9639aed9331389a5218c19a994e533717e7cad90e8673f99bdc7002942edee4a`

固定命令测试均使用官方 `play.py`、16 个环境、每环境 1000 步：

| 命令 | 实际平均 `(vx, vy, yaw_rate)` | 异常 termination | 动作饱和率 | 判定 |
|---|---|---:|---:|---|
| `vx=+0.30 m/s` | `(0.100, 0.042, 0.010)` | 0 | 82.8% | 响应偏弱且串轴 |
| `vy=+0.15 m/s` | `(0.103, 0.041, 0.000)` | 0 | 79.0% | 未区分横移与前进命令 |
| `yaw_rate=+0.30 rad/s` | `(-0.190, -0.282, 0.191)` | 0 | 78.1% | 会转向但线速度串轴严重 |

指标与日志：

- `/home/ni/robot_projects/csdog/commanded_v12_forward_metrics.json`
- `/home/ni/robot_projects/csdog/commanded_v12_lateral_metrics.json`
- `/home/ni/robot_projects/csdog/commanded_v12_yaw_metrics.json`
- `/home/ni/robot_projects/csdog/ppo_commanded_locomotion_v12_axis_decoupling_256env_500iter.log`

结论：v12 checkpoint 可加载且整段推理无跌倒，证明仿真和训练链路稳定；但它尚未
学会合格的统一 `vx/vy/yaw_rate` 条件控制。特别是前进和横移命令产生近似相同的
运动，而转向伴随明显线速度串轴。当前阶段不得标记为 locomotion 完成，也不应仅靠
继续增加 iteration 来掩盖奖励/动作饱和问题。

另保留一次工具沙箱无 GPU 权限导致的启动失败日志：
`/home/ni/robot_projects/csdog/commanded_v12_lateral_play_sandbox_failure.log`。
随后在真机 GPU 上用相同命令复测成功，因此该日志不代表 NVIDIA 驱动故障。

## v13-v15 单变量 A/B

所有训练均为 256 environments、seed 42、从零开始、500 iterations，未安装或升级依赖。

| 版本 | 唯一关键差异 | 训练结果 | 固定命令结论 |
|---|---|---|---|
| v13 | 沿用 v12 奖励但从零训练 | 3,072,000 transitions；205.13 s | 低姿态近静止；yaw 测试 54 次 termination |
| v14 | 零命令不获得正 tracking reward | 3,072,000 transitions；218.69 s；最终 episode length 约 186 | 训练期频繁跌倒，未进入三轴 play 验收 |
| v15 | 零命令三轴 tracking mask 各 `1/3` | 3,072,000 transitions；208.93 s；最终 episode length 约 695 | 存活改善，但 X/Y 基本无响应，yaw 偏弱 |

v13 量化结果：

| 命令 | 实际平均 `(vx, vy, yaw_rate)` | termination | 平均高度 | 动作饱和率 |
|---|---|---:|---:|---:|
| `vx=+0.30` | `(0.001, 0.009, 0.014)` | 0 | 0.094 m | 72.1% |
| `vy=+0.15` | `(-0.002, 0.013, 0.021)` | 0 | 0.101 m | 63.5% |
| `yaw_rate=+0.30` | `(-0.002, 0.002, 0.043)` | 54 | 0.085 m | 88.0% |
| 站立 | `(0.008, 0.008, 0.052)` | 0 | 0.099 m | 65.8% |

v13 站立命令的 mean reward per step 为 0.239，而前进命令仅 0.009、横移命令
0.041。这证实零命令同时领取 X/Y/Yaw 三份 tracking reward 会形成显著奖励捷径。

v15 量化结果：

| 命令 | 实际平均 `(vx, vy, yaw_rate)` | termination | 平均高度 | 动作饱和率 |
|---|---|---:|---:|---:|
| `vx=+0.30` | `(-0.005, -0.001, 0.007)` | 0 | 0.093 m | 91.2% |
| `vy=+0.15` | `(-0.006, -0.003, 0.009)` | 0 | 0.093 m | 90.9% |
| `yaw_rate=+0.30` | `(0.024, -0.010, 0.096)` | 0 | 0.093 m | 76.1% |

Checkpoint SHA256：

- v13：`8d7095e4043fce1047cb6cbab2b46cd967e204d53527424158ef6ac444db7be4`
- v14：`a2fa27827ebe34c095f12fa73ecadc42714220d51a364e9888066ae22af6e056`
- v15：`ef09f9c42d1cb437836ffa0af287e4b0dd164bd5d1d2d0c7c72adc11442b3b5d`

结论：从零联合训练失败不是旧 checkpoint 惯性。归一化站立奖励修复了明确的三倍奖励
漏洞，但不足以单独解决三轴 locomotion。下一阶段应使用逐轴 curriculum：先建立稳定、
低饱和的单轴策略，通过固定命令门禁后再加入第二、第三轴，而不是继续无边界调整权重。

## v16-v17 横移课程门禁

训练入口新增两个不改变网络结构的课程参数：

```text
--command_axes x y yaw
--command_limit VALUE
```

`--command_axes` 禁用未列出的速度轴；单轴采样器也同步修改为只从非零范围的轴中
抽样。`--command_limit` 为启用轴设置对称命令范围。这避免了每阶段手改并忘记恢复配置。

v16 从 v7b 官方 resume，只启用 Y 轴，训练 200 iterations：

| 目标 `vy` | 实际平均 `(vx, vy, yaw_rate)` | termination | 平均高度 | 动作饱和率 |
|---:|---|---:|---:|---:|
| 0.15 | `(-0.007, 0.024, -0.020)` | 0 | 0.106 m | 89.7% |
| 0.50 | `(0.002, 0.491, 0.013)` | 0 | 0.123 m | 82.1% |

原始 v7b 在 `vy=0.15` 时也只有 `0.019 m/s`，且动作饱和率 98.8%。因此低速问题
不是 v16 适配造成，而是原横移专家只学会了较高速运动。

v17 从 v16 官方 resume，只启用 Y 轴并缩小到 `[-0.3, 0.3]`，训练 200 iterations：

| 目标 `vy` | 实际平均 `(vx, vy, yaw_rate)` | termination | 平均高度 | 动作饱和率 | 接触足端平面速度 |
|---:|---|---:|---:|---:|---:|
| 0.15 | `(-0.014, 0.010, 0.018)` | 0 | 0.106 m | 60.0% | 0.014 m/s |
| 0.30 | `(-0.128, 0.254, 0.017)` | 0 | 0.123 m | 67.9% | 0.145 m/s |

v17 证明低速课程能显著降低动作饱和，但没有消除 `0.15 m/s` 死区，并在
`0.30 m/s` 产生明显 X 串轴和足端滑动。因此 Y 单轴门禁仍为 FAIL，没有继续进入
X+Y 或 X+Y+Yaw 课程。下一轮应优先评估步态相位/足端目标或对称性约束，不能把
继续增加训练轮数当作解决方案。

Checkpoint SHA256：

- v16：`ae907a0c284d354c3057736c5217246a25e5435b1c3bdfa6508f8c3b5bf9d428`
- v17：`023468b434fc6c796c4ba4549135ab4cc1ee8bd5b00bfae6b36ef27d6f0c5a75`
