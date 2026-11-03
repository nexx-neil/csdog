# 机器狗项目目录结构与历史训练文件审计

审计根目录：`/home/zxq/robot_projects`。源码与文件检查日期：2026-10-25～2026-10-26（Asia/Shanghai）。报告生成日期：2026-10-26。

**核心结论：应保留三狗对战基础设施及 Isaac Lab / RSL-RL 训练框架，替换机器人资产、机器人适配与训练配置，并重新训练运动策略。现有工程不能据此认定已经实现“三只真实四足机器人在同一物理场景自主强化学习对战”。**

现有成果包括同场景三运动学代理的脚本对战、旧 Dog A 单机器人 PPO 训练，以及真实 Dog A 接入规则层的短测试。真实接入测试中的 B/C 没有物理实体，使用解析射线；旧策略转向验收失败；项目未实现战斗强化学习奖励、可训练的多智能体环境、自博弈或对手策略池。

## 审计方法与证据边界

先读取根目录 `AGENTS.md`、`dogfight_rl/AGENTS.md` 与根目录 `格式规范.md`。递归枚举全部文件和目录，检查规范业务源码、配置、模型 XML、压缩包目录、Git 状态/历史、入口与动态加载链，并逐文件比对主要重复树和历史权重哈希。大型第三方仓库只审查整体结构、版本、修改状态、任务入口与业务依赖。

本次仅创建本报告。没有安装依赖、启动 Isaac Sim、启动训练、运行会产生临时文件的 pytest、删除/移动缓存或修改源文件。唯一执行的项目检查程序是已经阅读源码确认只读的 `python -B migration/verify_integrity.py`，结果为缺失迁移清单而失败，详见第六部分。其余检查使用文件读取、Git 只读命令和标准库脚本。

证据标记：**本次静态确认**指已读源码、路径、XML、哈希或 Git；**历史实测**指已有日志/遥测支持，不表示本次重跑；**未验证**指本次未做仿真/GUI/训练验收；**缺失**指当前目录不存在或没有实现。历史报告中的 PASS 不自动代表当前可运行。

审计初始共有 **6,708 个普通文件、0 个软链接**；所有一级、二级、三级目录完整清单见附录一，重要业务文件清单见附录二，规范日志实验清单见附录三，当前规范权重清单及哈希见附录四。以下路径如未写绝对前缀，均相对审计根目录；`T/` 仅在叙述中指 `dogfight_rl/02_training`，`V/` 指 `dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0`。

# 第一部分：项目当前真实目录结构

## 1.1 一级目录实际用途

| 路径 | 实际内容及用途 | 结论 |
|---|---|---|
| `IsaacLab/` | NVIDIA Isaac Lab 第三方仓库，六个 Python 分发包、官方训练/推理脚本、示例任务，以及本机 ANYmal-C 验证输出 | A；框架与其训练输出分开管理 |
| `dogfight_rl/` | 实际业务项目；三层规范源码、训练日志、模型、对战包、兼容实体副本、Git 和迁移备份 | 主工程，不能整体当旧模型垃圾 |
| `model/` | 独立 ROS 包 `csdog_urdf`；两份等价 12 关节 URDF 与 13 个碰撞 STL | 新模型候选，当前训练未接入；必须保留、待用户确认身份 |
| `dogfight_env_freeze/` | 冻结包清单、环境/PhysX/ANYmal 检查报告、启动器、环境文件备份和 IsaacLab Git bundle | 环境恢复证据；C/A，不是 Python 环境本体 |
| `dogfight_env_info/` | 六份系统、GPU、Conda、pip、PyTorch、IsaacLab 版本文本 | 历史环境证据，与 docs 内副本相同 |
| `dogfight_final_tests/` | 2026-09-13 官方 ANYmal-C 长训练、恢复、GUI 视频与日志 | C；不是三狗对战或新模型验收 |
| 根目录文档 | `AGENTS.md` 是现行约定；`DOGFIGHT_ENVIRONMENT.md` 是环境说明；`格式规范.md` 实为 V0 三代理对战接口规格 | A；不能把规格文件当普通格式说明删除 |

根目录规范提到的 `path_migration/20261025/` **目前不存在**；不是遗漏扫描。其缺失已破坏完整性检查器的依赖。根目录也没有 `fix_new.SLDASM` 实体目录，原件在规范资产目录中。

## 1.2 dogfight_rl 的规范结构与实体兼容副本

| 目录 | 实际职责、内容及引用 |
|---|---|
| `01_robots/assets/original/` | 原始 SolidWorks 导出 ROS 包、原始 URDF、13 个 STL、CSV、launch、原始 zip，以及含 CAD/STEP 的接收压缩包 |
| `01_robots/assets/dog_a/` | 旧 Dog A 预处理 URDF、首次 USD 转换和 `usd_attempt_002_named_joints/` 命名关节版；后者是当前默认训练与真实 A 接入使用资产 |
| `01_robots/assets/dog_a_symmetric_v1/` | 对称模型 URDF/USD/Mesh、生成脚本、生成记录及原资产 SHA256；是旧模型分支，不是新模型 |
| `01_robots/assets/dog_b/` | 空占位；没有本机 Dog B 资产 |
| `01_robots/configs/` | 10 份站姿、显式 PD、隐式执行器与平衡补偿配置 |
| `01_robots/python/dogfight/robots/` | Dog A 本体常量、按运行时关节名生成站姿/PD 向量、URDF 预处理 |
| `01_robots/python/dogfight/geometry/` | 基于旧 URDF/Mesh 的真实足点、FK/Jacobian 与接触几何工具 |
| `01_robots/python/dogfight/analysis/` | 旧对称本体平衡、隐式站立结果分析 |
| `01_robots/python/dogfight/tests/` | 自由落体、单关节方向、足点、站姿搜索、PD、接触动力学和 reward sanity 等 32 个诊断脚本；不能仅看 tests 名称认为是 pytest |
| `02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/` | 直接式单机器人 RL 环境、奖励、动作审计 wrapper、PPO 训练、零动作物理验证、策略评估 |
| `02_training/configs/` | 原始/对称模型运动任务、X/Y/XY 方向课程式实验和 BACK 恢复等 17 份 YAML；实际数量由附录逐项列出 |
| `02_training/deployment/` | checkpoint actor 重建与单机器人环境创建；被 shared.policy 动态导入 |
| `02_training/scripts/` | 历史分阶段训练/恢复、选优、四方向评估、GUI 验证 Shell/Python 入口；部分有默认恢复旧权重 |
| `02_training/logs/` | 当前规范训练产物：checkpoint、TensorBoard、配置快照、CSV/JSON、图像、视频及 zip；不是 `checkpoints/` |
| `02_training/checkpoints/{dog_a,dog_b}/` | 空的分类占位，不代表没有权重 |
| `02_training/historical_tests/final_validation/` | 根目录 `dogfight_final_tests` 的完整实体副本 |
| `02_training/videos/` | 空占位；实际视频在日志和历史验收目录 |
| `03_battle/source/dogfight_v0/` | 独立 Python/Isaac 扩展包；`arena/battle/navigation/agents/sim/ui/logging/config` 为实际对战核心 |
| `03_battle/scripts/v0/` | 三代理 headless/GUI、15 项 smoke、HUD smoke、真实 A 接口与 prebattle gate 入口 |
| `03_battle/logs/` | 三代理事件、真实 A 短接入记录、V0.2-B 门禁失败与根因数据 |
| `03_battle/python/dogfight/` | `agents/battle/locomotion` 占位包目录，核心实现不在这里 |
| `03_battle/assets/arena/` | 空地图资产占位；当前场地由 Python TestMap 和 scene.py 程序化创建 |
| `shared/` | 项目根目录、规范路径、YAML 资源解析、训练部署公共接口、环境检查与 NVIDIA apt hold 脚本 |
| `tests/` | 对战规则、HUD、真实适配 mock、路径可迁移性与实体兼容副本契约的 pytest |
| `docs/` | 模型/训练/对战指南和历史诊断文档；environment 内有冻结副本、远程 Dog C 报告 |
| `migration/` | 原目录迁移脚本、路径重构/回滚脚本、文件迁移清单、checkpoint 索引、历史验证报告及大备份；不是日常训练入口 |
| `.git/` | 业务 Git 历史；当前规范层有大量未跟踪文件，不能只靠 Git 恢复全部当前工作 |
| `assets/configs/scripts/source/dogfight/logs/checkpoints/videos` | 迁移后的实体兼容快照/历史入口；不是软链接。不会同步更新，不能再作为新开发代码源 |

`dogfight/__init__.py:9` 重写包 `__path__`，把日常 `dogfight.*` 导入指向三个规范层的 `python/dogfight`。`launch.py:43` 的子进程 PYTHONPATH 和各脚本自身查找根目录机制，将 `dogfight_v0` 指向规范 `03_battle/source/dogfight_v0`。因此同名物理副本不是多套同时活动算法框架，但旧脚本仍可被直接执行，测试也明确依赖兼容样本存在。

## 1.3 IsaacLab 的框架边界

| 目录 | 实际作用 |
|---|---|
| `source/isaaclab/` | 仿真、Articulation、actuator、sensor、DirectRLEnv/DirectMARLEnv、scene 与工具核心 |
| `source/isaaclab_assets/` | 官方机器人/场景配置；许多资产仍来自 Nucleus/Isaac Sim，不等于全部模型已在项目本地 |
| `source/isaaclab_tasks/` | 官方任务、注册、奖励、课程/随机化模板；包含 ANYmal-C locomotion 和多智能体示例 |
| `source/isaaclab_rl/` | RSL-RL、SB3、SKRL、RL-Games 桥接配置与 wrapper；不是业务 PPO 算法本体 |
| `source/isaaclab_contrib/`、`source/isaaclab_mimic/` | 第三方扩展与模仿学习支持；不能因旧模型更换而移除冻结安装的一部分 |
| `scripts/reinforcement_learning/{rsl_rl,sb3,skrl,rl_games,ray}/` | 官方训练/推理及分布式工具；本项目证据实际使用 RSL-RL |
| `scripts/{tutorials,demos,environments,tools,benchmarks,imitation_learning,sim2sim_transfer}/` | 教程、示例、转换与测试工具，不是本项目专属逻辑 |
| `apps/` | Isaac Sim Kit 启动与渲染配置 |
| `docs/.github/docker/tools/.vscode` | 文档、CI、容器、项目模板和开发配置 |
| `.git/` | 冻结上游快照；当前无源码差异 |
| `logs/rsl_rl/`、`outputs/2026-09-13/` | 官方 ANYmal-C 实验和 Hydra 输出；可归档，不是框架源码 |

本次 Git 确认 HEAD=`37ddf626871758333d6ed89cf64ad702aef127d0`，tag=`v2.3.2`，`git status --short` 与 `git diff HEAD --name-only` 均空。可确认当前相对本地冻结提交无修改；不能凭此证明机器所有历史时刻都没有改过。仓库历史很浅，保留 Git 和 bundle，不通过 pull/切换版本补审计。

# 第二部分：磁盘空间分析

## 2.1 一级目录占用

下表“实际占用”为 `du -sx -B1` 的磁盘块口径（含目录）；“文件逻辑大小”为所有普通文件 st_size 之和。MiB=2^20 B，GiB=2^30 B，不能把两种口径相加。审计报告本身不计入初始统计。

| 文件或目录 | 文件数 | 文件逻辑大小 | 实际占用 | 用途与建议 |
|---|---:|---:|---:|---|
| `/home/zxq/robot_projects/AGENTS.md` | 1 | 6,159 B（0.01 MiB） | 8,192 B（0.01 MiB） | 项目规范/文档，A |
| `/home/zxq/robot_projects/DOGFIGHT_ENVIRONMENT.md` | 1 | 7,713 B（0.01 MiB） | 8,192 B（0.01 MiB） | 项目规范/文档，A |
| `/home/zxq/robot_projects/IsaacLab` | 2582 | 158,004,929 B（150.69 MiB） | 167,256,064 B（159.51 MiB） | 框架A；其 logs/outputs 单独C |
| `/home/zxq/robot_projects/dogfight_env_freeze` | 35 | 35,234,898 B（33.60 MiB） | 35,352,576 B（33.71 MiB） | 冻结恢复证据，A/C |
| `/home/zxq/robot_projects/dogfight_env_info` | 6 | 17,132 B（0.02 MiB） | 36,864 B（0.04 MiB） | 历史环境文本，C |
| `/home/zxq/robot_projects/dogfight_final_tests` | 30 | 2,262,398 B（2.16 MiB） | 2,383,872 B（2.27 MiB） | 官方 ANYmal-C 验收，C |
| `/home/zxq/robot_projects/dogfight_rl` | 4036 | 2,553,754,819 B（2435.45 MiB） | 2,568,523,776 B（2449.54 MiB） | 主工程；规范日志与实体快照重复较多 |
| `/home/zxq/robot_projects/model` | 16 | 1,958,667 B（1.87 MiB） | 2,007,040 B（1.91 MiB） | 12-DOF 候选模型，A/E |
| `/home/zxq/robot_projects/格式规范.md` | 1 | 23,045 B（0.02 MiB） | 24,576 B（0.02 MiB） | 项目规范/文档，A |

总体逻辑大小约 2.56 GiB，磁盘块统计约 2.59 GiB（命令人类可读输出约 2.6G）。主要空间消耗来自日志双份保存、734 MiB 左右的迁移备份和旧模型 USD，并非大量源代码。

## 2.2 重点冗余和训练产物

