# 裁判系统审计

审计日期：2026-11-03（Asia/Shanghai）。本次只读分析与低资源CPU规则测试；未启动Isaac Sim、GPU仿真、训练、模型转换或安装依赖。所有新文件均在本审计目录。

## 权威裁判与实际调用链

当前没有另一个必须名为referee的独立服务；规则权威是[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:20](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:20)组合IntelService、VisibilityService、WeaponService、HealthSystem。`runtime.create_isaac_battle`实际构造并使用这些对象；ScriptedBattlePolicy只返回BattleAction（速度/导航目标/fire），不直接扣血，HUD读取get_match_state。**职责层面裁判独立，进程/权限层面没有隔离；信息接口有实际泄漏。**

调用链：BattleManager.step → policy.act(observation) → pending_fire → _process_fire → WeaponService.fire → PhysX closest ray → apply_damage → HealthSystem → set_alive/DEATH → _evaluate_round → ROUND_END/WINNER → HUD。证据[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:106](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:106)、[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:204](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:204)、[dogfight_rl/src/dogfight_v0/battle/battle_manager.py:215](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/battle_manager.py:215)。

## 比赛生命周期

|功能|当前实现/验证|状态|
|---|---|---|
|初始化/3ID注册|构造函数严格dog_a/b/c与policy集合|已实现；接口固定3人|
|出生分配/开始|reset、start_round；SpawnManager|已通过规则测试和历史smoke|
|计时|step累计仿真dt，默认120s|本次超时探针通过；非墙钟秒|
|暂停/恢复|无显式pause/resume状态机|尚未实现；外部停止调用step不等于产品功能|
|结束/停止|_finish_round stop所有agent|本次解析超时通过，历史最后存活者专项PASS|
|重置|HP/情报/冷却/导航/策略/死亡/计时清空|本次解析重置恢复100HP；历史不关闭Sim重置PASS|
|自动下一局|仅GUI demo --auto-reset与结果停留|代码存在、历史demo多局；本次未跑GUI|

## 射击、伤害与死亡

默认[dogfight_rl/src/dogfight_v0/config/battle_cfg.py:12](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/config/battle_cfg.py:12)：HP100，伤害34，冷却1s，射程20m，前向枪口射线；视距20m、半视场60°、对准容差3°。三次有效命中可致死。GUI demo另用伤害20、冷却.9s、射程/视距22m、半FOV28°、容差1°、90s上限，不能混为同一比赛规则。

[dogfight_rl/src/dogfight_v0/battle/weapon_service.py:23](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/weapon_service.py:23)拒绝死者与冷却中请求，一次调用只处理一个closest hit；自射ID被排除，FFA没有队友机制。墙最先命中即吸收；没有弹丸飞行和穿透，多目标只命中最近对象。不要求策略指定target，避免“指定谁就扣谁”；命中方向取机器人forward。策略fire时才进该链，没有独立联网射击API。

[dogfight_rl/src/dogfight_v0/battle/health_system.py:18](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/health_system.py:18)拒绝负伤害，HP下限0；死亡立即set_alive(false)并stop，后续step不决策、不移动，WeaponService再拦截开枪。日志有SHOT_FIRED/SHOT_HIT/DAMAGE/DEATH，死亡事件记source；无专用击杀榜，demo从事件累加命中/伤害。单帧pending_fire按字典顺序结算，先射死后者则后者无法同帧反击：是顺序裁决，未实现同时伤害语义。未发现同一发沿链重复扣血，但无外部请求ID去重（当前单进程本地调用不需要网络重试）。

死者从BattleManager暴露的intel及可见目标中排除，但其场景Collider未移除；PhysX射线可能被尸体阻挡，AnalyticRayQuery跳过死者。此差异静态确认，具体效果需物理回归，不标记为已复现的GPU故障。

## 胜负

alive≤1立即结束：1个为胜者，0个为平局；多人活到上限一律平局，不比较HP、击杀或伤害。ROUND_END与WINNER自动写日志，HUD显示赢家/平局，所有运动指令停止。没有额外清场销毁，但reset复用对象；停止程序和重置一局是不同操作。

本次默认解析单局seed42：120.0167s超时，236次射击、3次命中、3次伤害、1死亡、2存活、平局，随后reset全员100HP。它证明本次解析规则闭环，可发现当前策略问题；不代表PhysX比赛结果，也不是三狗关节运动验证。最后存活者胜出仅历史20261026 smoke第14项有PASS，本次没有冒充重新覆盖该分支。

## 五秒情报与权限漏洞

[dogfight_rl/src/dogfight_v0/battle/intel_service.py:20](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/intel_service.py:20)首次0秒播报，之后按5秒网格更新；帧跳过时推进到下个网格，不补造过去坐标。timestamp_s记录实际采样时刻，位置在两个播报间不可变、排除请求者。底层快照包含全部其他ID及alive（含死者）；BattleManager策略层立即筛除health已死目标。没有TTL/显式过期拒绝，策略持续使用最近记录并在到达后扫描。

**关键故障：[dogfight_rl/src/dogfight_v0/battle/visibility_service.py:19](/home/zxq/robot_projects/dogfight_rl/src/dogfight_v0/battle/visibility_service.py:19) 在判断FOV/LOS前就从真实位姿算distance_m与yaw_error_rad；无论visible是否false均返回这些数值。BattleManager把所有敌人的VisibilityResult传给策略。** 已知自己(x,y,yaw)可立即反推出墙后或背后敌人的真实位置；本次墙遮挡探针visible=false、distance=4、yaw_error=0，可精确反推(2,0)。证据 `AUDIT_PROBES.json/invisible_target_information`。

当前ScriptedBattlePolicy先过滤visible再使用这些字段，未主动利用不可见字段；但“只能通过规定接口、每5秒获取隐藏敌人位置”的约束没有被接口保证，换策略即可绕过。裁判内部读取真值正常；问题是向策略返回隐藏目标真值。还存在公开manager.agents/get_match_state可读真值，无不可信策略沙箱。若策略均为可信进程内代码，先修观测最小化就能堵住已发现漏洞；不必无依据重做分布式裁判。

## 测试与缺口

本次13个pytest包括HP死亡/reset、射击墙挡/扣血、冷却、5秒与旧位置、FOV/LOS、出生点、直线接近、HUD文本。`pytest_results.xml`记录13通过，0.02s。历史[dogfight_rl/runs/battle/v0/20261026_102513_28328183/smoke_summary.json:1](/home/zxq/robot_projects/dogfight_rl/runs/battle/v0/20261026_102513_28328183/smoke_summary.json:1)15项物理专项PASS；[archive/historical_validation/battle_previous/v0/20261023_104627/hud_smoke_summary.json:1](/home/zxq/robot_projects/archive/historical_validation/battle_previous/v0/20261023_104627/hud_smoke_summary.json:1)6项HUD历史PASS。未测真实三狗、自伤重叠边界、尸体遮挡、同帧双方致死、公平顺序、跳帧五秒、暂停恢复与持续多局内存清理。
