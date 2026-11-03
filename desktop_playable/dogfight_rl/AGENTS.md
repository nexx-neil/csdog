# ENVIRONMENT IMMUTABILITY

This project uses a frozen robotics RL production environment named `dogfight`.

## DO NOT

- Upgrade Python, PyTorch, torchvision, Isaac Sim, Isaac Lab, or RSL-RL.
- Change the CUDA runtime or reinstall the NVIDIA driver.
- Run `conda update --all`, `conda upgrade --all`, or `pip install -U` on core dependencies.
- Run `git pull`, switch branches, merge, or rebase inside `~/robot_projects/IsaacLab`.
- Attempt to fix the known FastAPI / Starlette metadata conflict without a real related runtime error.

## Golden environment

- Python 3.11.16
- PyTorch 2.7.0+cu128
- Torchvision 0.22.0+cu128
- Isaac Sim 5.1.0.0
- Isaac Lab v2.3.2
- Isaac Lab commit `37ddf626871758333d6ed89cf64ad702aef127d0`
- RSL-RL 3.1.2

If a new dependency is needed, do not install it immediately. Explain why it is needed, check conflicts with the frozen environment, obtain user approval, and preferably test it in a separate `dogfight_test` or `dogfight_dev` Conda environment first. Never modify the golden environment silently.


# 当前工程约定

先阅读 PROJECT_STRUCTURE.md 与 dogfight_rl/AGENTS.md。当前正式项目为 `/home/zxq/robot_projects/dogfight_rl`，唯一 Python 权威源码在 `src/dogfight` 与 `src/dogfight_v0`。不能重新创建 01_robots/02_training/03_battle、根层 dogfight/source 等兼容源码树，禁止用新软链接、硬链接或复制源码维持旧路径。

新模型原件唯一位置为 `model/`（robot.urdf、robot.preview.urdf、STL、package.xml）；原始几何、质量和惯量字节不可直接修改。转换产物仅放 `dogfight_rl/assets/csdog_12dof/`。不能因同为12自由度而套用旧关节、PD、站姿、朝向或 checkpoint。新模型已转换USD并建立独立任务 Dogfight-CSDog-Velocity-Flat-v0；物理与短程实验见 dogfight_rl/runs/locomotion/csdog_ppo_20261026/reports/TRAINING_EXPERIMENT_REPORT.md。

三代理对战核心为 `dogfight_rl/src/dogfight_v0/`。保留 ProxyAgent 基线、BattleManager、Agent/Locomotion、地图/导航、规则、射击/HP/胜负、HUD/日志；dog_a/b/c 是代理ID，不等于使用旧 Dog A 本体。新模型适配器须独立实现，真实三本体与战斗RL目前未完成。

归档位于 `archive/`：legacy_dog_a 是旧模型完整成果；legacy_compatibility 是停用实体副本；historical_validation 是历史验收；environment_records 是历史冻结证据；migration_backups 是旧备份/迁移资料。禁止直接改写历史成果或运行旧迁移脚本。path_migration/20261025 是用户主动删除的废弃证据，不恢复、不伪造；当前 integrity 使用 reorganization/20261026 的真实清单。

新输出仅写 `dogfight_rl/runs/{locomotion,battle,validation}` 的独立 run，不覆盖任何历史权重。保护/回滚清单、原文备份在 `reorganization/20261026/`，先运行 rollback.py 预览并检查后续编辑再 apply。Git 包含历史未提交/未跟踪内容，不得 reset --hard 或 clean。

IsaacLab、Conda、CUDA、驱动与 Isaac Sim 安装均禁止移动/升级/重装；不改 IsaacLab 第三方源码。冻结解释器 /home/zxq/miniconda3/envs/dogfight/bin/python；IsaacLab v2.3.2 / 37ddf626871758333d6ed89cf64ad702aef127d0；RSL-RL 3.1.2、Isaac Sim 5.1.0.0、Python 3.11.16、torch 2.7.0+cu128。已知 FastAPI/Starlette 元数据冲突保留，不能为此升级环境。

正式入口 `python dogfight_rl/launch.py`：test、integrity、check-environment、battle、battle-smoke、battle-gui、hud-smoke、training-tools-check、train、evaluate、legacy-info、test-legacy。train/evaluate 已接入新任务，必须显式指定迭代数/独立run或checkpoint。当前短程预算已耗尽，不得自动继续训练。禁止长训练。GUI/物理/训练结果必须按实际执行证据报告，不能把静态导入或历史PASS当本次验证。

项目内普通包采用 src 布局；启动脚本显式添加 src，不把 archive 加入默认 PYTHONPATH。路径接口用 dogfight.common.paths；读取当前YAML用 load_project_yaml，拒绝01/02/03旧布局资源。不要再次安装/复制PPO库，沿用冻结环境。训练工具的运行时导入应在AppLauncher之后，普通导入不启动仿真。