| 文件或目录（完整根路径） | 实际用途 | 大小（逻辑） | 依赖旧模型 | 是否仍被引用 | 清理建议 |
|---|---|---:|---|---|---|
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs` | 规范训练/评估和配置证据 | 792,359,232 B（755.65 MiB） | 大部分是；external_* 为 ANYmal-C | 是：launch、factory、脚本默认恢复 | A（当前默认权重）/C（历史实验），不整体删 |
| `/home/zxq/robot_projects/dogfight_rl/logs` | 历史实体兼容日志 | 789,392,332 B（752.82 MiB） | 同规范日志 | 是：测试样本、历史参数路径与文档 | C/E；逐文件相同也不能直接删除 |
| `/home/zxq/robot_projects/dogfight_rl/migration/backups/pre_migration.tar.gz` | 迁移前项目、Git、日志及源文件恢复档 | 757,419,982 B（722.33 MiB） | 含旧模型及训练 | 是：迁移恢复链 | C；可能包含唯一旧版本，保留 |
| `/home/zxq/robot_projects/dogfight_rl/migration/backups/received_files.tar.gz` | 接收文件原件备份 | 11,479,605 B（10.95 MiB） | 是 | 迁移溯源 | C；不认定无价值重复 |
| `/home/zxq/robot_projects/dogfight_rl/01_robots/assets` | 规范机器人资产 | 87,415,500 B（83.37 MiB） | 除空 dog_b 外是 | 是：env、factory、站姿/几何诊断 | A（兼容期依赖）/C（迁移后归档） |
| `/home/zxq/robot_projects/dogfight_rl/assets` | 旧资产兼容快照 | 55,508,389 B（52.94 MiB） | 是 | 历史路径及直接入口可能使用 | C/E；先清引用再考虑去重 |
| `/home/zxq/robot_projects/dogfight_env_freeze/git/IsaacLab-v2.3.2.bundle` | 冻结框架 Git 离线恢复 | 35,111,598 B（33.49 MiB） | 否 | 恢复文档/哈希清单 | C，不删除唯一根层恢复入口 |
| `/home/zxq/robot_projects/dogfight_rl/docs/environment/freeze_snapshot/git/IsaacLab-v2.3.2.bundle` | bundle 实体副本 | 35,111,598 B（33.49 MiB） | 否 | 冻结快照 | C/E；同哈希但快照完整性需保留 |
| `/home/zxq/robot_projects/dogfight_final_tests` | ANYmal-C GUI 视频、截图、恢复验收 | 2,262,398 B（2.16 MiB） | 否（非旧 Dog A） | 报告与历史环境证据 | C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/historical_tests/final_validation` | 上述验收副本 | 2,262,398 B（2.16 MiB） | 否 | 训练目录历史索引 | C/E |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/logs` | 对战及真实 A 门禁事件 | 1,646,674 B（1.57 MiB） | 混合 | 是：根因/验收证据 | C，尤其保留转向失败记录 |
| `/home/zxq/robot_projects/IsaacLab/logs` | 官方 ANYmal-C checkpoints 和视频 | 65,329,298 B（62.30 MiB） | 否 | 官方验证报告与外部拷贝来源 | C/E，不能当旧 Dog A 权重删 |
| `/home/zxq/robot_projects/model` | 另一套 12-DOF URDF 与 STL | 1,958,667 B（1.87 MiB） | 不属于已运行旧 A | ROS package 自引用；业务未接入 | A/E；确认是否拟使用新模型 |
| `/home/zxq/robot_projects/dogfight_rl/.pytest_cache` | pytest 节点/失败记录缓存 | 3,400 B（0.00 MiB） | 否 | 没有业务消费；可重建 | D，仅建议；本次不清理 |

本次逐文件 SHA256 比对结果：

- `dogfight_rl/logs/` 的 **1,408 个文件、789,392,332 B（752.82 MiB）**在规范 `02_training/logs/` 中都有同内容副本；规范目录另有新文件。没有据此批准删除旧树。
- `dogfight_rl/assets/` 的 **43 个文件、55,508,389 B（52.94 MiB）**与规范资产同内容。
- `dogfight_rl/source/` 的 **77 个文件、255,733 B**与规范对战 source 同内容；直接执行路径与兼容测试仍是保留理由。
- 根层 `dogfight_final_tests/` 的 **30 个文件、2,262,398 B**与 `historical_tests/final_validation/` 相同；`dogfight_env_info/` 的 **6 个文件、17,132 B**也有规范副本。
- `dogfight_env_freeze/` 与 `docs/environment/freeze_snapshot/` 有 **33 个同内容文件、35,230,127 B**；两个脚本 `run_training.sh`、`check_environment.py` 内容不同，不能整体判定完全重复。
- 规范日志内 **38 组完全相同的权重**，81 个冗余路径共 **103,936,079 B（99.12 MiB）**。`model_final.pt`、迭代名与 `resume_iteration_*` 往往分别承担入口和溯源用途；同哈希不等于没有独立路径用途。组表见附录五。

以上六组实体树去重的候选体量约 **841.78 MiB**；若再考虑规范权重内部副本，约 **940.90 MiB**。这是需要修改入口、维护历史索引并人工确认后的理论范围，不是当前 D 类可释放空间；不得再把同一日志里的压缩包或 TensorBoard 与这些统计重复相加。大备份不计入“可释放”，其中历史唯一版本价值未确认。

扫描全项目 `.pt/.pth/.onnx` 共 **1,080 个、1,263,473,817 B**，包含规范权重、实体副本和 IsaacLab 官方 ANYmal-C 权重。TensorBoard 事件及 `.bin` 快照 **130 个、38,646,689 B**；视频扩展名文件 **24 个、8,792,745 B**；PNG/JPG/JPEG **398 个、62,330,199 B**，其中很多是上游文档插图，不能归为旧狗测试图。统计不展开压缩包内部文件，后缀统计不表示每个文件都有训练意义。

Python/pytest 缓存共 **661 个文件、5,950,097 B**：IsaacLab 内 3,378,236 B，Dogfight 内 2,571,861 B。IsaacLab 缓存按共享冻结环境保守列 E；Dogfight 中仅源文件存在且可重建的缓存列 D。没有发现项目内独立 venv、`.venv`、venv `pyvenv.cfg`、业务 build/dist/_build 编译树；发现六个 IsaacLab editable 包 `.egg-info`，它们是安装元数据，**不能当无用编译缓存删除**。

# 第三部分：旧机器人专属文件

## 3.1 模型身份与物理参数

旧 Dog A 原始模型为 `01_robots/assets/original/fix_new.SLDASM/urdf/fix_new.SLDASM.urdf`：13 links、12 revolute，原始关节名为 `1…12`。`prepare_dog_a_import_urdf.py` 及预处理 URDF 将关节映射为 FL/FR/RL/RR × HIP/THIGH/CALF；运行时顺序为：

```text
FL_HIP FR_HIP RL_HIP RR_HIP
FL_THIGH FR_THIGH RL_THIGH RR_THIGH
FL_CALF FR_CALF RL_CALF RR_CALF
```

顺序不是每条腿 3 关节连续排列。`env.py:60`、`:234` 和 `dog_a_locomotion_adapter.py:18`、`:173` 均强制验证，新的 12 自由度并不能自动通过这些检查。

旧模型质量、惯量、关节轴/限位、碰撞体位于原始与预处理 URDF、对称 URDF，以及各 USD `configuration/*_base.usd`、`*_physics.usd`。USD 根层通过相对路径引用 base/physics/robot/sensor 层；删除“中间 configuration”会破坏完整模型。导入 `config.yaml` 有 `convex_hull`、`self_collision: false`、`fix_base: false` 等设置。旧模型内部禁用 self_collision 不能据此推断三机器人间碰撞已处理。

旧本体 Mesh 被原始 URDF、预处理 URDF、几何诊断和对称生成脚本间接引用。原始与转换模型、所有 Mesh/配置的逐文件分类见附录二；不因含 Dog A 名称列 D。

## 3.2 强绑定文件与三种复用判断

此表“替换后用途”对应用户任务 2 的判断：①新机器人运行不再需要；②可修改后复用；③当前必须保留，否则已有功能会受影响。最终 A/B/C/D/E 分类另列，避免把“新机器人不用”误写成“现在可删”。

| 文件/文件组（dogfight_rl 下） | 绑定内容与引用证据 | 替换后用途 | 最终处理 |
|---|---|---|---|
| `01_robots/assets/original/fix_new.SLDASM/**`、两个接收 zip | 原始几何、惯量、关节和原件溯源；转换器/几何工具使用 | 新模型运行①；历史恢复③ | C；当前引用未切换前保留 |
| `01_robots/assets/dog_a/urdf/dog_a_import.urdf` | 旧关节重命名及 CAD link；配置、足点算法引用 | ① | C；随旧任务归档 |
| `01_robots/assets/dog_a/usd_attempt_002_named_joints/**` | 默认 train-a、factory 及站姿配置指向这里 | 当前③；切换后① | 兼容期间 A，迁移后 C |
| `01_robots/assets/dog_a/{dog_a.usd,configuration/**,config.yaml}` | 首次转换；旧测试、资源路径测试仍可能使用 | ① | C；未清引用不可删 |
| `01_robots/assets/dog_a_symmetric_v1/**` | 旧模型对称加工、Mesh/关节转换、生成/哈希记录 | ①；生成方法可参考② | C；不覆盖改造成新机器人 |
| `01_robots/configs/dog_a*standing_pose*.yaml` | 旧关节目标、约 0.14m 身高、足点、COM 与支撑多边形 | ②，所有数值重算 | B，原配置保留 C |
| `01_robots/configs/pd*.yaml`、`dog_a_dynamic_equilibrium_compensation.yaml` | 旧惯量/电机/站姿的增益与补偿 | ② | B；不能直接复制增益 |
| `01_robots/configs/dog_a_symmetric_v1_implicit_actuator.yaml` | 虽含 symmetric 名称，默认原始 Dog A 训练实际读取 candidate 01：HIP Kp/Kd=2/0.120，THIGH=3/0.130，CALF=3/0.065，10Nm、5rad/s | 当前③；新模型② | B；这是不能按文件名删除的明确例子 |
| `01_robots/python/dogfight/robots/{dog_a_cfg,prepare_dog_a_import_urdf}.py` | 旧 USD/站姿、关节重命名、HIP/THIGH/CALF 后缀分组 | ② | B |
| `01_robots/python/dogfight/geometry/foot_contact_solver.py` | URDF/STL 足点几何、旧链路 | ② | B；重标定足端与方向 |
| `01_robots/python/dogfight/{tests,analysis}/**` | 自由落体、PD、接触、雅可比、平衡诊断参数来自旧模型 | 诊断方法②；旧结论① | B/C；历史输出 C |
| `02_training/python/dogfight/tasks/.../env.py` | 关节顺序、48/12、旧足端别名、起始高度、PD 与终止阈值 | ② | B；保留环境框架 |
| 同目录 `reward_terms.py` | 滑移、抬脚、落足、进度等通用 tensor 核 | ②，主要改参数/接触几何 | B；不是无用旧代码 |
| 同目录 `train/evaluate/validate/action_audit_wrapper.py` | PPO/检查/评估大部分可复用；维度与默认配置绑定 | ② | B |
| `02_training/configs/*.yaml` 与 `02_training/scripts/**` | 模型 URI、任务名、旧 command 约定、reward 权重、恢复源 | ②，旧实验记录① | B/C；不能让新模型默认续训旧权重 |
| `02_training/deployment/policy_runtime.py` | 写死 obs=48、action=12，环境类与 actor MLP 结构 | ② | B |
| `03_battle/.../agents/dog_a_factory.py` | 默认旧配置、checkpoint、固定 SHA256 | ② | B；替换显式模型与策略来源 |
| `03_battle/.../agents/dog_a_locomotion_adapter.py` | 固定旧关节、obs/action、body frame，`(-vy,vx,yaw)` 坐标转换 | ② | B |
| `03_battle/.../agents/real_dog_agent.py` | 固定 ID dog_a、-π/2 本体朝向偏移和旧 root height | ② | B；需通用化，不能直接复制三实例 |
| `03_battle/.../config/battle_cfg.py` | 战斗参数大多通用；dog_a_root_height_m、枪口和 hit radius 与尺寸相关 | ②，规则可保留 | B（局部改） |
| `02_training/logs` 下旧 A weights、TB、CSV、图视频 | 单体运动实验；训练恢复、选优、历史故障和报告使用 | 新模型不直接使用①；复现③ | 默认权重当前 A，其余 C；不得当训练框架删 |
| 根层 `assets/configs/dogfight/scripts/source/logs` 兼容副本 | Python 正常导入避开大部分副本，但历史直接入口与测试依赖 | 是否可移除待确认 | C/E |

没有发现独立通用运动学控制库已经彻底脱离旧 Dog A。配置里的抬脚高度、air-time、接触点、增益与奖励权重属于步态塑形；没有证据表明有独立通用 CPG/MPC 步态控制器。

## 3.3 model/ 中的 12 自由度模型

`model/robot.urdf` 和 `robot.preview.urdf` 本次 XML 解析均为 **13 links、12 revolute**。关节按文件顺序为 LR/LF/RF/RR 每腿 `joint_*_1,2,3`；声明总质量 **7.6042608 kg**。所有关节声明 limit ±3.14rad、effort 10、velocity 3；这些是文件声明，不是硬件实测。左右侧关节轴符号、pitch/knee 轴方向不同，必须逐关节校验。

两份 URDF 仅 Mesh URI 前缀不同：主文件 `meshes/...`，preview 文件 `package://csdog_urdf/meshes/...`；替换 package 前缀后内容完全相同。每份 26 处 visual/collision Mesh 引用均能落到现有 13 个 STL。它们承担本地解析与 ROS package 解析两种用途，不算可以随意删的重复 URDF。

本次追踪规范入口、配置、factory 与动态 provider，没有发现该模型被训练代码消费；也没有它的训练 USD、站姿配置或专属 checkpoint。**它很可能是准备接入的模型候选，但无法仅凭目录确认就是用户最终新模型，故身份列 E，资产保留列 A。** 不需要为了获得另两只实例而等待不同 Dog B/C URDF：如果目标允许相同本体，可在同一场景复制此模型为三个独立 articulation；独立控制/策略与不同模型是两回事，现有入口尚未提供这种能力。

# 第四部分：必须保留的核心文件

## 4.1 核心文件与关键调用链

| 必保留文件/组件 | 保留理由及依赖 |
|---|---|
| 根目录与业务 `AGENTS.md`、`ENV_LOCK.md`、`ENVIRONMENT.md` | 冻结环境和业务边界约束 |
| `IsaacLab/source/**`、`apps/**`、`isaaclab.sh`、Git 元数据 | 本机 editable 安装直接映射；删/移将破坏环境 |
| `dogfight_rl/shared/paths.py` | ROOT、ISAACLAB、PYTHON、YAML 相对资源递归解析；多个入口依赖 |
| `dogfight_rl/dogfight/__init__.py` | 将历史包名指向三层规范代码，删除会改变正常 Python 导入 |
| `dogfight_rl/launch.py` | 单一业务入口、隔离子进程环境、输出覆盖检查；默认参数未来需 B 类修改 |
| `shared/policy.py` + `02_training/deployment/policy_runtime.py` | 对战与训练部署边界；后者内容 B 类修改，接口与能力必须保留 |
| `V/battle/{battle_manager,health_system,intel_service,visibility_service,weapon_service,scripted_policy,types,interfaces,ray_query}.py` | 对战规则、状态类型与后端契约；不依赖旧关节名 |
| `V/arena/{map_interface,test_map,spawn_manager}.py` | 场地、出生点和随机分配；后续可换地图 |
| `V/navigation/{navigation_interface,simple_navigation}.py` | 高层目标到速度命令，不控制关节 |
| `V/agents/{agent_interface,locomotion_interface,proxy_agent,real_locomotion_adapter}.py` | 机器人替换边界和可重现的代理基线；通用 adapter 尚是 skeleton |
| `V/sim/{scene,physx_ray_query}.py`、`V/runtime.py` | 三代理同场景与真实 PhysX 射线；真实三本体场景需新增 |
| `V/ui/battle_hud.py`、`V/logging/battle_logger.py` | 观察对战状态、血量、事件与验收证据 |
| `03_battle/scripts/v0/**` 与 `dogfight_rl/tests/**` | 既有对战与模型替换的验收入口；不能因旧 A 不用而删除全部测试 |
| `02_training/python/.../{env,train,reward_terms,action_audit_wrapper,evaluate,validate}.py` | 可复用单机器人 RL 主干；B 类修改而不是删除 |
| `migration/manifests/**`、`migration/backups/**`、`docs/**` | 原始文件/权重溯源和未提交源码恢复证据；缺失的外层迁移链另见第六部分 |
| 原始 CAD/URDF 与代表性权重+配置+遥测 | 不可只保存孤立 checkpoint；需保留复现所需整套数据 |

这里“必须保留能力”与“当前文件要修改”可以同时成立：A 类保障系统依赖，B 类说明实现需要适配，不意味着模型文件也要永久放在活动目录。

实际训练链：

```text
launch.py train-a
  -> 02_training/.../train.py
  -> DOG_A_LOCOMOTION_TASK_CFG（导入 env 前设置）
  -> load_project_yaml(config) -> pose YAML + actuator YAML + USD
  -> DogALocomotionPpoSmokeEnv(DirectRLEnv)
  -> ActionAuditRslRlVecEnvWrapper
  -> site-packages/rsl_rl/runners/on_policy_runner.py
  -> site-packages/rsl_rl/algorithms/ppo.py
  -> 02_training/logs/<新实验>/checkpoint + TensorBoard + telemetry
```

实际三代理对战链：

```text
launch.py battle / battle-gui
  -> 03_battle/scripts/v0/run_v0_headless.py / run_v0_battle_demo.py
  -> create_isaac_battle -> TestMap + scene.build_test_scene
  -> 3 ProxyAgent + IsaacPhysXRayQuery
  -> BattleManager + ScriptedBattlePolicy + Navigation/Intel/Visibility/Weapon/Health
  -> 03_battle/logs + HUD
```

真实 Dog A 接入链：

```text
run_dog_a_battle_integration_test.py
  -> dog_a_factory.create_dog_a_agent（旧配置+旧权重哈希检查）
  -> shared.policy -> importlib 加载 02_training/deployment/policy_runtime.py
  -> create_environment（num_envs=1）+ load_actor
  -> DogALocomotionAdapter + RealDogAgent
  -> BattleManager（A真实；B/C纯逻辑Proxy；AnalyticRayQuery）
```

`shared.policy._provider():10` 使用 `importlib.util.spec_from_file_location` 动态加载部署实现；普通 import 搜索可能漏掉它。YAML 路径、USD 子层引用、Shell 自定位、默认恢复和历史路径兼容均已纳入判断。

## 4.2 强化学习框架审计

| 问题 | 真实实现与可复用判断 |
|---|---|
| PPO / RSL-RL | 是。`train.py:57` 导入 OnPolicyRunner，`:190` 构造 RslRlOnPolicyRunnerCfg，`:257` 创建 runner；PPO 算法在 `/home/zxq/miniconda3/envs/dogfight/lib/python3.11/site-packages/rsl_rl/algorithms/ppo.py:20` |
| 版本 | 环境元数据为 RSL-RL 3.1.2、Isaac Sim 5.1.0.0、isaaclab 分发 0.54.2；仓库 tag v2.3.2 是另一个版本字段。冻结记录 Python 3.11.16、torch 2.7.0+cu128。本次未导入 GPU 软件重验运行时 |
| 其他框架 | IsaacLab 自带 SB3/SKRL/RL-Games/Ray 支持；源码存在不等于业务使用，没有自定义任务用它们训练的证据 |
| 多智能体框架 | IsaacLab 有 DirectMARLEnv 和 cart_double_pendulum 示例；Dogfight 业务环境是 DirectRLEnv，尚没有战斗 MARL wrapper/训练器 |
| 注册方式 | 官方 ANYmal-C 在 `IsaacLab/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_c/__init__.py` 通过 gym.register 注册；自定义 Dog A 直接实例化类，没有发现业务 gym.register；YAML task_name 不是 Gym ID |
| 观测 | `env.py:454` 拼接线速度3、角速度3、投影重力3、命令3、关节位置偏差12、关节速度12、上一动作12，共48；没有敌人信息 |
| 动作 | `env.py:447`：策略输出经 wrapper 缩放、clip[-1,1] 后，`default_joint_pos + action_scale * action` 为位置目标；`_apply_action` 交给隐式 PD。默认 BACK 配置 action_scale=0.25rad、actor_output_scale=0.50 |
| 奖励 | `env.py:520` 与 `:639` 起包括速度追踪、方向进度、低速惩罚、直立、横向/朝向/角速度、滑移/抬脚/air-time、STOP站稳、动作/关节速度/effort/终止；`:707` 乘 step_dt。没有击中、受伤、胜负等对战训练奖励 |
| 终止 | `env.py:476`：最低 base 高度、projected gravity 翻倒与episode timeout；这是运动任务终止，不能替代战斗胜负 |
| 默认 PPO 参数 | BACK config：64 env、240Hz physics、decimation4=60Hz policy、5.5s episode；rollout24、actor/critic [128,128,128] ELU、clip0.2、lr3e-4、gamma0.99、lambda0.95、epochs5、minibatches4、entropy0.005、grad_norm1。400 表示该阶段追加迭代配置，不是整个历史总迭代 |
| checkpoint 恢复 | `train.py:260` 调用 runner.load 并恢复学习迭代/优化器，可选 reset command 列和探索 std；新模型不能盲目恢复。同为48/12也可能动作语义完全不同 |
| 推理 | `evaluate.py` 加载策略评估；部署 provider 根据配置重建 MLP 并 strict load actor state，读取 infos 或配置中的 actor_output_scale；不是完整通用多机器人部署器 |
| validate-a | 指向 validate.py，主要做零动作、有限值、接触/关节和重置检查；并不是默认权重的完整运动能力评估。gui-a 指向 evaluate.py |
| 课程学习 | 有分阶段人工实验与恢复脚本、方向命令采样/切换平衡、站立warmup；自定义环境未实现 IsaacLab CurriculumManager 的自动难度课程 |
| 域随机化 | 自定义环境主要随机采样命令和时段；地面摩擦固定、站姿及根状态确定；没有业务级质量/惯量/摩擦/PD/推力扰动随机化机制。官方模板具备相关功能，不等于本任务已启用 |

RSL-RL/PPO、保存/恢复、TensorBoard、动作审计和大部分评估逻辑可以继续使用；需重写/参数化模型与观测映射、调整奖励尺度、执行器和终止条件。新本体运动权重应重新生成；未来战斗策略也需单独训练。

# 第五部分：三狗对战功能审计

## 5.1 功能完成度矩阵

| 功能 | 源码证据 | 已实现/验证范围 | 旧模型依赖与复用 |
|---|---|---|---|
| 三代理场景 | `V/runtime.py:27`、`sim/scene.py:50` | 同一 Isaac stage 创建三运动学 Cuboid，有碰撞体；历史 physical smoke 通过 | 不依赖旧 A，可保留代理基线 |
| 独立控制/重置 | `agents/proxy_agent.py`、`battle_manager.py:68` | 每代理独立 pose/command/HP；历史加载、移动、复位通过 | 高层接口可保留 |
| 出生位置 | `arena/test_map.py`、`spawn_manager.py` | 三点 (-4.2,-2.7,0.35)、(4.2,-2.7,2.79)、(0,3.7,-1.57)；seed可打乱分配 | 与旧关节无关；需按新尺寸复核间距 |
| 场地 | TestMap + scene | 12m×10m逻辑边界、两堵墙、14m×12m地面 | 可保留；未实现最终场地/复杂导航 |
| 物理碰撞 | `scene.py` kinematic_enabled、`ProxyAgent.update` set_world_pose | 有 PhysX collider 和射线命中；代理位姿直接积分，位置校验仅墙/边界 | 不能认为已实现动力学推挤、互撞稳定、碰撞伤害；需新本体测试 |
| 距离/角度/FOV/LOS | `visibility_service.py`、`physx_ray_query.py` | hypot距离、归一化yaw_error、FOV和最近命中遮挡；历史 smoke 通过 | 算法保留；枪口/目标高度依赖尺寸 |
| 情报 | `intel_service.py` | t=0,5,10…快照，间隔内保持旧坐标；历史测试通过 | 可直接保留 |
| 导航 | `simple_navigation.py` | 直接趋近目标、限速、转向、到点扫描 | 可保留基线；无寻路绕墙，遇墙可能卡住 |
| 攻击 | `scripted_policy.py`、`weapon_service.py` | 最近可见目标、转向瞄准、瞬时射线、1s冷却、34伤害 | 规则可保留；真实模型枪口/射线自命中需校验 |
| 防御 | ScriptedBattlePolicy 实现 | 没有专门闪避、掩体、撤退、受击决策策略 | 尚未实现，不应把追击/瞄准写成完整攻防学习 |
| HP/死亡 | `health_system.py`、manager.apply_damage | 初始100、命中扣血、死亡停命令、事件 | 可保留；停止命令不等于动态死亡本体已物理冻结/安全倒地 |
| 胜负/结束 | `battle_manager.py:222` | 最后存活者胜利；无人存活或120s超时为平局；可reset | 可保留，规则不是 RL reward |
| 多智能体观测/动作 | `battle/types.py` | BattleObservation/BattleAction dataclass 与 per-agent policy dict 已实现 | 是策略接口，非可训练 tensor observation/action space；可保留接口并增加编码层 |
| 学习型战斗策略 | 当前实际注入 ScriptedBattlePolicy | PPOBattlePolicy/IPPO/MAPPO 在规格中是未来目标，没有业务实现 | 缺失，需要新增 |
| 自博弈/策略池/对手checkpoint | 业务源码和入口追踪 | 无self-play训练循环、对手采样池或战斗策略加载器 | 缺失；加载运动actor不算对手策略加载 |
| 真实 Dog A | factory + DogALocomotionAdapter + RealDogAgent | 模型与旧actor可加载；历史短接入/复位通过；转向门禁失败 | 适配器需修改，旧策略不满足完整控制能力 |
| 三只真实本体同场景 | 现 runtime只建Proxy，factory只建单env旧A | 尚未实现；现 RealDogAgent 固定dog_a | 需共享scene和统一step，不是替换USD即可 |
| GUI/HUD | ui/battle_hud.py、demo、HUD smoke | 6项HUD状态历史通过；当前完整GUI视觉验收未完成 | 大部分可保留；新本体相机尺度与外观需检查 |

## 5.2 运行证据和不能外推的结论

1. `dogfight_rl/migration/reports/F_battle_smoke.log`：15/15，包括三代理、独立移动、5秒情报、FOV/LOS、墙挡射击、命中扣血、冷却、死亡、最后幸存者获胜与原进程reset。对应 `run_v0_smoke_tests.py` 及 `runtime` 的 PhysX 三代理场景。**这是历史实测，本次未启动仿真复核。**
2. `F_hud_smoke.log`：6/6状态测试，支持血量、死亡和reset显示同步；不代表已人工确认GUI视觉质量。
3. `F_real_a_integration.log` 与 `03_battle/logs/migration_real_a/20261023_104635/dog_a_integration_summary.json`：真实 A + 两逻辑代理短接入 PASS。**`run_dog_a_battle_integration_test.py:48` 没有调用 build_test_scene；B/C Proxy 没有 pose_writer；ray backend 是 AnalyticRayQuery；TestMap 也没有由该脚本创建物理墙体。因此不是三个可相互物理接触的本体。**
4. `03_battle/logs/v0_2b/gates/20260920_122706/prebattle_gate_summary.json`：A加载 PASS、B零命令 PASS、C方向门禁 FAIL、D NOT_RUN。`root_cause_analysis.json` 记录默认 actor 第11观测列（yaw command）首层权重全零；正负0.3rad/s命令都得到 -0.043614rad 的相同yaw变化和约 -0.0159435rad/s漂移。该checkpoint没有受命令控制的转向能力。文件中的checkpoint SHA256与当前默认文件一致，本次已核对索引与文件哈希。
5. `migration/reports/GATES.json` 将 GUI 标为 NOT VERIFIED；GUI应用启动后场景初始化卡住，headless evaluate 通过。根层 final_tests 的GUI PASS是2026-09-13官方 ANYmal-C 验证，不能拿来证明旧 Dog A 或当前三狗GUI通过。
6. 两个 `02_training/logs/path_migration_20261025*/telemetry.json` 记录旧权重恢复后一轮 PPO 成功、无 PhysX/CUDA error、checkpoint finite。只能证明训练链短时可用，不能证明四向、转向、长时间稳定或战斗能力。

## 5.3 新模型替换后能保留多少

按职责而不是按“包含 Dog A 字样的文件比例”判断：`battle/` 九个实现/接口模块，`arena/` 三个模块，`navigation/` 两个模块，`logging/` 一个模块，共 **15 个非 __init__ 的规则/场地/导航/日志模块可作为复用主体保留**。其中射线服务接入真实碰撞体、场地尺寸和配置参数仍要重验。HUD、Agent/Locomotion 契约和三代理 smoke 也保留。

需要实质修改的是旧 Dog A factory、locomotion adapter、RealDogAgent、部署provider与模型相关配置；现 scene/runtime 可继续保留代理演示用途，但要新增/扩展三真实本体场景。没有根据给出“整个三狗项目可直接复用80%/90%”这样的比例，因为最终 MARL、自博弈和三本体共享物理推进还未实现。

特别要解决统一仿真推进：`DogALocomotionAdapter.step():161` 直接调用单机器人 `environment.step`，`BattleManager.step():102` 又逐代理调用 `update`。若简单放入三个此adapter，会逐代理推进全局仿真、产生不同步动作和多次物理step；当前 `_validate_environment` 还要求 num_envs=1。正确后续实现应先收集三代理动作，再由共享场景按统一dt推进一次，最后统一更新状态/奖励。训练 num_envs=64/256 是并行独立单狗环境，不能当“三狗同场景”。

# 第六部分：文件清理建议

## 6.1 A/B/C/D/E 分类规则与总表

| 类别 | 目录/文件组 | 本次结论 |
|---|---|---|
| A 必须保留 | 冻结 IsaacLab 框架与安装元数据、shared、业务入口、对战规则与接口、规范测试、配置规范、原始唯一模型资料、当前依赖中的默认权重 | 维持已有系统与溯源；旧A资产要等新旧入口明确分离后才归档 |
| B 保留并修改 | 本体配置/关节与足点工具、单体env/reward/runner/evaluate、PPO配置、部署provider、真实机器人adapter、battle_cfg | 重用代码设计，参数与映射重新标定；新配置独立命名 |
| C 建议归档 | 原始旧模型/对称分支、历史权重/日志/图视频、ANYmal验证、冻结记录、迁移备份、兼容快照 | 归档必须保留配置、来源权重、哈希和诊断证据；本次不移动 |
| D 技术上可重建 | 下表中已逐个核实对应 `.py` 存在的 Dogfight bytecode 与 pytest缓存 | 不含模型/日志/weights/源码；当前约几MiB，精确总量见表尾 |
| E 人工确认 | 唯一无同位源文件的pyc、兼容目录未来是否撤除、缺失迁移链恢复、model身份、共享IsaacLab缓存/不明恢复资料 | 不可推定可删除 |

A/B/C 针对重要文件的具体分类见第三部分和附录二至四。这里 D 仅表示删除后可由现有源码/工具重建的技术判断；现行 AGENTS 仍要求保留缓存、历史日志、旧源码与 Git，**本次未获得清理执行任务，也未执行任何清理**。不能把本报告当批量删除授权。

## 6.2 D 类完整路径、大小与依据

只列 Dogfight 中可重建项。每个 `__pycache__` 已检查所有 `.pyc` 的源 `.py` 存在；若同目录存在无法确认源文件的pyc，则只列出其中可重建的单个文件，不能整个目录删除。业务 Git 未跟踪这些缓存，`.gitignore` 明确忽略它们；迁移完整性扫描源码明确排除缓存（`migration/verify_integrity.py:17`）。pytest缓存仅保存用例节点等运行信息，没有模型/权重内容。均不影响源代码和模型原件；下次导入/测试可能重新生成并有短暂启动成本。

| D 类完整路径 | 文件数 | 逻辑大小 | 判断依据 |
|---|---:|---:|---|
| `/home/zxq/robot_projects/dogfight_rl/01_robots/assets/dog_a_symmetric_v1/generation/__pycache__` | 1 | 76,336 B（0.07 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/01_robots/python/dogfight/analysis/__pycache__` | 2 | 36,365 B（0.03 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/01_robots/python/dogfight/geometry/__pycache__` | 1 | 26,528 B（0.03 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/01_robots/python/dogfight/robots/__pycache__` | 1 | 5,311 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/01_robots/python/dogfight/tests/__pycache__` | 21 | 521,874 B（0.50 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/deployment/__pycache__` | 1 | 4,106 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/python/dogfight/tasks/__pycache__` | 1 | 224 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/__pycache__` | 7 | 193,432 B（0.18 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/analyze_dog_a_four_direction.cpython-311.pyc` | 1 | 17,641 B（0.02 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/select_best_training_checkpoint.cpython-311.pyc` | 1 | 7,369 B（0.01 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/train_original_dog_a_straight.cpython-311.pyc` | 1 | 10,407 B（0.01 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/compare_dog_a_x_directions.cpython-311.pyc` | 1 | 6,381 B（0.01 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/validate_back_gait_primitive_config.cpython-311.pyc` | 1 | 6,013 B（0.01 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/select_best_back_gait_checkpoint.cpython-311.pyc` | 1 | 11,610 B（0.01 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/validate_yaxis_recovery_configs.cpython-311.pyc` | 1 | 3,536 B（0.00 MiB） | 对应 .py 已存在；仅此文件可重建，不含同目录孤立缓存 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/scripts/v0/__pycache__` | 8 | 112,293 B（0.11 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/__pycache__` | 2 | 5,246 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/__pycache__` | 8 | 45,658 B（0.04 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/__pycache__` | 5 | 19,363 B（0.02 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/__pycache__` | 10 | 63,680 B（0.06 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/config/__pycache__` | 2 | 3,505 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/logging/__pycache__` | 2 | 4,408 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/__pycache__` | 3 | 8,881 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/__pycache__` | 3 | 8,963 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/ui/__pycache__` | 2 | 11,629 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/assets/dog_a_symmetric_v1/generation/__pycache__` | 1 | 76,336 B（0.07 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/__pycache__` | 1 | 990 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/analysis/__pycache__` | 2 | 36,365 B（0.03 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/geometry/__pycache__` | 1 | 26,565 B（0.03 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/robots/__pycache__` | 1 | 5,311 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/tasks/__pycache__` | 1 | 224 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/__pycache__` | 7 | 193,432 B（0.18 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/dogfight/tests/__pycache__` | 21 | 521,874 B（0.50 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/scripts/__pycache__` | 8 | 69,013 B（0.07 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/scripts/v0/__pycache__` | 8 | 112,293 B（0.11 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/shared/__pycache__` | 3 | 5,501 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/__pycache__` | 2 | 5,246 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/agents/__pycache__` | 8 | 45,658 B（0.04 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/arena/__pycache__` | 5 | 19,363 B（0.02 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/battle/__pycache__` | 10 | 63,680 B（0.06 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/config/__pycache__` | 2 | 3,505 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/logging/__pycache__` | 2 | 4,408 B（0.00 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/navigation/__pycache__` | 3 | 8,881 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/sim/__pycache__` | 3 | 8,963 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/source/dogfight_v0/dogfight_v0/ui/__pycache__` | 2 | 11,629 B（0.01 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/tests/__pycache__` | 12 | 132,409 B（0.13 MiB） | 所有 pyc 均有同目录所属源码；导入可重建 |
| `/home/zxq/robot_projects/dogfight_rl/.pytest_cache` | 5 | 3,400 B（0.00 MiB） | pytest 缓存；非业务输入、非训练数据 |

**D 类合计：2,565,805 B（2.45 MiB）。** 这是本报告在不动历史成果和依赖的前提下确认的技术可重建体量；释放量远小于日志/备份的候选归档体量。磁盘实际释放会受块大小影响。

## 6.3 明确列 E 的项目与当前故障

- `/home/zxq/robot_projects/dogfight_rl/02_training/scripts/__pycache__/check_environment.cpython-311.pyc`：没有同位 `02_training/scripts/check_environment.py`；其他位置存在同名源码不证明这份bytecode可重建，故不列D。它不是孤立源码的已确认业务入口，但保留待确认。
- `dogfight_rl/assets/configs/scripts/source/dogfight/logs`：虽然多个树逐字节重复，历史脚本直接入口与 `tests/test_project_paths.py::test_legacy_names_are_physical_compatibility_copies` 显式读取样本。撤除会令测试失败，并可能破坏历史命令。需先设计兼容策略再判断。
- `path_migration/20261025/changes.json` 与 `backups/` 缺失：根 AGENTS 描述其存在，`migration/verify_integrity.py:12` 无条件读取，`:22` 还依赖每条修改的备份。**本次只读执行已返回 exit=1 / FileNotFoundError**。因此 `python launch.py integrity` 当前会失败，不能照抄历史 PASS。
- `migration/verify_integrity.py:16` 还写死旧规范绝对前缀；恢复迁移链后仍需审查移动工作区的可迁移性。本次不修代码，也不重建伪造清单。
- 迁移前 `pre_migration.tar.gz` 已只读查看成员目录，没有 `path_migration/20261025`，不能声称大备份必然能恢复这次后续迁移证据。
- `IsaacLab/**/__pycache__`：源文件多可重建，但共享冻结仓库的运行缓存由环境管理，不纳入本项目可执行清理名单。
- `IsaacLab/source/*/*.egg-info`：是editable安装元数据，保留A/E；不列D。
- 未确认价值的zip导出、最佳权重、测试失败日志与大备份：保持C/E；不能用“重复”或“失败”作唯一删除理由。失败记录可能解释当前模型限制。

