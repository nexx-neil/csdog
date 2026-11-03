# Dogfight RL 桌面快照（2026-11-03）

本目录包含真实 PPO 三狗键盘对战与 FSM 自主对战。源码位于 `src/dogfight` 与 `src/dogfight_v0`；当前策略/模型位于 `assets/csdog_12dof/peer_teleop_v1`。`launch.py battle` 仍是历史 Proxy 基线，真实桌面入口是 `teleop` 与 `fsm_battle`。

```bash
export DOGFIGHT_PYTHON="$HOME/miniconda3/envs/dogfight/bin/python"
./scripts/launch_dogfight_teleop.sh
# 退出后另启
./scripts/launch_dogfight_fsm.sh
```

三狗入口要求 CPU PhysX，RTX 渲染仍使用 GPU。启动锁停，C 开始，Space 暂停，R 重置，Esc 退出，FSM 模式 V 切换路线。PPO 零命令仍可能漂移。

完整最新进度、环境、操作与验证范围见[仓库 README](../../README.md)及[恢复清单](../github_backup_audit/RESTORE_CHECKLIST.md)。这里的精选 runs 是历史证据；完整训练记录、归档、环境安装和官方地面离线资产需单独备份。整库历史 integrity/训练评估需要未随轻量快照提供的历史数据，不保证本快照可运行所有历史开发工具。

本快照保留早期 AGENTS/PROJECT_STRUCTURE 等原文用于溯源，其中“真实三本体未完成”等描述早于 11 月 3 日桌面功能，应结合最新 README、交付文档和实际源码理解。战斗 RL、自博弈、网页端尚无实现证据。不要安装/升级黄金环境或自动启动训练。
