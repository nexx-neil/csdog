# 当前桌面可运行依赖审计

审计时间：2026-11-03T17:28:57.014972+08:00。本轮只读源码/配置/资产与Git；仅写 github_backup_audit 下五份报告。未操作现有窗口、未启动仿真/训练/测试器、未安装依赖、未改工程。运行中的原系统仍可能自行更新日志，体积是采样快照。

## 结论与可信度

实际桌面目录为 `/home/zxq/桌面`；`/home/zxq/Desktop` 不存在。检查两处及用户/系统 applications 中相关.desktop，只有上述两项指向本工程。AGENTS/PROJECT_STRUCTURE里旧“真实三本体未完成”文字早于11月3日实际teleop/fsm源码，不能作为当前最终状态。现有进程 PID48141 的命令行是冻结Python执行 scripts/teleop/run.py --config configs/teleop/fsm_battle.yaml；不发送信号、不注入按键。历史交付final_handoff及run存在。只据这些证据判定这是桌面当前启动系统，独立新机验收仍未执行。

```text
机器狗对战环境.desktop
  → scripts/launch_dogfight_teleop.sh
  → launch.py teleop
  → scripts/teleop/run.py
  → configs/teleop/default.yaml
  → multi_runtime.py (A/B键盘、C站立)
三狗自主对战.desktop
  → scripts/launch_dogfight_fsm.sh
  → 同一teleop脚本 --config configs/teleop/fsm_battle.yaml
  → multi_runtime.py → fsm/* (A/B/C自主)
两入口 → configs/robots/dog_a_teleop.yaml
  → IMPORT_MANIFEST.json / policies/v1/identity.json
  → model/robot_sim.urdf + model/meshes/*.stl
  → usd/csdog.usd + configuration四子层
  → policies/v1/model_final.pt
```

## 功能核对

|功能|实际实现/依赖|本轮结论|
|---|---|---|
|可运行模型|peer_teleop_v1/model/robot_sim.urdf + 13 STL + USD五层 + v1/model_final.pt|本轮文件存在/manifest/actor加载通过；桌面GUI未重启|
|地图/碰撞|teleop/maps.py → BoundedTestMap → dogfight_v0/arena/test_map.py；地面GroundPlaneCfg、墙CuboidCfg|程序生成地图；有中央墙与四周边墙，存在真实碰撞schema；外围墙全方向物理验收未重测|
|WASD/转向/停止|teleop/keyboard.py|W/S前后、A/D转向，Q/E转向优先归零vx；Space锁停、C解除、R重置、Esc退出、失焦/超时锁停；零命令不等于精准物理刹车|
|三狗键盘对战|default.yaml → multi_runtime.py|3个真实Articulation；A主键盘，B独立数字小键盘8/2/4/6、7/9/1/3、5停止；C默认站立；共享只读Actor但独立策略历史|
|状态机/自主三狗|fsm_battle.yaml → multi_runtime.py → fsm/controller.py|三狗fsm；状态/导航由源码实现；是基于规则的FSM，不是战斗RL、自博弈或新训练|
|导航/路径|fsm/navigation.py、controller.py、visualization.py|栅格A*、机身膨胀、跟踪、卡住有限恢复；V开关路线；debug_draw每次清空重绘红蓝绿线；无动态避障保证|
|激光/射程/遮挡|teleop/laser.py、combat.py → WeaponService/HealthSystem|CPU PhysX查询最近非自身命中；有效范围3m；墙/前狗/尸体遮挡；常亮线不代表逐帧伤害；single_dog无伤害|
|血量/裁判|teleop/combat.py:LiveBattleReferee + battle/weapon_service.py、health_system.py|HP100、伤害20、冷却1s、180s上限；暂停/死亡/胜负/重置；当前入口实际裁判是LiveBattleReferee，勿只按旧BattleManager推测|
|HUD/视角|teleop/multi_hud.py、first_person.py；omni.ui/ViewportWidget|主相机+右侧三第一视角/状态；属于本机Isaac桌面界面|
|网页端|全工程普通文件扩展与服务路由搜索|仅发现IsaacLab文档自带3个html/css文件；业务源码未发现HTML/JS/CSS、FastAPI/Flask/HTTPServer/uvicorn/WebSocket路由。无已实现网页遥控/地图/HUD证据；包依赖FastAPI不代表网页功能已完成|