## 6.4 依赖关系、绝对路径与外部重要数据

| 检查点 | 本次事实与影响 |
|---|---|
| 跨目录 | 训练读01资产/配置；对战经shared读02部署与旧权重；几何脚本读模型与02诊断日志；历史验证引用IsaacLab/logs。迁移必须保持这些映射 |
| 软链接 | 项目内递归枚举0个symlink，故失效symlink也是0。旧文档如BATTLE_GUIDE还称日志为符号链接，已过时，应以本次实体检查为准 |
| 业务绝对路径 | 活动训练/对战Python大多由文件位置找ROOT；USD导入器生成 `01_robots/assets/**/config.yaml` 仍有写死 `/home/zxq/robot_projects/...` 的asset_path/usd_dir。它们是转换元数据，不能误认为全部配置已彻底相对化 |
| Shell绝对位置 | 根层 `dogfight_rl/run_training.sh` 使用 `$HOME/robot_projects/IsaacLab`；freeze根层启动器使用兄弟IsaacLab+可覆盖变量；冻结快照脚本不能当通用迁移启动器 |
| Python导入 | `dogfight.__path__`、PYTHONPATH、各脚本sys.path及shared动态provider共同决定实际模块；仅rg无命中不等于未引用 |
| YAML动态加载 | `DOG_A_LOCOMOTION_TASK_CFG` 在env导入前决定全局TASK_YAML；load_project_yaml只解析01/02/03前缀，普通yaml.safe_load消费这些资源时需自行处理；单进程多不同机器人配置不能靠反复改环境变量解决模块导入缓存 |
| USD/URDF | USD子层按层相对路径；原始URDF package://fix_new.SLDASM映射到原始ROS包；新model package://csdog_urdf映射model；两者不能全局替换；OmniPBR.mdl由Isaac Sim提供 |
| IsaacLab修改 | 当前相对冻结commit无tracked diff；logs、缓存和egg-info是运行/安装数据，不能当自定义核心源码 |
| 重复训练框架 | 没有第二套活动IsaacLab/RSL-RL仓库证据；有业务代码/产物的实体快照与多框架官方适配示例，不是都在训练 |
| Python环境 | 项目内没有venv；冻结解释器在 `/home/zxq/miniconda3/envs/dogfight/bin/python`，环境约20G。Conda还有car_ai、fastreid、yopo等其他任务环境，不能判定为机器狗重复环境；未发现dogfight_test/dev副本 |
| editable依赖 | site-packages 的 `__editable___isaaclab_*_finder.py` 映射到当前 `/home/zxq/robot_projects/IsaacLab/source/...` 六包。移动IsaacLab会令已有解释器映射失效 |
| PPO算法位置 | `/home/zxq/miniconda3/envs/dogfight/lib/python3.11/site-packages/rsl_rl/`；算法不在项目旧checkpoint里，保留环境即可继续使用 |
| 外部模型/缓存 | Isaac Sim和Nucleus资产、内置MDL在环境/远程资产系统；不完全包含在此项目；离线迁移要另行清点 |
| 外部缓存体量 | `/home/zxq/.cache/ov`约571M、`.cache/warp`约560K、`.nv`约820K、`.nvidia-omniverse`约18M；仅为只读规模观察，未递归判定用途/可删性，不计D |
| 项目外日志 | `/home/zxq/logs`当前约12K，未发现普通文件；规范日志已有 `external_home/anymal_c_rough` 历史副本。不能因名字external_home就断言原位置仍保留完整历史 |
| 远程Dog C | docs/environment/remote_dog_c 是另一台 `/home/robo007`、RTX4050机器环境与ANYmal验证报告，不是本机Dog C模型/策略 |
| Git恢复风险 | Dogfight HEAD=d94aba2，历史含V0.1、V0.2-A、RealDog和prebattle门禁；当前01/02/03、shared等大量untracked，兼容源文件有modified。Git历史不能覆盖全部当前规范代码；勿reset/clean/丢备份 |

本次独立 `pxr.Sdf` 只读解析尝试因冻结解释器未直接暴露 pxr 报 ImportError，本次未启动 Isaac Sim 以获取运行时模块。因此USD完整组合沿用历史 `migration/reports/gate_c_assets.json` 等证据，未声称本次完成USD运行时验证；URDF/XML Mesh引用与复制哈希是本次静态验证。

# 第七部分：建议的新项目结构

优先沿用已建立的01/02/03层级，减少再次全量迁移。当前问题是兼容实体副本和模型参数硬绑定，不是缺少一个全新目录命名方案。建议目标如下（**未执行**）：

```text
robot_projects/
├── IsaacLab/                           # 冻结共享依赖，保持位置
├── model/                              # 新模型原始ROS包；确认身份后单一来源
├── dogfight_rl/
│   ├── launch.py                       # 明确机器人/任务/策略选择，新模型默认不恢复旧权重
│   ├── shared/                         # 路径、部署契约、模型索引
│   ├── 01_robots/
│   │   ├── configs/new_quadruped/       # 关节、站姿、执行器、足点/坐标标定
│   │   ├── assets/new_quadruped/        # 转换USD与manifest；不复制多份原始model
│   │   └── python/dogfight/robots/      # 通用模型加载和控制映射
│   ├── 02_training/
│   │   ├── configs/{locomotion,battle}/ # 算法与任务参数分离即可，不另拷一套PPO
│   │   ├── python/dogfight/tasks/
│   │   │   ├── locomotion/             # 新模型单体速度控制
│   │   │   └── battle/                 # 后续MARL观测/动作/奖励wrapper
│   │   ├── deployment/                 # 模型无关actor接口+每模型spec
│   │   ├── scripts/                    # 一套维护中的训练/评估入口
│   │   └── logs/new_runs/              # 唯一活动日志，独立run_id
│   ├── 03_battle/
│   │   ├── source/dogfight_v0/          # 保留已有独立包
│   │   │   └── dogfight_v0/
│   │   │       ├── battle/arena/navigation/ui/logging/
│   │   │       ├── agents/             # 可参数化ID/prim/frame的真实本体接口
│   │   │       └── sim/                # 共享场景三articulation、统一step
│   │   ├── scripts/                    # 代理基线和三本体验收
│   │   └── logs/
│   ├── tests/                          # 模型、策略契约、共享step和规则回归
│   ├── docs/                           # 规范、环境、清单、验收
│   └── migration/                      # 恢复链证据；先补缺失后再计划迁移
├── docs/                               # 工作区级文档索引（可选，不复制内容）
└── archive/                            # 后续显式批准归档才创建
    ├── old_dog_a/                      # 原始模型、最佳代表实验+配置+哈希
    └── historical_environment_tests/   # ANYmal与冻结历史的单一权威副本
```

这只是建议结构，不要求同时创建所有占位目录。单体与战斗训练共享已安装RSL-RL；“algorithms”如果只是YAML参数，可直接放02_training/configs，不另建空框架。不要同时维护根层和01/02/03内两套活动代码。

迁移风险与前置条件：

1. 先恢复/重新核实迁移清单依赖；没有完整证据链时不开始第二轮去重。
2. 决定兼容目录生命周期并更新依赖它们的测试/文档/入口；当前删除会破坏明确契约。
3. 归档旧USD必须将根层、configuration和Mesh相对引用作为闭包处理；原始ROS package内容不改字节。
4. 日志/权重归档要迁移默认恢复、factory SHA、历史续训脚本与索引；保留源run、算法参数、actor缩放和坐标约定。
5. `model/`原始资产只保留一个权威来源，转换产物另放规范资产。相同URDF不同URI用途可以通过显式导出流程维护，不全局替换。
6. 不移动IsaacLab/Conda环境。业务根目录仍依赖 `shared/paths.py` 的具体位置与环境editable映射，不能宣称整个项目已任意可搬。

# 第八部分：更换 12 自由度模型的影响分析

## 8.1 修改、复用与重训练清单

| 层次 | 必须修改/新增 | 可保留 |
|---|---|---|
| 模型导入 | 新URDF/USD转换配置、关节驱动/碰撞/质量惯量检查、资源manifest | IsaacLab importer/Articulation机制；旧原件归档 |
| 机器人spec | 新关节名/运行时顺序、每腿映射、轴正方向、限位、默认站姿、高度、足端link/局部接触点、body front变换 | 按名字解析与拒绝不匹配的门禁设计 |
| 执行器 | 新PD、力矩/速度限制、摩擦/armature依据；不要套旧10Nm/5rad/s或站姿 | 隐式执行器控制与action审计架构 |
| 单狗env | 用spec替换env.py与dog_a_cfg硬编码；足端sensor、root高度/终止阈值、reset、contact/body aliases | DirectRLEnv结构、批量采样、状态/日志机制 |
| obs/action | 12关节仍可采用48/12模板，但每列必须重定义；命令坐标、尺度、归一化按新本体验证 | 速度命令与位置目标控制思想 |
| reward | 新身体尺寸/质量/足点影响速度/effort/滑移/clearance尺度；增加非零yaw指令分布与对应奖励验收 | reward_terms通用tensor计算与奖励分项日志 |
| 训练入口 | 新模型独立task/config与输出；不要走默认自动恢复旧checkpoint；部署provider维度/spec参数化 | PPO、RSL-RL、TensorBoard、输出覆盖保护、恢复机制 |
| 真实adapter | ID参数化，prim路径/环境索引、root height、前向轴与枪口位置、关节映射、policy/spec加载 | Agent/Locomotion/VelocityCommand契约 |
| 三本体场景 | 在同一env建三个articulation、接触过滤/传感器、统一动作提交/物理step、独立reset/死亡状态 | Map、spawn、规则、射线后端接口、HUD |
| MARL任务 | 新增per-agent tensor obs/action/reward/done/state，公平同步动作、策略训练、对手加载 | 现BattleObservation/Action接口与规则状态来源 |
| 自博弈 | 新增策略池、对手采样、版本/评估/课程与checkpoint来源记录 | 当前脚本策略可作基线对手，不冒充学习结果 |

默认 `launch.py train-a` 自动追加旧 `--resume`；即使更换 `--config` 也会恢复旧权重。新模型必须先有明确“从零训练”的新入口/选项或直接使用已审查的底层train且不传resume，不能把现有默认命令原样用于新模型。当前审计不执行任何训练命令。

`DogALocomotionAdapter` 的 `(-vy,vx,yaw)` 与 `RealDogAgent` 的 -π/2 是旧本体被实测确定的适配。新URDF不保证相同，不能机械保留；应把“机器人本体坐标→对战+X前/+Y左/+Z上”的变换作为新spec。旧站姿YAML有+x前的文字说明，与旧actor实际坐标约定不是同一个层次，应按真实关节链与运动试验重建一致坐标。

## 8.2 哪些权重需要重新训练

- 旧 Dog A 和对称版本 locomotion checkpoint：新本体应从新策略训练，保留旧权重仅供参考与复现。旧actor同为48/12只说明张量形状可能加载，不说明动力学、坐标和关节动作语义兼容。
- 官方 ANYmal-C checkpoint：是环境验证和框架参考，不是新模型可直接使用策略。
- 战斗策略：当前没有已训练的战斗权重，未来需新增训练，而不是“恢复历史三狗战斗权重”。
- 无需重新训练的组件：场地接口、出生分配、情报、FOV/LOS/射线契约、HP/胜负/日志/HUD等程序规则本身；它们需要回归测试和尺寸参数重校验。

# 第九部分：下一步建议

1. **先固定审计与恢复证据。** 保留当前所有原件、日志、Git和备份；处理缺失 `path_migration/20261025` 的完整性链，更新过时的符号链接与checkpoint数量文档。当前530项索引逐项哈希全通过，规范日志实际536项，多出的6项是两次后续smoke；不重写旧清单伪装历史完整。
2. **确认新模型身份。** 确认 `model/robot.urdf` 是否最终本体。建立独立spec与导入manifest，保留URDF原始字节，先检查惯量、重心、关节轴/限位、碰撞几何和关节运行时顺序。无需安装/升级冻结环境。
3. **先单体物理门禁。** 新USD加载→自由落体→逐关节低幅方向测试→四足接触与站姿→保守PD站稳；未过门禁不做长训练。
4. **重建单体速度任务并从零训练。** STOP/四向低速→连续vx/vy→正负yaw_rate→组合速度与转向；每步用独立run和固定评估集。yaw命令必须包含非零样本，不能再次出现输入列永远为零的策略。再考虑课程与物理域随机化。
5. **先完成模型无关部署adapter。** 验证标准 body vx/vy/yaw 语义、停止、reset、动作/观测与checkpoint spec一致；把actor计算与全局物理step解耦。
6. **同一物理场景中复制三只新本体。** 若允许相同型号，直接三个实例；统一step、独立ID/command/state、碰撞与出生距离。先人工独立命令和脚本策略验收，再引入训练。多并行env不替代同env三本体。
7. **复用已有战斗基础设施。** 保留代理基线、情报/射击/HP/胜负/HUD；逐项完成真实墙体、真实本体射线、互撞/遮挡、死亡/重置与三体同步回归。补路径规划和防御行为时不改关节层接口。
8. **再实现战斗RL与自博弈。** 明确可见信息与5秒情报限制，定义per-agent观测/动作/奖励/终止、胜率评估、脚本对手与策略池。先验证学习型战斗策略优于脚本基线，再增加self-play。
9. **最后单独规划归档/去重。** 先保证新训练和三体对战可复现，再对约841MiB兼容实体副本及约99MiB权重路径副本逐项审批处理；不动冻结框架与环境。D类仅少量可重建缓存，本次全部保留。

---

# 附录一：所有一级、二级、三级目录及实际职责

以下为本次完整枚举，含隐藏目录；尺寸为普通文件逻辑大小，父子重复计入，不能纵向相加。更深的重要机器人、训练和对战路径另见正文及附录二。

| 目录（相对审计根） | 深度 | 递归逻辑大小 | 实际用途 |
|---|---:|---:|---|
| `IsaacLab/` | 1 | 158,004,929 B（150.69 MiB） | 冻结NVIDIA Isaac Lab框架及官方验证输出 |
| `IsaacLab/.git/` | 2 | 35,475,636 B（33.83 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/branches/` | 3 | 0 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/hooks/` | 3 | 23,442 B（0.02 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/info/` | 3 | 240 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/logs/` | 3 | 193 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/objects/` | 3 | 35,178,703 B（33.55 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.git/refs/` | 3 | 0 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `IsaacLab/.github/` | 2 | 71,154 B（0.07 MiB） | 上游CI、工作流与issue模板 |
| `IsaacLab/.github/ISSUE_TEMPLATE/` | 3 | 3,637 B（0.00 MiB） | 上游CI、工作流与issue模板 |
| `IsaacLab/.github/actions/` | 3 | 14,158 B（0.01 MiB） | 上游CI、工作流与issue模板 |
| `IsaacLab/.github/workflows/` | 3 | 42,037 B（0.04 MiB） | 上游CI、工作流与issue模板 |
| `IsaacLab/.vscode/` | 2 | 19,982 B（0.02 MiB） | 上游编辑器与开发配置 |
| `IsaacLab/.vscode/tools/` | 3 | 13,561 B（0.01 MiB） | 上游编辑器与开发配置 |
| `IsaacLab/apps/` | 2 | 76,303 B（0.07 MiB） | Kit启动与渲染配置 |
| `IsaacLab/apps/isaacsim_4_5/` | 3 | 36,627 B（0.03 MiB） | Kit启动与渲染配置 |
| `IsaacLab/apps/rendering_modes/` | 3 | 2,954 B（0.00 MiB） | Kit启动与渲染配置 |
| `IsaacLab/docker/` | 2 | 75,499 B（0.07 MiB） | 官方容器、集群和ROS工具 |
| `IsaacLab/docker/.ros/` | 3 | 1,698 B（0.00 MiB） | 官方容器、集群和ROS工具 |
| `IsaacLab/docker/cluster/` | 3 | 12,883 B（0.01 MiB） | 官方容器、集群和ROS工具 |
| `IsaacLab/docker/test/` | 3 | 1,972 B（0.00 MiB） | 官方容器、集群和ROS工具 |
| `IsaacLab/docker/utils/` | 3 | 30,571 B（0.03 MiB） | 官方容器、集群和ROS工具 |
| `IsaacLab/docs/` | 2 | 43,132,967 B（41.13 MiB） | 上游文档/示例插图/许可证 |
| `IsaacLab/docs/_redirect/` | 3 | 213 B（0.00 MiB） | 上游文档/示例插图/许可证 |
| `IsaacLab/docs/_templates/` | 3 | 1,035 B（0.00 MiB） | 上游文档/示例插图/许可证 |
| `IsaacLab/docs/licenses/` | 3 | 702,154 B（0.67 MiB） | 上游文档/示例插图/许可证 |
| `IsaacLab/docs/source/` | 3 | 42,406,791 B（40.44 MiB） | 上游文档/示例插图/许可证 |
| `IsaacLab/logs/` | 2 | 65,329,298 B（62.30 MiB） | 官方RL实验产物 |
| `IsaacLab/logs/rsl_rl/` | 3 | 65,329,298 B（62.30 MiB） | 官方RL实验产物 |
| `IsaacLab/outputs/` | 2 | 305,595 B（0.29 MiB） | Hydra运行输出 |
| `IsaacLab/outputs/2026-09-13/` | 3 | 305,595 B（0.29 MiB） | Hydra运行输出 |
| `IsaacLab/scripts/` | 2 | 975,440 B（0.93 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/benchmarks/` | 3 | 115,703 B（0.11 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/demos/` | 3 | 191,391 B（0.18 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/environments/` | 3 | 58,428 B（0.06 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/imitation_learning/` | 3 | 119,427 B（0.11 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/reinforcement_learning/` | 3 | 199,421 B（0.19 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/sim2sim_transfer/` | 3 | 16,056 B（0.02 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/tools/` | 3 | 137,709 B（0.13 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/scripts/tutorials/` | 3 | 137,305 B（0.13 MiB） | 官方训练、推理、转换、教程或验证脚本 |
| `IsaacLab/source/` | 2 | 12,306,116 B（11.74 MiB） | 六个editable Python包 |
| `IsaacLab/source/isaaclab/` | 3 | 7,802,469 B（7.44 MiB） | 仿真/控制/环境核心 |
| `IsaacLab/source/isaaclab_assets/` | 3 | 198,994 B（0.19 MiB） | 官方机器人资产配置 |
| `IsaacLab/source/isaaclab_contrib/` | 3 | 282,570 B（0.27 MiB） | 贡献扩展 |
| `IsaacLab/source/isaaclab_mimic/` | 3 | 526,432 B（0.50 MiB） | 模仿学习支持 |
| `IsaacLab/source/isaaclab_rl/` | 3 | 183,421 B（0.17 MiB） | 算法桥接wrapper |
| `IsaacLab/source/isaaclab_tasks/` | 3 | 3,312,230 B（3.16 MiB） | 官方任务注册、奖励及配置 |
| `IsaacLab/tools/` | 2 | 139,436 B（0.13 MiB） | 上游项目生成模板/工具 |
| `IsaacLab/tools/template/` | 3 | 93,671 B（0.09 MiB） | 上游项目生成模板/工具 |
| `dogfight_env_freeze/` | 1 | 35,234,898 B（33.60 MiB） | 环境冻结与恢复证据 |
| `dogfight_env_freeze/backup/` | 2 | 21,545 B（0.02 MiB） | 冻结时环境/脚本原件备份 |
| `dogfight_env_freeze/backup/dogfight_rl_lock_files/` | 3 | 10,311 B（0.01 MiB） | 冻结时环境/脚本原件备份 |
| `dogfight_env_freeze/git/` | 2 | 35,111,598 B（33.49 MiB） | IsaacLab离线Git bundle |
| `dogfight_env_freeze/hashes/` | 2 | 2,551 B（0.00 MiB） | 冻结文件哈希 |
| `dogfight_env_freeze/manifests/` | 2 | 50,444 B（0.05 MiB） | 系统/包/驱动清单 |
| `dogfight_env_freeze/reports/` | 2 | 32,808 B（0.03 MiB） | 历史环境验证结果 |
| `dogfight_env_freeze/scripts/` | 2 | 5,320 B（0.01 MiB） | 冻结环境检查及官方训练启动器 |
| `dogfight_env_info/` | 1 | 17,132 B（0.02 MiB） | 历史系统、GPU、包版本文本 |
| `dogfight_final_tests/` | 1 | 2,262,398 B（2.16 MiB） | 官方ANYmal-C验收证据 |
| `dogfight_final_tests/logs/` | 2 | 6,725 B（0.01 MiB） | 验收前后环境健康日志 |
| `dogfight_final_tests/reports/` | 2 | 0 B（0.00 MiB） | 历史验收分类目录 |
| `dogfight_final_tests/screenshots/` | 2 | 0 B（0.00 MiB） | 历史图像分类目录 |
| `dogfight_final_tests/test1_long_ppo/` | 2 | 195,211 B（0.19 MiB） | 官方ANYmal-C训练/续训输出 |
| `dogfight_final_tests/test2_checkpoint/` | 2 | 70,103 B（0.07 MiB） | 官方恢复/推理验收 |
| `dogfight_final_tests/test3_gui/` | 2 | 1,980,915 B（1.89 MiB） | 官方ANYmal-C GUI视频/截图 |
| `dogfight_final_tests/test3_gui/screenshots/` | 3 | 807,026 B（0.77 MiB） | 官方ANYmal-C GUI视频/截图 |
| `dogfight_rl/` | 1 | 2,553,754,819 B（2435.45 MiB） | 机器狗业务主工程 |
| `dogfight_rl/.git/` | 2 | 15,233,349 B（14.53 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/branches/` | 3 | 0 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/hooks/` | 3 | 23,442 B（0.02 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/info/` | 3 | 240 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/logs/` | 3 | 2,536 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/objects/` | 3 | 15,179,611 B（14.48 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.git/refs/` | 3 | 205 B（0.00 MiB） | Git对象、引用、日志或钩子；保留历史 |
| `dogfight_rl/.pytest_cache/` | 2 | 3,400 B（0.00 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/.pytest_cache/v/` | 3 | 2,870 B（0.00 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/01_robots/` | 2 | 88,412,782 B（84.32 MiB） | 规范机器人层 |
| `dogfight_rl/01_robots/assets/` | 3 | 87,415,500 B（83.37 MiB） | 旧Dog A原始/转换/对称资产及空Dog B |
| `dogfight_rl/01_robots/configs/` | 3 | 14,358 B（0.01 MiB） | 站姿/PD/执行器/补偿YAML |
| `dogfight_rl/01_robots/python/` | 3 | 982,924 B（0.94 MiB） | 本体、几何、分析与物理诊断源码 |
| `dogfight_rl/02_training/` | 2 | 795,133,238 B（758.30 MiB） | 规范训练层 |
| `dogfight_rl/02_training/checkpoints/` | 3 | 0 B（0.00 MiB） | 空权重分类占位，实际权重在logs |
| `dogfight_rl/02_training/configs/` | 3 | 41,628 B（0.04 MiB） | 17份旧本体训练任务YAML |
| `dogfight_rl/02_training/deployment/` | 3 | 6,385 B（0.01 MiB） | actor重建与单体环境部署provider |
| `dogfight_rl/02_training/historical_tests/` | 3 | 2,262,398 B（2.16 MiB） | 历史官方ANYmal验收副本 |
| `dogfight_rl/02_training/logs/` | 3 | 792,359,232 B（755.65 MiB） | 规范实验产物 |
| `dogfight_rl/02_training/python/` | 3 | 326,534 B（0.31 MiB） | 单体DirectRLEnv/PPO/奖励/评估源码 |
| `dogfight_rl/02_training/scripts/` | 3 | 137,061 B（0.13 MiB） | 训练/续训/选优/评估入口 |
| `dogfight_rl/02_training/videos/` | 3 | 0 B（0.00 MiB） | 空占位，视频实际在日志 |
| `dogfight_rl/03_battle/` | 2 | 2,081,766 B（1.99 MiB） | 规范对战层 |
| `dogfight_rl/03_battle/assets/` | 3 | 0 B（0.00 MiB） | 地图资产占位；当前场地由Python创建 |
| `dogfight_rl/03_battle/logs/` | 3 | 1,646,674 B（1.57 MiB） | 对战事件与真实A门禁证据 |
| `dogfight_rl/03_battle/python/` | 3 | 0 B（0.00 MiB） | 高层包占位，实际实现位于source |
| `dogfight_rl/03_battle/scripts/` | 3 | 179,359 B（0.17 MiB） | 三代理、HUD与真实A验收入口 |
| `dogfight_rl/03_battle/source/` | 3 | 255,733 B（0.24 MiB） | 独立dogfight_v0包；规则/代理/仿真/HUD |
| `dogfight_rl/assets/` | 2 | 55,508,389 B（52.94 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/assets/arena/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/assets/dog_a/` | 3 | 30,981,792 B（29.55 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/assets/dog_a_symmetric_v1/` | 3 | 24,526,597 B（23.39 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/assets/dog_b/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/checkpoints/` | 2 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/checkpoints/dog_a/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/checkpoints/dog_b/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/configs/` | 2 | 55,986 B（0.05 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/docs/` | 2 | 35,568,312 B（33.92 MiB） | 模型/训练/对战指南；environment为冻结和远程报告 |
| `dogfight_rl/docs/environment/` | 3 | 35,268,949 B（33.64 MiB） | 模型/训练/对战指南；environment为冻结和远程报告 |
| `dogfight_rl/dogfight/` | 2 | 1,310,930 B（1.25 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/__pycache__/` | 3 | 990 B（0.00 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/dogfight/agents/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/analysis/` | 3 | 59,146 B（0.06 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/battle/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/geometry/` | 3 | 41,742 B（0.04 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/locomotion/` | 3 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/robots/` | 3 | 11,050 B（0.01 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/tasks/` | 3 | 326,534 B（0.31 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/dogfight/tests/` | 3 | 871,023 B（0.83 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/` | 2 | 789,392,332 B（752.82 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/back_gait_primitive_recovery/` | 3 | 21,077,312 B（20.10 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/base_frame_analysis/` | 3 | 6,311 B（0.01 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/dog_a_locomotion_ppo_smoke_v1/` | 3 | 345,658 B（0.33 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/dog_a_symmetric_static_equilibrium/` | 3 | 17,949 B（0.02 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/dog_a_symmetric_v1/` | 3 | 307,009 B（0.29 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/drop_test/` | 3 | 62,976 B（0.06 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/dynamic_contact_diagnosis/` | 3 | 2,026,096 B（1.93 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/external_home/` | 3 | 34,756,875 B（33.15 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/external_isaaclab/` | 3 | 65,329,298 B（62.30 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/implicit_actuator_symmetric_v1/` | 3 | 1,733,528 B（1.65 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/joint_direction_test/` | 3 | 220,606 B（0.21 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/lateral_ppo/` | 3 | 1,209,815 B（1.15 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/locomotion_smoke_test/` | 3 | 16,927,513 B（16.14 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/migration_smoke/` | 3 | 2,967,198 B（2.83 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/model_forensic_audit/` | 3 | 387,356 B（0.37 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/path_migration_20261025_smoke/` | 3 | 2,966,872 B（2.83 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/pd_alpha_equilibrium/` | 3 | 1,285,658 B（1.23 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/pd_dynamic_equilibrium/` | 3 | 4,162,551 B（3.97 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/pd_stand/` | 3 | 789,595 B（0.75 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/pd_stand_v2/` | 3 | 1,497,823 B（1.43 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/pd_symmetric_v1/` | 3 | 2,687,130 B（2.56 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/rsl_rl/` | 3 | 14,283,700 B（13.62 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/standing_geometry_v2/` | 3 | 67,634 B（0.06 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/standing_pose_preview/` | 3 | 5,634 B（0.01 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/static_contact_diagnosis/` | 3 | 26,966 B（0.03 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/straight_ppo/` | 3 | 118,809,232 B（113.31 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/v0/` | 3 | 989,026 B（0.94 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/v0_2b/` | 3 | 650,655 B（0.62 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_anti_slip_ppo/` | 3 | 134,934,340 B（128.68 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_anti_slip_train_smoke_16env_13iter/` | 3 | 3,295,510 B（3.14 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_anti_slip_train_smoke_16env_13iter_v2/` | 3 | 3,311,182 B（3.16 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_anti_slip_train_smoke_16env_13iter_v3/` | 3 | 3,311,336 B（3.16 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_anti_slip_train_smoke_256env_1iter/` | 3 | 2,305,840 B（2.20 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/x_bidirectional_ppo/` | 3 | 137,151,769 B（130.80 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/xy_body_frame_diagnosis/` | 3 | 3,726,158 B（3.55 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/xy_body_frame_ppo/` | 3 | 38,203,785 B（36.43 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/xy_discrete_ppo/` | 3 | 52,868,365 B（50.42 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/yaxis_recovery_400/` | 3 | 23,621,060 B（22.53 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/yaxis_reward_recovery_400/` | 3 | 24,231,406 B（23.11 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/yaxis_reward_recovery_A/` | 3 | 12,741,592 B（12.15 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/logs/yaxis_reward_recovery_B/` | 3 | 12,664,523 B（12.08 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/migration/` | 2 | 770,265,392 B（734.58 MiB） | 迁移/回滚工具与溯源 |
| `dogfight_rl/migration/backups/` | 3 | 768,900,886 B（733.28 MiB） | 迁移前完整归档与接收原件备份 |
| `dogfight_rl/migration/manifests/` | 3 | 887,169 B（0.85 MiB） | 原文件迁移、checkpoint、实验、哈希索引 |
| `dogfight_rl/migration/reports/` | 3 | 413,688 B（0.39 MiB） | 迁移时静态/仿真/训练/HUD结果 |
| `dogfight_rl/migration/tools/` | 3 | 44,125 B（0.04 MiB） | 历史迁移审查/报告/运行门禁工具 |
| `dogfight_rl/scripts/` | 2 | 322,287 B（0.31 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/scripts/__pycache__/` | 3 | 69,013 B（0.07 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/scripts/v0/` | 3 | 179,359 B（0.17 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/shared/` | 2 | 13,774 B（0.01 MiB） | 根路径、YAML解析、部署公共API与环境检查 |
| `dogfight_rl/shared/__pycache__/` | 3 | 5,501 B（0.01 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/shared/scripts/` | 3 | 5,867 B（0.01 MiB） | 根路径、YAML解析、部署公共API与环境检查 |
| `dogfight_rl/source/` | 2 | 255,733 B（0.24 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/source/dogfight_v0/` | 3 | 255,733 B（0.24 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `dogfight_rl/tests/` | 2 | 156,362 B（0.15 MiB） | 业务pytest契约/规则测试 |
| `dogfight_rl/tests/__pycache__/` | 3 | 132,409 B（0.13 MiB） | 运行缓存；D/E区分见第六部分 |
| `dogfight_rl/videos/` | 2 | 0 B（0.00 MiB） | 历史实体兼容快照/入口；不自动同步；以规范层维护 |
| `model/` | 1 | 1,958,667 B（1.87 MiB） | 新模型候选ROS包 |
| `model/meshes/` | 2 | 1,932,842 B（1.84 MiB） | 13个STL碰撞/视觉网格 |

