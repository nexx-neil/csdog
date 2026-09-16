# 第一阶段执行手册：现有模型转 URDF 并完成基础行走训练

更新时间：2026-09-16  
适用环境：Ubuntu 22.04、Isaac Sim 5.1.0、Isaac Lab 2.3.2、RSL-RL 3.1.2  
阶段目标：将现有四足机器人模型转换为可用 URDF，导入 Isaac Lab，完成 PD 站立和基础速度跟踪训练。

> 本阶段不做双狗对战、视觉、高层战斗策略或 Self-Play。只有单狗基础运动通过验收后，才进入下一阶段。

## 1. 本阶段最终交付物

- 原始 CAD 装配体及导出前备份；
- 完整 URDF 包：URDF、网格、纹理（如有）；
- Isaac Lab 中的机器人资产配置；
- 平地 locomotion 环境与 PPO 配置；
- 可加载的 checkpoint；
- 训练命令、关键曲线、测试录像和简短实验记录；
- 关节映射表与最终验收结果。

完成标准：机器人能稳定站立，能跟踪前进速度和转向速度命令，并可从保存的 checkpoint 独立加载运行。

## 2. 工作目录与变量

建议不要修改黄金环境中的 Isaac Lab 源码。自定义代码放在独立项目中。

```bash
export TERM=xterm-256color
export LC_ALL=C

export ISAACLAB_ROOT=/home/ni/robot_projects/IsaacLab
export PROJECT_ROOT=/home/ni/robot_projects/csdog
export ROBOT_NAME=csdog
```

后续命令中的 `<...>` 是待替换内容，不能原样执行。

每次工作前检查：

```bash
cd "$ISAACLAB_ROOT"
git status --short
git rev-parse HEAD

./isaaclab.sh -p -c \
  "import torch; print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0))"
```

基线要求：Isaac Lab 工作区干净，commit 为
`37ddf626871758333d6ed89cf64ad702aef127d0`，CUDA 返回 `True`。

## 3. CAD 模型导出前整理

### 3.1 简化模型

在 SolidWorks、Inventor 或其他 CAD 软件中复制一份训练专用模型，然后：

1. 删除螺钉、倒角、装饰件和不影响质量分布的小零件；
2. 将刚性连接、不会相对运动的零件合并成一个 link；
3. 保留机身和四条腿的真实运动链；
4. 每条腿保持 3 个驱动关节，总动作维度通常为 12；
5. 为足端、腿段和机身准备简化碰撞体；
6. 统一装配体单位，优先使用米、千克、弧度；
7. 将机器人置于标准零位，避免导出时关节处于任意姿态。

不要用高面数 visual mesh 直接充当 collision mesh。复杂碰撞体会降低并行训练速度并导致接触不稳定。

### 3.2 固定坐标约定

整个项目统一采用：

- `+X`：机器人前方；
- `+Y`：机器人左方；
- `+Z`：机器人上方；
- 关节正方向遵循右手定则；
- 角度使用弧度；
- 长度使用米；
- 质量使用千克。

### 3.3 建立关节映射表

在导出前填写并提交这张表：

| 序号 | URDF 关节名 | 腿 | 功能 | 轴向 | 下限 | 上限 | 默认角 |
|---:|---|---|---|---|---:|---:|---:|
| 0 | `<FL_HIP>` | 左前 | 外展/内收 | `<axis>` |  |  |  |
| 1 | `<FL_THIGH>` | 左前 | 髋俯仰 | `<axis>` |  |  |  |
| 2 | `<FL_CALF>` | 左前 | 膝俯仰 | `<axis>` |  |  |  |
| ... |  |  |  |  |  |  |  |

这张表是 CAD、URDF、Isaac Lab action 和策略输出之间的唯一对照。不要依赖文件中的自然排序。

## 4. 导出 URDF

如果使用 SolidWorks，可使用维护良好的 URDF Exporter；其他 CAD 软件可以先导出 STEP，再在机器人建模工具中建立关节和 URDF。无论使用什么工具，最终都必须人工检查 URDF。

导出时设置：

- `base_link` 为机身主体；
- 每个活动关节使用 `revolute`，不是 `continuous` 或 `fixed`；
- parent/child 与真实运动链一致；
- joint origin 位于真实转轴；
- axis 与关节正方向一致；
- effort、velocity 和 position limit 均非空；
- 每个 link 均有合理质量、质心和惯性张量；
- mesh 路径使用可迁移的相对路径；
- transmission/controller 标签不是 Isaac Lab 训练的核心，不要用它替代 actuator 配置。

