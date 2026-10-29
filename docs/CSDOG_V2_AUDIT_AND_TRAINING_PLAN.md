# CSDog v2 审计、诊断与训练计划

日期：2026-10-29

审计起点 commit：`00ff66dd1dffe5d7c098475403cec58d389fcc18`

v2 首个独立资产提交：`1c6ceaf1d43260e43cbdac06f6ce23fc00bbd098`

## 当前结论

v2 的 URDF 结构门禁通过，物理就绪门禁失败，因此未启动 Isaac Sim 动态测试，
也未启动 PPO smoke/长训练。旧资产、旧任务
`Template-GeneratedRobot-Direct-v0`、checkpoint 和日志均未修改或删除。

v2 使用独立目录 `assets/robots/csdog_v2` 和独立校准任务
`CSDog-V2-Calibration-Direct-v0`。该任务明确设置 `training_enabled=False`；训练入口会
直接拒绝它。v1 checkpoint 的关节名、顺序、质量、几何和控制参数与 v2 不兼容，禁止加载。

## 已证实问题

### 旧任务与 v12-v17

1. **速度条件控制失败。** v12 的 `vx=0.30` 和 `vy=0.15` 实际都主要产生约
   `vx=0.10 m/s`；纯 yaw 命令还产生 `vx=-0.190, vy=-0.282 m/s`。这是固定命令结果，
   不是只根据训练 reward 作出的判断。
2. **低速死区存在。** v16 在 `vy=0.15` 仅达到 `0.024 m/s`，v17 仅达到
   `0.010 m/s`；v17 在 `vy=0.30` 达到 `0.254 m/s`，但带来 `vx=-0.128 m/s`。
3. **动作长期饱和。** v12 为 78.1%-82.8%，v16 为 82.1%-89.7%；v17 虽降至
   60.0%-67.9%，仍明显偏高。
4. **旧模型膝关节目标可越过软限位。** URDF 硬限位为 `±1.57 rad`，配置的软限位
   因子为 0.95，即约 `±1.4915 rad`。膝默认角为 `-1.3 rad`，而
   `action_scale=0.5` 允许目标到 `-1.8 rad`。负动作小于约 `-0.383` 时目标已经越过
   软限位。现有 `action_saturation_fraction` 只统计 policy action 是否达到 `±1`，
   没有统计这种关节目标/物理限位饱和。
5. **纯 yaw 的 `feet_air_time` 被屏蔽。** 当前条件是
   `norm(commands[:, :2]) > 0.1`，所以 `(0, 0, yaw)` 不可能获得该项，与转向步态需求不符。
6. **`feet_slide` 不是接触点滑动。** 当前实现使用 distal link 刚体原点的世界系 XY
   线速度，并以当前帧净接触力 `>1 N` 作开关。它没有加入 `omega × r` 得到足底接触点
   速度，也没有使用 history/hysteresis 抗接触抖动。
7. **“足端接触”无法区分足底与小腿碰撞。** v1 的 foot body 是整个 `*3` link；v2
   的 foot body 是整个 `*_knee` link。两代 URDF 都没有独立 foot/sole link 或接触点，
   因而当前 contact sequence 代表 distal link 任意位置接触，而不是已验证的足底落地。
8. **低速静止具有明确的奖励优势。** 以 `0.15 m/s` 单轴命令和静止速度计算，指数
   tracking 仍约为最大值的 91.4%；同时 action magnitude、joint deviation、action rate、
   acceleration 和 air-time 门槛都偏向少动。这个奖励地形与实测低速死区一致。
9. **低姿态惩罚量级很弱。** base height 使用平方误差且 scale 为 -1；下降 4 cm 的
   未缩放惩罚只有 `0.0016`，远小于 tracking 项的单位量级。v13/v15 的约 0.093 m
   低姿态因此没有受到足够区分。
10. **air-time 项没有上限或目标带。** 当前是首次接触时直接奖励
    `last_air_time - 0.1`，可能偏好过长腾空；它不是“达到期望摆动时间”的有界目标。

### v2 静态模型

1. 结构为 13 links、12 revolute joints、13 个 mesh，关节名和 URDF 顺序与独立
   manifest 一致；总质量为 `7.60426080 kg`。
2. 零关节位形下，URDF 惯性计算出的整机质心相对 base 为
   `(-0.001992, -0.000022, -0.073962) m`。这只证明 XML 内部计算结果，不证明真实装机质心。
3. 所有质量为正，惯性矩阵通过正定检查，mesh 均存在。
4. 12 个关节全部使用同一组 `[-3.14, 3.14, 10 N·m, 3 rad/s]`。仓库没有机械硬限位、
   电机峰值/连续力矩、减速比或速度来源，不能视作真实参数。
5. 13 个 mesh 同时承担 visual 和 collision；12 个 collision mesh 超过 1000 triangles，
   collision 三角形合计 38,635。没有独立简化碰撞资产的来源记录。
6. v2 质量约为旧模型的 9.95 倍，关节名、轴、几何和限位也不同。因此旧站高、默认角、
   `action_scale=0.5`、PD `20/0.5`、termination 高度及 checkpoint 均不能直接复用。

## 待测试假设

1. v17 的 X 串轴可能来自左右/前后关节轴和几何不完全对称、接触滑动与奖励缺少镜像约束
   的组合；目前不能只归因于任一项。