# 附录二：规范业务源码、配置和模型逐文件分类

穷举以下规范目录中的 `.py/.sh/.yaml/.toml/.urdf/.usd/.stl/.xml/.csv/.zip/.STL` 重要文件；原始模型包中的其他辅助文件归该包C。兼容副本继承对应条目的用途，但撤除独立列E；未重复列出同内容路径。A/B/C指当前职责与后续处理，`C〔当前依赖〕`表示归档前必须先切换消费者；不是D。行号为相关定义起始行或文件起始行，便于定位。

| 文件 | 类别 | 实际用途与依赖依据 |
|---|---|---|
| [dogfight_rl/01_robots/assets/dog_a/config.yaml](dogfight_rl/01_robots/assets/dog_a/config.yaml) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_base.usd](dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_base.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_physics.usd](dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_physics.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_robot.usd](dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_robot.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_sensor.usd](dogfight_rl/01_robots/assets/dog_a/configuration/dog_a_sensor.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/dog_a.usd](dogfight_rl/01_robots/assets/dog_a/dog_a.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/urdf/dog_a_import.urdf](dogfight_rl/01_robots/assets/dog_a/urdf/dog_a_import.urdf) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/config.yaml](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/config.yaml) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_base.usd](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_base.usd) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_physics.usd](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_physics.usd) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_robot.usd](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_robot.usd) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_sensor.usd](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_sensor.usd) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/dog_a.usd](dogfight_rl/01_robots/assets/dog_a/usd_attempt_002_named_joints/dog_a.usd) | C〔当前依赖〕 | 旧模型默认训练USD及其转换配置/子层；env与factory仍依赖 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/generation/generate_symmetric_model.py](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/generation/generate_symmetric_model.py) | B/C | 旧对称模型生成工具，算法可参考，参数与输出归旧模型 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_CALF.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_CALF.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_HIP.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_HIP.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_THIGH.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FL_THIGH.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_CALF_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_CALF_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_HIP_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_HIP_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_THIGH_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/FR_THIGH_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_CALF.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_CALF.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_HIP.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_HIP.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_THIGH.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RL_THIGH.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_CALF_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_CALF_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_HIP_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_HIP_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_THIGH_MIRRORED.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/RR_THIGH_MIRRORED.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/base_link_symmetric.STL](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/meshes/base_link_symmetric.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/urdf/dog_a_symmetric_v1.urdf](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/urdf/dog_a_symmetric_v1.urdf) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/config.yaml](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/config.yaml) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_base.usd](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_base.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_physics.usd](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_physics.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_robot.usd](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_robot.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_sensor.usd](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_sensor.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/dog_a_symmetric_v1.usd](dogfight_rl/01_robots/assets/dog_a_symmetric_v1/usd/dog_a_symmetric_v1.usd) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/config/joint_names_fix_new.SLDASM.yaml](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/config/joint_names_fix_new.SLDASM.yaml) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/base_link.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/base_link.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou1.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou1.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou2.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lhou2.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian1.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian1.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian2.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/lqian2.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou1.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou1.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou2.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rhou2.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian1.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian1.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian2.STL](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/meshes/rqian2.STL) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/package.xml](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/package.xml) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/urdf/fix_new.SLDASM.csv](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/urdf/fix_new.SLDASM.csv) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM/urdf/fix_new.SLDASM.urdf](dogfight_rl/01_robots/assets/original/fix_new.SLDASM/urdf/fix_new.SLDASM.urdf) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/fix_new.SLDASM.zip](dogfight_rl/01_robots/assets/original/fix_new.SLDASM.zip) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/assets/original/received/机器狗模型.zip](dogfight_rl/01_robots/assets/original/received/机器狗模型.zip) | C | 旧模型资产/生成溯源；URDF、USD子层、几何诊断构成引用闭包 |
| [dogfight_rl/01_robots/configs/dog_a_dynamic_equilibrium_compensation.yaml](dogfight_rl/01_robots/configs/dog_a_dynamic_equilibrium_compensation.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/dog_a_standing_pose.yaml](dogfight_rl/01_robots/configs/dog_a_standing_pose.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/dog_a_standing_pose_v2.yaml](dogfight_rl/01_robots/configs/dog_a_standing_pose_v2.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/dog_a_symmetric_v1_implicit_actuator.yaml](dogfight_rl/01_robots/configs/dog_a_symmetric_v1_implicit_actuator.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/dog_a_symmetric_v1_standing_pose.yaml](dogfight_rl/01_robots/configs/dog_a_symmetric_v1_standing_pose.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/pd_alpha_equilibrium.yaml](dogfight_rl/01_robots/configs/pd_alpha_equilibrium.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/pd_symmetric_v1_01.yaml](dogfight_rl/01_robots/configs/pd_symmetric_v1_01.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/pd_symmetric_v1_02.yaml](dogfight_rl/01_robots/configs/pd_symmetric_v1_02.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/pd_v2_01.yaml](dogfight_rl/01_robots/configs/pd_v2_01.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/configs/pd_v2_02.yaml](dogfight_rl/01_robots/configs/pd_v2_02.yaml) | B | 旧站姿/PD/执行器/补偿参数；配置被本体诊断或训练动态加载 |
| [dogfight_rl/01_robots/python/dogfight/analysis/analyze_implicit_standing.py](dogfight_rl/01_robots/python/dogfight/analysis/analyze_implicit_standing.py) | B/C | 旧实验分析；方法可复用，旧数值结论归档 |
| [dogfight_rl/01_robots/python/dogfight/analysis/dog_a_symmetric_static_equilibrium.py](dogfight_rl/01_robots/python/dogfight/analysis/dog_a_symmetric_static_equilibrium.py) | B/C | 旧实验分析；方法可复用，旧数值结论归档 |
| [dogfight_rl/01_robots/python/dogfight/geometry/foot_contact_solver.py](dogfight_rl/01_robots/python/dogfight/geometry/foot_contact_solver.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/robots/dog_a_cfg.py](dogfight_rl/01_robots/python/dogfight/robots/dog_a_cfg.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/robots/prepare_dog_a_import_urdf.py](dogfight_rl/01_robots/python/dogfight/robots/prepare_dog_a_import_urdf.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/analyze_contact_dynamics.py](dogfight_rl/01_robots/python/dogfight/tests/analyze_contact_dynamics.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/analyze_dynamic_equilibrium.py](dogfight_rl/01_robots/python/dogfight/tests/analyze_dynamic_equilibrium.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/analyze_pd_alpha_equilibrium.py](dogfight_rl/01_robots/python/dogfight/tests/analyze_pd_alpha_equilibrium.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/analyze_pd_v2_02.py](dogfight_rl/01_robots/python/dogfight/tests/analyze_pd_v2_02.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/back_gait_reward_sanity.py](dogfight_rl/01_robots/python/dogfight/tests/back_gait_reward_sanity.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/base_frame_analysis.py](dogfight_rl/01_robots/python/dogfight/tests/base_frame_analysis.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/collider_foot_point_micro.py](dogfight_rl/01_robots/python/dogfight/tests/collider_foot_point_micro.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/contact_dynamics_diagnosis.py](dogfight_rl/01_robots/python/dogfight/tests/contact_dynamics_diagnosis.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/contact_force_sanity.py](dogfight_rl/01_robots/python/dogfight/tests/contact_force_sanity.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_free_drop.py](dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_free_drop.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_joint_direction_test.py](dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_joint_direction_test.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_runtime_audit.py](dogfight_rl/01_robots/python/dogfight/tests/dog_a_symmetric_runtime_audit.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/dog_a_x_reward_sanity.py](dogfight_rl/01_robots/python/dogfight/tests/dog_a_x_reward_sanity.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/dog_a_xy_reward_sanity.py](dogfight_rl/01_robots/python/dogfight/tests/dog_a_xy_reward_sanity.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/drop_test.py](dogfight_rl/01_robots/python/dogfight/tests/drop_test.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/fk_jacobian_micro.py](dogfight_rl/01_robots/python/dogfight/tests/fk_jacobian_micro.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/identify_dynamic_equilibrium_sensitivity.py](dogfight_rl/01_robots/python/dogfight/tests/identify_dynamic_equilibrium_sensitivity.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/implicit_actuator_symmetric_v1.py](dogfight_rl/01_robots/python/dogfight/tests/implicit_actuator_symmetric_v1.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/joint_direction_test.py](dogfight_rl/01_robots/python/dogfight/tests/joint_direction_test.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/mirrored_standing_pose_search.py](dogfight_rl/01_robots/python/dogfight/tests/mirrored_standing_pose_search.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_alpha_equilibrium_trial.py](dogfight_rl/01_robots/python/dogfight/tests/pd_alpha_equilibrium_trial.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_dynamic_equilibrium_trial.py](dogfight_rl/01_robots/python/dogfight/tests/pd_dynamic_equilibrium_trial.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_stand_test.py](dogfight_rl/01_robots/python/dogfight/tests/pd_stand_test.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_stand_v2.py](dogfight_rl/01_robots/python/dogfight/tests/pd_stand_v2.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_stand_v2_02.py](dogfight_rl/01_robots/python/dogfight/tests/pd_stand_v2_02.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/pd_symmetric_v1.py](dogfight_rl/01_robots/python/dogfight/tests/pd_symmetric_v1.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/prefilter_dynamic_equilibrium.py](dogfight_rl/01_robots/python/dogfight/tests/prefilter_dynamic_equilibrium.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/runtime_initial_state_diagnosis.py](dogfight_rl/01_robots/python/dogfight/tests/runtime_initial_state_diagnosis.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/spawn_robot.py](dogfight_rl/01_robots/python/dogfight/tests/spawn_robot.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/standing_pose_preview.py](dogfight_rl/01_robots/python/dogfight/tests/standing_pose_preview.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/standing_pose_search_v2.py](dogfight_rl/01_robots/python/dogfight/tests/standing_pose_search_v2.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/01_robots/python/dogfight/tests/static_contact_diagnosis.py](dogfight_rl/01_robots/python/dogfight/tests/static_contact_diagnosis.py) | B | 旧URDF、Mesh、关节/足点/动力学诊断；由脚本入口或dogfight规范包加载 |
| [dogfight_rl/02_training/configs/back_gait_primitive_recovery.yaml](dogfight_rl/02_training/configs/back_gait_primitive_recovery.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_bidirectional_lateral_ppo.yaml](dogfight_rl/02_training/configs/dog_a_bidirectional_lateral_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_bidirectional_x_ppo.yaml](dogfight_rl/02_training/configs/dog_a_bidirectional_x_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_body_xy_transition_ppo.yaml](dogfight_rl/02_training/configs/dog_a_body_xy_transition_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_locomotion_ppo_smoke_v1.yaml](dogfight_rl/02_training/configs/dog_a_locomotion_ppo_smoke_v1.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_original_locomotion_ppo_smoke.yaml](dogfight_rl/02_training/configs/dog_a_original_locomotion_ppo_smoke.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_original_straight_ppo.yaml](dogfight_rl/02_training/configs/dog_a_original_straight_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_anti_slip_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_anti_slip_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_command_transition_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_command_transition_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_left_focus_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_left_focus_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_left_reexplore_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_left_reexplore_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_mixed_drift_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_mixed_drift_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_x_right_recovery_ppo.yaml](dogfight_rl/02_training/configs/dog_a_x_right_recovery_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_xy_discrete_transition_ppo.yaml](dogfight_rl/02_training/configs/dog_a_xy_discrete_transition_ppo.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/dog_a_yaxis_recovery_400.yaml](dogfight_rl/02_training/configs/dog_a_yaxis_recovery_400.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/yaxis_reward_recovery_A.yaml](dogfight_rl/02_training/configs/yaxis_reward_recovery_A.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/configs/yaxis_reward_recovery_B.yaml](dogfight_rl/02_training/configs/yaxis_reward_recovery_B.yaml) | B | 旧运动任务配置；train/evaluate经环境变量与YAML动态读取 |
| [dogfight_rl/02_training/deployment/__init__.py](dogfight_rl/02_training/deployment/__init__.py) | B | shared.policy动态加载的actor/spec和单体环境部署实现；包初始化 |
| [dogfight_rl/02_training/deployment/policy_runtime.py](dogfight_rl/02_training/deployment/policy_runtime.py) | B | shared.policy动态加载的actor/spec和单体环境部署实现 |
| [dogfight_rl/02_training/python/dogfight/tasks/__init__.py](dogfight_rl/02_training/python/dogfight/tasks/__init__.py) | B | 训练任务包初始化；包初始化 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/__init__.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/__init__.py) | B | 训练任务包初始化；包初始化 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/action_audit_wrapper.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/action_audit_wrapper.py) | B | 策略缩放、clip、动作遥测及训练安全门禁 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/env.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/env.py) | B | DirectRLEnv单体环境；硬编码48/12、旧关节和足端映射 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/evaluate.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/evaluate.py) | B | actor推理、轨迹、reward/足端评估和可视化 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/reward_terms.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/reward_terms.py) | B | 通用滑移/air-time/抬脚/进度奖励tensor核 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/train.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/train.py) | B | RSL-RL PPO runner；配置、旧权重恢复和遥测 |
| [dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/validate.py](dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/validate.py) | B | 零动作物理/有限值/重置检查 |
| [dogfight_rl/02_training/scripts/analyze_dog_a_four_direction.py](dogfight_rl/02_training/scripts/analyze_dog_a_four_direction.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/compare_dog_a_x_directions.py](dogfight_rl/02_training/scripts/compare_dog_a_x_directions.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/evaluate_dog_a_x_directions.sh](dogfight_rl/02_training/scripts/evaluate_dog_a_x_directions.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_x_700_from_300.sh](dogfight_rl/02_training/scripts/resume_dog_a_x_700_from_300.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_x_finetune_300_from_999.sh](dogfight_rl/02_training/scripts/resume_dog_a_x_finetune_300_from_999.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_x_straight_500_from_1599.sh](dogfight_rl/02_training/scripts/resume_dog_a_x_straight_500_from_1599.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_x_transition_300_from_1299.sh](dogfight_rl/02_training/scripts/resume_dog_a_x_transition_300_from_1299.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_xy_500_from_2099.sh](dogfight_rl/02_training/scripts/resume_dog_a_xy_500_from_2099.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/resume_dog_a_yaxis_recovery_400.sh](dogfight_rl/02_training/scripts/resume_dog_a_yaxis_recovery_400.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/run_yaxis_reward_recovery_smoke.sh](dogfight_rl/02_training/scripts/run_yaxis_reward_recovery_smoke.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/select_best_back_gait_checkpoint.py](dogfight_rl/02_training/scripts/select_best_back_gait_checkpoint.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/select_best_training_checkpoint.py](dogfight_rl/02_training/scripts/select_best_training_checkpoint.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/train_back_gait_primitive_recovery_400.sh](dogfight_rl/02_training/scripts/train_back_gait_primitive_recovery_400.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/train_original_dog_a_straight.py](dogfight_rl/02_training/scripts/train_original_dog_a_straight.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_back_gait_five_direction_fresh_reset_gui.sh](dogfight_rl/02_training/scripts/validate_back_gait_five_direction_fresh_reset_gui.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_back_gait_primitive_config.py](dogfight_rl/02_training/scripts/validate_back_gait_primitive_config.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_back_gait_primitive_fresh_reset_gui.sh](dogfight_rl/02_training/scripts/validate_back_gait_primitive_fresh_reset_gui.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_dog_a_yaxis_recovery_400_gui.sh](dogfight_rl/02_training/scripts/validate_dog_a_yaxis_recovery_400_gui.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_yaxis_recovery_configs.py](dogfight_rl/02_training/scripts/validate_yaxis_recovery_configs.py) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/validate_yaxis_reward_recovery_gui.sh](dogfight_rl/02_training/scripts/validate_yaxis_reward_recovery_gui.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/visualize_dog_a_left_stop_right.sh](dogfight_rl/02_training/scripts/visualize_dog_a_left_stop_right.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/visualize_dog_a_straightness_left_stop_right.sh](dogfight_rl/02_training/scripts/visualize_dog_a_straightness_left_stop_right.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/visualize_dog_a_transition_left_stop_right.sh](dogfight_rl/02_training/scripts/visualize_dog_a_transition_left_stop_right.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/02_training/scripts/visualize_dog_a_xy_continuous.sh](dogfight_rl/02_training/scripts/visualize_dog_a_xy_continuous.sh) | B/C | 历史分阶段续训/评估/选优入口；需切换模型、恢复源与实验目录 |
| [dogfight_rl/03_battle/scripts/v0/run_dog_a_battle_integration_test.py](dogfight_rl/03_battle/scripts/v0/run_dog_a_battle_integration_test.py) | A/B | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_dog_a_v0_smoke_test.py](dogfight_rl/03_battle/scripts/v0/run_dog_a_v0_smoke_test.py) | A/B | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v02_hud_smoke_tests.py](dogfight_rl/03_battle/scripts/v0/run_v02_hud_smoke_tests.py) | A | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v02b_prebattle_gates.py](dogfight_rl/03_battle/scripts/v0/run_v02b_prebattle_gates.py) | A/B | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v0_battle_demo.py](dogfight_rl/03_battle/scripts/v0/run_v0_battle_demo.py) | A | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v0_gui.py](dogfight_rl/03_battle/scripts/v0/run_v0_gui.py) | A | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v0_headless.py](dogfight_rl/03_battle/scripts/v0/run_v0_headless.py) | A | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/scripts/v0/run_v0_smoke_tests.py](dogfight_rl/03_battle/scripts/v0/run_v0_smoke_tests.py) | A | 对战/模型替换验收入口；真实A脚本参数需要迁移 |
| [dogfight_rl/03_battle/source/dogfight_v0/config/extension.toml](dogfight_rl/03_battle/source/dogfight_v0/config/extension.toml) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/agent_interface.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/agent_interface.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_factory.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_factory.py) | B | 旧Dog A模型/关节/坐标/权重/尺寸适配，必须为新模型修改 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_locomotion_adapter.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_locomotion_adapter.py) | B | 旧Dog A模型/关节/坐标/权重/尺寸适配，必须为新模型修改 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/locomotion_interface.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/locomotion_interface.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/proxy_agent.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/proxy_agent.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/real_dog_agent.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/real_dog_agent.py) | B | 旧Dog A模型/关节/坐标/权重/尺寸适配，必须为新模型修改 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/real_locomotion_adapter.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/real_locomotion_adapter.py) | A | 通用速度接口skeleton与mock；不是已完成策略控制器 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/map_interface.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/map_interface.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/spawn_manager.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/spawn_manager.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/test_map.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/arena/test_map.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/battle_manager.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/battle_manager.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/health_system.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/health_system.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/intel_service.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/intel_service.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/interfaces.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/interfaces.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/ray_query.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/ray_query.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/scripted_policy.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/scripted_policy.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/types.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/types.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/visibility_service.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/visibility_service.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/weapon_service.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/battle/weapon_service.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/config/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/config/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/config/battle_cfg.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/config/battle_cfg.py) | B | 旧Dog A模型/关节/坐标/权重/尺寸适配，必须为新模型修改 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/logging/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/logging/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/logging/battle_logger.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/logging/battle_logger.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/navigation_interface.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/navigation_interface.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/simple_navigation.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/navigation/simple_navigation.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/runtime.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/runtime.py) | A | 组合三Proxy+PhysX射线+脚本策略与manager |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/physx_ray_query.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/physx_ray_query.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/scene.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/sim/scene.py) | A | 同场景三个kinematic代理；保留基线并新增三articulation场景 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/ui/__init__.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/ui/__init__.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线；包初始化 |
| [dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/ui/battle_hud.py](dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/ui/battle_hud.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/pyproject.toml](dogfight_rl/03_battle/source/dogfight_v0/pyproject.toml) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/03_battle/source/dogfight_v0/setup.py](dogfight_rl/03_battle/source/dogfight_v0/setup.py) | A | 模型无关三代理规则/接口/导航/日志/可视化或仿真基线 |
| [dogfight_rl/shared/__init__.py](dogfight_rl/shared/__init__.py) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖；包初始化 |
| [dogfight_rl/shared/paths.py](dogfight_rl/shared/paths.py) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖 |
| [dogfight_rl/shared/policy.py](dogfight_rl/shared/policy.py) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖 |
| [dogfight_rl/shared/scripts/check_environment.py](dogfight_rl/shared/scripts/check_environment.py) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖 |
| [dogfight_rl/shared/scripts/check_environment.sh](dogfight_rl/shared/scripts/check_environment.sh) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖 |
| [dogfight_rl/shared/scripts/manage_nvidia_apt_hold.sh](dogfight_rl/shared/scripts/manage_nvidia_apt_hold.sh) | A | 项目路径/部署边界/环境冻结检查，跨层直接依赖 |
| [dogfight_rl/tests/conftest.py](dogfight_rl/tests/conftest.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_dog_a_interface.py](dogfight_rl/tests/test_dog_a_interface.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_hud.py](dogfight_rl/tests/test_hud.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_intel_5s.py](dogfight_rl/tests/test_intel_5s.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_navigation.py](dogfight_rl/tests/test_navigation.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_portable_resources.py](dogfight_rl/tests/test_portable_resources.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_project_paths.py](dogfight_rl/tests/test_project_paths.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_real_adapters.py](dogfight_rl/tests/test_real_adapters.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_round.py](dogfight_rl/tests/test_round.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_spawn.py](dogfight_rl/tests/test_spawn.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_visibility.py](dogfight_rl/tests/test_visibility.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [dogfight_rl/tests/test_weapon.py](dogfight_rl/tests/test_weapon.py) | A/B | 规则/adapter/path契约测试，保留并更新模型样本；本次未执行pytest |
| [model/meshes/base_collision.stl](model/meshes/base_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lf_hip_pitch_collision.stl](model/meshes/link_lf_hip_pitch_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lf_hip_roll_collision.stl](model/meshes/link_lf_hip_roll_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lf_knee_collision.stl](model/meshes/link_lf_knee_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lr_hip_pitch_collision.stl](model/meshes/link_lr_hip_pitch_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lr_hip_roll_collision.stl](model/meshes/link_lr_hip_roll_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_lr_knee_collision.stl](model/meshes/link_lr_knee_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rf_hip_pitch_collision.stl](model/meshes/link_rf_hip_pitch_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rf_hip_roll_collision.stl](model/meshes/link_rf_hip_roll_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rf_knee_collision.stl](model/meshes/link_rf_knee_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rr_hip_pitch_collision.stl](model/meshes/link_rr_hip_pitch_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rr_hip_roll_collision.stl](model/meshes/link_rr_hip_roll_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/meshes/link_rr_knee_collision.stl](model/meshes/link_rr_knee_collision.stl) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/package.xml](model/package.xml) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/robot.preview.urdf](model/robot.preview.urdf) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |
| [model/robot.urdf](model/robot.urdf) | A/E | 12-DOF候选模型原件/ROS资源；URDF引用闭包有效；是否最终新模型待确认 |