## 本轮真正执行的验证

用冻结Python -B分别调用 load_settings(default/fsm_battle/single_dog)，校验manifest、模型SHA、权重SHA、ABI，再调用 PolicyLoader.load(weights_only=True)。三者均通过；Actor 50→256→256→128→12，iter1043，无训练器/optimizer创建。没有调用run.py preflight：其前置isaaclab.app导入及可能环境行为与纯验证不同。

历史证据实际读取：`/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/20261103_164416_cec1d1f6/{metrics.json,validation_summary.json}`；31.52比赛秒dog_b胜、80HP、15次发射/11次伤害/2死亡；三狗PPO steps1632/1632/1142，28成功规划/3失败。仅核对历史JSON，不把其中PASS算作本次GUI验收。人工双击、180s完整超时、长时多轮、全部外墙碰撞、本轮新机还原均未测。

## 所有项目运行文件（逐项）

相对路径以 `/home/zxq/robot_projects` 为基准。源码通过AST递归追踪所有层级import、函数内import和包__init__，保留条件验证分支；这是保守依赖集合，不声称每个文件在每次运行都加载。第三方二进制环境按下面“外部依赖”整体锁定，不把数十万SDK库文件伪装成项目源码。

|绝对路径|项目相对路径|字节|类型|直接调用/入口|必要性|上传方式|理由|
|---|---|---|---|---|---|---|---|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json|2203|.json|teleop/config.py:load_settings|是|普通 Git|逐项验证模型字节；来源绝对路径是溯源信息|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/README.md|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/README.md|1693|.md|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|1484|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|190484|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|236484|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|53684|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|190634|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|236984|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|53734|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|197184|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|236234|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|53634|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|190784|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|237534|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|53984|.stl|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|12505|.urdf|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|18907|.urdf|config.py asset manifest验证；robot_sim.urdf网格引用|是|普通 Git|即便原始robot.urdf/README未直接渲染，也被manifest验证|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json|1367|.json|teleop/config.py:load_settings|是|普通 Git|权重SHA及50/12观测动作ABI声明|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|2722815|.pt|PolicyLoader.load；default/fsm/single共用|是|普通 Git|唯一当前推理权重；.gitignore当前忽略，需显式例外|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash|32|无扩展|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/config.yaml|1719|.yaml|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd|2795101|.usd|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd|6438|.usd|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd|2075|.usd|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd|645|.usd|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd|1454|.usd|teleop/runtime.py:create_robot → UrdfFileCfg|是（可由URDF重建，但不建议首次恢复重转换）|普通 Git|冻结转换闭包/防止重转换；config含绝对路径仅元数据|
|/home/zxq/robot_projects/dogfight_rl/assets/ui/dogfight_teleop.svg|dogfight_rl/assets/ui/dogfight_teleop.svg|521|.svg|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/configs/robots/dog_a_teleop.yaml|dogfight_rl/configs/robots/dog_a_teleop.yaml|1251|.yaml|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/default.yaml|dogfight_rl/configs/teleop/default.yaml|968|.yaml|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/fsm_battle.yaml|dogfight_rl/configs/teleop/fsm_battle.yaml|1764|.yaml|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/configs/teleop/single_dog.yaml|dogfight_rl/configs/teleop/single_dog.yaml|612|.yaml|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/launch.py|dogfight_rl/launch.py|3837|.py|两桌面脚本|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_fsm.sh|dogfight_rl/scripts/launch_dogfight_fsm.sh|302|.sh|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh|dogfight_rl/scripts/launch_dogfight_teleop.sh|2304|.sh|桌面Exec → launch.py → scripts/teleop/run.py|是（相应入口）|普通 Git|模式配置/启动器/图标；single_dog是兼容诊断入口|
|/home/zxq/robot_projects/dogfight_rl/scripts/teleop/run.py|dogfight_rl/scripts/teleop/run.py|3864|.py|launch.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/__init__.py|dogfight_rl/src/dogfight/__init__.py|75|.py|包初始化 dogfight.common.paths, 包初始化 dogfight.fsm.controller, 包初始化 dogfight.fsm.navigation, 包初始化 dogfight.fsm.perception, 包初始化 dogfight.fsm.physical_validation, 包初始化 dogfight.fsm.visualization, 包初始化 dogfight.teleop.agent, 包初始化 dogfight.teleop.combat, 包初始化 dogfight.teleop.config, 包初始化 dogfight.teleop.first_person, 包初始化 dogfight.teleop.hud, 包初始化 dogfight.teleop.keyboard, 包初始化 dogfight.teleop.laser, 包初始化 dogfight.teleop.maps, 包初始化 dogfight.teleop.multi_hud, 包初始化 dogfight.teleop.multi_runtime, 包初始化 dogfight.teleop.policy, 包初始化 dogfight.teleop.runtime|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/common/__init__.py|dogfight_rl/src/dogfight/common/__init__.py|48|.py|包初始化 dogfight.common.paths|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/common/paths.py|dogfight_rl/src/dogfight/common/paths.py|1454|.py|launch.py, src/dogfight/teleop/config.py, src/dogfight/teleop/runtime.py, src/dogfight_v0/logging/battle_logger.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/__init__.py|dogfight_rl/src/dogfight/fsm/__init__.py|77|.py|包初始化 dogfight.fsm.controller, 包初始化 dogfight.fsm.navigation, 包初始化 dogfight.fsm.perception, 包初始化 dogfight.fsm.physical_validation, 包初始化 dogfight.fsm.visualization|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/controller.py|dogfight_rl/src/dogfight/fsm/controller.py|7329|.py|src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/navigation.py|dogfight_rl/src/dogfight/fsm/navigation.py|6498|.py|src/dogfight/fsm/controller.py, src/dogfight/fsm/physical_validation.py, src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/perception.py|dogfight_rl/src/dogfight/fsm/perception.py|3112|.py|src/dogfight/fsm/physical_validation.py, src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/physical_validation.py|dogfight_rl/src/dogfight/fsm/physical_validation.py|7601|.py|src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/fsm/visualization.py|dogfight_rl/src/dogfight/fsm/visualization.py|2392|.py|src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/__init__.py|dogfight_rl/src/dogfight/teleop/__init__.py|66|.py|包初始化 dogfight.teleop.agent, 包初始化 dogfight.teleop.combat, 包初始化 dogfight.teleop.config, 包初始化 dogfight.teleop.first_person, 包初始化 dogfight.teleop.hud, 包初始化 dogfight.teleop.keyboard, 包初始化 dogfight.teleop.laser, 包初始化 dogfight.teleop.maps, 包初始化 dogfight.teleop.multi_hud, 包初始化 dogfight.teleop.multi_runtime, 包初始化 dogfight.teleop.policy, 包初始化 dogfight.teleop.runtime|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/agent.py|dogfight_rl/src/dogfight/teleop/agent.py|1592|.py|src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/combat.py|dogfight_rl/src/dogfight/teleop/combat.py|3555|.py|src/dogfight/fsm/perception.py, src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/config.py|dogfight_rl/src/dogfight/teleop/config.py|4999|.py|scripts/teleop/run.py, src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/policy.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/first_person.py|dogfight_rl/src/dogfight/teleop/first_person.py|9340|.py|src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/hud.py|dogfight_rl/src/dogfight/teleop/hud.py|1285|.py|src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/keyboard.py|dogfight_rl/src/dogfight/teleop/keyboard.py|9496|.py|src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/laser.py|dogfight_rl/src/dogfight/teleop/laser.py|3451|.py|src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/maps.py|dogfight_rl/src/dogfight/teleop/maps.py|2422|.py|src/dogfight/teleop/config.py, src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/multi_hud.py|dogfight_rl/src/dogfight/teleop/multi_hud.py|2001|.py|src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/multi_runtime.py|dogfight_rl/src/dogfight/teleop/multi_runtime.py|17671|.py|scripts/teleop/run.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/policy.py|dogfight_rl/src/dogfight/teleop/policy.py|4110|.py|scripts/teleop/run.py, src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight/teleop/runtime.py|dogfight_rl/src/dogfight/teleop/runtime.py|11988|.py|scripts/teleop/run.py, src/dogfight/teleop/multi_runtime.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/__init__.py|dogfight_rl/src/dogfight_v0/__init__.py|214|.py|包初始化 dogfight_v0.agents.agent_interface, 包初始化 dogfight_v0.agents.locomotion_interface, 包初始化 dogfight_v0.agents.proxy_agent, 包初始化 dogfight_v0.agents.real_dog_agent, 包初始化 dogfight_v0.agents.real_locomotion_adapter, 包初始化 dogfight_v0.arena.map_interface, 包初始化 dogfight_v0.arena.spawn_manager, 包初始化 dogfight_v0.arena.test_map, 包初始化 dogfight_v0.battle.battle_manager, 包初始化 dogfight_v0.battle.health_system, 包初始化 dogfight_v0.battle.intel_service, 包初始化 dogfight_v0.battle.interfaces, 包初始化 dogfight_v0.battle.ray_query, 包初始化 dogfight_v0.battle.types, 包初始化 dogfight_v0.battle.visibility_service, 包初始化 dogfight_v0.battle.weapon_service, 包初始化 dogfight_v0.config.battle_cfg, 包初始化 dogfight_v0.logging.battle_logger, 包初始化 dogfight_v0.navigation.navigation_interface, 包初始化 dogfight_v0.navigation.simple_navigation|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/__init__.py|dogfight_rl/src/dogfight_v0/agents/__init__.py|425|.py|包初始化 dogfight_v0.agents.agent_interface, 包初始化 dogfight_v0.agents.locomotion_interface, 包初始化 dogfight_v0.agents.proxy_agent, 包初始化 dogfight_v0.agents.real_dog_agent, 包初始化 dogfight_v0.agents.real_locomotion_adapter|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/agent_interface.py|dogfight_rl/src/dogfight_v0/agents/agent_interface.py|756|.py|src/dogfight/teleop/runtime.py, src/dogfight_v0/agents/__init__.py, src/dogfight_v0/battle/battle_manager.py, src/dogfight_v0/battle/intel_service.py, src/dogfight_v0/battle/interfaces.py, src/dogfight_v0/battle/ray_query.py, src/dogfight_v0/battle/visibility_service.py, src/dogfight_v0/battle/weapon_service.py, src/dogfight_v0/navigation/navigation_interface.py, src/dogfight_v0/navigation/simple_navigation.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|dogfight_rl/src/dogfight_v0/agents/locomotion_interface.py|367|.py|src/dogfight_v0/agents/__init__.py, src/dogfight_v0/agents/real_dog_agent.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|dogfight_rl/src/dogfight_v0/agents/proxy_agent.py|3149|.py|src/dogfight_v0/agents/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py|dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py|5216|.py|src/dogfight/teleop/agent.py, src/dogfight_v0/agents/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py|2055|.py|src/dogfight_v0/agents/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/__init__.py|dogfight_rl/src/dogfight_v0/arena/__init__.py|236|.py|包初始化 dogfight_v0.arena.map_interface, 包初始化 dogfight_v0.arena.spawn_manager, 包初始化 dogfight_v0.arena.test_map|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/map_interface.py|dogfight_rl/src/dogfight_v0/arena/map_interface.py|468|.py|src/dogfight/teleop/maps.py, src/dogfight_v0/arena/__init__.py, src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|dogfight_rl/src/dogfight_v0/arena/spawn_manager.py|1507|.py|src/dogfight_v0/arena/__init__.py, src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py|dogfight_rl/src/dogfight_v0/arena/test_map.py|1906|.py|src/dogfight/teleop/maps.py, src/dogfight_v0/arena/__init__.py, src/dogfight_v0/battle/ray_query.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/__init__.py|dogfight_rl/src/dogfight_v0/battle/__init__.py|22|.py|包初始化 dogfight_v0.battle.battle_manager, 包初始化 dogfight_v0.battle.health_system, 包初始化 dogfight_v0.battle.intel_service, 包初始化 dogfight_v0.battle.interfaces, 包初始化 dogfight_v0.battle.ray_query, 包初始化 dogfight_v0.battle.types, 包初始化 dogfight_v0.battle.visibility_service, 包初始化 dogfight_v0.battle.weapon_service|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py|dogfight_rl/src/dogfight_v0/battle/battle_manager.py|11416|.py|src/dogfight_v0/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/health_system.py|dogfight_rl/src/dogfight_v0/battle/health_system.py|965|.py|src/dogfight/teleop/combat.py, src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/intel_service.py|dogfight_rl/src/dogfight_v0/battle/intel_service.py|1732|.py|src/dogfight/fsm/perception.py, src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/interfaces.py|dogfight_rl/src/dogfight_v0/battle/interfaces.py|2105|.py|src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/ray_query.py|dogfight_rl/src/dogfight_v0/battle/ray_query.py|3466|.py|src/dogfight/fsm/perception.py, src/dogfight_v0/battle/visibility_service.py, src/dogfight_v0/battle/weapon_service.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/types.py|dogfight_rl/src/dogfight_v0/battle/types.py|2036|.py|src/dogfight/fsm/controller.py, src/dogfight/fsm/navigation.py, src/dogfight/fsm/perception.py, src/dogfight/fsm/physical_validation.py, src/dogfight/teleop/combat.py, src/dogfight/teleop/keyboard.py, src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/policy.py, src/dogfight/teleop/runtime.py, src/dogfight_v0/agents/agent_interface.py, src/dogfight_v0/agents/locomotion_interface.py, src/dogfight_v0/agents/proxy_agent.py, src/dogfight_v0/agents/real_dog_agent.py, src/dogfight_v0/agents/real_locomotion_adapter.py, src/dogfight_v0/arena/map_interface.py, src/dogfight_v0/arena/spawn_manager.py, src/dogfight_v0/arena/test_map.py, src/dogfight_v0/battle/__init__.py, src/dogfight_v0/battle/battle_manager.py, src/dogfight_v0/battle/intel_service.py, src/dogfight_v0/battle/interfaces.py, src/dogfight_v0/battle/ray_query.py, src/dogfight_v0/battle/visibility_service.py, src/dogfight_v0/battle/weapon_service.py, src/dogfight_v0/logging/battle_logger.py, src/dogfight_v0/navigation/navigation_interface.py, src/dogfight_v0/navigation/simple_navigation.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/visibility_service.py|dogfight_rl/src/dogfight_v0/battle/visibility_service.py|2135|.py|src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/weapon_service.py|dogfight_rl/src/dogfight_v0/battle/weapon_service.py|1752|.py|src/dogfight/teleop/combat.py, src/dogfight_v0/battle/battle_manager.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/config/__init__.py|dogfight_rl/src/dogfight_v0/config/__init__.py|66|.py|包初始化 dogfight_v0.config.battle_cfg|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/config/battle_cfg.py|dogfight_rl/src/dogfight_v0/config/battle_cfg.py|1305|.py|src/dogfight/teleop/combat.py, src/dogfight/teleop/multi_runtime.py, src/dogfight/teleop/runtime.py, src/dogfight_v0/__init__.py, src/dogfight_v0/agents/real_dog_agent.py, src/dogfight_v0/battle/battle_manager.py, src/dogfight_v0/battle/visibility_service.py, src/dogfight_v0/battle/weapon_service.py, src/dogfight_v0/config/__init__.py, src/dogfight_v0/navigation/simple_navigation.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/logging/__init__.py|dogfight_rl/src/dogfight_v0/logging/__init__.py|69|.py|包初始化 dogfight_v0.logging.battle_logger|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/logging/battle_logger.py|dogfight_rl/src/dogfight_v0/logging/battle_logger.py|1531|.py|src/dogfight/teleop/multi_runtime.py, src/dogfight_v0/battle/battle_manager.py, src/dogfight_v0/logging/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/__init__.py|dogfight_rl/src/dogfight_v0/navigation/__init__.py|158|.py|包初始化 dogfight_v0.navigation.navigation_interface, 包初始化 dogfight_v0.navigation.simple_navigation|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|dogfight_rl/src/dogfight_v0/navigation/navigation_interface.py|553|.py|src/dogfight_v0/battle/battle_manager.py, src/dogfight_v0/navigation/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py|2470|.py|src/dogfight_v0/navigation/__init__.py|是/条件分支保留|普通 Git|AST追踪源码/包初始化；包含条件分支，保守闭包|
|/home/zxq/桌面/三狗自主对战.desktop|项目外：/home/zxq/桌面/三狗自主对战.desktop|500|.desktop|Ubuntu桌面|是（桌面启动）；CLI可不用|普通 Git|实际Exec/Path/Icon入口；提交脱敏模板，不原样硬编码用户路径|
|/home/zxq/桌面/机器狗对战环境.desktop|项目外：/home/zxq/桌面/机器狗对战环境.desktop|480|.desktop|Ubuntu桌面|是（桌面启动）；CLI可不用|普通 Git|实际Exec/Path/Icon入口；提交脱敏模板，不原样硬编码用户路径|

