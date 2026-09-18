# CSDog 项目交接

更新时间：2026-09-18

本文是新开发者或新 AI 的首要入口。开始工作前同时阅读 `CURRENT.md`、
`PARAMETERS.md` 和最近的实验记录，但以本文和仓库当前源码为准。

## 1. 项目目的

CSDog 是大学课程项目中的自定义四足机器人强化学习系统。最终目标是：

1. 在两台软件栈一致的电脑上分别训练 Dog A 和 Dog B；
2. 底层 locomotion policy 接收 `vx`、`vy`、`yaw_rate`；
3. 高层战斗策略未来接收/输出移动与 `fire` 动作；
4. 将两只机器狗放入同一个 CS 风格对抗场景，开展双智能体对战。

当前阶段只做单狗基础运动。尚未开始战斗场景、射击、视觉策略或 Self-Play。

```text
坐标：X=前，Y=左，Z=上
单位：m, kg, s, rad
底层命令：vx, vy, yaw_rate
未来高层动作：vx, vy, yaw_rate, fire
```

## 2. 固定黄金环境

禁止为解决训练问题而升级依赖。

```text
Ubuntu                 22.04.5 LTS
Kernel                 6.8.0-138-generic
GPU                    NVIDIA GeForce RTX 4060 Laptop GPU, 8188 MiB
NVIDIA Driver          580.178.04
Conda                  /home/ni/miniconda3
Conda env              dogfight
Python                 3.11.16
PyTorch                2.7.0+cu128
torchvision            0.22.0+cu128
PyTorch CUDA Runtime   12.8
Isaac Sim              5.1.0.0
Isaac Lab              v2.3.2
Isaac Lab commit       37ddf626871758333d6ed89cf64ad702aef127d0
RSL-RL                 3.1.2
Display session        Xorg (x11)
```

系统没有安装 `nvcc`，也不需要系统 CUDA Toolkit。`nvidia-smi` 显示 CUDA 13.0
只是驱动支持能力，不是 PyTorch 使用的 runtime。

Conda 环境包含处理 `CXXABI_1.3.15` 的 activation hook。不要删除它，不要替换系统
`libstdc++`，不要执行 `pip install -U`、`conda update --all`、Isaac Lab `main/develop`
或 3.x beta。

## 3. 仓库与本机目录

GitHub：`git@github.com:nexx-neil/csdog.git`

当前机器已于 2026-09-18 完成目录统一：

```text
/home/ni/robot_projects/csdog
    当前唯一的源码和文档 Git 工作区，也是实际运行入口

/home/ni/robot_projects/archive/csdog-runtime-2026-09-17
    2026-09-17 以前的完整训练日志、checkpoint、指标、视频和旧导出包，只作历史归档

/home/ni/robot_projects/csdog/logs
/home/ni/robot_projects/csdog/outputs
/home/ni/robot_projects/csdog/local_artifacts
    指向上述历史归档的本地软链接，均被 Git 忽略

/home/ni/robot_projects/dogfight_env_info
    黄金环境版本快照

/home/ni/robot_projects/dogfight_final_tests
    Isaac Lab 官方任务的环境、checkpoint 和 GUI 验收证据
```

当前有效 `source/`、`scripts/`、文档和精选 JSON 指标均在同一个 Git 仓库中。
新机器应直接将仓库 clone 为 `/home/ni/robot_projects/csdog`，不要重新建立
`csdog-docs` 双目录结构。大体积训练产物不进入普通 Git。

恢复项目包时只执行：

```bash
source /home/ni/miniconda3/etc/profile.d/conda.sh
conda activate dogfight
cd /home/ni/robot_projects/csdog
python -m pip install --no-deps -e source/stackforce_simready_generated_robot_lab
python scripts/list_envs.py
```

不要运行旧导出包中的 `scripts/setup_stackforce_isaac_lab_sim_env.sh`，它会安装或替换
环境依赖。该脚本没有纳入当前源码交付。

## 4. 机器人和任务基线

任务 ID：`Template-GeneratedRobot-Direct-v0`

```text
13 links
12 revolute joints
12-dimensional action
48-dimensional observation
93 STL meshes
URDF total mass = 0.764637 kg（几何估算，待与真实 CAD 核对）
```

有效名义关节角：

```text
FR = (-0.3, 0.9, -1.3)
FL = (+0.3, 0.9, -1.3)
RL = (+0.3, 0.9, -1.3)
RR = (-0.3, 0.9, -1.3)
```

有效高度：

```text
spawn height       = 0.1527 m
base height target = 0.1327 m
minimum height     = 0.08 m
```

已经通过：ROS `check_urdf`、30 秒零动作站立、12 关节映射/方向、Isaac Sim GUI
GPU 渲染、PPO 训练、checkpoint 保存、官方 load/play/resume。站立证据位于：

```text
experiments/results/2026-09-17/nominal_pose_v7_height_threshold_30s.json
```

## 5. 当前训练设计

Policy observation 包含机身线速度、角速度、projected gravity、三维速度命令、关节
位置偏差、关节速度和上一动作。Policy 输出 12 维关节位置偏移：

```text
q_target = q_default + 0.5 * clip(action, -1, 1)
```

命令采样：

- 每个环境/episode 只激活一个速度轴；
- X/Y/Yaw 默认范围均为 `[-0.8, 0.8]`；
- 非零命令最小幅值 0.15；
- 10% 为站立命令；
- `--command_axes` 选择课程阶段允许的轴；
- `--command_limit` 设置启用轴的对称范围。

