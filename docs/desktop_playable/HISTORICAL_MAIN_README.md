# CSDog

CSDog 是一个基于 Isaac Lab 和 RSL-RL 的自定义四足机器人强化学习项目。

当前阶段目标：在黄金环境中完成自定义模型标定、PD 稳定站立和基础速度跟踪训练。双狗对战、视觉策略和 Self-Play 暂不属于当前阶段。

## 开始工作

每次开始前依次阅读：

1. [`HANDOFF.md`](HANDOFF.md)：给新开发者或新 AI 的完整交接入口；
2. [`CURRENT.md`](CURRENT.md)：目前做到哪里、下一步做什么；
3. [`docs/LINUX_FIRST_RUN.md`](docs/LINUX_FIRST_RUN.md)：Linux 首次部署与测试顺序；
4. [`PARAMETERS.md`](PARAMETERS.md)：当前有效参数及修改历史；
5. [`docs/MODEL_VALIDATION.md`](docs/MODEL_VALIDATION.md)：模型包静态检查结果和已知风险。

完整执行手册见 [`docs/MODEL_TO_URDF_AND_LOCOMOTION.md`](docs/MODEL_TO_URDF_AND_LOCOMOTION.md)。

## 在 Linux 获取和恢复进度

首次使用：

```bash
cd /home/ni/robot_projects
git clone git@github.com:nexx-neil/csdog.git
cd csdog
cat HANDOFF.md
```

以后每次开始工作：

```bash
cd /home/ni/robot_projects/csdog
git pull --rebase
cat HANDOFF.md
```

完成一次有效调试或训练后：

```bash
cp experiments/TEMPLATE.md experiments/YYYY-MM-DD-实验名称.md
# 填写实验记录，并同步更新 CURRENT.md 和 PARAMETERS.md
git add CURRENT.md PARAMETERS.md experiments/
git commit -m "记录：本次实验结论"
git push
```

私有仓库首次在 Linux 访问时，需要使用 GitHub CLI 登录，或为 HTTPS 配置 Personal Access Token；不要把 token 写入仓库文件。

## 固定环境

```text
Ubuntu                 22.04.5 LTS
Python                 3.11.16
PyTorch                2.7.0+cu128
Isaac Sim              5.1.0.0
Isaac Lab              2.3.2
Isaac Lab commit       37ddf626871758333d6ed89cf64ad702aef127d0
RSL-RL                 3.1.2
GPU                    RTX 4060 Laptop 8 GB
```

未经明确确认，不升级驱动、CUDA、PyTorch、Isaac Sim、Isaac Lab 或 RSL-RL，不运行导出包内的环境重装脚本。

## 日常记录规则

- 当前状态只更新 `CURRENT.md`；
- 当前有效参数及每次重要改动写入 `PARAMETERS.md`；
- 每次重要训练复制 `experiments/TEMPLATE.md` 创建一份记录；
- checkpoint、视频和完整日志保存在 Linux，不提交普通 Git；
- 实验记录中保存 checkpoint 路径、SHA256 和对应 Git commit。

## 仓库内容

- `source/`：当前有效的 Isaac Lab extension、URDF 和 STL；
- `scripts/`：训练、推理与模型诊断脚本；
- `experiments/results/`：精选的小型 JSON 定量指标；
- `assets/`：早期原始导出压缩包，仅用于追溯，不代表当前有效源码；
- `logs/`：本机训练输出，不进入普通 Git。