## 权重与归一化

|绝对路径|字节|SHA256|入口/上传|
|---|---|---|---|
|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|2722815|283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7|两个桌面及单狗共用；普通Git显式放行，不必LFS|

归一化：contract.observation_normalization=false；PolicyLoader会拒绝normalizer/running_mean键。本轮实际加载通过，没有需要随运行上传的独立归一化文件。全工程仅名称搜索到历史归一化说明等4项，无当前normalizer资源；不因此推断历史权重都无归一化。其他训练权重不进入当前闭包。

|权重范围|文件数|逻辑字节|
|---|---|---|
|IsaacLab/logs/rsl_rl|11|64243326|
|archive/historical_validation/anymal|16|98653027|
|archive/legacy_compatibility/logs|533|598139070|
|archive/legacy_dog_a/checkpoints_and_runs|520|502438394|
|dogfight_rl/runs/locomotion|624|2787370389|
|dogfight_rl/runs/validation|50|42994292|
|peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0|2|3177358|
|当前必需|1|2722815|

## URDF与USD/动态资源闭包

|URDF mesh原引用|解析后绝对路径|存在|
|---|---|---|
|meshes/base_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|True|
|meshes/link_lf_hip_pitch_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|True|
|meshes/link_lf_hip_roll_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|True|
|meshes/link_lf_knee_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|True|
|meshes/link_lr_hip_pitch_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|True|
|meshes/link_lr_hip_roll_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|True|
|meshes/link_lr_knee_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|True|
|meshes/link_rf_hip_pitch_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|True|
|meshes/link_rf_hip_roll_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|True|
|meshes/link_rf_knee_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|True|
|meshes/link_rr_hip_pitch_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|True|
|meshes/link_rr_hip_roll_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|True|
|meshes/link_rr_knee_collision.stl|/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|True|

