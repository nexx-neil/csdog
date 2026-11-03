# 项目目录整理执行报告

整理日期：2026-10-26，工作区 `/home/zxq/robot_projects`。已实际完成同盘目录重构和新旧隔离，未删除模型、权重、训练数据、备份或 Git。没有创建软链接/硬链接，没有修改 IsaacLab 源码、Conda、CUDA/驱动或安装依赖，没有训练或USD转换。

## 整理前与整理后

整理前：`dogfight_rl/01_robots`、`02_training`、`03_battle` 是当时权威源码，根层 `dogfight/source/scripts/assets/configs/logs` 是已有实体副本；`shared`、包路径改写和脚本 bootstrap 共同维持导入。根层另有环境冻结和验收资料。原详细树完整保留于 [审计报告](PROJECT_STRUCTURE_AUDIT.md)。

整理后：正式业务源码只有 `dogfight_rl/src/dogfight` 与 `dogfight_rl/src/dogfight_v0`；新模型原件只有 `model`；旧模型、兼容副本、历史验收、冻结记录和旧迁移备份分别归入 `archive` 五类。实际目录树和命令见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)。未为了目录形式创建空的训练环境或配置包。

## 实际移动与保护

- 迁移清单覆盖 3,783 个原始普通文件（不包括从未移动/修改的第三方 IsaacLab 和 Git 对象），包含未跟踪源码、日志和权重。
- 共 150 个文件/目录移动操作，涉及 3,726 个文件路径变更。使用同文件系统 `os.rename`，全部移动原始字节验收通过；没有复制752MiB日志或大型tar。
- 每个文件的原路径、新路径、迁移前字节数、SHA256、设备/inode 在 [manifest.json](reorganization/20261026/manifest.json)；逐文件易读表为 [file_mapping.csv](reorganization/20261026/file_mapping.csv)，分组说明见 [迁移清单](REORGANIZATION_MANIFEST.md)。实际顺序见 moves_done.json。
- 改写源码/配置/文档前按需保存原文至 `reorganization/20261026/originals`，约484KiB（非2.6GB全项目复制）。changes.json 逐项记录备份、修改前后摘要；created.json 记录新增文件。
- Git原有大量修改/未跟踪内容；初始状态及完整二进制diff已保存为 git_status_before.txt / git_diff_before.patch，HEAD保持 d94aba28e9de91842a972885e93c236c7c5d39cc。未自动提交/暂存，不reset/clean，.git原位置保留。
- 回滚工具 `python -B reorganization/20261026/rollback.py` 预检为 READY；显式 `--apply` 才反序恢复。它先核验哈希、拒绝后续编辑，新增文件先移动到回滚保留目录，不删除新run；本次没有执行最终回滚。首次移动阶段的同名目录顺序问题已整阶段反序恢复后修正，记录在 stage_note.txt。

## 正式代码与旧模型分离

| 当前正式位置 | 复用与边界 |
|---|---|
| `src/dogfight/common/paths.py` | 从shared迁出并重写当前布局解析；明确拒绝旧01/02/03资源路径 |
| `src/dogfight/robots/csdog_12dof.py`、`configs/robots/csdog_12dof.yaml` | 仅新模型原件身份/路径，声明关节顺序不当作运行时动作顺序；没有PD或策略 |
| `src/dogfight/training/reward_terms.py` | 原通用张量奖励核，未直接套旧奖励权重/几何 |
| `src/dogfight/training/action_audit_wrapper.py` | 保留RSL-RL动作缩放、截断前记录和审计回调 |
| `src/dogfight/training/ppo.py` | 从旧train提取PPO配置和显式environment的runner构造；算法仍来自已安装RSL-RL |
| `src/dogfight/training/deployment.py` | 提取actor重建，观测/动作维度必须显式提供；低层工具不创建环境，不推定模型兼容 |
| `src/dogfight/training/checkpoints.py`、`telemetry.py` | run来源/配置哈希、模型与观测动作语义校验；提取GPU内存采样 |
| `src/dogfight_v0` | 完整保留BattleManager、Agent/Locomotion、Proxy、规则策略、射击/HP/胜负、地图/导航、UI/日志、场景和射线 |
| `scripts/battle`、`scripts/diagnostics`、`tests` | 唯一正式入口与当前验收 |

