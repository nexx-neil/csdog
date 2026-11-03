# 地图与场景审计

审计日期：2026-11-03（Asia/Shanghai）。本次只读分析与低资源CPU规则测试；未启动Isaac Sim、GPU仿真、训练、模型转换或安装依赖。所有新文件均在本审计目录。

## 数量、格式与实际选择

按“不同比赛几何”计数，当前正式源码找到 **1张基础比赛地图**：Python程序化 `TestMap`，不是独立USD地图文件。`DemoTestMap`只更改出生点，属于同一几何的第2出生配置，不应算成两张完整不同地图。归档有同源旧副本，不算新增地图。PPO平地TerrainImporter和同学训练plane是运动测试场地，不是带裁判和出生点的比赛地图。未在已扫描业务代码中找到其他接入比赛的独立地图；未解包历史tar，不能声称所有压缩备份绝对没有其他地图。

|资源|格式/内容|入口|状态|
|---|---|---|---|
|TestMap|Python边界、墙和Pose2D|battle默认create_isaac_battle|基础场景已实现，有20261026物理smoke|
|DemoTestMap|TestMap继承，仅替换3出生点|battle-gui|有历史代理demo，当前GUI需回归|
|运动平地|TerrainImporterCfg plane|单狗PPO各版本|不是比赛地图|
|旧TestMap副本|archive源码快照|不在默认PYTHONPATH|历史证据，不作当前功能计数|

证据：[dogfight_rl/src/dogfight_v0/arena/test_map.py:22](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py:22)、[dogfight_rl/scripts/battle/run_v0_battle_demo.py:47](/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_battle_demo.py:47)、[dogfight_rl/src/dogfight/locomotion/env_cfg.py:19](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py:19)。完整命名索引见 `MAP_BATTLE_RESOURCE_INDEX.txt`。

## 地图内容与完成情况

[dogfight_rl/src/dogfight_v0/arena/test_map.py:26](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py:26) 定义x∈[-6,6]、y∈[-5,5]；地面由[dogfight_rl/src/dogfight_v0/sim/scene.py:47](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/scene.py:47)创建14×12m。两面内部墙：中心(0,0,.75)、尺寸(.35,3.2,1.5)；侧墙(2.6,1.6,.75)、尺寸(2.4,.35,1.5)。它们可作为遮挡/简易掩体，但没有掩体占位或战术语义。未生成四周实体围墙；边界是位置校验而非封闭碰撞。

默认出生(-4.2,-2.7)、(4.2,-2.7)、(0,3.7)，最小中心间距约7.65m，无重复。Demo出生(-4,-3)、(4,-3)、(0,-4.2)，最小约4.18m。seed打乱分配，不随机搜索有效点。当前点远离墙且适合Proxy；换真实本体后需按足迹/朝向/初始高度复核。[dogfight_rl/src/dogfight_v0/arena/spawn_manager.py:12](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py:12)只查ID和数量，不查几何重叠，`zip(strict=True)`对多于3个出生点也会报错，当前恰好3点不触发此问题。

## 显示、碰撞、通行与射线不是同一层

|项目|证据|判断|
|---|---|---|
|地面/两墙真实Collider|scene.py CollisionPropertiesCfg|有创建代码与历史PhysX专项证据；本次不启动加载|
|射击/视线墙阻挡|PhysX closest ray，历史15项smoke；本次解析测试|基础墙遮挡已验证；真实狗高度/碰撞待回归|
|导航可通行检查|is_position_valid，墙外扩0.25m|仅检查终点中心；非完整机器人形体|
|Proxy撞墙|ProxyAgent.update拒绝非法终点|软件阻止位姿，不是动力学碰撞响应|
|机器人之间碰撞|kinematic cuboid + set_world_pose|有碰撞形状，不保证阻止两个代理重叠；本次相同位置可接受|
|边界|仅x/y有效性检查|部分完成；没有实体边界墙|
|自动绕障/寻路|SimpleNavigation不读取get_navigation_data|尚未实现|
|地图切换|工厂接arena_map参数，有MapInterface|可注入代码对象；无用户地图选择器、地图库及切换回归|

本次24秒解析探针：dog_a从(-2,0)追(2,0)，最终(-0.44,0)，goal_reached=false；中央墙前卡住。见 `AUDIT_PROBES.json/blocked_direct_navigation_24s`。这不是低层腿部控制故障，是直线导航没有绕障。

校验margin .25小于Proxy半长.375，且不随yaw变化，因此中心合法不能保证形体不碰墙；大步长可能跨过薄墙，尚未做连续扫掠测试。导航逻辑用扩张二维AABB，PhysX用实际三维墙，同源参数保证主要几何一致，但通行余量、身体尺寸、枪口高度与射线时刻尚未统一验证。AnalyticRayQuery以圆近似代理并跳过死者，真实PhysX用方块且死亡没有禁用collider，两后端并非完全等价。

## 验证边界与下一步方案（未执行）

现有20261026 smoke覆盖三Proxy加载、墙挡视线/子弹等15项；没有完整障碍绕行、边缘朝向碰撞、狗间动力学接触、真实三狗出生检查。下一轮先在CPU规则层增加尺寸/重复点/多出生点/扫掠协议，再经批准做独立短时Isaac碰撞矩阵：每面墙正向/斜向、三出生点、同场三本体、枪口不同高度。不得把显示成功当作地图逻辑完整。
