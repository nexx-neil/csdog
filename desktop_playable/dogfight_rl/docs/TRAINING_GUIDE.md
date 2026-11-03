# 当前新模型训练

新模型任务 `Dogfight-CSDog-Velocity-Flat-v0` 已在 `src/dogfight/locomotion` 独立实现。完整使用说明见 [LOCOMOTION_PPO](LOCOMOTION_PPO.md)。统一入口为 launch.py train/evaluate/play，训练必须显式指定迭代数和唯一run，评估必须显式指定新模型checkpoint。默认不会恢复旧模型。

通用工具仍在 src/dogfight/training。新任务使用官方 ManagerBasedRLEnv、RslRlVecEnvWrapper 和 OnPolicyRunner，未复制算法库。Actor45/Critic48、12动作具有独立身份定义；不能因维度接近旧模型而加载旧权重。

本轮预算已用满：PPO smoke3 + 正式150+146 + 官方入口验证1 = 300。预算账本存于 runs/locomotion/csdog_ppo_20261026/training_budget.json，禁止自动重置或继续训练。新模型仅具备部分运动能力，详细失败项见实验报告；不视为三真实机器狗对战已接入。

旧PPO任务/模型/完整run仍保存在 archive/legacy_dog_a，本次没有修改、移动或覆盖它们。
