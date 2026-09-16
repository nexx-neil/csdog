# Linux 首次运行流程

## 1. 保持黄金环境不变

```bash
export TERM=xterm-256color
export LC_ALL=C

cd /home/ni/robot_projects/IsaacLab
git status --short
git rev-parse HEAD
```

期望 commit：

```text
37ddf626871758333d6ed89cf64ad702aef127d0
```

不要运行导出项目中的：

```text
scripts/setup_stackforce_isaac_lab_sim_env.sh
```

该脚本会安装或替换 PyTorch、Isaac Sim、Isaac Lab 和 RSL-RL。

## 2. 准备项目

将 `Stackforce-simready-generated_robot-isaac-lab.zip` 解压到：

```text
/home/ni/robot_projects/csdog
```

进入已经验收过的 Conda 环境，然后只安装当前项目：

```bash
cd /home/ni/robot_projects/csdog
python -m pip install -e source/stackforce_simready_generated_robot_lab
python scripts/list_envs.py
```

应能看到：

```text
Template-GeneratedRobot-Direct-v0
```

## 3. 单环境 GUI 测试

```bash
python scripts/zero_agent.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --num_envs 1
```

依次记录：

1. 模型是否为正常尺寸；
2. `+X` 是否朝前，`+Z` 是否朝上；
3. 机器人是否悬空、穿地或爆炸；
4. 12 个关节与腿段是否一一对应；
5. 每个关节的 `+0.1 rad` 和 `-0.1 rad` 方向；
6. 哪些 link 实际接触地面；
7. 正常站立时 base 高度。

## 4. 优先修改配置

文件：

```text
source/stackforce_simready_generated_robot_lab/
  stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/
  generated_robot_env_cfg.py
```

首先校准：

```python
init_state.pos
default_joint_angles
stiffness
damping
effort_limit_sim
velocity_limit_sim
base_height_target
min_base_height
```

每次有效修改同步记录到 `PARAMETERS.md`。

## 5. 30 秒站立门禁

继续使用单环境和零动作。通过条件：

- 连续站立至少 30 秒；
- 没有非足端持续接触；
- 没有高频抖动；
- 关节没有越限；
- 力矩没有长期饱和；
- 无 NaN、PhysX fatal error 或崩溃。

失败时按以下顺序排查：

```text
关节映射和方向
→ 默认站立角
→ 出生高度
→ 质量、质心和惯量
→ collision
→ stiffness / damping
→ 仿真步长
```

## 6. PPO 冒烟测试

站立门禁通过后执行：

```bash
python scripts/rsl_rl/train.py \
  --task Template-GeneratedRobot-Direct-v0 \
  --headless \
  --num_envs 8 \
  --max_iterations 20 \
  --seed 42
```

检查：

- reward 和 observation 无 NaN；
- action space 为 12；
- reset 和 termination 正常；
- 显存稳定；
- 能保存 checkpoint；
- 机器人没有通过趴倒、跳跃或蹭地刷奖励。

通过后才扩大到 64、256 个环境。

## 7. 每次实验结束

```bash
git status --short
git rev-parse HEAD
sha256sum <checkpoint-path>
```

复制 `experiments/TEMPLATE.md`，记录命令、commit、参数改动、结果和下一步，然后更新 `CURRENT.md`。