建议输出：

```text
robot_description/
├── urdf/csdog.urdf
├── meshes/visual/
├── meshes/collision/
└── README.md
```

## 5. URDF 静态检查

先安装或使用系统已有的 URDF 检查工具：

```bash
check_urdf "$PROJECT_ROOT/robot_description/urdf/csdog.urdf"
```

生成结构图（可选）：

```bash
urdf_to_graphiz "$PROJECT_ROOT/robot_description/urdf/csdog.urdf"
```

人工检查：

- 是否只有一个根 link；
- 是否恰好有 12 个预期驱动关节；
- 关节名是否唯一；
- 网格是否全部存在；
- 惯性主对角线是否为正；
- 是否存在极小质量、零惯量或明显异常的质心；
- 左右腿和前后腿的关节方向是否一致；
- 关节限位是否允许正常站立但不会穿过自身。

这一关未通过时不要打开 PPO 训练。

## 6. 转换并检查 Isaac Sim 资产

先查看当前版本转换器参数，避免照搬其他版本命令：

```bash
cd "$ISAACLAB_ROOT"
./isaaclab.sh -p scripts/tools/convert_urdf.py --help
```

按帮助中的参数将 URDF 转为 USD。输入和输出应使用绝对路径，例如：

```bash
./isaaclab.sh -p scripts/tools/convert_urdf.py \
  "$PROJECT_ROOT/robot_description/urdf/csdog.urdf" \
  "$PROJECT_ROOT/assets/csdog.usd"
```

若实际 CLI 要求命名参数，以 `--help` 为准。四足机器人必须保留浮动基座，不要设为 fixed base。

在 Isaac Sim GUI 中检查：

1. 模型朝向和比例正确；
2. 机体离地高度合理；
3. 分别给 12 个关节小幅目标，确认转动方向；
4. 关闭驱动后受重力自然下落；
5. 碰撞体不会明显互穿；
6. 足端与地面接触位置正确；
7. articulation root 位于预期位置。

## 7. 创建 Isaac Lab 项目配置

在独立项目中定义机器人资产配置，至少包含：

- USD 路径；
- 初始 base 位置和姿态；
- 12 个默认关节角；
- actuator 的关节匹配表达式；
- stiffness、damping、effort limit、velocity limit；
- 接触传感器配置；
- 需要记录的 base、foot 和非足端 body 名称。

程序启动时必须打印最终解析到的 12 个关节名，并与第 3.3 节的映射表逐项比较。若数量不是 12 或顺序不正确，立即停止。

## 8. 先做 PD 站立，不训练 PPO

创建最小测试场景：一个机器人、平地、重力和关节位置控制。给 12 个关节持续发送默认站立角。

从保守参数开始调试：

1. 先降低 stiffness，确认关节方向和默认角正确；
2. 逐步提高 stiffness，使机器人能够支撑自重；
3. 调整 damping，抑制持续振荡；
4. 检查 effort limit 是否长期饱和；
5. 连续运行至少 30 秒。

通过条件：

- 机器人保持直立 30 秒；
- base、机身和大腿没有触地；
- 无持续高频抖动；
- 关节没有越限；
- 力矩没有长期顶到上限；
- 日志无 NaN、PhysX fatal error 或崩溃。

失败排查顺序：关节方向和默认角 → 质量/惯量 → 碰撞体 → PD 参数 → 仿真步长。不要先改奖励函数。

## 9. 建立平地基础行走任务

建议先注册任务：

```text
CSDog-Velocity-Flat-v0
```

### Observation

第一版只保留必要信息：

- base angular velocity；
- projected gravity；
- 12 个关节位置相对默认角的偏差；
- 12 个关节速度；
- 命令 `vx`、`vy`、`yaw_rate`；
- 上一时刻的 12 维 action。

### Action

Policy 输出 12 维归一化动作，经缩放后作为默认关节角的偏移：

```text
q_target = q_default + action_scale * action
```

再由 PD 控制器得到关节力矩。第一版不要直接输出力矩。

### Reward

第一版建议包含：

- `+` 线速度命令跟踪；
- `+` yaw 角速度跟踪；
- `-` 非期望垂直速度；
- `-` 非期望 roll/pitch 角速度；
- `-` 姿态倾斜；
- `-` 关节力矩；
- `-` 关节加速度；
- `-` action rate；
- `-` 足端滑动；
- 非足端触地直接终止或重罚。

