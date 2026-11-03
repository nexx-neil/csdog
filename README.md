# CSDog：运动训练与桌面三狗对战

本分支 `backup/2026-11-03-desktop-playable` 保存 **2026-11-03 Ubuntu 桌面可运行系统快照**。新增内容位于 [`desktop_playable/`](desktop_playable/)，原有运动训练源码、实验记录与历史资产分支保留。`main` 不由本次备份覆盖。

## 最新进度

- **真实模型与 PPO 推理**：三只独立 12 自由度 Articulation 使用经过摘要和 ABI 校验的 `peer_teleop_v1` 模型与同一只读 Actor，各自保留独立策略历史。当前不是三种不同狗模型。
- **键盘对战**：A 狗使用 W/S 前后、A/D 转向、Q/E 转向优先；B 狗使用独立数字小键盘；C 狗默认站立。Space 锁停、C 解除、R 重置、Esc 退出，失焦/输入超时锁停。
- **自主对战**：三狗 FSM、定时情报与视野/遮挡、栅格 A*、速度闭环跟踪、有限卡住恢复；V 切换红/蓝/绿路线与目标/路点标记。
- **物理与裁判**：有碰撞的地图墙体与机器人；CPU PhysX 最近非自身射线命中；枪口起算 3 m 射程，墙体、前方机器人和尸体可遮挡。HP 100、单次伤害 20、冷却 1 s、180 s 比赛上限及死亡/胜负判定。
- **桌面界面**：主相机、HUD、三路第一视角、HP/状态/目标/导航显示。它们是 Isaac 桌面功能；本快照没有业务网页端、浏览器遥控或网页 HUD。

FSM 是规则控制器，PPO 负责运动；尚未实现战斗强化学习、自博弈、SLAM、动态避障或精确物理刹车。停车前漂、转向侧漂、倒地安全暂停及有限恢复仍是已知边界。

## 启动

先按[恢复与验收清单](desktop_playable/github_backup_audit/RESTORE_CHECKLIST.md)恢复冻结环境和官方资产。以下命令不安装或升级依赖，也不启动训练：

```bash
cd desktop_playable/dogfight_rl
export DOGFIGHT_PYTHON="$HOME/miniconda3/envs/dogfight/bin/python"
# 两个入口轮流运行；不要同时启动
./scripts/launch_dogfight_teleop.sh
# 关闭原窗口后再启动自主模式
./scripts/launch_dogfight_fsm.sh
```

启动三狗模式后点击主窗口，按 **C** 开始。Space 暂停，R 重置并锁停。键盘模式 B 狗使用数字小键盘 8/2/4/6，7/9/1/3 组合驾驶，5 停止；字母区与数字小键盘相互独立。单狗兼容入口：

```bash
./scripts/launch_dogfight_teleop.sh --config configs/teleop/single_dog.yaml
```

桌面模板位于 [`scripts/teleop/*.desktop.in`](desktop_playable/dogfight_rl/scripts/teleop/)。安装时将 `@PROJECT_ROOT@` 替换为该机器 `dogfight_rl` 的绝对路径，并设置本机可执行/可信任标记。`DISPLAY`、`XAUTHORITY`、Conda 路径由本机提供，不应照抄审计日志里的会话值。

## 环境与当前策略

|组件|版本/身份|
|---|---|
|Ubuntu / Python|22.04.5 LTS / 3.11.16|
|PyTorch / torchvision|2.7.0+cu128 / 0.22.0+cu128|
|Isaac Sim|5.1.0.0|
|IsaacLab|v2.3.2，`37ddf626871758333d6ed89cf64ad702aef127d0`|
|RSL-RL|3.1.2；桌面入口仅执行 Actor 推理|
|模型|`assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf`|
|权重|`assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt`，2,722,815 字节，iter 1043|
|权重 SHA256|`283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7`|
|策略 ABI|50 观测 → 256 → 256 → 128 → 12 动作，ELU，无观测归一化|

完整模型/策略身份由 `IMPORT_MANIFEST.json`、`policies/v1/identity.json` 和 `configs/robots/dog_a_teleop.yaml` 约束。不要混用其他训练 checkpoint 或按“同为 12DOF”替换。IsaacLab 的 Git tag 与 Python distribution 版本号不是同一个编号。

## 验证范围与恢复限制

历史 GUI 证据保留在 [`20261103_164416_cec1d1f6`](desktop_playable/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/)：31.52 比赛秒 dog_b 以 80 HP 获胜，三狗均执行独立 PPO 步进，15 次发射、11 次伤害、2 次死亡；路线显示/隐藏及清理记录见该目录 JSON 与截图。这是原机历史证据，不是新机器验收。

本次备份的文件校验、独立路径策略加载与轻量回归结果见[发布验证记录](docs/desktop_playable/PUBLISH_VALIDATION.md)。本轮不重启现有 Isaac 窗口、不进行训练；新机 GUI、全部外围墙方向、完整 180 秒超时、长时多轮可靠性及断网恢复均不能据此宣称通过。

地图墙体由代码生成，**地面仍依赖 NVIDIA 官方在线 USD、3 张贴图和 SDK MDL**。SDK、Conda、驱动、官方离线场景包和约 39 GiB 历史训练/归档不包含在此轻量快照。离线自足性尚未验收；第三方模型/权重来源与再分发许可状态见[备份审计](desktop_playable/github_backup_audit/GITHUB_BACKUP_PLAN.md)，本分支不额外授予第三方资源许可。

## 目录与历史

|路径|用途|
|---|---|
|[`desktop_playable/dogfight_rl/`](desktop_playable/dogfight_rl/)|桌面启动器、唯一 src 源码布局、配置、当前模型/策略、测试与精选验收证据|
|[`desktop_playable/model/`](desktop_playable/model/)|原始设计模型；桌面运行实际使用上面的 robot_sim.urdf|
|[`desktop_playable/github_backup_audit/`](desktop_playable/github_backup_audit/)|依赖、上传清单、远端对比、备份方案与恢复清单；均为审计当时的记录|
|[`docs/desktop_playable/SOURCE_COPY_MANIFEST.json`](docs/desktop_playable/SOURCE_COPY_MANIFEST.json)|源文件到快照路径映射与复制 SHA256|
|[`source/`](source/)、[`scripts/`](scripts/)、[`experiments/`](experiments/)|原 main 的运动训练工程与历史实验，原路径保留|
|[`HISTORICAL_MAIN_README.md`](docs/desktop_playable/HISTORICAL_MAIN_README.md)|更新前的 main README 原文|

更早的遥控完整资产包仍位于历史分支 [`csdog-v2-teleop-v0.1.0-assets`](https://github.com/nexx-neil/csdog/tree/csdog-v2-teleop-v0.1.0-assets)。它保存了当前权重来源，但不能替代本次新增的三狗系统快照。