|导入manifest相对路径|字节|实际SHA256|匹配|
|---|---|---|---|
|policies/v1/model_final.pt|2722815|283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7|True|
|model/robot_sim.urdf|18907|4806d4e0c2db659a37e9f595d739df60121d2640895f505a0aec4277779566d1|True|
|model/README.md|1693|676f3b2d0e7926328ba0cdc887d034d29e7771e9f15947a3456281b6d11dd7fb|True|
|model/robot.urdf|12505|20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d|True|
|model/meshes/link_rf_hip_roll_collision.stl|236234|cdd1f1a41f4160d680d91290f3b219ac997ea544758b08d419601daebfb22fa4|True|
|model/meshes/link_rr_knee_collision.stl|53984|eda21673b014b7b392d1f1ebbc0aa31dabd3d4a351244a92a135f8aeb46c9dd8|True|
|model/meshes/link_lf_knee_collision.stl|53684|cb0146a5bc3f73180ed02082054dd9fb8cd634c3abd3f38b75aee8090f1a3beb|True|
|model/meshes/link_lr_knee_collision.stl|53734|7fa626081e4394d74cc615afe4c0e51323013875c607dc57e2a38c4be6df6c23|True|
|model/meshes/link_rf_knee_collision.stl|53634|6418e0c18075866d356c1bdc3dcf4f364fedc16caa219e65345382c1e5bacf31|True|
|model/meshes/link_lf_hip_roll_collision.stl|236484|a942c5e921a3b5bbd17f2f53a5fcf439526b8aec6eaed38cc92575b16b904043|True|
|model/meshes/link_lr_hip_roll_collision.stl|236984|c3a5d8e7282b55c3d114e46ad34c29f34ff6c4927b009de3dd07ac2ebe27b957|True|
|model/meshes/link_lr_hip_pitch_collision.stl|190634|cba39b20e1a2e078ea98122d99c3fb5a86dd87ee0b2b8d2cbce268208dfca5d8|True|
|model/meshes/link_rf_hip_pitch_collision.stl|197184|b276f7c04b288794a97f3a78fb1acc404a9e0123cd90002424cdf36bb1710666|True|
|model/meshes/link_rr_hip_pitch_collision.stl|190784|6f1fc0b7b00902bdd611ec403f03d5eacfbfe165350470699bf2dbfce7c926c7|True|
|model/meshes/base_collision.stl|1484|9c93aa72fd27c40d50539c5cbf45d5e0418986f6f0a09481c363969ed5eb6079|True|
|model/meshes/link_rr_hip_roll_collision.stl|237534|b5ac7b6b6beb836cf1d5d18e3f8ec08ae87133cb0bc0d875757a02a35f53e04f|True|
|model/meshes/link_lf_hip_pitch_collision.stl|190484|04945bf61bf4f2e49ca242de5069a1fab2bda87e2da1b5704bbd2a04ce100b80|True|

