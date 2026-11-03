# 三机器人自主对战、HUD与集成审计

审计日期：2026-11-03（Asia/Shanghai）。本次只读分析与低资源CPU规则测试；未启动Isaac Sim、GPU仿真、训练、模型转换或安装依赖。所有新文件均在本审计目录。

## 能否完成目标中的三狗比赛

**当前正式入口不能直接完成三只最新关节机器狗的自主对战。** 可以运行的代码链是三Proxy规则比赛；运动策略在另一套单狗/批环境任务中。具备脚本规则自主选择与开枪，不等于PPO自主战斗。三真实本体装载、各自PPO适配、共享物理步进与完整物理对战验收缺失。

## 多代理现状

[dogfight_rl/src/dogfight_v0/runtime.py:47](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:47)严格构建dog_a/b/c三个独立对象，独立pose/command/alive/策略target/冷却/HP；同一场景下不同prim、红蓝绿颜色。导航字典按ID存目标，状态共享由manager统一管理，未发现直接共用一个目标变量的代码。dog_a只是代理身份，不表示自动使用旧Dog A。

[dogfight_rl/src/dogfight_v0/sim/scene.py:62](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/scene.py:62)配合IsaacPoseWriter.set_world_pose；Proxy按速度在Python中积分位姿。三体各有Collider，但kinematic teleport没有狗间相互避碰/动力学响应保障。本次相同坐标能被两个Proxy同时接受。真实关节机器人各自独立加载策略、接触碰撞、出生无穿插，目前证据不足。

历史[archive/historical_validation/battle_previous/migration_real_a/20261023_104635/dog_a_integration_summary.json:1](/home/zxq/robot_projects/archive/historical_validation/battle_previous/migration_real_a/20261023_104635/dog_a_integration_summary.json:1)写dog_a=RealDogAgent、b/c=Proxy，时间只有.0167s；这是旧模型混合拓扑单步接口试验，不是三真狗、不是新模型、不是一场比赛。

## 自主导航与作战决策逐项

|功能|实际实现|当前判断|
|---|---|---|
|目标位置获取|0/5/10…秒情报，视野内实时距离/方位|已实现；隐藏目标字段泄漏待修|
|选择多敌人|可见优先最近，非可见保持旧target否则最近intel|规则决策已实现，无战术学习|
|追踪目标变化|intel更新后更改navigation目标|基础实现；不含预测|
|转向瞄准|yaw_error×2.5限幅，进入容差即停并fire|规则实现；默认容差/命中尺寸可能不匹配|
|自主射击|可见且对准后fire，裁判查冷却/射线|链路存在且规则层验证|
|失去目标搜索|追旧位置，到达后scan；无intel也scan|简单扫描，非全地图搜索|
|路径规划/障碍绕行|SimpleNavigation直线命令，无图/NavMesh/A*|尚未实现；本次卡墙复现|
|卡住脱困|无进展监控、重规划或逃逸状态|尚未实现|
|主动躲避/后退|当前policy没有威胁/HP驱动后退、闪避逻辑|尚未实现；低层能退不等于决策会退|
|有利位置/掩体利用|未见掩体评分或选点|尚未实现|
|防止静止|只在到达目标/无目标时扫描|部分完成；对准但射不中可无限停射|
|战斗RL/自博弈|没有接入正式battle的训练环境/策略|尚未实现；PPO现用于运动|

证据：[dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:21](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:21)、[dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:44](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:44)。本次默认解析单局seed42，两存活者最终在x=±4.2,y=-2.7，近3°偏角后不断射击，236发仅3次命中，120秒平局。默认3°在8.4m距离对应横向约.44m，解析目标半径.4m，因此进入fire阈值不保证打中，策略又停止继续对准。该原因与几何/轨迹相容，是明确复现的解析后端僵持；真实方块半宽.24m与PhysX时序不同，需独立回归，不能照抄同一数值当物理实测。GUI demo已用1°容差和开放三角出生，不能将其成功外推默认battle配置。