# 附录三：规范训练日志的逐实验空间与处理

均为 `/home/zxq/robot_projects/dogfight_rl/02_training/logs/` 下直接子项。大小含其子文件；此表不与父目录占用相加。checkpoint/导出数仅按 `.pt/.pth/.onnx` 计。所有旧实验为C或当前依赖A/C；没有因失败/重复而列D。

| 实验/文件 | 文件数 | 逻辑大小 | 权重/导出数 | 用途与建议 |
|---|---:|---:|---:|---|
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/back_gait_primitive_recovery` | 29 | 21,077,312 B（20.10 MiB） | 19 | 当前默认actor、完整BACK恢复实验；当前A，替换后C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/back_gait_primitive_recovery_training.log` | 1 | 877,185 B（0.84 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/base_frame_analysis` | 1 | 6,311 B（0.01 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/dog_a_locomotion_ppo_smoke_v1` | 9 | 345,658 B（0.33 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/dog_a_symmetric_static_equilibrium` | 4 | 17,949 B（0.02 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/dog_a_symmetric_v1` | 12 | 307,009 B（0.29 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/drop_test` | 2 | 62,976 B（0.06 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/dynamic_contact_diagnosis` | 42 | 2,026,096 B（1.93 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/external_home` | 13 | 34,756,875 B（33.15 MiB） | 5 | 官方ANYmal-C框架验证历史，非旧Dog A；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/external_isaaclab` | 36 | 65,329,298 B（62.30 MiB） | 11 | 官方ANYmal-C框架验证历史，非旧Dog A；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/implicit_actuator_symmetric_v1` | 27 | 1,733,528 B（1.65 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/joint_direction_test` | 4 | 220,606 B（0.21 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/lateral_ppo` | 8 | 1,209,815 B（1.15 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/locomotion_smoke_test` | 62 | 16,927,513 B（16.14 MiB） | 15 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/migration_smoke` | 10 | 2,967,198 B（2.83 MiB） | 3 | 路径/结构迁移后短PPO恢复验证；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/model_forensic_audit` | 19 | 387,356 B（0.37 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/path_migration_20261025_physical_smoke` | 10 | 2,966,900 B（2.83 MiB） | 3 | 路径/结构迁移后短PPO恢复验证；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/path_migration_20261025_smoke` | 10 | 2,966,872 B（2.83 MiB） | 3 | 路径/结构迁移后短PPO恢复验证；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/pd_alpha_equilibrium` | 30 | 1,285,658 B（1.23 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/pd_dynamic_equilibrium` | 43 | 4,162,551 B（3.97 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/pd_stand` | 21 | 789,595 B（0.75 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/pd_stand_v2` | 21 | 1,497,823 B（1.43 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/pd_symmetric_v1` | 28 | 2,687,130 B（2.56 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/rsl_rl` | 84 | 14,283,700 B（13.62 MiB） | 12 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/standing_geometry_v2` | 1 | 67,634 B（0.06 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/standing_pose_preview` | 3 | 5,634 B（0.01 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/static_contact_diagnosis` | 4 | 26,966 B（0.03 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/straight_ppo` | 149 | 118,809,232 B（113.31 MiB） | 113 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/v0` | 50 | 989,026 B（0.94 MiB） | 0 | 对战旧日志快照；03_battle/logs有规范对应；C/E |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/v0_2b` | 5 | 650,655 B（0.62 MiB） | 0 | 对战旧日志快照；03_battle/logs有规范对应；C/E |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_candidate_2300_neg.json` | 1 | 4,737 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_candidate_2300_pos.json` | 1 | 4,697 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_candidate_3500_neg.json` | 1 | 4,719 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_candidate_3500_pos.json` | 1 | 4,740 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_ppo` | 184 | 134,934,340 B（128.68 MiB） | 99 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_probe_short.json` | 1 | 4,683 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_reward_sanity.json` | 1 | 1,014 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_neg.json` | 1 | 4,720 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_pos.json` | 1 | 4,733 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_zero.json` | 1 | 4,729 B（0.00 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter` | 10 | 3,295,510 B（3.14 MiB） | 4 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2` | 10 | 3,311,182 B（3.16 MiB） | 4 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3` | 10 | 3,311,336 B（3.16 MiB） | 4 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_anti_slip_train_smoke_256env_1iter` | 9 | 2,305,840 B（2.20 MiB） | 3 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/x_bidirectional_ppo` | 182 | 137,151,769 B（130.80 MiB） | 136 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_body_frame_diagnosis` | 15 | 3,726,158 B（3.55 MiB） | 0 | 旧本体站姿/几何/接触/PD或奖励诊断证据；C |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_body_frame_ppo` | 70 | 38,203,785 B（36.43 MiB） | 20 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_adapt_50iter.log` | 1 | 58,241 B（0.06 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_adapt_plus_200iter.log` | 1 | 206,869 B（0.20 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_reset_ycmd_200iter.log` | 1 | 207,288 B（0.20 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/xy_discrete_ppo` | 52 | 52,868,365 B（50.42 MiB） | 26 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_recovery_400` | 33 | 23,621,060 B（22.53 MiB） | 20 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_recovery_400.zip` | 1 | 19,364,431 B（18.47 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_recovery_400_training.log` | 1 | 407,516 B（0.39 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_400` | 33 | 24,231,406 B（23.11 MiB） | 20 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_400.zip` | 1 | 19,632,248 B（18.72 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_400_training.log` | 1 | 414,338 B（0.40 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_A` | 27 | 12,741,592 B（12.15 MiB） | 8 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_A_training.log` | 1 | 110,299 B（0.11 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_B` | 27 | 12,664,523 B（12.08 MiB） | 8 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |
| `/home/zxq/robot_projects/dogfight_rl/02_training/logs/yaxis_reward_recovery_B_training.log` | 1 | 110,303 B（0.11 MiB） | 0 | 旧Dog A运动训练/评估/打包成果；C，脚本可能恢复引用 |

# 附录四：当前规范权重/导出完整清单与哈希

本次未反序列化所有checkpoint；以只读SHA256核对已有 `migration/manifests/CHECKPOINTS.json` 的530项，**全部存在且哈希一致**。其历史load=PASS保留为历史证据，不能说本次重新加载通过。当前规范日志共536项，新增6项是20261025两次smoke。其他根层兼容副本和IsaacLab官方权重不重复计入本表。`external_home/external_isaaclab` 是ANYmal-C，其余主要为旧Dog A；均保留C，默认旧actor在消费者切换前保留A。