使用已安装SDK的Sdf只读解析USD（仅临时子进程设置库搜索路径，不改环境）：csdog.usd references configuration/csdog_base.usd，并payload physics/sensor/robot四层；physics sublayer csdog_base.usd；base几何已嵌入，无外部STL/贴图；13处材质动态引用 OmniPBR.mdl（SDK自带）。其余子层无外部资产引用；各本地引用存在。

## 外部依赖和恢复阻塞

1. 冻结Python `/home/zxq/miniconda3/envs/dogfight/bin/python`、site-packages中的Isaac Sim/Kit/PhysX/Omni、PyTorch、PyYAML、numpy。外部导入顶层：`__future__, argparse, carb, collections, ctypes, dataclasses, datetime, fcntl, hashlib, heapq, isaaclab, isaacsim, json, math, omni, os, pathlib, pxr, random, signal, subprocess, sys, time, torch, traceback, typing, uuid, yaml`。这些是本机独有安装，必须单独备份/按版本恢复，不能直接提交Conda整目录。
2. `/home/zxq/robot_projects/IsaacLab` 为可编辑安装来源，工作树本轮git状态干净，commit37ddf626871758333d6ed89cf64ad702aef127d0。DOGFIGHT_ISAACLAB变量不会自动重定位既有editable安装；新机需正确安装/注册该固定提交。
3. GroundPlaneCfg默认引用云端 `https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/default_environment.usd`，该默认值来自IsaacLab/apps kit设置。地图并非纯本地自足。地面及其材质/贴图需合法缓存/离线资产包；见恢复报告，未修改当前地图。
4. OmniPBR.mdl当前位于 `/home/zxq/miniconda3/envs/dogfight/lib/python3.11/site-packages/isaacsim/kit/mdl/core/Base/OmniPBR.mdl`，随SDK恢复，遵循NVIDIA授权。
5. X11/libX11.so.6、DISPLAY和当前用户Xauthority；flock、bash；zenity为失败弹窗可选；GUI验证器另需ffmpeg/XTest/gio，仅验收所需。不要提交Xauthority/lock/socket。