2. 当前 link-origin 速度可能高估或低估真实足底滑动，尤其在 distal link 快速转动时。
3. v2 的 mesh 末端是否形成稳定、对称、尺寸一致的支撑面尚未验证；mesh 存在不等于
   接触几何正确。
4. URDF 质心是否落在实际四足支撑多边形内、加载电池后的质心是否仍合理，尚待 CAD/
   实物数据和仿真姿态共同确认。
5. 旧策略是否存在拖脚、对角步、同侧步或跳跃，需要逐足接触时序和摆动高度数据；现有
   汇总 contact fraction 不足以判断。
6. B 组的接触点防滑与摆动高度目标是否消除死区，C 组的相位/对称性是否降低串轴，必须
   由相同 seed 和固定命令矩阵验证。

## 分阶段门禁

### 0. 静态与参数来源（当前 FAIL）

- 结构、名称、顺序、mesh、mass、inertia 自动检查；
- 获取并记录 v2 每类关节的真实 position/continuous torque/peak torque/velocity；
- 确认传动比和控制器输出侧定义；
- 为足底建立独立、可追溯的 collision/contact reference；
- 确认训练 collision 的简化方式和 SHA256。

阻断项未解决前，后续阶段均为 `NOT_RUN`。

### 1. 关节方向与目标角跟踪

固定 base、腿悬空，按 manifest 顺序对每个关节做 `±0.05` 和 `±0.10 rad`。记录目标、
实测位移、直接 child 和该腿末端的 XYZ 位移、峰值力矩。方向一致且实测幅度至少为请求的
50% 才 PASS。该测试不得使用 v1 的关节名推导。

### 2. 默认站姿和 30 秒 PD 门禁

从 v2 几何重新确定默认角和 spawn height；独立扫描低增益 PD，逐步增加承载能力。PASS
要求 30 秒无 reset/NaN/非足端持续接触，稳态线速度不超过 `0.05 m/s`、角速度不超过
`0.20 rad/s`、任一关节稳态力矩不超过限位的 95%。失败即停止。

### 3. 接触、滑动、饱和和步态诊断

- 接触采用 on/off 双阈值或 history，输出逐足 duty factor、触地/离地次数和序列；
- 滑动使用明确的 foot reference/contact point 速度，不能再称 link origin 速度为足底速度；
- 输出 action、目标关节位置、实际关节位置和力矩四类饱和率；
- 输出每足摆动期最大/平均 clearance、拖脚比例；
- 输出对角足/同侧足相位差和支撑足数量分布。

### 4. A/B/C PPO smoke

共同设置来自 `config/experiments/csdog_v2_abc.json`：seed 42、64 env、5 iterations；
评估均为 16 env × 1000 steps，使用同一组站立、0.15/0.30 前进、0.15/0.30 横移和
0.30 yaw 命令。只做 smoke，不自动进入长训练。

- A：仅采用已通过门禁的物理和控制修正；
- B：A + 一个“接触感知足端目标”主因素（接触点防滑 + 摆动 clearance）；
- C：B + 一个“步态组织”主因素（相位或镜像对称引导）。

每组 checkpoint 必须带 `csdog_v2_joint_order_v1` 兼容标签，并写入独立实验目录。任何旧
`generated_robot` checkpoint 都视为结构不兼容。

## 可复现命令

静态审计与总门禁：

```bash
python scripts/run_csdog_v2_gates.py \
  --json-output experiments/results/2026-10-29/csdog_v2_gate_pipeline.json \
  --markdown-output experiments/2026-10-29_CSDOG_V2_GATES.md
```

静态门禁修复后，才允许执行：

```bash
python scripts/diagnose_joint_directions.py \
  --task CSDog-V2-Calibration-Direct-v0 --delta 0.05 --headless \
  --output experiments/results/<date>/csdog_v2_joint_directions_005.json

python scripts/diagnose_zero_pose.py \
  --task CSDog-V2-Calibration-Direct-v0 --use-configured-pose \
  --duration 30 --stability-window 5 --headless \
  --output experiments/results/<date>/csdog_v2_pd_stand_30s.json
```

这些命令目前只作为下一阶段接口，不是已运行证据。

## v2 改造文件清单

- `assets/robots/csdog_v2/`：与 v1 隔离的原始 URDF、mesh、来源 SHA256；
- `config/csdog_v2_urdf_expectations.json`：关节/link 顺序、质量和兼容性 manifest；
- `scripts/audit_urdf.py`：无 Isaac Sim 依赖的 mesh/mass/inertia/limit 静态门禁；
- `tasks/direct/csdog_v2/`：独立校准任务和显式训练阻断；
- `scripts/diagnose_joint_directions.py`：基于配置映射的目标角方向门禁；
- `scripts/diagnose_zero_pose.py`：30 秒站立 PASS/FAIL 与力矩占限位比例；
- `scripts/rsl_rl/play.py`：目标角、关节、力矩饱和和逐足时序指标；
- `scripts/evaluate_fixed_commands.py`：A/B/C 共用固定命令、seed、阈值批测；
- `scripts/run_csdog_v2_gates.py`：失败即停的阶段编排和 JSON/Markdown 汇总；
- `config/experiments/csdog_v2_abc.json`：A/B/C 单变量设计与共同评估定义；
- `tests/test_urdf_audit.py`：顺序错误与当前静态门禁回归测试。

完整代码审查范围：

```bash
git diff 00ff66dd1dffe5d7c098475403cec58d389fcc18..HEAD
```