| 规范文件（dogfight_rl 下） | 字节数 | SHA256 | 索引/处理 |
|---|---:|---|---|
| `02_training/logs/back_gait_primitive_recovery/model_3950.pt` | 983,925 | `2696ce188bdecb2c75f53edc539bd601c0b572e7c04792ea3a265536ab3f3896` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_3975.pt` | 983,925 | `48613d0b828beccb18dd7ecc17b69833d7638a5ffa6241d7defb39998d6b9406` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4000.pt` | 983,925 | `a7c98a0c749fee503ebbb3f62cc72c20493a5b19323f39fe6683d94bcca48a5b` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4025.pt` | 983,925 | `85b145cc483888cfaa405f454c6483c64e4073c61c9732c93d89e32787932162` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4050.pt` | 983,925 | `1609bf400163c041be4fee1c7fe70c2895b5e765f1d1107d56e4f51a11917c62` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4075.pt` | 983,925 | `62f24898d181a005534ebc1cb765e9e3f3508c6ee3443d89f64f0bd3109273e9` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4100.pt` | 983,925 | `560fe53a7b9781523a7778d4cb01ac9117fc368a8a1d245dd595bc9dc7722a5a` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4125.pt` | 983,925 | `b44f3c79bc5b7d9747886bd3e2371e74fdb05705a799fd01297fb54f731f5e7a` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4150.pt` | 983,925 | `78f34620419cebb0695e8ef195dce46b9281cd36eff7979034804c3254dea8a5` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4175.pt` | 983,925 | `7fba1ee1dc1ea5c7c3087c80625a3b7756538fa55409c520cb5fc2cafbd2df9c` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4200.pt` | 983,925 | `33be5a051537dd4fd821c3f2df9176317a63c07739790bade915ce54ef258306` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4225.pt` | 983,925 | `038b9e458633b8959a7a6c5b2baff4b6321cab0a3d4491822523883b556d94fd` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4250.pt` | 983,925 | `152706a4ea9f83f2cc1e71ba934eaf4d4629ef2eb1db4798e055f8ffc4b685ae` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4275.pt` | 983,925 | `ead587d3ddc77dfcc2079647cf27c56e14e414c2bafc32c0b8ddb3c1a45d2007` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4300.pt` | 983,925 | `7e324e44d91e03744995302b61622f014efd5136b86f4461f6951f8fbc5de09b` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4325.pt` | 983,925 | `9ca12fb29977fa3ba3b039813ca7aed280a40d7333de59e41ab97cd5fcc70fe4` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_4349.pt` | 984,117 | `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | 历史索引哈希一致；C |
| `02_training/logs/back_gait_primitive_recovery/model_final.pt` | 984,117 | `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | 默认factory/launch依赖；当前A，迁移后C |
| `02_training/logs/back_gait_primitive_recovery/resume_iteration_3950.pt` | 984,117 | `fa10aba5c45a41a72b15b88784bea0844d106f2fcf7bfc9865f016a476d36dd9` | 历史索引哈希一致；C |
| `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-17-12/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-17-12/model_100.pt` | 6,882,219 | `2e1ac42832e64a65c44825b9e683c18c1c5af1c9b2fc204cf080965b80eb45e4` | 历史索引哈希一致；C |
| `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-17-12/model_150.pt` | 6,882,219 | `f5fe582b71d482357314d19173f3d0eccaaa30f076c4daa271041f027c5a52e8` | 历史索引哈希一致；C |
| `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-17-12/model_50.pt` | 6,882,145 | `1dcb2b80ac2b2150fe775dd20aab3c826177e614c01f401a4c13342c3eb17466` | 历史索引哈希一致；C |
| `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-19-41/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_12-49-40_anymal_c_256/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_12-51-47_anymal_c_256_dependency_regression/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-14-59_golden_freeze_verification/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-32-22_dogfight_final_test1_50_retry/model_0.pt` | 6,881,559 | `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-32-22_dogfight_final_test1_50_retry/model_49.pt` | 6,882,145 | `61839040ddffea4c963a46a79c754604c31f0e5722df18b4661e59538fbd37a3` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-34-39_dogfight_final_test1_resume_to_100/exported/policy.onnx` | 1,147,671 | `5da7f988751b5fc51036d2f1c6079549c9d723bcab6207c77764f22222183c42` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-34-39_dogfight_final_test1_resume_to_100/exported/policy.pt` | 1,158,546 | `83d0c5d6da6b511263788c93b3784d661264e617c327fb702cbd9c7467c5745b` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-34-39_dogfight_final_test1_resume_to_100/model_50.pt` | 6,882,145 | `e9f28b061a9b6267b8f08b3b9d28286b1141f3b6b7b195725c506e3c86c7789c` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-34-39_dogfight_final_test1_resume_to_100/model_99.pt` | 6,882,145 | `21a9f8230835c472f7fd2ba306e6fd19387e4c4c4e5cb6a14450ba0645670d5b` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-36-36_dogfight_final_test2_resume_5/model_100.pt` | 6,882,219 | `ce92a9c5b0ab08168cfd002ac7bd73898b237f3c181b522f7cbb2c7b17b8ce16` | 历史索引哈希一致；C |
| `02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-36-36_dogfight_final_test2_resume_5/model_103.pt` | 6,882,219 | `fdacdcafd6d2fde3cf3be54d110681cd3643d8475cb22732255b14d8ed7e324c` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_0.pt` | 983,255 | `f12a916e6eb6661ee91abfaba6a41d0b4212b00f4203700543e01df50f664737` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_0_initial.pt` | 328,104 | `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_9.pt` | 983,255 | `a520a12c302e1c3951d8bba813818e78a0726774da6c34c205ba552ee6a4f981` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_final.pt` | 983,255 | `a520a12c302e1c3951d8bba813818e78a0726774da6c34c205ba552ee6a4f981` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/iteration_10.pt` | 983,255 | `a520a12c302e1c3951d8bba813818e78a0726774da6c34c205ba552ee6a4f981` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_10.pt` | 983,777 | `b15945627de58f09e16305bbc881674b368ffc0cbc8dacff623db77c72457797` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_20.pt` | 983,777 | `94ac383c94e72812cce30ddac5623bf5caf66c3828d2954f4d6e657281daa360` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_29.pt` | 983,777 | `2befa5aee2d4fcf1ba694e65b40b341d68aca5d2112761e07f6e41c1e4d47153` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_final.pt` | 983,777 | `2befa5aee2d4fcf1ba694e65b40b341d68aca5d2112761e07f6e41c1e4d47153` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/iteration_10.pt` | 983,777 | `2befa5aee2d4fcf1ba694e65b40b341d68aca5d2112761e07f6e41c1e4d47153` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_30.pt` | 983,777 | `0c22ecc0199e776052ed73265cfc1b8b0d899c77dd5b5e3cbef745173c137d89` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_40.pt` | 983,777 | `daf411fa204205ad9950d1940aec599a4b6f5da6b98d1f2ec7f6d2354896d4bd` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_50.pt` | 983,777 | `ad509a23d905553f51bfd61cdd77878793a2b79f315319089cb319ea7a2f3088` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_59.pt` | 983,777 | `b29f383c2b8d1ef655d395b4e5d2f7e23543abeba6ffc89c8a58dca91e042622` | 历史索引哈希一致；C |
| `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_final.pt` | 983,777 | `b29f383c2b8d1ef655d395b4e5d2f7e23543abeba6ffc89c8a58dca91e042622` | 历史索引哈希一致；C |
| `02_training/logs/migration_smoke/one_update/model_4350.pt` | 984,117 | `c7ac2ba3a71d553c320429c8bbc2de10a019747c0963dfe2675e66960905bfd5` | 历史索引哈希一致；C |
| `02_training/logs/migration_smoke/one_update/model_final.pt` | 984,117 | `c7ac2ba3a71d553c320429c8bbc2de10a019747c0963dfe2675e66960905bfd5` | 历史索引哈希一致；C |
| `02_training/logs/migration_smoke/one_update/resume_iteration_4350.pt` | 984,117 | `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | 历史索引哈希一致；C |
| `02_training/logs/path_migration_20261025_physical_smoke/model_4350.pt` | 984,117 | `e86971d98a3d58f8e091f53687249321ebffbf1e391ea00752e00c626c9b423c` | 后续smoke新增；C |
| `02_training/logs/path_migration_20261025_physical_smoke/model_final.pt` | 984,117 | `e86971d98a3d58f8e091f53687249321ebffbf1e391ea00752e00c626c9b423c` | 后续smoke新增；C |
| `02_training/logs/path_migration_20261025_physical_smoke/resume_iteration_4350.pt` | 984,117 | `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | 后续smoke新增；C |
| `02_training/logs/path_migration_20261025_smoke/model_4350.pt` | 984,117 | `e86971d98a3d58f8e091f53687249321ebffbf1e391ea00752e00c626c9b423c` | 后续smoke新增；C |
| `02_training/logs/path_migration_20261025_smoke/model_final.pt` | 984,117 | `e86971d98a3d58f8e091f53687249321ebffbf1e391ea00752e00c626c9b423c` | 后续smoke新增；C |
| `02_training/logs/path_migration_20261025_smoke/resume_iteration_4350.pt` | 984,117 | `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | 后续smoke新增；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_0.pt` | 983,255 | `f0a8f159c2af1d7a60d477ff4a115045d3bb90ca080e7041ac2e39356347c70c` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_0_initial.pt` | 328,104 | `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_100.pt` | 983,851 | `0b92133441faed86b66a69114d9045147527c15c43421ea7eb71a859d7138d90` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_150.pt` | 983,851 | `aa6af7b36a43fa4d31bf9c094a0564f68464edfe1d18c63edd54f2db77686616` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_199.pt` | 983,851 | `2e8e88ecb1e95d6ed8d64c2792bbf901000a2aecc086cfd15626f7e28d190466` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_50.pt` | 983,777 | `a4590e4c552939b98a1a4b8fd7c729f85015dcd15b704ae9d1fe5765c6a0f267` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_final.pt` | 983,851 | `2e8e88ecb1e95d6ed8d64c2792bbf901000a2aecc086cfd15626f7e28d190466` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_nofabric/model_0_initial.pt` | 328,104 | `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_0.pt` | 983,255 | `6b355e2e5858db406a870f53b0e7d9940be150a2bca8c3ac689984bf8a75d6d7` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_0_initial.pt` | 328,104 | `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_1.pt` | 983,255 | `fbefd268f739b1f56e01ba8df37312caa06586f2b0d4fb92808d8a7a8abfe4b8` | 历史索引哈希一致；C |
| `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_final.pt` | 983,255 | `fbefd268f739b1f56e01ba8df37312caa06586f2b0d4fb92808d8a7a8abfe4b8` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_100.pt` | 983,851 | `ef5134fab044313408f15233dfb856558cdf74d8a0985225367b4b9ccdd97feb` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_125.pt` | 983,851 | `2c50f1208c0d98ed75c830d63e315e3258d52daf4233af29e393d76c934fdd2a` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_150.pt` | 983,851 | `ef682c254f72265780be7da00990df0309aeb3594d7eac8565a00b7fa3d9e3f4` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_159.pt` | 983,851 | `6da81a01927155a3214df3228f6829de0295d53e9a58729c8d1d0f3b5be5227a` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_75.pt` | 983,777 | `2abe6f0a310283f41bc93cf74380ee6301098045b5c10a3eee5e39968dffc102` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_final.pt` | 983,851 | `6da81a01927155a3214df3228f6829de0295d53e9a58729c8d1d0f3b5be5227a` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/20260915_143217_straight/resume_iteration_60.pt` | 983,777 | `b29f383c2b8d1ef655d395b4e5d2f7e23543abeba6ffc89c8a58dca91e042622` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_0.pt` | 983,255 | `be533a322fd2d818730306bc3f0f4a091d630af7e2c3628713614088ec4f680d` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_0_initial.pt` | 328,104 | `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_10.pt` | 983,777 | `046841ca89a1c590e4c309e4af1ea09419c4b37945069fbbbfdbafebed601267` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_100.pt` | 983,851 | `59c5ab63c7652f845fe6db95bb86f778c54fa102052239018363ba2779f20617` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_110.pt` | 983,851 | `10be9604c11c7d1f4bf0344eb42f8596c55126f51f7fa64cf4fe008c618a6a81` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_120.pt` | 983,851 | `700b90936871167fd2bde06afcf0b8143a15f313265dd8179de0025a6454a58e` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_130.pt` | 983,851 | `834486822a784814e3ddbac8afc1ac739790bb0430eab7839765b927b268f536` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_140.pt` | 983,851 | `1f66a9245127966d2bdc3926a1beaa29bc4e9275306cf11fdd05a7b9cefd0a33` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_150.pt` | 983,851 | `f3e8d1b1f9d684717ae2c471cdcf3bc79e7b6a07bd90699a6f660249361b38e5` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_160.pt` | 983,851 | `e639201f9fd5f516dcc23167086df23d42106cfca77b1d826aeb6b55874ece49` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_170.pt` | 983,851 | `dbc468e99f5c87153cef45311fb21c1e9c8932a1660997d7b329b0b365bd2c84` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_180.pt` | 983,851 | `b24cd34f77680d75983e5ae75a68defc8eb951e9c71c7e3229fc69ca21333466` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_190.pt` | 983,851 | `ab354366c4e8ea882576f90ea091e88bda4ec19808b2c46c8fb19e94394b9073` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_20.pt` | 983,777 | `160e1bb47a02f03167f3a3b83a2954923dee8b1fcde21e6accad07b8b403a3ce` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_200.pt` | 983,851 | `15724e090771de654a266bb67932b6694c553ab34ecd0d1f32e7fb1b3347e031` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_210.pt` | 983,851 | `c3931152a4ceb49e57652c213bb3ac476d961e5606f59cef1c08ee68b5e57a6e` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_220.pt` | 983,851 | `1a1db713015cf84943c62f349cc9385a4f7619c398409352749ac57ccc3d757b` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_230.pt` | 983,851 | `49d531ccfbfd553c5ae9f437c2f7882c0024a0e5dffd637020ce3bd65251350f` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_240.pt` | 983,851 | `1f71548e6613ddd110a1d794ce23638264f393aa8f7ed567786fbdd76c16ae99` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_250.pt` | 983,851 | `69e6dae0d5103b30312335a4fccbbb33d901dd5eae005e217f0ce19291ffa539` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_260.pt` | 983,851 | `f63a9211e2a3cbbd9c710a588d65218566ad9f8e66ba282a446c5fdc3baf214e` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_270.pt` | 983,851 | `ecc0cc5549b6087c6d0a8e72b4f131e8161bb7e88c932b7ace4766777cacfe1d` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_280.pt` | 983,851 | `1498712b1807beb94c3685acf03b460462a4bebe14cb2651db7e6d9bb0cef88a` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_290.pt` | 983,851 | `e3cf22a12e57a9acad4786084481c1843496060727b66e6705f3341d2ca48327` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_299.pt` | 983,851 | `896dc8bcf0a364eb1485f8c1134a010f7554da8aff697eccc59027bcca0113f7` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_30.pt` | 983,777 | `5cb46efeb8372acf851d39b882e383073263c749e7ce8e945cbe86356cf74e78` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_40.pt` | 983,777 | `c35c78c00bd5a28a6827ae8eceea9fb10b493c5bf96278b73dfb3090f0d8bcfa` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_50.pt` | 983,777 | `62a32997d0e453abc97f891ab1182272464a50de4656c90af7413f5952a762a7` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_60.pt` | 983,777 | `291f76fa498ef41fcebadb601c49e3fb42cfa1e8f5721e1174cd8b8cbdd50670` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_70.pt` | 983,777 | `5d35401ef84aaeb532f6c03001f64ef1ce1e730fd88e62e718e6ac9377fcc755` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_80.pt` | 983,777 | `e1eee496c35360918ba3314e1ec26c8f5ee930ae41b4cebb42511cbcd2145e47` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_90.pt` | 983,777 | `163f0706b9ded884c9373bdcc1d71d1ad88b6362ce54914bb4b5b2777f764541` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_final.pt` | 983,851 | `896dc8bcf0a364eb1485f8c1134a010f7554da8aff697eccc59027bcca0113f7` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_300.pt` | 983,851 | `bf5fe198ea89ba1a2c85e5807d64e492775b6a65b9a9a0a5cf7855eb5d7807f4` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_310.pt` | 983,851 | `a7b28665e64362f06fb8f1fbadc9e4494243ec4de2a0e01611d592c06e0c7631` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_320.pt` | 983,851 | `026d1d1104ecaefc91ccd10f51c906d6366db9dbae8bc170a58271a8bdf68a85` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_330.pt` | 983,851 | `5d449acc1ede299b1ae06ce45f16330e16cb17fbea3d95a65a5836797368e3f6` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_340.pt` | 983,851 | `e7cd53c6238c5d354a8cda35e236a596170135f0040a2f590d100ef780e94dc1` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_350.pt` | 983,851 | `25b6e0eddd7c168faec7ff38aaa4c6febf6ecccd585cba322bc901ba2b4df53d` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_360.pt` | 983,851 | `a9012cd4cd4b1ebd2728cb9c367c546f72f4246eaf5850bcb0e03732dd7f9231` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_370.pt` | 983,851 | `248e75fecc3b01c4a44b2fc9f7690c19edbeeabfbb89292fc5706bc9a99a5e86` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_380.pt` | 983,851 | `340446c2f060d57ecaa1648c039ee2a6af818b536edf19989cfb0f9b581c9792` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_390.pt` | 983,851 | `f5bf413346c69c74c0a375cc32e1464da6e8632202bf75080c01cf95f6498c09` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_400.pt` | 983,851 | `149863a03fe01eceb0f3875563bee5d399f37ef96ec4fa1463c96493f43df77d` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_410.pt` | 983,851 | `78f74bfdbf70471d3bd611d108a2a8c86990bb00dfe9713e786ec8d7292c4b1c` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_420.pt` | 983,851 | `2a68f1d6ab925a49524b4896923beba0ac8de9d60f7e4163435587224aa60318` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_430.pt` | 983,851 | `5f97cabe2e068b2bf3e08137e0046ba5afe615c1095080526bd2f556e7fe127e` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_440.pt` | 983,851 | `ae14032ef771679ff74105c4892fafb19622468475908953f136662670f60d45` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_450.pt` | 983,851 | `e41451b286e03814736985efe0ee559e934d19ee03d4f90bb3da82a906b091ea` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_460.pt` | 983,851 | `de06fd8cacc947b771190649dc696ac7a0513b311736d205d0cc4a61317fe2c4` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_470.pt` | 983,851 | `0a4b9ab08a958a1a78ab4344251b820ba4a1fcc6a34d030721d1e671750b0ecb` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_480.pt` | 983,851 | `4d711865ee514a00da0c664304df31a642c22c39101356a089b7b25daf54fddd` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_490.pt` | 983,851 | `f4c6b984e943bc2efccae2dc55d1ffcef60ad42c90041060cec72adec0526ad4` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_500.pt` | 983,851 | `4223154b41e80b2e1d6dbc454a417a924999c5f97956b682c3739fea09ca7205` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_510.pt` | 983,851 | `e9338ffaebf6cd06bf96590e26b5bd8e0ab6546bfa76ba37061cef510c90b6f1` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_520.pt` | 983,851 | `7496e9520f4557c8cd7f109a3176a20c28f16bee204b9f95aec8447c1d33b9be` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_530.pt` | 983,851 | `c79151f677978425917eb4726cbdcf562d1670c5aca7ab7e28499676034c5256` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_540.pt` | 983,851 | `f65705d9efb07c3328abe16ef959928906dcd17b0bc110427c5500cf22a9faff` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_550.pt` | 983,851 | `df274967cfad98ef856ae75627ba670c1b0f2b189d59a645dc2b54e80eaea9c3` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_560.pt` | 983,851 | `073082c9172caa9bc0e08f611690414ae925524bb763f069fe0110dde421dedd` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_570.pt` | 983,851 | `b1f9da41d2c56bc68adb8c2b094feae251bf18b70334d6c2880a6bb58dda2fd1` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_580.pt` | 983,851 | `bd19e43282ad27d6c8e432283b3cbc5339e16b01b1bff960c41eaf98bfe93550` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_590.pt` | 983,851 | `144e7f4784f8a453dff4e1180c7b351e937c096387b60f6d485eed6fdf0e08be` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_600.pt` | 983,851 | `e5009c9f5a17d2180a09fec90b595f16329698c5ad23079724865530a31ca90d` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_610.pt` | 983,851 | `07d489c32f83bb8cbe48469aa028d1619fed91f0778ecd51472226783a32d69b` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_620.pt` | 983,851 | `d7fc794c04ed174b2f16d433981ce003cafc6788e59f38d7cbe43d43f383213b` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_630.pt` | 983,851 | `fd961d71efebd96e9e433c8e315cfc30dba350dac2f385f74662cbfb5a270cad` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_640.pt` | 983,851 | `b5704c3684ecd34a0d9b3d0475793f47e4f51f7c5f18fab27e01cfa3d6bdbcfd` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_650.pt` | 983,851 | `51c7237ddf81ee998a66c68ef56c5dd840072cada067ac11bf6c0504d308a05f` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_660.pt` | 983,851 | `7520c524fdbee574b7d2ef14ee370e17e497c95616c9a42ace17dfd4ae2a0e31` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_670.pt` | 983,851 | `13598409396acb4cda0dd7b54142931c5fd6fa4ebb796ea9a4556b25ad633a38` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_680.pt` | 983,851 | `60c7cbe35c8a837e3d135f67fd28bf9aa962441b48abe6a9fbf1882540a507e3` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_690.pt` | 983,851 | `16bcdd9c51b6557d7c7354d21d8daaa4781c9b214a7b58efebba6e497149bc0c` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_700.pt` | 983,851 | `d9f553c53f0fa15e42602bef4125369331e61e1bbb2f4ab2ee9553947ea580e5` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_710.pt` | 983,851 | `ee2cb9054f3f36f5eee6b31560e61ab766b086c93d640a61a36ede60f8b924e3` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_720.pt` | 983,851 | `7fbe1894471c0470dd1b4004994bb07823ac05d70a1c3564d53fb3b299e11c53` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_730.pt` | 983,851 | `848d30c3de0dfe0a69540d223a5db5f6bafe09e7d92a34ebdfc73255992e4617` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_740.pt` | 983,851 | `a9f577c2f40fa2163b95281584ceb74af8869e8e83a60acd8e2ac61efee6bfe6` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_750.pt` | 983,851 | `1d08f5a64f7fad2c8856e3ca6503ea352de125ea696693fdff17153b7b1f3ede` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_760.pt` | 983,851 | `f1a9d45b373b0f483d81927fc70ab0d7ddf2008aecf2148286f3d6f92a7602a3` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_770.pt` | 983,851 | `f497883807b32068a556fa5696ec74f0e023287d49deee4a387c4cd3495043c2` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_780.pt` | 983,851 | `16c977fb70fd504e143f214ef0137e48e32f0e2f0d789f116160e20e1e3a8ca6` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_790.pt` | 983,851 | `67948cc4020bc22b2c39fd7898eb524e211bec48d14820128ab77d9dee11f4d2` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_800.pt` | 983,851 | `649af5d99e4e72c6b0bec5296570bd8df888aebe219fc34e64137ce296149e89` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_810.pt` | 983,851 | `b9a166ac392dd2cd0cf679b0ccd20af60d219951d1bf982b132f686b4681b000` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_820.pt` | 983,851 | `8dd35a14e37b28e8c171c7c0d9cdae91b48476940e32a6e6540b46f951020fc2` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_830.pt` | 983,851 | `15372d749215d6cef465137c03be4b69a47c418d2c8632147518e9d824d2e335` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_840.pt` | 983,851 | `3408f975c59feffdfd63b3c9d55382120dffc471d8f2b39baf107f9836b2d2a2` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_850.pt` | 983,851 | `ed630ec23bc777c72bc195fb5427844f8fb7a76284a084a8e27fbfe31c826b0f` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_860.pt` | 983,851 | `f830302398e75f03e018c9a0e4e6a31c202233505f26e7663d144f6db18cc830` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_870.pt` | 983,851 | `3b1b60f1fd8db61f27f18dd69630a1b50dbfc76e825b27184120eba3b871d0c5` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_880.pt` | 983,851 | `5eb1c33be6a8cb05533c025f3034470036fbe26733ed1891eccc80dcb1abb9a5` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_890.pt` | 983,851 | `0ba3b6bbdb476ca7fb3c1c251ef0cbf7d4e481cefa227fd762a3fe3d0711b042` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_900.pt` | 983,851 | `238fb905444829412f80976334d01e7deb50249383b417c2a1b36bd0f583809f` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_910.pt` | 983,851 | `b4c7ee0cc621f2e2223af20b3a6b1fb33a47a3ca1b12d8c1de38bbe93fca41f2` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_920.pt` | 983,851 | `0579b36e18209818b0742e833831387189e327fc2b6764cf067010546add69ce` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_930.pt` | 983,851 | `19f01a967351d00d804da9aa2c8da51c2c07d45a0b38df6fe8635eba8255b185` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_940.pt` | 983,851 | `e9cf8e3cf7d0daf4ce2df016869cc89e945ee46b1a65ac93f87aad71c2e5de76` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_950.pt` | 983,851 | `eded02279c231dd2b8130a621deb50778bf1272595444850546bc6ab92a1888b` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_960.pt` | 983,851 | `0dfa902110eac27cfa8ba469b3d05d4c6dced9b13cad8569ac11ec920ed9fc41` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_970.pt` | 983,851 | `e535abb1e0d2cff55f6b993a9457e1f706c6012f681f57f24698fb1fdc11a56b` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_980.pt` | 983,851 | `d1e8a158c99160c9c822d29e12dcca598ebc093ddce3fd65db7610efcaa1cdfd` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_990.pt` | 983,851 | `918133fddb12136ded10605d64f5f28c5525075e424804a9a788e7e05909311f` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_999.pt` | 983,851 | `f6b265cbc9f7c4701d5d97040457197863e10cdec776cea3fe904ddb9bb31cec` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_final.pt` | 983,851 | `f6b265cbc9f7c4701d5d97040457197863e10cdec776cea3fe904ddb9bb31cec` | 历史索引哈希一致；C |
| `02_training/logs/straight_ppo/runs/straight_300_to_1000/resume_iteration_300.pt` | 983,851 | `896dc8bcf0a364eb1485f8c1134a010f7554da8aff697eccc59027bcca0113f7` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1000.pt` | 983,925 | `1ee18ec8b680e98d3edcede620d513dfdd4f599f970de5eb4e180c547b587fdf` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1025.pt` | 983,925 | `9bc116b68a53cd17c2bba7d7ee67cd84fd13df6c6ccafb868ac33053450d5c1f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1050.pt` | 983,925 | `417d194761ccd03101fe1a958b91e105fcf93fd542521e36b512d80637e4de21` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1075.pt` | 983,925 | `8b5bda2f8977254301e333969621273c903771951f5b820dc190182f5b559397` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1100.pt` | 983,925 | `4aab947323f7e10ab145b604bb6ca47edbf02bbf5465ca213b5e11a46f08ee29` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1125.pt` | 983,925 | `b84f1d2889fe109fe97847d3e850b9b00dc673d1ff0670a3e86a2f2756b78452` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1150.pt` | 983,925 | `81e2defd24802dcae642646593087cb72b43a677d33d6f6c240e1d8c06c055c4` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1175.pt` | 983,925 | `7c2b729f0317e28658949e2d245ca8133e15fd6b4972dd8d11c17941a36edfdf` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1200.pt` | 983,925 | `9eebdf4312988db2492f261f6db269a58ebbe45a8dff3c7bb14efc462c4c34de` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1225.pt` | 983,925 | `5778d53713ba6fda353f38dab7f729d2349062fbe67829f9b355ca4c5a551bd6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1250.pt` | 983,925 | `e033d2cb60b4132b34b275576324ffbff18f6196fbb57253f7f88883e5747971` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1275.pt` | 983,925 | `386605eb9f12bb05078fca7928a7b6893b37a63702d3833e0ad1c46898d3cd8f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1299.pt` | 983,925 | `8916c5920904c0e48c8d82d3574785c31b624e87c49b10c80405c10af468fc67` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_final.pt` | 983,925 | `8916c5920904c0e48c8d82d3574785c31b624e87c49b10c80405c10af468fc67` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/resume_iteration_1000.pt` | 983,851 | `d60ed1ba20397a1b124cc68ebc6aab9e01a0dc578574a51f693b74cdca22a68f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_300.pt` | 983,851 | `7c1e76ff4152ed44b3195acfd529d2ab2873de29c46ec373c448c83b56f2de4d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_325.pt` | 983,851 | `052890de6779bb08f32e339538a3ad4400536163d34cd569170adb85fcacbbfb` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_350.pt` | 983,851 | `fb3b8b5b59188b53a27e62bd796d2ba2aac34285d4402ebf1126c8fd67643c43` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_375.pt` | 983,851 | `82e6c083b82edda2b2840d4cc1eb73fafd3ba7696d17d94b773a5ee319f2e48a` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_400.pt` | 983,851 | `18e9e904b3e60b6fbbff7bb52d0218f5b672d5aa0d22b51f28de608d3a77e05e` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_425.pt` | 983,851 | `5175429cbd861a7e22bcab708a53ca5877638d5b4ad76696619891cfc360ec8d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_450.pt` | 983,851 | `932019aee90fbc9e2bf4cbe11317a28d6ee3039e553adfdf39edab7ab0628c0c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_475.pt` | 983,851 | `dba210f2d09d3d82ed690443f137b6cda71b3989d92ee6189b5bb3f5d5ab21c2` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_500.pt` | 983,851 | `3523e12f694a54623319e25796939ced369bdb979ea3b60de7910703d17a45c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_525.pt` | 983,851 | `b1773494ceecfc8d20ef34ed046d00011f55afa15c2e09370404cb7852262493` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_550.pt` | 983,851 | `66df791ac84c4d31f0db9f4a25ba4e231d28de924f99d5ef174cd772e06d0c10` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_575.pt` | 983,851 | `8a95abb2edcc7f1699d340822c21422c1c8638bad11abd14b47c13c4c167e6a8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_600.pt` | 983,851 | `cd12b53eb87dc1e9fff16dc2e9fe2ef68aeba256f78f6596cb01090327780610` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_625.pt` | 983,851 | `d007ed56f9b49c490d4c367f445fb75d3b39c5fb7a512c64ca38436410262605` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_650.pt` | 983,851 | `a8671c2eef67b3072670ae042449a223da1c704022a93c1e4796d3e1e9c30e7d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_675.pt` | 983,851 | `6d24d61fb50ad8e0a883b413c2b55db2f05999ced3d6bb2d6e110b7dde39dea5` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_700.pt` | 983,851 | `024b8f5173fd0071702b9b259d0d79eb44ade61b8f2bbe90ee672f11b49ad5d4` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_725.pt` | 983,851 | `fc9053e124364df8719d83e97f7c9767847eaeb65c45e81132bd3563662f7f3d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_750.pt` | 983,851 | `3828390890a696121feb3f591aad5ca31a9a9917ad380438a7248acaaed0cc44` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_775.pt` | 983,851 | `ee96a4516746a0960745597734efbdf405e7b15d3ead0419e4c0ec5ab2b9a292` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_800.pt` | 983,851 | `8249b1798db2ba18e5b6bb751e5beaef74ab01155298ba1d3aa5903c87e07c09` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_825.pt` | 983,851 | `2137e11e2316c01391cdc2ef20a86556f27d663b52b416d5e49adfe6efc07cc6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_850.pt` | 983,851 | `65f422ddde12ce98319a1dedd7b86a32a9db0c20d656cd830046300b1fae20a6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_875.pt` | 983,851 | `8fd778f8b5d3669a53bd49953d0faedfdcb8545a3d0b63bc4891e87af7c66592` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_900.pt` | 983,851 | `a4aa087d791d525bb64d8bb9b43a22bd253e020cd2747ceb3639bfe80947bd31` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_925.pt` | 983,851 | `984023db041e2cfe88a86f411c1a19b5c0ddf4f73a22c4f304a4f7c10c62504c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_950.pt` | 983,851 | `4c834c8f5d3ef8039c1f3c823abca31bc2ef178ee83ee7dacdc3108fa7657c23` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_975.pt` | 983,851 | `03792a1fa7189fb5efd38583b641fb6780ab47337ca77da0bdca82a15e0e8d17` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_999.pt` | 983,851 | `d60ed1ba20397a1b124cc68ebc6aab9e01a0dc578574a51f693b74cdca22a68f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_final.pt` | 983,851 | `d60ed1ba20397a1b124cc68ebc6aab9e01a0dc578574a51f693b74cdca22a68f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/resume_700_from_300/resume_iteration_300.pt` | 983,851 | `77d684a5eca6b9f9115d4c927f12f3962d4889c2da2fffc2632de943d5d8d38d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_0.pt` | 983,255 | `0694fe39408f21fdd1856e2f2d85c9b2110ad23241ff23321870ae77c90fdd95` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_0_initial.pt` | 328,104 | `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_100.pt` | 983,851 | `abcb7af824f53eab311ef003716607a00b6ded998bbb34cf7ff8815a1494b665` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_125.pt` | 983,851 | `9463f7554f19984dd7489d7180d86270c8c6bce307759bba4e97d730292aa6c6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_150.pt` | 983,851 | `20c601f94199ba1eb3272238d631f2a2488b8d7d8e5ae600c1b1932533e53868` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_175.pt` | 983,851 | `f7e6e5db56bfcd03e34c91671db6bccf102869e758844cc87700643c51d7eea9` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_200.pt` | 983,851 | `852d48c8bdaffb48a9a093b1577dff2330e3a1011c396a0c777cbbcb0a708424` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_225.pt` | 983,851 | `40b6e4b2846f39a0dc6f2ec3f209929896689a54132c6df64e6939a260bc32f5` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_25.pt` | 983,777 | `b3a7efac7df58b3d114717f97cabf58e495bcbe81c3512bb7c4377fc83a2f0ee` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_250.pt` | 983,851 | `74e4dfc400418c2b50650eece33543fb8a18c380d55cbfa58357fb245605cacb` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_275.pt` | 983,851 | `ee5e39dff009e376f8a26819e50d4b510d02050d6fdafa19d0ed3b85b444e3b3` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_299.pt` | 983,851 | `77d684a5eca6b9f9115d4c927f12f3962d4889c2da2fffc2632de943d5d8d38d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_50.pt` | 983,777 | `31bc541f1dfea57bb1e5d99875901a769ee3046a16cb224053947d8378a3cc24` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_75.pt` | 983,777 | `81d64c807941f101877652b0e927e1e96e52f889a710492b1f01d6e617ccf16d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/scratch_300/model_final.pt` | 983,851 | `77d684a5eca6b9f9115d4c927f12f3962d4889c2da2fffc2632de943d5d8d38d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1600.pt` | 983,925 | `665f5ade7976f7de89207b1512750ff1aad26b6ad03b0592db7b42b858c435f6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1625.pt` | 983,925 | `c017f04ed1dffd152e2cba2b89d4df27ffd7d5c202a9618061f56867234cdf92` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1650.pt` | 983,925 | `d7c0712ab55ca49803138c6cd57c81bc03b3c947e78d4763f560e96fb2d329c3` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1675.pt` | 983,925 | `199e974ff24d0c0030d375b262fec09260e9263e4624c52bcdeff3edaeff402c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1700.pt` | 983,925 | `49c65ddac7f3b219c7c7a4ba0a0a90311eba1345ff6a6465fe315ba84d2b3d74` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1725.pt` | 983,925 | `c9113977aaef6e2d6aec1cdcf8118ac50949ced241ad28cf584ee050ac69bb73` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1750.pt` | 983,925 | `06d0639b2f660114d1e083b6720377d51dbeb2467ffcb4afbd48bed1ce38dff7` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1775.pt` | 983,925 | `ff8a534068afb5440eb203f0a583f6fdfc2bf734eb3306ba2de6b633296926ab` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1800.pt` | 983,925 | `4a67e0f25e0d45a0b72d1b1d48cca0fb61802a237af90c7d93c2cf0368e725fb` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1825.pt` | 983,925 | `6178c531ccebfb1ecf6d3270473cb52f0d1d64058f936948eb9cdecc7badaa46` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1850.pt` | 983,925 | `425061175c35ab5c4d253f9a683826c03419d6365557a4fad12a7d9e516b37e6` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1875.pt` | 983,925 | `bedfed5131f53e3ddd5ea211ca36203416266c2757019273adcc213af75b6a88` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1900.pt` | 983,925 | `8e9b7b3cee2f3e244963ea7993b13c5aba0978ca92851bae02f2e59c2db76545` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1925.pt` | 983,925 | `a2f4c238bbd362d71bb971a52b96636bf3f8808a69f7991d93abc3dffe8c036c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1950.pt` | 983,925 | `71ddfbbe3180b4e52fbd55e7e9289e062f83003522a362baa40b2b82b8d06296` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_1975.pt` | 983,925 | `6c0a5769972c6f9393a860bb0f68c041b29592259ff87a56f116f196b53a37c4` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2000.pt` | 983,925 | `15631bb544a6cb77b2f5d647d1fac8c5216d9708100bbd51e774c1e9029c0949` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2025.pt` | 983,925 | `222a611f19e24e55c2ace9a080b166a93c3ee5e5e292b947d07aa3cb3165be8f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2050.pt` | 983,925 | `cdf83bd86f4acc8705688994842739de13b102f0a024839510657c648562619b` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2075.pt` | 983,925 | `81d39153b7ee3b262067389f18b93b8d4978bcf9770c23c09f40e5214466c98e` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2099.pt` | 983,925 | `8c42da122665158c068a839c8308d98b848d0d98b75850d10de465416430d3c3` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_final.pt` | 983,925 | `8c42da122665158c068a839c8308d98b848d0d98b75850d10de465416430d3c3` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/resume_iteration_1600.pt` | 983,925 | `ba408462b721ff3087bb9a30196417033b71b6955f0516b4bcb9084c94687d8d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1300.pt` | 983,925 | `b6d5f178d93425f3a4e76f9c5d23558d72fc3634cdd153c92b91ae7f4a88360e` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1325.pt` | 983,925 | `cec008974ae9f2495900b217ce17dd671ff6509968f74bb68a32416208f446fa` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1350.pt` | 983,925 | `410baccd322e35d5dad57b6b8be0f760eaf2dbef54a5abc17bbc2110cd146abf` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1375.pt` | 983,925 | `2e36d1eb4aa2542397f09a7b8863aff5a283d692c0d5043c658b87d0ec8a446d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1400.pt` | 983,925 | `396d5c1f17804a162639a3e8fe3e4e3bbdad754bbbb76b8e2e6444be181c187f` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1425.pt` | 983,925 | `2ae3bbc97de35de28128fc741b8949a9487b11848f0779869841f46a07848143` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1450.pt` | 983,925 | `1ab43d1e3f0f5a47044ffc0fcaf9fd8fc966fb9a78c0b402b2fe505f10d96913` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1475.pt` | 983,925 | `b03621034db0a309917b3d19e99b8b2a8cf07311e3122d5d66f32a2aed28ab5c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1500.pt` | 983,925 | `9573b867ba60a9f3cac0f7525dfcc8f296d35d2b4a37d6f8ab95d77ac9ef205c` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1525.pt` | 983,925 | `d83f47021b29b6591531acba907b4f87f158954d9e3929530e02b9ccc25c3834` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1550.pt` | 983,925 | `0f66c2f1a68f273361714716b275570bb82d2f8a97e0bfbfc629484cfbc078f8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1575.pt` | 983,925 | `d9549fec23b5c06c46143aa8b9cef655bd1e965f616ddaf4fcc2d34d3d1d08df` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1599.pt` | 983,925 | `ba408462b721ff3087bb9a30196417033b71b6955f0516b4bcb9084c94687d8d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_final.pt` | 983,925 | `ba408462b721ff3087bb9a30196417033b71b6955f0516b4bcb9084c94687d8d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/resume_iteration_1300.pt` | 983,925 | `8916c5920904c0e48c8d82d3574785c31b624e87c49b10c80405c10af468fc67` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_0.pt` | 983,255 | `6c9b5846d4b083ba1025cef421b6e534ce02ffabcdcf037b11c25e26a36fa0fd` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_0_initial.pt` | 328,104 | `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_12.pt` | 983,777 | `ee269eee370d0f269a331666231e41b5c6f590d7ab40d81f93a0c0dded906781` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_final.pt` | 983,777 | `ee269eee370d0f269a331666231e41b5c6f590d7ab40d81f93a0c0dded906781` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_0.pt` | 983,255 | `6c9b5846d4b083ba1025cef421b6e534ce02ffabcdcf037b11c25e26a36fa0fd` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_0_initial.pt` | 328,104 | `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_12.pt` | 983,777 | `ee269eee370d0f269a331666231e41b5c6f590d7ab40d81f93a0c0dded906781` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_final.pt` | 983,777 | `ee269eee370d0f269a331666231e41b5c6f590d7ab40d81f93a0c0dded906781` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_0.pt` | 983,255 | `e27df286f08c45e9c742bcd32a2d26a83282c9ca803cfd18b8698ad8878345d5` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_0_initial.pt` | 328,104 | `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_12.pt` | 983,777 | `95473a55f4629dea21687ecd7907aae1fbc02acdb6612aa564a5dce20704272d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_final.pt` | 983,777 | `95473a55f4629dea21687ecd7907aae1fbc02acdb6612aa564a5dce20704272d` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_0.pt` | 983,255 | `0694fe39408f21fdd1856e2f2d85c9b2110ad23241ff23321870ae77c90fdd95` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_0_initial.pt` | 328,104 | `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | 历史索引哈希一致；C |
| `02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_final.pt` | 983,255 | `0694fe39408f21fdd1856e2f2d85c9b2110ad23241ff23321870ae77c90fdd95` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1300.pt` | 983,925 | `e48e3f51541ef790722b1805f3c0c50aa56e50fdf471d4fe578be74ba972b71b` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1325.pt` | 983,925 | `3591e9f3743e10f7f76ec2df5651297a385ade666deb4b861fdd6f1e08c41880` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1350.pt` | 983,925 | `84ccf9def4b8947fdccbcbc3990a9f01ccf0418e69d67740a7c296deb6ec2b61` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1375.pt` | 983,925 | `c1e2623926686879ca27407d7e0bc3a34a10ae190c45d851bf0bb1f6986f7aea` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1400.pt` | 983,925 | `abaa0881239ecdc2d19443aebc92343f0fc552438f4efe8e94e6e42054b098ec` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1425.pt` | 983,925 | `2baf601f8ea6fcf5c0e1a7d4864ad768dce6ebb678815d3735eefae8967b69e3` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1450.pt` | 983,925 | `364f579128152bdd555ef6f95d6dff0a44f0e36dda913e48e3c5edc9f0682fb4` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1475.pt` | 983,925 | `3e0b3d02ab376ef15b206ecb48a01e6c43cdf307cc2c0974371d5fcf33036b19` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1500.pt` | 983,925 | `4fd3fb402c7f932c3bc5e755f6ceaa01d55b56394c050e4199ee5c17f8c7344d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1525.pt` | 983,925 | `8d6b33ec8a783c225b9560388509ee32b0aa118cf7f819548b9ebe6ae936bfdb` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1550.pt` | 983,925 | `eea37ba00991e1295317a276735e24b7b7c77a1fca82891bb92ed7586b3e3196` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1575.pt` | 983,925 | `b6e8546c4c54d7d5677e396296e7240f01f24260b83a19d71f9b6ae3a8cacca6` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1600.pt` | 983,925 | `9e216d0e266c0324248f4a7bacf3c3f1ef98046d47d93ac8510c79e12b01490d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1625.pt` | 983,925 | `4b67cf74f940654c8a575ab9543546a99a766e4c8d77ab10f41c0efbf55d3343` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1650.pt` | 983,925 | `79aea5cf93cf35f782359a2de8566f6338398b4049f82557562cc0228a56a766` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1675.pt` | 983,925 | `e6cca6553aa9381dc51a3de0887513482a492ebc6a28af46364c7cee5736e4dc` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1700.pt` | 983,925 | `7421af59df5086dbc1c87c1d6ce9316d0d65ef310f1c8c1a54f9a3b4447a7b6b` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1725.pt` | 983,925 | `9ee8d3a4a0f7a531470ad0cc7e883eeffbf66c2582783792fb4bf8653de47db8` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1750.pt` | 983,925 | `253b370730da90996426cf68570845f1480135a9520c6b0e061dec8acc99395d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1775.pt` | 983,925 | `be7bc87a0950de43e52d36e5441be26dffb8c01cd65d8f912315ba3ce5188c4a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1800.pt` | 983,925 | `acf5ce110ac8e8bad0acac26c8bdb246eebba50a6c5c68870f58a4fe39dbbbd4` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1825.pt` | 983,925 | `55e78567572b172c97e07e82713db1eed78cb2118a5e6ede7f4a2188d56c922f` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1850.pt` | 983,925 | `46885e6d41ea92c309487e85558248242d42ecc692efe6f63d139000301ec891` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1875.pt` | 983,925 | `004aeacae654e70174bdd3d6debac939cbb72553fe2a87811822bafb7310f9b2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1900.pt` | 983,925 | `b204991753fb42ace79f72ebfb30f7623cae718ae0935ad9c4f2eeddaed2ab52` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1925.pt` | 983,925 | `3147679f7478906a57d06ec3c964baa71aec984fcd7463a0c01ef000874b1fd9` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1950.pt` | 983,925 | `63b619ad466dafbc8fb2410502617589a80c138da6db41914f30e62ba2456233` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_1975.pt` | 983,925 | `59d225d5cb887025d469ed64a9d1508d8c7edcf6b1821167fabef539c467bc03` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2000.pt` | 983,925 | `92bb42d8186c37b831a7cc59898e58471e643f49b597c20124cf9aa31d2d71a2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2025.pt` | 983,925 | `cd698db22af953627e487f636558b429a6d9c86244f275b7f95049169e4c569d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2050.pt` | 983,925 | `8afb02f322c842cf18cde2de1c76f50f6fac1e4c75989ecd8a56a19ede711eb9` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2075.pt` | 983,925 | `de6582533521b58d8129696d69ed2e2129e19d4229de08ed1154c60220a45338` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2100.pt` | 983,925 | `04b798005ec3f063e9317e018c4c7aae3a8fff974c5cbb0a31eda38dd30722b3` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2125.pt` | 983,925 | `2266a754672e8b3a4854ffc2c130f4d1e5607d81bc642c9b7afb260cf654fa6d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2150.pt` | 983,925 | `1ae752942f9c5b051e0fa579610a25d8870959779dfb4bb0d49dda8f82e2851a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2175.pt` | 983,925 | `4c22bdd78e90d9c36ac47d8a7b152796098980c7e4da3019650bef6e98231c36` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2200.pt` | 983,925 | `e84a8256d425e4c48bc4fe765ebf2b1b8dc1d28c80e0a2e31c5181547ce1d923` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2225.pt` | 983,925 | `643c6486836e16a2af54464a78734b4da995c77b2396e8bc733bfa9ed666ad60` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2250.pt` | 983,925 | `d1d7b885e94d9c114aaf5b1ee3e4d18197bb60370df027bc0875819b7b53129c` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2275.pt` | 983,925 | `ccf68ddd472f9b2d3f7a6bbe94a568f8a08a479e9a856f1dc3108ee438b0d01d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2299.pt` | 983,925 | `249cc5ece14f5d1cf5dbdc9647294c1368cca6fd1c746dc5b563db396a0687bf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_final.pt` | 983,925 | `249cc5ece14f5d1cf5dbdc9647294c1368cca6fd1c746dc5b563db396a0687bf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/resume_iteration_1300.pt` | 983,925 | `7045d15bdb1bc0cbfb94d7995ad028d0f7f512a3ac782ae90991dd1798202034` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1000.pt` | 983,925 | `0737f210b06e27a3689ad3e9531175ac52a407d620347717c246becf679fbc52` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1025.pt` | 983,925 | `8d903107f9a1d67d4de0eb4379219f57f3192c6f6e270b7bdfec16511321cdf6` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1050.pt` | 983,925 | `41a10be7578536586ba362f58c3193f630d3a7ced193d3318d2a83001d92c866` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1075.pt` | 983,925 | `2c02c927daf09c0436a2539cb43526bfba73d95d74bec66b209e7dba11bfdfeb` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1100.pt` | 983,925 | `e53f4094ef9605d51f5aafe694d65feab9e59717924625e3cda310df17f5019e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1125.pt` | 983,925 | `1fffc40de55dab1d3b28ac4e2dba4bf16f776879b0e081fb54699df555c9f737` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1150.pt` | 983,925 | `508097a6cf50816d76dd0fc06921fce31c6547e5f7b23f86564f9419890c5483` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1175.pt` | 983,925 | `06fdf2db67fa14e5d016a4acea4735c97a2d692dc32755a60f8d8eef5e4b8b8b` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1200.pt` | 983,925 | `9f2e017f1ddfa0b73d00df779756eabf5a95ea4195e56ca62d7aa9e304540881` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1225.pt` | 983,925 | `180181069b969bcd7eb0259ed53292773bf05b10144ebf6e4c0f8e283d36b167` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1250.pt` | 983,925 | `6e061d054f7582b504af19fb25facec36f870b95a382ad3dcf3fa8c699e0b491` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1275.pt` | 983,925 | `8e6fe86e8ef0a776b0ef6060f839fc73fe4797d7ca1b92ee41dfb5effef03436` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1299.pt` | 983,925 | `7045d15bdb1bc0cbfb94d7995ad028d0f7f512a3ac782ae90991dd1798202034` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_final.pt` | 983,925 | `7045d15bdb1bc0cbfb94d7995ad028d0f7f512a3ac782ae90991dd1798202034` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/resume_iteration_1000.pt` | 983,851 | `f6b265cbc9f7c4701d5d97040457197863e10cdec776cea3fe904ddb9bb31cec` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2300.pt` | 983,925 | `05eb6cbc2e2cd80ea0dc8690d1c3fdedaeec6ecc6f4c765cbfda934424ed3f99` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2325.pt` | 983,925 | `76e468fcd2a290f7e27b3a70248d27a3021cb9332522a7bcff0e83fa3b2dabc0` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2350.pt` | 983,925 | `a299cc856756bb9b8218df96e28d804511b9009caa3978fe67fe6438bf43be38` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2375.pt` | 983,925 | `52b0e1cec494fc34ff8274784bde06f9c0441d2938bfc0bcfdd52d5ce6bb7f55` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2400.pt` | 983,925 | `8cdb9cdf10d8e34615e5a8ea5df84aecb54705a3cac335d05eb67f7325ad2dec` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2425.pt` | 983,925 | `9c38aed2191da007744bd6f7c873afceae90867e4723002ea1d77766b67f5dab` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2450.pt` | 983,925 | `89fa09557cce98a70000691f85847e7f5b229e55805534b44e19cb42084ad875` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2475.pt` | 983,925 | `ed31a5bb3744a34db76fe3655937e46df5279f53b9da61a2ed8423e446a10659` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2500.pt` | 983,925 | `10e4c5772b77a1a4b3dec2b186f0863153550a147a4680452d9aae27fe653537` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2525.pt` | 983,925 | `272b6dcd0b6bc94adf5d94597a73f8cb43bee361301b041716ce4763481d7208` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2550.pt` | 983,925 | `7a5f260575c800c1086117e8a6b16e4b8db5dd7b2581ba01799658391dc59caa` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2575.pt` | 983,925 | `427f3cef3d6e0769ae14ca34029a037d1ac20b2cd837155f7e2dd8f730f05d17` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2600.pt` | 983,925 | `4295ba91aef563c16166b02c714502400ec75b78d4b43ff3809cb32e7de4b2ef` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2625.pt` | 983,925 | `3c6d232b28f49e1a19138df1a540aa0cd62399a7960103751e2c94f39056803e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2650.pt` | 983,925 | `d79ae778afa991394873d44cf7af8dd1a43c9fe3173e084d6ab7261c979ee2e2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2675.pt` | 983,925 | `bcf5c1d101429c2c9cc70e2e2a74a362311ddd9b8c5443978704edb1e146c6f7` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2700.pt` | 983,925 | `472a2a74e212451c0298c9b2074e8f5659887e1a6cb30becf0775639b9a02be6` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2725.pt` | 983,925 | `1860ef6450b7837a2bf23a936be42363ab72881c1fe35654f53a69054c2bbe91` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2750.pt` | 983,925 | `93e12b489c6f73ac5f38861092561bcf1851d6837268d45a7a62e898c0b6e402` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2775.pt` | 983,925 | `cc1ab2893e71978e272af4ffc1ea5cf0d41520de62c9481ab797d9df5e3f77f9` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2799.pt` | 983,925 | `6e3a96b66bf3da10e78ceeebbe155a1b169485d5be27d7039c1aa277f2ee7c00` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_final.pt` | 983,925 | `6e3a96b66bf3da10e78ceeebbe155a1b169485d5be27d7039c1aa277f2ee7c00` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/resume_iteration_2300.pt` | 983,925 | `249cc5ece14f5d1cf5dbdc9647294c1368cca6fd1c746dc5b563db396a0687bf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2800.pt` | 983,925 | `afd387c1424bc3f16d4741c42f0e958df7be7fbca9f2a784e6275f01efe6e2ce` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2800_adapted_initial.pt` | 328,613 | `4903a830b761f67582da6e17d87cd883baac1241600c606fb663cbd0d17faa08` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2825.pt` | 983,925 | `c214b50bdd3f0f44ea702f4fbdd8e4d161cb4ae58b6e93b1be9efea2235e7e48` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2850.pt` | 983,925 | `9b020da34dd9ea106c46ac4d45f4df8a2d5b60bb4a4e8473bf9fe5f4153134bb` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2875.pt` | 983,925 | `f327acf2d6ad7ded305c19819236853285bf4db209ca860236dcd4696608161b` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2900.pt` | 983,925 | `2821a9f2ef52663b8c91b1006445cdf03f04cece9656987501670d0c5b1d41b1` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2925.pt` | 983,925 | `f206c6f3581b884a8dbb63335a415093afdd3533098ff32a1dedb0d72b0031c0` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2950.pt` | 983,925 | `66856b64ae50d80d6fb30662401de243566b65a6e7ab1e10b2159557d8106f74` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2975.pt` | 983,925 | `7116dcafbaa4b9bac1d32538520cbc8bc0b5d395788de298d5543dffb5be8235` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2999.pt` | 983,925 | `63d64761e80cc3d89efc3e3c36ba692361fba193b8045a98ca5d9ab8e0b09b9e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_final.pt` | 983,925 | `63d64761e80cc3d89efc3e3c36ba692361fba193b8045a98ca5d9ab8e0b09b9e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/resume_iteration_2800.pt` | 983,925 | `6e3a96b66bf3da10e78ceeebbe155a1b169485d5be27d7039c1aa277f2ee7c00` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3000.pt` | 983,925 | `cf2c43dc07bafaa4c3ff54117fc972d8cab8a3171f8832f4fef926f1bf78c210` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3025.pt` | 983,925 | `d97b9c874fc47edd2fec9b366e2d2c7a08318742cf73f10b5290aff5e446b800` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3050.pt` | 983,925 | `777bc3b187c9c188683e42259d4592be7d0d3ff84c007d51402c2c9edabb741a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3075.pt` | 983,925 | `9fe4ffedcee2d322de5d0422ca7dd4afd8d39e5e484bcb5614efddaf227b2bdd` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3100.pt` | 983,925 | `47ece46bfdf6ed6a3567d9200e1e7ae28260613191530f7ce9f2f58c040885b1` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3125.pt` | 983,925 | `e459676a1661715d690ebcb180a8210c1b38abfef952df0ffc5ade6ad651e7bd` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3150.pt` | 983,925 | `0b228dc04cef4c81562f14325211bd6b40935da9dbd72f3a31dc66120a12bc00` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3175.pt` | 983,925 | `b531c3415ef1cbdde55dd75c242c9571f28d056df3b7992cdf63ae84ca83313a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3200.pt` | 983,925 | `ceeaa7bce4a5839cf16fd33737e0f4a44165a7080550f1dc90f7b80994f568e1` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3225.pt` | 983,925 | `e22b5a48e58983e32fe0ad2ed25f8168530c5e1dbad56b3bd9c83954337328ea` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3250.pt` | 983,925 | `27b41c1e3ee439783d5f2d90104aaca5839ca59b5177ba47c1a99a33a01f4446` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3275.pt` | 983,925 | `3b4a08c9656d65359bde7a64e2860a95b9dcd7e9e17f68d54c8e1c17becef98e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3300.pt` | 983,925 | `0b37d2ec931309f9e229099cda0eda247c11e98718b0f441dd19a919b3ff2e4a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3325.pt` | 983,925 | `ce8fc0ad5b7ce54ed4597993809bf674bb4302694e7ed3bc08372bee964c4243` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3350.pt` | 983,925 | `c7ac00998bf486e7cb5bb947be0e463250fcacb723d10c2e7549fe8d98a19781` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3375.pt` | 983,925 | `6b56ce8e2dccf94db3771c2d075bbd5bc38883f632b3b3335923b0edab2f50c3` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3400.pt` | 983,925 | `0dd22f9b9fa40f14b547088309e5fb9cb0d90c543f2007db5eb46547612344bf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3425.pt` | 983,925 | `94bd6c208d2025778970853c59beb2c4d7952af968b6e572e2e5b831d9e8f51d` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3450.pt` | 983,925 | `1ff091abfaa2a0344e91f808d92d8bc1e972f3888315c61dfc1e7729486ba466` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3475.pt` | 983,925 | `b710c35fcaae8c833be473464036a4537ea37d349014f8ea2d4b16acd2745724` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3499.pt` | 983,925 | `cc81f546006a95a4a92e3ad6a1478d2bfb96dfbf07527ccab4245dc7e80d8484` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_final.pt` | 983,925 | `cc81f546006a95a4a92e3ad6a1478d2bfb96dfbf07527ccab4245dc7e80d8484` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/resume_iteration_3000.pt` | 983,925 | `63d64761e80cc3d89efc3e3c36ba692361fba193b8045a98ca5d9ab8e0b09b9e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3500.pt` | 983,925 | `104acd35a95bdb4aabede164bba9c3d1b55976a2b30e14bf9f51f060c2d85200` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3500_adapted_initial.pt` | 328,613 | `8e6e8063e543dbe711ab73cb1ac1715feecc4df377e39e4dc5f33c7867f84de2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3525.pt` | 983,925 | `97e6fc7323eedfd9c64434329e7e8ec9dd5855318bde153bdf2dfb83af3428bf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3550.pt` | 983,925 | `af8e160fa2d865a89263aafecbaa6934ddff140b00cf5fbda516c31f23ed97c2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3575.pt` | 983,925 | `a03b2c95cf7e6161564f3e8ef0597040b06799017fd1d3bcd673c26509d6e4cf` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3600.pt` | 983,925 | `a8a06a9b7b0e6ed436e2a62b21adbc09597394f41802cfdf78ecf950e669621f` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3625.pt` | 983,925 | `3edf9da7929e78abfab6d55ea7303e5947c04ff2c5853862001570d42b40c5cd` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3650.pt` | 983,925 | `3d6737604985e07cdcccc792e11c4db392af1d28af2fdf7f491d6597eb9951bd` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3675.pt` | 983,925 | `d177bf346fd5b393cac21cb7fbd6c5f173ebd3816fee817fef56fee4b8eb6a3e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3700.pt` | 983,925 | `1befab41fe8b7164fc631fff5889a283ac2f08cee87d6da6cf71594842c9f528` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3725.pt` | 983,925 | `bdcbbaeeccedb82fb1f11ede9e32f37b076ed9f551509667d298802dc41a195a` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3750.pt` | 983,925 | `576cd07424d13f55fa738bf859cd8b4c26cce8faf24de72bdb9c45cfd11bb83c` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3775.pt` | 983,925 | `574be7dab89dcb3aee3fa854b5d637c3ca4435b989d94c7af6488cd6c3df49c2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3800.pt` | 983,925 | `111f8103d704d4858fd80e12e1f54ca730e2ff5d077f8f281263a512d38e2d5e` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3825.pt` | 983,925 | `45c2a72a50a39a0cad8a8fa657451ef6adcfdf4bbf5ab33c56c17d7c578703d8` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3850.pt` | 983,925 | `bb6a8df76fcda93785930f489a93f8f820b1ddeb55681983e2418cfd464397a2` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3875.pt` | 983,925 | `c29afc9e175ab3b023c31631b680e23fd054504e6e2afaf7fcb9204fe5982e20` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3899.pt` | 983,925 | `9d7db6b3290adbaa6c1b76f2ed7e5da37a4d64afe81fec25c0e508be5c9889f4` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_final.pt` | 983,925 | `9d7db6b3290adbaa6c1b76f2ed7e5da37a4d64afe81fec25c0e508be5c9889f4` | 历史索引哈希一致；C |
| `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/resume_iteration_3500.pt` | 983,925 | `cc81f546006a95a4a92e3ad6a1478d2bfb96dfbf07527ccab4245dc7e80d8484` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_2600.pt` | 983,925 | `d3745bfd92909c637cea886cfb893e63a914060a46ec1d5ddcdbdf335a73287e` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_2600_adapted_initial.pt` | 328,613 | `16975277c1767d99682b80d4a5cabf39f51908b962a580621edd1eaff1328b52` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_2649.pt` | 983,925 | `e720e529a95c176b6a9cfd7db01c2ef58691c34dc9b0d7631b2cc0984c527d64` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_final.pt` | 983,925 | `e720e529a95c176b6a9cfd7db01c2ef58691c34dc9b0d7631b2cc0984c527d64` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/resume_iteration_2600.pt` | 983,925 | `c95a49ad12312a1d199a9cece255336d3f6a1aaf162b2840cc39a53367b31110` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2650.pt` | 983,925 | `e3bf88e78bd2e3a9fe21b61a8443813c9f133691cafd8c35c4f9534b967f1630` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2700.pt` | 983,925 | `ba2d15040719eca6d00db43ab652b850229d178e37f4360e907a591d1870968a` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2750.pt` | 983,925 | `74faa3995bfbe1e8aa701a988134eabf804ee9e3e6fa8cfd66254e46ffbc84eb` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2800.pt` | 983,925 | `0695c6fd0f0e5a983566dfff5de8c2d4b81d6ad5dc730388594b3ec807301398` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2849.pt` | 983,925 | `f7aaa2ead97084b6ae28b701219b200b5d4bbd85a4669cc353cf67f4f5b659b7` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_final.pt` | 983,925 | `f7aaa2ead97084b6ae28b701219b200b5d4bbd85a4669cc353cf67f4f5b659b7` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/resume_iteration_2650.pt` | 983,925 | `e720e529a95c176b6a9cfd7db01c2ef58691c34dc9b0d7631b2cc0984c527d64` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_2850.pt` | 983,925 | `e1400e5c01cd11113bd666a313ab165bc0b55f6ba1febe38684c473194129789` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_2850_adapted_initial.pt` | 328,677 | `99f8ee94489336205bd89a8bff40046ad85ad7fa3ca1c6ab08e71a43222e06fb` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_2900.pt` | 983,925 | `458ca70b18e053e9433118b5e935a45840014add69a66c8c3aae8665cc65c7ce` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_2950.pt` | 983,925 | `b9635eadfcbee897edc33b5e0a0ed49a1082dc5255187b19f1cc5021b41e9e50` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_3000.pt` | 983,925 | `ce1a8ddca2a21c447bcbef961dfc5424c7baee034917074be7e5ebcdf5ca0eff` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_3049.pt` | 983,925 | `9e20b9e3598d0b9f67ddcb8d28f1107357062c6a1ec7011004af16d9013f5d80` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_final.pt` | 983,925 | `9e20b9e3598d0b9f67ddcb8d28f1107357062c6a1ec7011004af16d9013f5d80` | 历史索引哈希一致；C |
| `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/resume_iteration_2850.pt` | 983,925 | `f7aaa2ead97084b6ae28b701219b200b5d4bbd85a4669cc353cf67f4f5b659b7` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2100.pt` | 983,925 | `57f60bf3738f123c525ad1a646883a710542a66f16cfff45329e3fa8818124df` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2125.pt` | 983,925 | `2195fe494c6229fda527fc6b41cbe92a1c1054ef0998e0bb305b94280b8ba61d` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2150.pt` | 983,925 | `31ea8b315477f67fdd162058e34e0d84c7678a192be4914c00c0f01c7bc111a1` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2175.pt` | 983,925 | `e69d531ff0db693959414a348326d2cb690ecae19cd5924faa2d8b7735935ec9` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2200.pt` | 983,925 | `f9485a43f73e74a21258eb7eaf8d8fe40cb8974403fc221defd42c70dbfbceac` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2225.pt` | 983,925 | `f359670779c3d0ca70003e501cc6a6726d7e941e03a8950589b68a41ccf35d70` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2250.pt` | 983,925 | `2d31daeeb696a401f84ccceb39f2f26b4599c710d0bba629675cb0a4b6f1d4b7` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2275.pt` | 983,925 | `42370e9a6d60cee3693174e6a7581edb1af1916c573a7e3efb5b52630a58b426` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2300.pt` | 983,925 | `930cbe9a378a164c0c13f1d45e2285e029d23de293fdbac88dfd5f18fe71b8f3` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2325.pt` | 983,925 | `6fa0590f587c33ab5686879b82246107bf303dc961cdb4727e25b5dc2d6df825` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2350.pt` | 983,925 | `72d4887b30b72bc86b079150e624b90815928fef8ac62d5f64069fe086d9f215` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2375.pt` | 983,925 | `3e2196f9b3edb3d7fa6b5db00dc7219b59a68a334432776a2f0ced8aff81f620` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2400.pt` | 983,925 | `611bb2bc84ea3166a959eec614fac60ca5abd2faad482daa05158e5821c5e73c` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2425.pt` | 983,925 | `21ded96fbcae377691a1642d96056d64bf310be5b9f7cc968d80a9dc7e03d941` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2450.pt` | 983,925 | `2abd2c0a82619be0052d3ea4214196aa8767b096ad5e252a261e038b5836ae19` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2475.pt` | 983,925 | `2dc9ae6f95badb519d833adc6416f9dabfdb697b3562bd8dd9928daaed573b9e` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2500.pt` | 983,925 | `ff4fc88d092b953d2dd6e4a5e615d111fff9ec09f16b35f352297abc6e1c33b6` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2525.pt` | 983,925 | `e46a359f92ed6bb86f8942aec63e4407044dad078a9d36daefd5deb4d9efe984` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2550.pt` | 983,925 | `9ec591b5a7e0c6bec8cbd27a5ec633ebdd6a4b3fee928b8608d09276b72b0569` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2575.pt` | 983,925 | `27b1e5c84f728181b7ec9f44f8a34212174eb83d3f1f507c8dccf2114cd8ed17` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2599.pt` | 983,925 | `c95a49ad12312a1d199a9cece255336d3f6a1aaf162b2840cc39a53367b31110` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_final.pt` | 983,925 | `c95a49ad12312a1d199a9cece255336d3f6a1aaf162b2840cc39a53367b31110` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/resume_iteration_2100.pt` | 983,925 | `8c42da122665158c068a839c8308d98b848d0d98b75850d10de465416430d3c3` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/model_2100.pt` | 983,925 | `c7aa33e7690e0af8bf6f3cfe2936971c4c9a287ad24cc54143ebfb8e376077d3` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/model_final.pt` | 983,925 | `c7aa33e7690e0af8bf6f3cfe2936971c4c9a287ad24cc54143ebfb8e376077d3` | 历史索引哈希一致；C |
| `02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/resume_iteration_2100.pt` | 983,925 | `8c42da122665158c068a839c8308d98b848d0d98b75850d10de465416430d3c3` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3050.pt` | 983,925 | `6a8dd79478a9a60f21f29be1767d190068d26cef3ac92e5c124354cf6af6dfbd` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3075.pt` | 983,925 | `d97d008d3206f9f86e124d18dfeefd24ad5c41e6218a387dd6d842439fb162a2` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3100.pt` | 983,925 | `5fca3ddff9b4dbd352a9974217bc6f369d1438f7dbf29b6a7b0db537e0493f38` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3125.pt` | 983,925 | `b1000fdec6a03ff109c8d5f9f1100a324537f580817350de73287e9df4072e36` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3150.pt` | 983,925 | `3cd5950a76e4083ba1d849ff268604d38431d61e6bfbfcdfa1d1316748c52b99` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3175.pt` | 983,925 | `5eca280f5c75d2001f7ca49ea8d45503481f54692b9f1002a117f911cf5ac752` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3200.pt` | 983,925 | `523835ce54d1955193a24c4c990ea7a109741082e97defcd817c57b421efd6a4` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3225.pt` | 983,925 | `f07fe1cb6ddbf8ae5d9bdbb359b1a9c9b6f606bda1309324075fd6affe3035bf` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3250.pt` | 983,925 | `ddeffb540fffa1adf5ccc8fb706a366932eea20221b8db7d4ad25a199dc71333` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3275.pt` | 983,925 | `a3d986d416a50468598f32fd2c1db8b8ed9c954485ba7c675fbee23fe8119834` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3300.pt` | 983,925 | `64f514533afd10ec43c8cf688353deee277f386d5c111794bad743383fc50ea6` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3325.pt` | 983,925 | `0d2f7762ed1a51289f796b87c3180ec472c4379988cb7c7891141c5bfa104fde` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3350.pt` | 983,925 | `76fcc1bf2c6dfc32fdbf9b3483ae104e0e29b640280a306bd5f6b79d50dd59c6` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3375.pt` | 983,925 | `c483786754e6915d430b39f4e7d52198d7680e28138ed26d0078088aa4d03667` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3400.pt` | 983,925 | `d85535e43493f93f3dc547ff3c1153c91797cd025340fcffe1f45480bca7af11` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3425.pt` | 983,925 | `27457b5b62699df32114462c60049d9ac7d87b8fdd1b46bdba86e2a5c0583c4e` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_3449.pt` | 983,925 | `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_best.pt` | 983,925 | `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/model_final.pt` | 983,925 | `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_recovery_400/resume_iteration_3050.pt` | 983,925 | `9e20b9e3598d0b9f67ddcb8d28f1107357062c6a1ec7011004af16d9013f5d80` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3550.pt` | 983,925 | `238c566fc7c593f25b146c8daa61a9e493bc0f5c529bc56c2da2aa2365d77eb2` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3575.pt` | 983,925 | `e1faa10d16f53711b8334e318522bc4cfbb8f00b97c89b3c6397bb83d5dd4f4c` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3600.pt` | 983,925 | `ea53c219a0ff35de59065346b8ba327b4d4c4113b1976e542d98b54445438881` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3625.pt` | 983,925 | `37406cf738135f65d457fbfd4e75b0d6ebfd4e5ff2b3e5e58fbc9b0e37ac8d0a` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3650.pt` | 983,925 | `51b641a34ccd58d20bb0bb4c7f3d70d7bfb6d081edbf906e7337516aa88897dc` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3675.pt` | 983,925 | `e8ebfbee1f9440ad80adb71c49dc741219d0de402172bab37147d1e8be0cad0d` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3700.pt` | 983,925 | `6973b491224b53f2ec4e94af8f8efaa57ccbfe1247a36d9f761bd039275e7778` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3725.pt` | 983,925 | `ea26746640b3315df3a7d8bd4b5fa086fc4bfcaf87cfc752bbecdd3e4995a768` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3750.pt` | 983,925 | `437f0e5f3d33e80583c35147b0d0176c44996141c9edb77fc1c2b2b4fd0fc04c` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3775.pt` | 983,925 | `51fb3d2f2a4a968339d3f0e4c2275759afb220139a3ff245e5871c94cd24c432` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3800.pt` | 983,925 | `765d7654af7f77f231146cffcc692cce2d88593ec93efd275570e9cd76c74e56` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3825.pt` | 983,925 | `63ad287bba6e92521700c6ad0b536561945598d2c6943bc5aed8c39cd5d3e417` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3850.pt` | 983,925 | `5881c046632d3db9b931deeb63a7c1df0c6f5863d6f614900cb4a3c0c1b22bb2` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3875.pt` | 983,925 | `d5b70b3a6ed976ac3c7ba3be84474fa439fc45708246a506117681dcd4117c2d` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3900.pt` | 983,925 | `06d9debd37b0bc412ec0b9b3be3636ee4a8eb04da77f98aae908f6b44a58b8f4` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3925.pt` | 983,925 | `7bd893891b0882644742672f3aea5ce23de8b578995a71151f6c3df929839255` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_3949.pt` | 984,117 | `fa10aba5c45a41a72b15b88784bea0844d106f2fcf7bfc9865f016a476d36dd9` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_best.pt` | 983,477 | `ea9d54828a95667b285c131e7b12fca6625f1795169e300e1023ede20b28f25d` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/model_final.pt` | 984,117 | `fa10aba5c45a41a72b15b88784bea0844d106f2fcf7bfc9865f016a476d36dd9` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_400/resume_iteration_3550.pt` | 984,117 | `c5973179aa8d27e4789eade533f596a2cab5c20b6cb8fab2f5e8d728f1c010cc` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_3450.pt` | 983,925 | `6a3e0d09b7d29c1dfe478e681a0ebb16d862fbbe8bbba119491331b8f221fe93` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_3475.pt` | 983,925 | `34f7d7e5a9bf39b9055d6e56a47c89e7d9ff84518928f82c35e053e583c66217` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_3500.pt` | 983,925 | `6937fad384b38f1a7bc70570d80e10a2febc3735429bf4038abf21a861f1a88e` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_3525.pt` | 983,925 | `a7083c969474b54d3e47ef3747564cfcde213e016baa3265b3c00e3869148fd9` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_3549.pt` | 984,117 | `c5973179aa8d27e4789eade533f596a2cab5c20b6cb8fab2f5e8d728f1c010cc` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_best.pt` | 983,477 | `716db21ec61ce7133661598cb3c6bbc26ceed6c692edc706600d1bb6f284daa3` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/model_final.pt` | 984,117 | `c5973179aa8d27e4789eade533f596a2cab5c20b6cb8fab2f5e8d728f1c010cc` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_A/resume_iteration_3450.pt` | 983,925 | `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_3450.pt` | 983,925 | `05d1c48ca7251e71e0396f154967a65c495a3d25dd7ca80e58023d8f5a599059` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_3475.pt` | 983,925 | `70be0bd789e2894ef4a7d08a72921178e7965221c75f52825d69c1e13444e639` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_3500.pt` | 983,925 | `9aa3c945641f1eca35eca6c189e31aa39a2db46aea4a193d8c61374cdda6685a` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_3525.pt` | 983,925 | `2f5deedafaa6ca4c469b529456060168cf5cedc1560a81f2881f2498a7d18a48` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_3549.pt` | 984,117 | `0e0078bc8e41a7f32ba7d82fff87870a4f7344d39b17992bd6eb2058419d720b` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_best.pt` | 983,477 | `a824b476df6e0203744c06d500eab07cc9e8e375ecfad03f103922e3647fbed4` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/model_final.pt` | 984,117 | `0e0078bc8e41a7f32ba7d82fff87870a4f7344d39b17992bd6eb2058419d720b` | 历史索引哈希一致；C |
| `02_training/logs/yaxis_reward_recovery_B/resume_iteration_3450.pt` | 983,925 | `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | 历史索引哈希一致；C |

