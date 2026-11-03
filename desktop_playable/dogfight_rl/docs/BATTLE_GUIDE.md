# 三代理对战

正式包 `src/dogfight_v0` 保留 BattleManager、Agent/Locomotion 契约、规则策略、HP/胜负、FOV/LOS、射击、地图、导航、日志和 HUD。`dog_a/b/c` 是代理 ID，不表示加载了旧 Dog A 本体。

`python launch.py battle --duration 10` 启动三代理 headless 场景；`battle-smoke` 执行 15 项 PhysX 对战检查；`battle-gui --duration 30` 打开演示；`hud-smoke` 运行原 GUI 状态检查。日志统一写入 `runs/battle`，每次独立目录。轻量 HUD 状态测试包含在 `launch.py test`。

RealDogAgent 是显式参数化接口：必须提供 agent_id、prim_path、root_height_m 和 articulation_yaw_from_agent_yaw。它没有默认机器人或策略。多机器人共享物理推进需要未来适配器统一提交动作/推进，不能把三个逐环境 step 的旧控制器简单拼接。

旧 factory、旧 adapter 和旧坐标实现已归档到 `archive/legacy_dog_a/training_code/battle_adapters`。新模型控制器未实现。扩展元数据在 `configs/battle/extension.toml`，Python 模块路径指向 `src`；Python 打包元数据在项目根 pyproject.toml/setup.py。本次不安装包。
