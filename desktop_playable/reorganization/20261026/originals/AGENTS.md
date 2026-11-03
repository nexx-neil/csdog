# 机器人项目工作约定

统一工作区根目录为 `/home/zxq/robot_projects`。Dogfight 工程根目录为其下的 `dogfight_rl`；代码必须按自身文件位置定位根目录，不能依赖当前工作目录或 Home 下的旧兼容入口。Dogfight 的细则还见 `dogfight_rl/AGENTS.md`。

## 目录和资源

- `dogfight_rl/01_robots`：Dog A 原始 CAD/URDF、转换 USD、对称模型、Mesh、本体配置和本体测试。原始资源在 `assets/original/fix_new.SLDASM`；常用训练资产在 `assets/dog_a/usd_attempt_002_named_joints/dog_a.usd`；对称版本在 `assets/dog_a_symmetric_v1`。
- `dogfight_rl/02_training`：训练、评估、部署和历史成果。PPO 入口在 `python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/{train,validate,evaluate}.py`，配置在 `configs`，checkpoint 和 TensorBoard 日志实际在 `logs`（不是 `02_training/02_training/logs`）。默认恢复权重为 `logs/back_gait_primitive_recovery/model_final.pt`。`checkpoints` 是占位/分类目录，不代表所有历史权重的位置。
- `dogfight_rl/03_battle`：对战逻辑、场地、代理和 HUD；`source/dogfight_v0` 是独立包目录。
- `model`：另一套本地 URDF 和 13 个碰撞 Mesh；`robot.urdf` 使用文件相对路径，`robot.preview.urdf` 使用 `package://csdog_urdf`，ROS 使用时将工作区根目录加入资源搜索路径。
- `IsaacLab`：共享第三方软件仓库，虽然在本工作区内，仍按冻结软件依赖管理，不随机器人业务代码改动。Git 标签 `v2.3.2`，commit `37ddf626871758333d6ed89cf64ad702aef127d0`；安装分发版本 `isaaclab 0.54.2` 与仓库标签是不同的版本字段。
- `dogfight_env_freeze`：冻结环境清单、只读检查器、通用 IsaacLab 训练启动器和 Git bundle。`docs/environment/freeze_snapshot` 是历史快照，不用于重新配置当前系统。
- 根目录 `dogfight_env_info`、`DOGFIGHT_ENVIRONMENT.md`、`dogfight_final_tests` 是实体副本。`fix_new.SLDASM` 和 `fix_new.SLDASM.zip` 也曾完成实体化及哈希校验，但最终复核时被用户同期整理移出根目录；规范原件仍在 `dogfight_rl/01_robots/assets/original`。开发以规范位置为准，根目录副本不自动同步。
- `path_migration/20261025`：本次迁移的逐文件哈希、原代码备份、链接清单、完整扫描和测试证据。旧 `dogfight_rl/migration` 保留此前的迁移记录、备份和 checkpoint 清单；这些历史迁移脚本不能作为日常启动器再次执行。

## 路径和模型解析

使用 `dogfight_rl/shared/paths.py` 中的 `ROOT`、`ASSETS`、`LOGS`、`CHECKPOINTS`、`ISAACLAB`、`project_path`。配置内以 `01_robots/`、`02_training/`、`03_battle/` 开头的值相对 Dogfight 工程根目录，读取必须使用 `load_project_yaml`；仅用普通 `yaml.safe_load` 的外部消费程序需自行解析这些相对值。其他字符串、系统绝对路径和 URL 保留原义。

Shell 入口通过脚本自身位置向上查找 `shared/paths.py`，可从任意工作目录调用规范入口或兼容实体入口。当前文件系统中 87 个原有 symlink 已全部实体化，剩余 0 个。旧 `logs`、`assets`、`configs`、`scripts`、`source`、`dogfight` 子目录现在是物理兼容快照，不会自动同步；日常开发只修改分类目录中的规范文件。`dogfight/__init__.py` 通过标准 Python 包搜索路径将日常导入指向三个分类目录，避免维护多套活动 Python 模块。新训练日志以 `02_training/logs` 为准，根层 `logs` 不再自动显示新实验。

URDF 的 `package://fix_new.SLDASM` 映射到 `dogfight_rl/01_robots/assets/original/fix_new.SLDASM`；`package://csdog_urdf` 映射到 `model`。保留原模型字节，不能全局替换 URI。USD 的相对 sublayer/reference 按 USD 层解析。`OmniPBR.mdl` 来自 Isaac Sim 的内置 MDL 库，是共享软件依赖，不复制到模型目录。

## 实测环境和冻结要求（2026-10-25）

Ubuntu 22.04.5 LTS，内核 6.8.0-138-generic；GPU RTX 4070 Laptop 8188 MiB，驱动 580.178.04。冻结解释器 `/home/zxq/miniconda3/envs/dogfight/bin/python`：Python 3.11.16，torch 2.7.0+cu128，torchvision 0.22.0+cu128，Isaac Sim 5.1.0.0，RSL-RL 3.1.2。CUDA runtime 12.8；这里不据此推断系统 CUDA Toolkit 版本。

不升级/重装 Python、PyTorch、CUDA、驱动或 Isaac 软件，不更改共享 IsaacLab 的 Git 状态。可用 `DOGFIGHT_PYTHON` 指定已有解释器、`DOGFIGHT_ISAACLAB` 指定已有软件仓库；不得静默修改 Conda 环境。IsaacLab 采用 editable 安装，环境内的映射仍指向当前仓库；如未来移动整个工作区，需要另行规划环境映射，当前工程资源独立不等于解释器和共享安装可直接搬迁。

## 已执行验证和复用命令

在 `dogfight_rl` 中执行（统一入口也支持绝对路径从任意目录调用）：

```bash
python launch.py test
python launch.py integrity
python launch.py check-environment
python launch.py train-a --dry-run --num-envs 2 --max-iterations 1
# 实际 smoke：每次使用尚不存在的新输出目录，绝不能覆盖历史权重
python launch.py train-a --num-envs 2 --max-iterations 1 --output-dir 02_training/logs/new_runs/UNIQUE_NAME
python launch.py validate-a --help
```

本次最终实测 33 项 pytest、50 个修改过的 Python/Shell 文件语法、88 处配置资源路径、7 个 URDF 的 182 处 Mesh 引用和 30 个 USD 层。全部内部链接实体化后，再次完成 2 环境、1 次 PPO 更新，默认历史 checkpoint 恢复成功。两次 smoke 的产物分别在 `02_training/logs/path_migration_20261025_smoke` 和 `02_training/logs/path_migration_20261025_physical_smoke`；详细遥测在对应目录 `telemetry.json`。历史 530 个 checkpoint 哈希仍与原清单一致。

GUI 渲染、真实硬件、长训练、全部历史实验重跑没有验证。Dog B 无模型、Dog C 只有远程报告，不可宣称它们可训练。FastAPI / Starlette 的已知元数据冲突按冻结规则保留。缓存、编译产物、历史日志、旧源文件和 Git 历史均不得擅自删除。