# 附录五：规范日志中完全相同的权重组

按SHA256而非名称判重；每组全部路径都列出，**均不列D**。默认别名、续训入口与跨run来源记录仍可能分别使用这些路径。不能只保留体积最小的文件或只按迭代编号判断价值。

| SHA256 | 同内容文件（相对dogfight_rl） | 只保留一个时的理论冗余字节 |
|---|---|---:|
| `0694fe39408f21fdd1856e2f2d85c9b2110ad23241ff23321870ae77c90fdd95` | `02_training/logs/x_anti_slip_ppo/scratch_300/model_0.pt`<br>`02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_0.pt`<br>`02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_final.pt` | 1,966,510 |
| `0e0078bc8e41a7f32ba7d82fff87870a4f7344d39b17992bd6eb2058419d720b` | `02_training/logs/yaxis_reward_recovery_B/model_3549.pt`<br>`02_training/logs/yaxis_reward_recovery_B/model_final.pt` | 984,117 |
| `176d25bad6a01eab28b8eb03e669d6835a18ad8ade8c7b7856cd1e7d457ba82c` | `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_0_initial.pt`<br>`02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_0_initial.pt`<br>`02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_nofabric/model_0_initial.pt`<br>`02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_0_initial.pt`<br>`02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_0_initial.pt` | 1,312,416 |
| `249cc5ece14f5d1cf5dbdc9647294c1368cca6fd1c746dc5b563db396a0687bf` | `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_2299.pt`<br>`02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/model_final.pt`<br>`02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/resume_iteration_2300.pt` | 1,967,850 |
| `2befa5aee2d4fcf1ba694e65b40b341d68aca5d2112761e07f6e41c1e4d47153` | `02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_29.pt`<br>`02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/model_final.pt`<br>`02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/iteration_10.pt` | 1,967,554 |
| `2e8e88ecb1e95d6ed8d64c2792bbf901000a2aecc086cfd15626f7e28d190466` | `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_199.pt`<br>`02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/2026-09-15_ppo_smoke_128env_200iter/model_final.pt` | 983,851 |
| `5cc45d85250b2a8b77e592e62c52810c2f790d8cff52f5872d54cf20aa8db0c8` | `02_training/logs/x_anti_slip_ppo/scratch_300/model_0_initial.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_0_initial.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_0_initial.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_0_initial.pt`<br>`02_training/logs/x_anti_slip_train_smoke_256env_1iter/model_0_initial.pt` | 1,312,416 |
| `63d64761e80cc3d89efc3e3c36ba692361fba193b8045a98ca5d9ab8e0b09b9e` | `02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_2999.pt`<br>`02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/model_final.pt`<br>`02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/resume_iteration_3000.pt` | 1,967,850 |
| `6c9b5846d4b083ba1025cef421b6e534ce02ffabcdcf037b11c25e26a36fa0fd` | `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_0.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_0.pt` | 983,255 |
| `6da81a01927155a3214df3228f6829de0295d53e9a58729c8d1d0f3b5be5227a` | `02_training/logs/straight_ppo/runs/20260915_143217_straight/model_159.pt`<br>`02_training/logs/straight_ppo/runs/20260915_143217_straight/model_final.pt` | 983,851 |
| `6e3a96b66bf3da10e78ceeebbe155a1b169485d5be27d7039c1aa277f2ee7c00` | `02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_2799.pt`<br>`02_training/logs/x_bidirectional_ppo/left_focus_500_from_2300/model_final.pt`<br>`02_training/logs/x_bidirectional_ppo/left_reexplore_200_from_2800/resume_iteration_2800.pt` | 1,967,850 |
| `7045d15bdb1bc0cbfb94d7995ad028d0f7f512a3ac782ae90991dd1798202034` | `02_training/logs/x_bidirectional_ppo/bidirectional_x_1000_from_1300/resume_iteration_1300.pt`<br>`02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_1299.pt`<br>`02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/model_final.pt` | 1,967,850 |
| `77d684a5eca6b9f9115d4c927f12f3962d4889c2da2fffc2632de943d5d8d38d` | `02_training/logs/x_anti_slip_ppo/resume_700_from_300/resume_iteration_300.pt`<br>`02_training/logs/x_anti_slip_ppo/scratch_300/model_299.pt`<br>`02_training/logs/x_anti_slip_ppo/scratch_300/model_final.pt` | 1,967,702 |
| `7d3c0556e2946477632e287dd2f84eaa803d52f28f4554858e79e43f0966b3b5` | `02_training/logs/yaxis_recovery_400/model_3449.pt`<br>`02_training/logs/yaxis_recovery_400/model_best.pt`<br>`02_training/logs/yaxis_recovery_400/model_final.pt`<br>`02_training/logs/yaxis_reward_recovery_A/resume_iteration_3450.pt`<br>`02_training/logs/yaxis_reward_recovery_B/resume_iteration_3450.pt` | 3,935,700 |
| `8916c5920904c0e48c8d82d3574785c31b624e87c49b10c80405c10af468fc67` | `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_1299.pt`<br>`02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/model_final.pt`<br>`02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/resume_iteration_1300.pt` | 1,967,850 |
| `896dc8bcf0a364eb1485f8c1134a010f7554da8aff697eccc59027bcca0113f7` | `02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_299.pt`<br>`02_training/logs/straight_ppo/runs/straight_300_from_scratch/model_final.pt`<br>`02_training/logs/straight_ppo/runs/straight_300_to_1000/resume_iteration_300.pt` | 1,967,702 |
| `8c42da122665158c068a839c8308d98b848d0d98b75850d10de465416430d3c3` | `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_2099.pt`<br>`02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/model_final.pt`<br>`02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/resume_iteration_2100.pt`<br>`02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/resume_iteration_2100.pt` | 2,951,775 |
| `95473a55f4629dea21687ecd7907aae1fbc02acdb6612aa564a5dce20704272d` | `02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_12.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3/model_final.pt` | 983,777 |
| `9d7db6b3290adbaa6c1b76f2ed7e5da37a4d64afe81fec25c0e508be5c9889f4` | `02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_3899.pt`<br>`02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/model_final.pt` | 983,925 |
| `9e20b9e3598d0b9f67ddcb8d28f1107357062c6a1ec7011004af16d9013f5d80` | `02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_3049.pt`<br>`02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/model_final.pt`<br>`02_training/logs/yaxis_recovery_400/resume_iteration_3050.pt` | 1,967,850 |
| `a520a12c302e1c3951d8bba813818e78a0726774da6c34c205ba552ee6a4f981` | `02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_9.pt`<br>`02_training/logs/locomotion_smoke_test/headless_256env_10iter/model_final.pt`<br>`02_training/logs/locomotion_smoke_test/headless_256env_iter10_to_30/iteration_10.pt` | 1,966,510 |
| `b29f383c2b8d1ef655d395b4e5d2f7e23543abeba6ffc89c8a58dca91e042622` | `02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_59.pt`<br>`02_training/logs/locomotion_smoke_test/headless_256env_iter30_to_60/model_final.pt`<br>`02_training/logs/straight_ppo/runs/20260915_143217_straight/resume_iteration_60.pt` | 1,967,554 |
| `ba408462b721ff3087bb9a30196417033b71b6955f0516b4bcb9084c94687d8d` | `02_training/logs/x_anti_slip_ppo/straightness_resume_500_from_iter1599/resume_iteration_1600.pt`<br>`02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_1599.pt`<br>`02_training/logs/x_anti_slip_ppo/transition_resume_300_from_iter1299/model_final.pt` | 1,967,850 |
| `c02ed3de0f27ff3a3a7595d23d5d322ebcd9b04e81e8fa67f52344b0af8e5058` | `02_training/logs/back_gait_primitive_recovery/model_4349.pt`<br>`02_training/logs/back_gait_primitive_recovery/model_final.pt`<br>`02_training/logs/migration_smoke/one_update/resume_iteration_4350.pt`<br>`02_training/logs/path_migration_20261025_physical_smoke/resume_iteration_4350.pt`<br>`02_training/logs/path_migration_20261025_smoke/resume_iteration_4350.pt` | 3,936,468 |
| `c5973179aa8d27e4789eade533f596a2cab5c20b6cb8fab2f5e8d728f1c010cc` | `02_training/logs/yaxis_reward_recovery_400/resume_iteration_3550.pt`<br>`02_training/logs/yaxis_reward_recovery_A/model_3549.pt`<br>`02_training/logs/yaxis_reward_recovery_A/model_final.pt` | 1,968,234 |
| `c7aa33e7690e0af8bf6f3cfe2936971c4c9a287ad24cc54143ebfb8e376077d3` | `02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/model_2100.pt`<br>`02_training/logs/xy_discrete_ppo/smoke_train_16env_1iter/model_final.pt` | 983,925 |
| `c7ac2ba3a71d553c320429c8bbc2de10a019747c0963dfe2675e66960905bfd5` | `02_training/logs/migration_smoke/one_update/model_4350.pt`<br>`02_training/logs/migration_smoke/one_update/model_final.pt` | 984,117 |
| `c95a49ad12312a1d199a9cece255336d3f6a1aaf162b2840cc39a53367b31110` | `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/resume_iteration_2600.pt`<br>`02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_2599.pt`<br>`02_training/logs/xy_discrete_ppo/resume_500_from_iter2099/model_final.pt` | 1,967,850 |
| `cc81f546006a95a4a92e3ad6a1478d2bfb96dfbf07527ccab4245dc7e80d8484` | `02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_3499.pt`<br>`02_training/logs/x_bidirectional_ppo/mixed_drift_500_from_3000/model_final.pt`<br>`02_training/logs/x_bidirectional_ppo/right_recovery_400_from_3500/resume_iteration_3500.pt` | 1,967,850 |
| `d60ed1ba20397a1b124cc68ebc6aab9e01a0dc578574a51f693b74cdca22a68f` | `02_training/logs/x_anti_slip_ppo/finetune_300_from_iter999/resume_iteration_1000.pt`<br>`02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_999.pt`<br>`02_training/logs/x_anti_slip_ppo/resume_700_from_300/model_final.pt` | 1,967,702 |
| `e720e529a95c176b6a9cfd7db01c2ef58691c34dc9b0d7631b2cc0984c527d64` | `02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_2649.pt`<br>`02_training/logs/xy_body_frame_ppo/smoke_adapt_50iter/model_final.pt`<br>`02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/resume_iteration_2650.pt` | 1,967,850 |
| `e86971d98a3d58f8e091f53687249321ebffbf1e391ea00752e00c626c9b423c` | `02_training/logs/path_migration_20261025_physical_smoke/model_4350.pt`<br>`02_training/logs/path_migration_20261025_physical_smoke/model_final.pt`<br>`02_training/logs/path_migration_20261025_smoke/model_4350.pt`<br>`02_training/logs/path_migration_20261025_smoke/model_final.pt` | 2,952,351 |
| `ee269eee370d0f269a331666231e41b5c6f590d7ab40d81f93a0c0dded906781` | `02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_12.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter/model_final.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_12.pt`<br>`02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2/model_final.pt` | 2,951,331 |
| `f6b265cbc9f7c4701d5d97040457197863e10cdec776cea3fe904ddb9bb31cec` | `02_training/logs/straight_ppo/runs/straight_300_to_1000/model_999.pt`<br>`02_training/logs/straight_ppo/runs/straight_300_to_1000/model_final.pt`<br>`02_training/logs/x_bidirectional_ppo/bidirectional_x_300_from_1000/resume_iteration_1000.pt` | 1,967,702 |
| `f74d45e3aa9dbb19d167302c0b9a2bcd1b37d811e93c5a33c850c213f3d31e91` | `02_training/logs/external_home/anymal_c_rough/2026-09-13_13-17-12/model_0.pt`<br>`02_training/logs/external_home/anymal_c_rough/2026-09-13_13-19-41/model_0.pt`<br>`02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_12-49-40_anymal_c_256/model_0.pt`<br>`02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_12-51-47_anymal_c_256_dependency_regression/model_0.pt`<br>`02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-14-59_golden_freeze_verification/model_0.pt`<br>`02_training/logs/external_isaaclab/anymal_c_rough/2026-09-13_13-32-22_dogfight_final_test1_50_retry/model_0.pt` | 34,407,795 |
| `f7aaa2ead97084b6ae28b701219b200b5d4bbd85a4669cc353cf67f4f5b659b7` | `02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_2849.pt`<br>`02_training/logs/xy_body_frame_ppo/smoke_adapt_plus_200iter/model_final.pt`<br>`02_training/logs/xy_body_frame_ppo/smoke_reset_ycmd_200iter/resume_iteration_2850.pt` | 1,967,850 |
| `fa10aba5c45a41a72b15b88784bea0844d106f2fcf7bfc9865f016a476d36dd9` | `02_training/logs/back_gait_primitive_recovery/resume_iteration_3950.pt`<br>`02_training/logs/yaxis_reward_recovery_400/model_3949.pt`<br>`02_training/logs/yaxis_reward_recovery_400/model_final.pt` | 1,968,234 |
| `fbefd268f739b1f56e01ba8df37312caa06586f2b0d4fb92808d8a7a8abfe4b8` | `02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_1.pt`<br>`02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1/probe_2iter_ok/model_final.pt` | 983,255 |

