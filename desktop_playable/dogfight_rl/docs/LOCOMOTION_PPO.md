# 新12自由度机器狗 PPO

权威代码：`../src/dogfight/locomotion/`；配置：`../configs/locomotion/csdog_ppo/`；独立Gym任务 `Dogfight-CSDog-Velocity-Flat-v0`。

完整说明与实际命令：[实验README](../runs/locomotion/csdog_ppo_20261026/README.md)。[实验报告](../runs/locomotion/csdog_ppo_20261026/reports/TRAINING_EXPERIMENT_REPORT.md)。

正式150+146、smoke3、官方入口1，总计300次更新，已停止。第二轮前进有明显改善，但右移、右转、零速度停止与动作饱和仍有问题；不建议直接长训或部署。两阶段视频/轨迹/曲线/checkpoint均保留在该实验目录。旧任务和冻结环境未修改。