## 符号链接、路径与重复副本

工作区发现 184 个软链接，全部位于runs测试临时目录；没有生产源码/模型入口软链接。完整表见上传清单。不沿软链接扫描外部个人目录。发现多路径同inode组 0 组；只对当前资源按大小候选再SHA做重复核验：

|当前权威资源|同SHA的现存副本（相对项目）|
|---|---|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|model/meshes/base_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/base_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/base_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|model/meshes/link_lf_hip_pitch_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_pitch_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_pitch_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|model/meshes/link_lf_hip_roll_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_roll_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_roll_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|model/meshes/link_lf_knee_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_knee_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_knee_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|model/meshes/link_lr_hip_pitch_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_pitch_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_pitch_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|model/meshes/link_lr_hip_roll_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_roll_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_roll_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|model/meshes/link_lr_knee_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_knee_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_knee_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|model/meshes/link_rf_hip_pitch_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_pitch_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_pitch_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|model/meshes/link_rf_hip_roll_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_roll_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_roll_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|model/meshes/link_rf_knee_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_knee_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_knee_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|model/meshes/link_rr_hip_pitch_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_pitch_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_pitch_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|model/meshes/link_rr_hip_roll_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_roll_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_roll_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|model/meshes/link_rr_knee_collision.stl ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_knee_collision.stl ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_knee_collision.stl|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|model/robot.urdf ; dogfight_rl/runs/validation/submission_20261103_three_dog/repository/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf ; peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot_sim.urdf|
|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|peer_csdog_review/extracted/csdog-v2-teleop-v0.1.0/logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt|