# 附录六：审计验证与限制记录

- 全项目递归普通文件、目录、软链接扫描完成；三级目录穷举，重要层级深入源码/资产/日志。
- 主要兼容树逐文件SHA256比对完成；不是仅依据同名/体积。
- 历史权重清单530项独立SHA256核验：0缺失、0不匹配；当前规范权重536项逐项记录。
- 新模型两份URDF共52处Mesh引用静态解析有效；7份业务URDF（原始、导入/对称及兼容副本、新模型两种URI）共182处Mesh引用已逐项解析，0缺失；关节链与调用配置已检查，USD运行时组合未重验。
- IsaacLab Git当前clean、commit/tag符合冻结说明；业务Git已有修改/未跟踪内容未动。
- 只读完整性程序已执行并失败：缺失path_migration外部清单；报告未自行修复或绕过。
- 未运行pytest、GUI、Isaac物理仿真或训练；未安装依赖、清缓存或更改环境。任何“可运行”结论限定为现有源码与指定历史证据，不等于本次仿真实测。
- 项目外仅核对直接相关的冻结环境元数据、editable映射、已知日志与缓存体量；没有全面审计Home下其他无关工程，未知外部引用不能以未搜到等同不存在。
- 后续如果用户明确要求清理/重构，需要以最新目录和正在运行进程重新核验；本报告仅为审计交付。

最终只读一致性复核：除本报告外的6,708个原有文件，路径/文件大小/mtime_ns清单摘要仍为 `d04ce1de8f431bb650b712e908da6ce078783aac4201922a37da2deed32073e5`，与报告生成前及中断前相同；未见原文件增删或内容修改迹象（此项是元数据一致性，不替代全文件内容哈希）。报告全部本地文件链接已检查存在。IsaacLab当前Git状态仍为空，仓库为shallow快照。
