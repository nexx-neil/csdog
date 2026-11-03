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


# 项目工程约定

1. 唯一根目录是 `/home/zxq/robot_projects/dogfight_rl`。本机其他旧机器狗路径是兼容链接或受保护的历史资料，不创建第二套开发代码。
2. `01_robots` 管本体、URDF/USD/Mesh、PD、站姿与本体测试；`02_training` 管 PPO、奖励、Observation/Action、checkpoint、实验日志、deployment；`03_battle` 管地图、代理、决策、导航、射击、血量、HUD。跨层通过公共接口；日常开发不得另建活动代码副本，不得在对战规则层导入 PPO 内部 runner。本次用户明确要求实体化兼容链接，保留的物理兼容快照是迁移例外。
3. 上述环境冻结规则继续生效。miniconda3、IsaacLab、CUDA、Isaac Sim 安装位置不动；不得更改驱动、依赖或 IsaacLab Git 状态。当前环境和历史硬件记录差异写报告，不能通过升级掩盖。
4. Dog A 原始资源在 `01_robots/assets/original/fix_new.SLDASM`、转换资源在 `01_robots/assets/dog_a`，Symmetric V1 在 `01_robots/assets/dog_a_symmetric_v1`，本体配置在 `01_robots/configs`。Dog B 原目录为空，Dog C 仅有远程环境报告；不得虚构模型或权重。
5. 从根目录 `python launch.py train-a`、`validate-a`、`gui-a` 启动。PPO 实现和原入口在 `02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1`。训练配置在 `02_training/configs`，全部入口见 docs/TRAINING_SCRIPTS.md。
6. `python launch.py battle --duration 10` 启动三代理对战；`battle-gui` 启动 HUD 演示；`battle-real-a-test --duration 1 --headless` 验证真实 Dog A 接入。三真实本体对战尚缺 Dog B/C。
7. 所有旧权重和日志禁止删除或覆盖。历史权重在 `02_training/logs` 的各实验目录，空的 checkpoints 占位目录不代表权重丢失；全部位置和 SHA256 见 docs/CHECKPOINT_INDEX.md 与 migration/manifests/CHECKPOINTS.json。新实验使用独立时间/UUID目录，记录配置、来源权重和哈希，不覆盖同名 model_final.pt。
8. 使用 `shared.paths` 管理根目录和外部软件位置；相对参数以项目根目录解析。脚本不依赖调用者的当前目录。工作区内旧 symlink 已按用户要求全部实体化，旧入口目录是兼容快照，不会自动同步；维护和训练以 01_robots/02_training/03_battle 规范目录为准，Python dogfight 包搜索路径指向规范源码。读取相对资源 YAML 必须使用 shared.paths.load_project_yaml，不无差别替换历史文件里的路径。URDF package URI 必须按原 ROS package 映射解析，原始 URDF 和 USD 字节不可随意改写。
9. 修改后运行 `python launch.py test`、`python launch.py integrity`。本体修改补模型加载及短物理验证；训练修改补 actor/checkpoint 与至多 1 次更新 smoke；对战修改补 battle-smoke/HUD/真实 A 接口测试。所有输出必须新目录，禁止自动长训练。GUI 无法验证时记录 NOT VERIFIED 和命令，缺模型记录 MISSING，只有实际执行通过才写 PASS。
10. 迁移备份、原始 SHA256 和新旧路径映射位于 migration。`python migration/rollback.py` 只读展示回滚计划；实际回滚须停止项目进程后用 `--apply`。保留全部 Git 历史，禁止 git reset --hard、git clean -fd。