桌面Exec/TryExec/Path/Icon硬编码/home/zxq；launch wrapper冻结Python默认$HOME/miniconda3/envs/dogfight/bin/python，可用DOGFIGHT_PYTHON覆盖；common.paths根据源码解析ROOT/WORKSPACE。IMPORT_MANIFEST.source_project/source_checkpoint和usd/config.yaml保留来源/转换绝对路径，当前读取只用manifest.files；不得在本机修改模型字节，且不要把溯源路径误认为运行依赖。配置中的assets/configs为ROOT相对；当前输入资源无缺失，云端地面离线闭包待完成。

## 分类统计（详情见上传清单）

|类别|普通文件数|逻辑字节|MiB|
|---|---|---|---|
|必须上传|86|7664841|7.310|
|推荐上传|469|27778351|26.491|
|必须单独备份|9615|42163589708|40210.333|
|不上传|5844|225911342|215.446|


## 补充：官方地面USD与贴图动态引用实核

只读HTTP取回地面USD至内存，使用Sdf匿名层Import解析（memfd，不创建落盘资产、不启动Kit）。地面自身13622字节，SHA256 `8a21c317d638d33a4e6c20c958a7ed8f4d8c5195efd7e20f1b85178b4a15638a`；无外部USD层引用，但材质引用SDK的OmniPBR.mdl及下面三张贴图。纹理URL按原层所在目录解析，均属外部依赖，没有可列出的项目内绝对路径；不能因本机未缺图就认为Git包自足。