旧 `env.py`、任务绑定 train/evaluate/validate、旧部署器、模型几何、站姿/PD、旧脚本和权重均已归档。旧Train中通用PPO配置/GPU采样改为引用提取模块；奖励核/动作审计没有制造第二套正式副本。旧 TrainingSafetyMonitor 依赖旧任务指标，保持历史实现。

`dog_a_factory.py`、`dog_a_locomotion_adapter.py`、旧 `real_dog_agent.py` 归入 `archive/legacy_dog_a/training_code/battle_adapters`。正式 RealDogAgent 由通用边界提取，必须显式提供 agent_id、prim_path、朝向偏移、复位高度，移除了默认Dog A身份/-π/2朝向/旧站姿高度。真实多本体统一物理推进仍待独立实现，不能把三个旧单体environment.step直接拼装。

## 归档与可追溯性

- `legacy_dog_a/assets`：原CAD/zip/URDF/Mesh、首次/命名关节USD、对称分支及全部相对子层原字节保留。
- `legacy_dog_a/configs`：旧关节站姿、PD/执行器、17份训练配置及动作/奖励参数。
- `legacy_dog_a/checkpoints_and_runs`：旧模型完整实验、权重、配置快照、遥测、TensorBoard、视频/图像；没有仅保留孤立pt或丢弃失败实验。
- `legacy_compatibility`：以前已有实体源码/资产/日志副本、旧占位目录与缓存；已退出正式导入路径，明确不再维护。
- `historical_validation`：官方ANYmal资料、历史对战日志、旧项目验收/文档。训练日志中的 external_home/external_isaaclab 单独归类，未误标为Dog A。
- `environment_records`：根冻结包/版本清单、docs中的冻结副本/环境资料和远程Dog C报告，保留bundle和各版本脚本。
- `migration_backups/previous_migration`：完整保留旧迁移清单、checkpoint索引、报告、工具与大型tar。历史脚本标为归档，不作为当前完整性工具。

[checkpoint_index.json](reorganization/20261026/checkpoint_index.json) 索引本轮范围内 1,069 个权重/导出文件（含归档实体副本），保留迁移前后路径与摘要；IsaacLab原位置官方文件未计入此索引。代表BACK权重、对应配置/48观测/12动作定义、缩放0.50与来源说明见 [旧模型README](archive/legacy_dog_a/README.md)。旧配置与实验内容作为历史证据原样保留，旧命令不保证直接执行。

因依赖/边界继续原位保留：`IsaacLab/logs` 与 `IsaacLab/outputs` 是冻结第三方仓库中的官方验证输出，本次不移动整个仓库或修改第三方工作树；Conda和安装映射也原位保留。没有因未知引用而继续留两套活动业务源码。历史脚本复现阻塞是旧布局查找/资源路径/provider，需要显式修订配置和独立入口，不通过重建兼容目录解决。

## 路径、包元数据和入口

Python导入/PYTHONPATH统一指向src；正式库移除了旧sys.path改写，脚本按自身位置查找新路径；测试也只搜src。包元数据从旧嵌套目录移至根 pyproject.toml/setup.py，setuptools采用src发现，未重新安装。Isaac扩展 `configs/battle/extension.toml` 指向 `../../src`，README路径修复；独立扩展在Kit扩展管理器的启用尚未验收。

当前YAML解析支持model/assets/configs/runs，旧01/02/03路径明确报错。原始模型URDF不改，package URI通过显式模型包映射检查；USD相对子层随资产闭包原样移动。历史转换config里的旧绝对导入路径保持来源证据，不能作为当前转换配置直接使用。活动Shell环境检查入口已修复，新日志统一runs/battle，使用独立UUID目录并拒绝覆盖。

`launch.py train/evaluate` 为新模型独立入口，当前报未实现/退出2；不加载旧checkpoint，不借旧48/12语义冒充新模型支持。旧train-a/validate-a/gui-a明确拒绝；legacy-info展示归档与复现条件，test-legacy只运行历史mock。`battle`仍为三Proxy；默认无旧模型恢复。

逐项改写前后摘要及原文位置见 [changes.json](reorganization/20261026/changes.json)。当前指南已更新；历史文档已移出当前docs，历史路径通过manifest查询，不无差别改写历史日志/配置。