## 两条关键集成链

|链条|当前实际通路|断点|
|---|---|---|
|决策→速度/方向|ScriptedBattlePolicy→导航/override→ProxyAgent.set_velocity_command|已连通Proxy|
|速度→PPO→关节→最新机器狗|仅独立locomotion环境内有，battle工厂未使用|RealLocomotionAdapter.compute_action/step抛NotImplementedError；无CSDog具体适配器|
|三本体统一仿真|RealDogAgent注释要求adapter安排shared stepping|实际scene只创建方块，缺共享步进调度的验证|
|策略→射击请求→裁判→扣血→死亡/结果|BattleAction.fire→WeaponService→HealthSystem→_evaluate_round|解析层本次完整运行；PhysX当前全场回归未执行|

[dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py:40](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py:40)只返回12个零动作并计数；Mock/接口测试通过不能视为策略推理。真正三机器人可共享同一权重文件但各有独立观测/动作状态；不必为了“三只狗”重新训练三个模型，是否分别策略由后续方案决定。

## HUD与演示

|展示项|实现/证据|状态|
|---|---|---|
|三个颜色/ID|scene.AGENT_COLORS、dog_a/b/c|当前代码+历史三Proxy显示|
|HP/存活/死亡|BattleHUD.update读manager快照|本次2个HUD文本测试通过；当前GUI未重跑|
|比赛时间/赢家/平局|format_round_status|本次文本通过|
|机器人精确位置数值/小地图|场景可看位置，HUD不显示坐标/小地图|尚未实现专用HUD显示|
|击杀记录|日志DEATH带source；无HUD击杀列表|部分完成|
|5秒暴露倒计时|intel有period；HUD无对应控件|尚未实现|
|视角切换|runtime仅固定set_camera_view|专用跟随/多视角切换尚未实现；平台手动视角非项目功能|
|重新开始|demo --auto-reset，HUD.reset|有历史多局结果；无专用重开按钮|
|录像/回放|有运动视频与事件JSONL；未见接入battle完整录像/状态回放|部分完成/证据不足|

[dogfight_rl/src/dogfight_v0/ui/battle_hud.py:8](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/battle_hud.py:8)说明HUD只拥有文本而非独立血量，设计正确。V0/v0.2 HUD没有全部废弃：当前BattleHUD在demo入口实际导入并build/update；历史GUI6项PASS是20261023，当前只做文本回归。旧legacy_compatibility副本不在PYTHONPATH，不是另一条正式入口。

## 当前实际可展示内容与测试范围

1. 现存同学原任务单狗前/后/转5秒视频与10秒指标，可直接播放已有视频；不能称三狗自主比赛。
2. 地图两墙+三色方块、规则射击、HP/死亡/结果，有旧代理演示与smoke证据。当前GUI代码保留，启动需独立短时回归；本次没有重新打开GUI保证现场成功。
3. 本次CPU解析规则可以重复演示一局并输出伤害/死亡/超时结果；解析几何不是Isaac场景。
4. 历史混合真A+两代理只是单步接线。旧ANYmal/旧DogA训练及视频不代替新模型能力。

历史[archive/historical_validation/battle_previous/v0/battle_demo/20260920_104814/demo_summary.json:1](/home/zxq/robot_projects/archive/historical_validation/battle_previous/v0/battle_demo/20260920_104814/demo_summary.json:1)记4局完成（总16.133s）且有轮流赢家；早期104104无伤害、104154未完成，也保留。它们只证明对应历史代理配置。当前默认battle运行上限30s、规则限120s，可能因外层duration先到而结束但没裁决；退出码0不能当作“一局完成”。GUI demo默认120总活跃秒、内部90秒，支持结果停留/auto-reset。

高资源后续测试仅列方案：锁定身份与入口→1真狗替换1Proxy→确认所有agent只在同一个sim.step推进→3真狗同场静止/碰撞→固定速度→接规则→多局自主。每步用独立输出目录、不覆盖历史权重；本次全部未执行。
