# 正式项目目录说明

2026-10-26 整理后。先读根 AGENTS.md、dogfight_rl/AGENTS.md；审计事实仍见 PROJECT_STRUCTURE_AUDIT.md，本次实际变化见 REORGANIZATION_REPORT.md。

```text
robot_projects/
├── IsaacLab/                         # 冻结第三方，位置和源码不变
├── model/                            # 新 csdog_12dof 原始资产唯一权威位置
│   ├── robot.urdf / robot.preview.urdf
│   ├── meshes/                       # 13个STL，几何/惯量原字节保留
│   └── package.xml
├── dogfight_rl/                       # 唯一正式业务工程，原 .git 保留
│   ├── src/
│   │   ├── dogfight/
│   │   │   ├── robots/csdog_12dof.py  # 原始资产身份/路径，无PD或训练环境
│   │   │   ├── common/paths.py       # 统一路径和当前YAML资源解析
│   │   │   ├── locomotion/             # 新12DOF独立ManagerBased速度任务
│   │   │   └── training/             # PPO桥接、奖励核、动作审计、actor、run与遥测
│   │   └── dogfight_v0/
│   │       ├── agents/               # Agent/Locomotion、Proxy、显式参数化真实本体接口
│   │       ├── arena/                # 地图、出生点
│   │       ├── battle/               # 规则/射击/HP/胜负/情报/可见性/策略
│   │       ├── navigation/           # 速度命令导航
│   │       ├── sim/                  # 三Proxy同场景、PhysX射线
│   │       ├── ui/                   # HUD
│   │       ├── logging/              # 独立run事件日志
│   │       └── config/battle_cfg.py  # 唯一规则配置类，保留Proxy尺寸默认值
│   ├── configs/
│   │   ├── robots/csdog_12dof.yaml   # 仅原始资产元数据；无站姿/增益/策略
│   │   └── battle/extension.toml     # Isaac扩展元数据，指向src
│   ├── assets/csdog_12dof/           # 新模型USD与完整转换闭包
│   ├── scripts/{train,evaluate}/csdog_12dof.py
│   ├── scripts/battle/               # 唯一维护的Proxy/GUI/smoke脚本
│   ├── scripts/diagnostics/          # 环境/完整性/训练工具验证
│   ├── tests/                        # 正式轻量回归
│   ├── runs/{locomotion,battle,validation}/
│   ├── docs/                         # 当前说明与通用接口规格
│   ├── launch.py                     # 唯一正式启动入口
│   ├── pyproject.toml / setup.py     # src包布局，未重装依赖
│   └── .git/                         # 未删、未reset、未自动提交
├── archive/
│   ├── legacy_dog_a/
│   │   ├── assets/                   # 旧CAD/URDF/USD/Mesh与完整子层
│   │   ├── configs/{robots,training}/
│   │   ├── training_code/            # 旧环境/训练/部署/本体/适配器
│   │   ├── checkpoints_and_runs/     # 成套旧训练成果
│   │   └── diagnostics/             # 旧mock、真实A脚本与模型诊断报告
│   ├── legacy_compatibility/         # 以前已有实体副本，已停用/不维护
│   ├── historical_validation/        # ANYmal/历史对战验收/旧项目文档
│   ├── environment_records/          # 冻结清单、bundle和历史环境报告
│   └── migration_backups/            # 以前迁移资料和大型tar备份
├── reorganization/20261026/          # 本次映射、SHA、原文保护、检查日志与回滚
├── AGENTS.md
├── DOGFIGHT_ENVIRONMENT.md
├── 格式规范.md                       # 原V0接口规格，非普通排版指南
├── PROJECT_STRUCTURE_AUDIT.md         # 原审计报告，不改写历史结论
├── REORGANIZATION_MANIFEST.md
└── REORGANIZATION_REPORT.md
```

未创建没有实现内容的 locomotion/sim 通用空包或大量配置占位。当前 `dogfight_v0/sim` 负责现有仿真，`dogfight/training` 只提供复用工具；新 locomotion 环境后续应独立实现。Python模块只有一个正式源码位置；archive中的同名历史文件不加入默认导入路径。

正式命令可从任意工作目录调用：

```bash
python /home/zxq/robot_projects/dogfight_rl/launch.py test
python /home/zxq/robot_projects/dogfight_rl/launch.py integrity
python /home/zxq/robot_projects/dogfight_rl/launch.py check-environment
python /home/zxq/robot_projects/dogfight_rl/launch.py battle --duration 10
python /home/zxq/robot_projects/dogfight_rl/launch.py battle-smoke
python /home/zxq/robot_projects/dogfight_rl/launch.py training-tools-check
python /home/zxq/robot_projects/dogfight_rl/launch.py train
python /home/zxq/robot_projects/dogfight_rl/launch.py evaluate
python /home/zxq/robot_projects/dogfight_rl/launch.py legacy-info
python /home/zxq/robot_projects/dogfight_rl/launch.py test-legacy
```

`train`、`evaluate`、`play` 已接入新模型独立任务；当前短程训练结果与命令见 dogfight_rl/docs/LOCOMOTION_PPO.md。不得恢复旧 Dog A checkpoint 来伪装新模型训练。训练算法仍使用冻结环境的 RSL-RL/PPO，不复制/重装算法库。`battle` 是三Proxy规则基线，三真实本体、战斗RL、自博弈尚未实现。

历史脚本中的旧路径保留为证据，不保证直接复现；使用 reorganization/20261026/manifest.json 的 old/new 查找现位置。禁止新建软链接、硬链接、第二套正式源码或旧路径伪装入口。当前完整性不依赖已废弃的 path_migration；回滚预览用 `python -B reorganization/20261026/rollback.py`。

## 新模型运动训练（本次新增）

权威源码 `dogfight_rl/src/dogfight/locomotion/`；独立配置 `dogfight_rl/configs/locomotion/csdog_ppo/`；转换USD `dogfight_rl/assets/csdog_12dof/import_v1/`。旧正文为整理完成当时状态；最新接入与实际短程结果见 `dogfight_rl/docs/LOCOMOTION_PPO.md`，train/evaluate/play已实现，不再是占位报错入口。当前实验已达到300次总预算，禁止继续自动训练。旧模型与对战代码未修改。