## 测试与验收证据

| 验证 | 本次结果与证据 |
|---|---|
| 迁移前轻量基线 | 33 PASS；baseline_isolated_pytest.log |
| 整理后正式轻量回归 | 35 PASS；final_pytest.log。包括规则、Proxy、HUD、新路径、旧入口拒绝、策略维度/身份、显式真实agent边界 |
| 归档旧Dog A接口mock | 9 PASS；legacy_mock_pytest.log，未替代真实旧模型物理测试 |
| Isaac三Proxy物理smoke | 15/15 PASS；isaac_battle_smoke.log；新run见 dogfight_rl/runs/battle/v0/*/smoke_summary.json |
| 冻结环境 | PASS；environment_check.log；IsaacLab Git工作树仍clean |
| 训练工具运行时 | PASS；training_runtime_validation_final.log。wrapper导入、PPO配置、显式旧actor加载通过；0次训练更新 |
| USD资产闭包 | 三套根USD、15个依赖层；内部缺失0。Sdf未直接解析的OmniPBR.mdl已在Isaac Sim内置MDL库确认存在，未复制/删除材质 |
| 语法与资源静态核验 | 71个Python、2个Shell；182处URDF Mesh引用有效；3,783个原始文件/修订链校验通过；static_validation.json |
| 当前integrity | PASS；integrity_initial.json，最终复核见 integrity_final.json。核验实际本轮基线、原文备份、修订摘要、新增正式文件封存和原始新模型资源；0软链接、0正式源码硬链接 |
| 回滚预检 | READY；rollback_preview.json。未对正式工程执行--apply |

迁移前直接pytest曾被Shell带入的ROS插件阻断（缺lark），见 baseline_pytest.log；使用项目级 PYTEST_DISABLE_PLUGIN_AUTOLOAD 与唯一src/PYTHONPATH隔离后通过，无安装或环境变更。第一轮迁移后4项旧路径测试失败，原因是它们明确要求恢复旧兼容目录/导入旧环境；已经替换为对应新契约断言，不删除对战/模型安全断言。第一次训练工具验证日志未flush结果输出，已修正flush并重跑取得明确PASS记录。

尚未验收：GUI人工视觉、Kit扩展管理器启用、新模型USD转换/物理仿真、长训练、真实硬件、三真实本体与战斗RL。HUD纯状态测试通过不等于GUI视觉验收。历史转向门禁失败依然是旧策略限制，未改成PASS。

`path_migration/20261025` 是用户主动删除；未创建、未恢复、未伪造。旧验证器原件仍在归档，当前完整性使用新的真实基线和修改保护链，不能把历史迁移证据缺失描述成“旧迁移验证通过”。当前checker明确返回 RETIRED 的历史状态而实际核验本轮所有原始文件。

## 去重建议（未执行删除）

逐文件当前SHA256复核得到 1,347 组候选，理论冗余 **988,584,510 字节（942.79 MiB）**。完整保留候选/删除候选/哈希/大小在 [deduplication_candidates.json](reorganization/20261026/deduplication_candidates.json)。仅限归档兼容副本、权重路径副本和历史环境/验收副本，不推荐删除正式Python模块。

主要空间仍来自原logs实体副本、资产副本、冻结bundle副本和run内相同权重。保留全部旧配置与来源，删除前需再次审查历史路径、USD/URDF闭包和快照完整性，不能直接按同哈希删除；该数字不是已释放空间。约733MiB旧迁移大备份不计入删除候选，其唯一历史版本价值未确认。本次释放训练数据空间为0，未新增大型复制。

## 当前状态与下一步入口

没有两套并行维护的正式训练或对战源码；历史同名副本仅在archive。正式入口不会意外导入旧Dog A参数或默认权重，`model`原件SHA256保持迁移前一致。新模型仅有原始URDF/STL/package.xml与独立身份配置，没有USD、站姿/PD、训练环境或新checkpoint。

下一步新模型训练使用 **`python dogfight_rl/launch.py train`** 对应 `scripts/train/csdog_12dof.py`，先实现新模型独立环境和物理门禁，再启用训练；目前该命令会明确提示“新模型训练环境尚未实现。”。评估入口为 `launch.py evaluate`。不能改走归档旧train-a恢复权重来绕过门禁。