|URL/绝对路径|字节|SHA256|调用入口|必要性/上传方式/理由|
|---|---:|---|---|---|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/default_environment.usd|13622|`8a21c317d638d33a4e6c20c958a7ed8f4d8c5195efd7e20f1b85178b4a15638a`|maps.build_map → GroundPlaneCfg|是；必须单独备份/官方恢复；NVIDIA资产不直接纳入Git|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/Wireframe_blue.png|111895|`940b96ee8c8e53bd1acbc770d4ca0ac98bed9c96439ab386d1b27dbc9790cc4e`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/WireframeBlur_basecolor.png|436257|`deab39088eaf39ed7be951966c5e6bd5e58b90ab64743b0cdc8e5579fd5a99d9`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|https://omniverse-content-production.s3-us-west-2.amazonaws.com/Assets/Isaac/5.1/Isaac/Environments/Grid/Materials/Textures/WireframeBlur_blue.png|1474958|`44fc0e82007bb0bd94631cd7ec45986a71ed74b9413899fbffac13efe151be4b`|default_environment.usd材质|渲染恢复需要；必须单独备份/官方恢复；HTTP读取验证；未落盘|
|/home/zxq/miniconda3/envs/dogfight/lib/python3.11/site-packages/isaacsim/kit/mdl/core/Base/OmniPBR.mdl|15591|`685a82c18b381f1cd29831490e4c356e61dbeac2d86803babc115cd6a4a845db`|模型USD与地面材质|是；随SDK及MDL依赖库整体恢复，不上传Git|

本次已识别并验证三张直接纹理，不把它们写成“未知文件”；尚未将官方资源合法离线落盘、配置新的资产根或执行断网恢复，故离线自足性仍未通过。MDL内部标准库依赖随完整固定SDK恢复，不从中抽取不完整单文件。外部HTTP资源字节不计入本地文件分类体积。