零命令的 X/Y/Yaw 正 tracking mask 各为 `1/3`，总正奖励上限与单个活动轴相同。
这是为了修复早期“站立同时领取三份 tracking reward”的漏洞。

## 6. 关键实验结论

不要只看训练总 reward。所有候选模型必须使用固定命令、至少 16 个环境、每环境
1000 步做定量验收。

### v12：三轴 resume 候选，未通过

稳定、无跌倒，会部分转向，但前进和横移命令产生近似同一种运动；动作饱和率
78%-83%。它证明 checkpoint 链路可用，但不是真正的统一速度控制策略。

### v13-v15：联合从零训练，均未通过

- v13 证明失败并非只由旧 checkpoint 惯性导致；
- v14 完全取消站立正 tracking 后频繁跌倒；
- v15 将站立 tracking 归一化后存活改善，但 X/Y 基本不响应，主要偏向 yaw。

因此不应继续用“三轴全范围冷启动 + 猜 reward 权重”的方式堆 iteration。

### v16：Y 轴课程

从已证明能横移的 v7b checkpoint resume，只启用 Y 轴训练 200 iterations：

```text
target vy=0.15 -> actual vy=0.024 m/s, saturation=89.7%
target vy=0.50 -> actual vy=0.491 m/s, saturation=82.1%
terminations=0
```

结论：中高速横移存在，但低速有明显死区。

### v17：Y 轴低速课程，当前最新

从 v16 resume，只启用 Y，训练范围缩小为 `[-0.3, 0.3]`：

```text
target vy=0.15 -> actual (vx,vy,yaw)=(-0.014,0.010,0.018)
target vy=0.30 -> actual (vx,vy,yaw)=(-0.128,0.254,0.017)
terminations=0
action saturation=60%-68%
```

动作饱和明显改善，但 0.15 m/s 仍近乎静止，0.30 m/s 有明显负 X 串轴和足端滑动。
Y 单轴门禁仍为 FAIL，因此没有继续加入 X 或 Yaw。

完整数值见 `experiments/results/2026-09-17/` 和
`experiments/2026-09-17_LINUX_BASELINE_AND_PPO_SMOKE.md`。

## 7. 本机 checkpoint

Checkpoint 不在普通 Git 中。不要删除以下本机文件：

```text
v12 /home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_16-26-02_commanded_locomotion_v12_axis_decoupling/model_final.pt
SHA256 9639aed9331389a5218c19a994e533717e7cad90e8673f99bdc7002942edee4a

v16 /home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_18-44-19_commanded_locomotion_v16_stage_y_normalized_reward/model_final.pt
SHA256 ae907a0c284d354c3057736c5217246a25e5435b1c3bdfa6508f8c3b5bf9d428

v17 /home/ni/robot_projects/csdog/logs/rsl_rl/generated_robot/2026-09-17_18-49-00_commanded_locomotion_v17_stage_y_low_speed/model_final.pt
SHA256 023468b434fc6c796c4ba4549135ab4cc1ee8bd5b00bfae6b36ef27d6f0c5a75
```

v16 是当前较好的中高速横移证据；v17 只改善了动作饱和，不是完整 locomotion 模型。

## 8. 下一步计划

严格按以下顺序推进：

1. 先保留 v16/v17，不继续盲目 resume；
2. 解决 Y 单轴的 `0.15 m/s` 低速死区；
3. 同时约束 `vy=0.30` 时的 X 串轴和足端滑动；
4. 优先评估步态相位/足端目标、左右镜像对称约束，或围绕解析步态的 residual policy；
5. 每个方案先通过 `vy=0.15/0.30/0.50` 三档门禁；
6. 然后按 Y -> X+Y -> X+Y+Yaw 的课程逐轴加入；
7. 三轴定量通过后再做 GUI 演示、长训练和跨机 checkpoint 验证；
8. 单狗 locomotion 完成后才开始 Dog A、Dog B 和 battle arena。

可选 ONNX 导出仍报 `too many indices for tensor of dimension 2`。它不影响训练、
checkpoint 或 play；不要为此升级依赖。

## 9. 常用验收命令

先定义 checkpoint，避免长路径被终端换行拆断：

```bash
cd /home/ni/robot_projects/csdog
CHECKPOINT="logs/rsl_rl/generated_robot/2026-09-17_18-49-00_commanded_locomotion_v17_stage_y_low_speed/model_final.pt"
```

定量测试：

```bash
python scripts/rsl_rl/play.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --num_envs 16 \
  --headless \
  --checkpoint "$CHECKPOINT" \
  --num_steps 1000 \
  --command 0 0.30 0 \
  --metrics-output commanded_manual_check.json
```

GUI：

```bash
python scripts/rsl_rl/play.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --num_envs 1 \
  --checkpoint "$CHECKPOINT" \
  --num_steps 3000 \
  --command 0 0.30 0 \
  --follow-robot
```

`--command` 顺序为 `vx vy yaw_rate`。验收至少记录：实际三轴速度、termination、
平均/最低 base 高度、动作饱和率和接触足端滑动速度。

## 10. 禁止事项

- 不安装或升级 NVIDIA Driver、CUDA Toolkit、Python、PyTorch、Isaac Sim、Isaac Lab、RSL-RL；
- 不切换 Isaac Lab main/develop/3.x beta；
- 不删除 Conda activation hook；
- 不修改系统 `libstdc++`；
- 不删除旧 checkpoint、日志或指标；
- 不以“训练能运行”代替固定命令定量验收；
- 不把 GPU 型号、驱动 patch 或 kernel patch 差异误判为 checkpoint 不兼容；
- 不把大型 checkpoint 和完整训练日志直接提交到普通 Git。
