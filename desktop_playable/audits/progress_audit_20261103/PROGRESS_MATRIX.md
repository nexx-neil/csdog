# 项目完成度矩阵

口径：状态评估当前正式工程及明确区分的外部运动成果。“已完成且验证通过”只针对该行限定的CPU规则/结构范围；不外推GUI、PhysX或三真实机器人。历史物理PASS不自动升级为本次当前物理验证。详细函数、入口、验证日期和问题见各专项报告，源码函数索引见SOURCE_SYMBOL_INDEX.md。

|模块|子功能|代码实现|测试情况|当前状态|证据位置|
|---|---|---|---|---|---|
|机器狗模型|URDF结构/12DOF|13link/12revolute，本次解析|本次结构/惯量通过|已完成且验证通过|[model/robot.urdf:1](/home/zxq/robot_projects/model/robot.urdf:1)|
|机器狗模型|Isaac URDF→USD加载|转换闭包及训练引用|20261026 physics_gate PASS；当前未重跑|已实现但未验证|[dogfight_rl/runs/locomotion/csdog_ppo_20261026/reports/physics_gate.json:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_20261026/reports/physics_gate.json:1)|
|机器狗模型|质量惯量/COM机械真实性|张量正定，总重一致|无实机/CAD校核完整证据|证据不足|[course_presentation/model_audit_readonly.json:1](/home/zxq/robot_projects/course_presentation/model_audit_readonly.json:1)|
|机器狗模型|足底独立碰撞/传感|本地膝链聚合、V7候选；同学独立sole|各配置历史测试，未统一|部分完成|[dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md:1)|
|机器狗运动|稳定站立|固定PD历史成功；PPO零命令漂移|当前无新物理测试|部分完成|[dogfight_rl/runs/locomotion/csdog_ppo_20261026/reports/physics_gate.json:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_20261026/reports/physics_gate.json:1)|
|机器狗运动|前进|同学Teleop短测成功，本地V7未合格|同学10秒/1env；当前battle未接|部分完成|[peer_csdog_review/peer_perturbed_forward_025.json:1](/home/zxq/robot_projects/peer_csdog_review/peer_perturbed_forward_025.json:1)|
|机器狗运动|后退|同学短测成功、本地V6.2失败|同学-.25→-.211；非本次复测|部分完成|[peer_csdog_review/peer_perturbed_backward_025.json:1](/home/zxq/robot_projects/peer_csdog_review/peer_perturbed_backward_025.json:1)|
|机器狗运动|原地旋转|同学左右转成功但侧漂|当地短测；严格原地未合格|部分完成|[peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md:1](/home/zxq/robot_projects/peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md:1)|
|机器狗运动|停止运动|所有已比对策略有漂移|V7 stop_speed .2126；同学.032|存在故障|[dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/STATUS_SUMMARY.md:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/STATUS_SUMMARY.md:1)|
|机器狗运动|连续速度/动作切换|命令接口存在|连续组合鲁棒性未充分验证|已实现但未验证|[dogfight_rl/src/dogfight/locomotion/env_cfg.py:25](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py:25)|
|机器狗运动|横移|有采样/历史单命令配置|当地7项复测未覆盖，缺统一标准|证据不足|[peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md:1](/home/zxq/robot_projects/peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md:1)|
|机器狗运动|摔倒检测|姿态/触地终止|历史物理评估使用|已实现但未验证|[dogfight_rl/src/dogfight/locomotion/env_cfg.py:71](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py:71)|
|机器狗运动|摔倒后自主起身|未找到接入实现|无验证|尚未实现|[dogfight_rl/src/dogfight/locomotion/env_cfg.py:71](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py:71)|
|PPO训练|训练/保存/评估工具|多版本runner、日志、identity、权重|已有训练/单因素评估记录|部分完成|[dogfight_rl/scripts/train/csdog_12dof.py:1](/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_12dof.py:1)|
|PPO训练|全动作运动验收|独立Gate与物理指标|本地V6.3/V7未通过|存在故障|[dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md:1)|
|地图系统|地图加载|1套程序化几何，2出生配置|历史物理smoke；本次静态|已实现但未验证|[dogfight_rl/src/dogfight_v0/sim/scene.py:43](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/sim/scene.py:43)|
|地图系统|障碍物碰撞|真实墙collider+Proxy中心校验|历史射线PASS，真实狗撞墙未测|部分完成|[dogfight_rl/src/dogfight_v0/arena/test_map.py:53](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py:53)|
|地图系统|三机器人出生点|固定3点、seed分配|本次2项出生测试PASS|已完成且验证通过|[dogfight_rl/src/dogfight_v0/arena/spawn_manager.py:12](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/spawn_manager.py:12)|
|地图系统|实体围墙/边界|仅逻辑边界|没有封闭围墙|部分完成|[dogfight_rl/src/dogfight_v0/arena/test_map.py:26](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/arena/test_map.py:26)|
|地图系统|多地图切换|接口可注入，缺其他成品地图与选择器|未验证|部分完成|[dogfight_rl/src/dogfight_v0/runtime.py:26](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:26)|
|地图系统|狗间不穿插|运动学方块，无相互位置验证|本次同位置接受|存在故障|[dogfight_rl/src/dogfight_v0/agents/proxy_agent.py:72](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/proxy_agent.py:72)|
|裁判系统|射击命中|closest hit射线、方向/射程/冷却|本次解析测试与历史PhysX专项|已完成且验证通过|[dogfight_rl/src/dogfight_v0/battle/weapon_service.py:23](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/weapon_service.py:23)|
|裁判系统|血量管理|100HP，下限0，34伤害默认|本次规则测试/解析单局|已完成且验证通过|[dogfight_rl/src/dogfight_v0/battle/health_system.py:18](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/health_system.py:18)|
|裁判系统|死亡判定|HP0→alive false→stop/fire禁用|本次HP与解析单局；真狗未接|已完成且验证通过|[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:195](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:195)|
|裁判系统|胜负判定|最后存活胜/无人或超时平局|本次超时通过，最后存活历史PASS需回归|部分完成|[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:215](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:215)|
|裁判系统|重置/下一局|manager reset；demo自动下一局|本次reset通过，自动多局仅历史|部分完成|[dogfight_rl/scripts/battle/run_v0_battle_demo.py:202](/home/zxq/robot_projects/dogfight_rl/scripts/battle/run_v0_battle_demo.py:202)|
|裁判系统|暂停恢复|无显式状态机|无|尚未实现|[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:1)|
|对战机制|5秒位置暴露|0秒起网格快照/时间戳/过滤自身|本次2个测试PASS|已完成且验证通过|[dogfight_rl/src/dogfight_v0/battle/intel_service.py:20](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/intel_service.py:20)|
|对战机制|限制隐藏敌人实时位置|不可见仍返回距离/方位|本次墙后位置精确反推|存在故障|[dogfight_rl/src/dogfight_v0/battle/visibility_service.py:36](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/visibility_service.py:36)|
|对战机制|尸体射线一致性|解析忽略死者，物理collider保留|静态差异，未物理回归|部分完成|[dogfight_rl/src/dogfight_v0/battle/ray_query.py:46](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/ray_query.py:46)|
|自主导航|目标追踪|直线目标接近、5秒更新|本次直线接近测试PASS|已完成且验证通过|[dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:44](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:44)|
|自主导航|障碍物绕行|没有规划器|本次24s卡墙|尚未实现|[dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:1)|
|自主导航|卡住重规划/脱困|无进展监控|无|尚未实现|[dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/navigation/simple_navigation.py:1)|
|作战决策|自主射击|规则可见/对准fire|解析单局有命中/死亡；默认僵持|部分完成|[dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:21](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:21)|
|作战决策|追击/多敌选择/丢失扫描|规则策略已实现|无完整物理对抗回归|已实现但未验证|[dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:1)|
|作战决策|主动躲避/后退/掩体|当前policy无战术逻辑|无|尚未实现|[dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/scripted_policy.py:1)|
|作战决策|战斗RL/自博弈|无接入的高层RL|无|尚未实现|[dogfight_rl/src/dogfight_v0/runtime.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:1)|
|系统集成|三代理规则比赛|Proxy→射击→HP→结果|本次解析单局超时平局；历史物理专项|部分完成|[dogfight_rl/src/dogfight_v0/runtime.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:1)|
|系统集成|三狗同时对战|scene只创建Proxy，缺具体适配器|无三真狗对战记录|尚未实现|[dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py:33](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_locomotion_adapter.py:33)|
|系统集成|决策→PPO→关节动作|独立运动环境可推理，未连battle|mock不算真实链验证|部分完成|[dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/agents/real_dog_agent.py:1)|
|可视化|HUD血量显示|读裁判快照、存活/HP|本次文本测试PASS；GUI历史需回归|部分完成|[dogfight_rl/src/dogfight_v0/ui/battle_hud.py:88](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/battle_hud.py:88)|
|可视化|时间/赢家/平局文本|format_round_status|本次HUD文本测试PASS|已完成且验证通过|[dogfight_rl/src/dogfight_v0/ui/battle_hud.py:136](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/battle_hud.py:136)|
|可视化|5秒倒计时/击杀列表/坐标|无专用HUD控件|无|尚未实现|[dogfight_rl/src/dogfight_v0/ui/battle_hud.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/ui/battle_hud.py:1)|
|可视化|专用视角切换/重开按钮|固定镜头、CLI自动重置|专用UI无证据|尚未实现|[dogfight_rl/src/dogfight_v0/runtime.py:37](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:37)|
|可视化|完整比赛录像/回放|事件日志存在、单狗视频存在|比赛全程回放未验证|部分完成|[dogfight_rl/src/dogfight_v0/logging/battle_logger.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/logging/battle_logger.py:1)|
|系统集成|完整比赛闭环|代理规则链已有；真实三狗缺失|本次只验解析规则，非最终目标|部分完成|[dogfight_rl/src/dogfight_v0/runtime.py:1](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/runtime.py:1)|

状态严格采用六种指定标识。每行的范围/复杂度并不相同，不将已实现行数或此表条目占比换算为项目完成百分比。“尚未实现”表示在当前有效调用链中未找到实现；与归档或同学分支某项历史成果并不冲突。
