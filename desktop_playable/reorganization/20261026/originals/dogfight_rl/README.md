# Dogfight RL

唯一项目根目录：`/home/zxq/robot_projects/dogfight_rl`。

本体、训练和对战分别位于 `01_robots`、`02_training`、`03_battle`。旧路径通过符号链接兼容，全部历史训练成果保留。冻结软件环境保持原安装位置。

```bash
cd /home/zxq/robot_projects/dogfight_rl
python launch.py train-a --num-envs 4 --max-iterations 1
python launch.py gui-a --duration 10 --realtime
python launch.py tensorboard --port 6006
python launch.py battle --duration 10
python launch.py battle-gui --duration 30
python launch.py test
python launch.py integrity
```

Dog A 有原始及 Symmetric V1 模型；Dog B/C 缺本机模型与训练资源。当前三狗对战是三代理版本，另有真实 Dog A 接口测试，不能视为三只真实本体已接入。

文档：

- [项目结构](docs/PROJECT_STRUCTURE.md)
- [训练与验证](docs/TRAINING_GUIDE.md)
- [训练脚本索引](docs/TRAINING_SCRIPTS.md)
- [对战指南](docs/BATTLE_GUIDE.md)
- [全部权重索引](docs/CHECKPOINT_INDEX.md)
- [迁移报告与 Gate A–G](migration/reports/MIGRATION_REPORT.md)
- [逐文件路径与 SHA256](migration/manifests/FILE_MIGRATION_MAP.csv)
- [冻结环境记录](docs/environment/)

统一入口从任何工作目录都可用绝对路径调用：`python /home/zxq/robot_projects/dogfight_rl/launch.py <任务>`。