奖励项必须分别记录，不能只看总 reward。

### Command curriculum

分阶段扩大命令范围：

1. 站立：`vx=0, vy=0, yaw=0`；
2. 缓慢前进：仅小范围正 `vx`；
3. 前进/后退；
4. 加入转向；
5. 最后加入侧移。

不要第一轮就同时要求高速前进、侧移、转向和崎岖地形。

## 10. 训练执行流程

先查看项目训练入口的帮助：

```bash
cd "$PROJECT_ROOT"
<ISAAC_LAB_PYTHON> <TRAIN_SCRIPT> --help
```

基础训练命令形式：

```bash
<ISAAC_LAB_PYTHON> <TRAIN_SCRIPT> \
  --task CSDog-Velocity-Flat-v0 \
  --num_envs 256 \
  --max_iterations 50 \
  --headless \
  --seed 42
```

这里故意保留 `<ISAAC_LAB_PYTHON>` 和 `<TRAIN_SCRIPT>`：项目生成方式不同，入口可能位于 Isaac Lab 官方 `scripts/reinforcement_learning/rsl_rl/train.py`，也可能复制在项目自己的 `scripts/rsl_rl/train.py`。必须以仓库实际结构为准。

### 10.1 冒烟训练

先运行 20～50 次 PPO update，仅验证管线：

- action space 为 12；
- observation 维度符合配置；
- reward 各分量有数值且无 NaN；
- reset 和 termination 正常；
- GPU 显存稳定；
- 能生成 checkpoint；
- 机器人没有通过趴倒、跳跃或剧烈摆腿刷分。

### 10.2 正式训练

冒烟测试通过后才扩大迭代数。保存：

- 完整命令；
- Git commit；
- seed；
- 环境数；
- reward 权重；
- checkpoint 路径和 SHA256；
- TensorBoard 曲线；
- 失败现象和下一步改动。

一次实验只改变一个主要因素，否则无法判断改动原因。

### 10.3 断点续训

使用训练入口的 `--help` 确认 `--resume`、`--load_run` 和 `--checkpoint` 参数。启动后必须在日志中看到实际加载的 checkpoint。续训 3～5 次 update 后确认能够保存新 checkpoint，再开始长训。

## 11. 独立推理和验收

对候选 checkpoint 执行 headless 和 GUI 两类测试。

```bash
<ISAAC_LAB_PYTHON> <PLAY_SCRIPT> \
  --task CSDog-Velocity-Flat-v0 \
  --num_envs 32 \
  --checkpoint <ABSOLUTE_CHECKPOINT_PATH> \
  --headless
```

GUI 检查时将环境数降为 1～4，并录制固定命令序列：

```text
站立 5 秒
→ 前进 10 秒
→ 左转 5 秒
→ 右转 5 秒
→ 停止 5 秒
```

最终验收指标：

- 站立 30 秒成功；
- 指定速度下不依赖偶然初始状态；
- 前进速度跟踪误差可接受；
- 左右转向均正常；
- 固定种子的多回合跌倒率可记录；
- checkpoint 可重新加载并继续训练；
- 推理无 NaN、崩溃和明显关节越限；
- 完成 JIT/ONNX 导出（若当前项目需要跨仿真器或部署）。

## 12. GitHub 记录方式

本阶段只需要维护三类信息：

1. 本文档：流程和验收标准；
2. `CURRENT.md`：当前做到哪一步、下一步是什么；
3. `experiments/<日期>-<名称>.md`：重要训练的命令、改动和结果。

不要提交 `*.pt`、`*.onnx`、视频、完整日志或缓存。提交 checkpoint 的绝对路径、大小和 SHA256 即可。

建议提交顺序：

```text
docs: add model-to-URDF and locomotion workflow
feat: add custom quadruped URDF package
feat: add CSDog asset configuration
test: verify 30-second PD standing
feat: add flat velocity locomotion task
exp: record first locomotion training result
```

## 13. 当前应执行的第一批任务

- [ ] 复制并简化 CAD 模型；
- [ ] 确定坐标系和 12 个关节名称；
- [ ] 填写关节映射表；
- [ ] 导出 URDF 和简化 mesh；
- [ ] 运行 URDF 静态检查；
- [ ] 转换 USD 并逐关节检查；
- [ ] 完成 30 秒 PD 站立测试；
- [ ] 站立测试通过后，再创建 Flat locomotion 任务。

当前阶段门：**在 30 秒 PD 站立测试通过以前，不开始 PPO 正式训练。**
