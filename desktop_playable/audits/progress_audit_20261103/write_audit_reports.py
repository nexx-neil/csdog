from pathlib import Path
import json,re,datetime,hashlib,subprocess,collections
R=Path('/home/zxq/robot_projects');A=Path(__file__).parent;D='dogfight_rl/';V=D+'src/dogfight_v0/';L=D+'src/dogfight/locomotion/';RUN=D+'runs/locomotion/'
def e(path,needle=None,label=None):
 p=R/path;line=1
 if needle and p.is_file():
  lines=p.read_text(errors='replace').splitlines();line=next((i for i,s in enumerate(lines,1) if needle in s),1)
 return f'[{label or path+":"+str(line)}]({p}:{line})'
def w(name,s): (A/name).write_text(s.strip()+'\n',encoding='utf-8')
def ve(p,n=None):return e(V+p,n)
def le(p,n=None):return e(L+p,n)
def rr(p,n=None):return e(RUN+p,n)
common='审计日期：2026-11-03（Asia/Shanghai）。本次只读分析与低资源CPU规则测试；未启动Isaac Sim、GPU仿真、训练、模型转换或安装依赖。所有新文件均在本审计目录。'
w('PROJECT_OVERVIEW.md',f'''# 项目结构与当前入口

{common}

## 核心结论与版本边界

正式业务工程是 `dogfight_rl`，对战入口 `launch.py battle` / `battle-gui`；包名带v0不意味着停用。当前源码保留V0规则与v0.2 HUD。{e(D+'launch.py','scripts =')} 直接分派headless与demo脚本；{ve('runtime.py','agents =')} 明确只实例化3个ProxyAgent，{ve('sim/scene.py','size=(0.75')} 创建运动学方块。当前对战不加载URDF、USD关节机器人或checkpoint。

运动分支没有统一升级后的默认入口：`launch.py train/evaluate/play` 仍指向最早csdog_12dof脚本（45/48维观测），V2–V6.3有独立脚本，V7由 `scripts/autoppo/v7.py` 与 `phase_v7_manager.py` 管理。最新试验记录是V7，不能称“已部署主策略”。同学Teleop方案在 `peer_csdog_review/extracted/` 独立运行，11月1日课程汇报采用它的运动成果，但正式battle工厂没有引用它。见{e('course_presentation/PROJECT_EVIDENCE.md','第三页修订')}、{e('peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md')}。

## 目录结构

```text
robot_projects/
├── model/                 最新机械原件：URDF、preview、package.xml、13 STL
├── dogfight_rl/            正式工程
│   ├── launch.py          默认命令分派
│   ├── src/dogfight/      模型身份、路径、PPO工具、locomotion多版本、autoppo
│   ├── src/dogfight_v0/   agents/arena/battle/navigation/sim/ui/logging/config
│   ├── assets/            import_v1 USD闭包、sole候选及被拒绝候选
│   ├── configs/           机器人元数据、课程/实验/PPO/服务配置
│   ├── scripts/           train/evaluate/battle/diagnostics/autoppo
│   ├── tests/             规则、接口、预算、评估器等轻量测试
│   ├── runs/locomotion/   V1–V7、A/B诊断、权重、遥测与视频
│   ├── runs/battle/       当前保留的20261026规则smoke
│   └── docs/              当前/过时说明并存
├── peer_csdog_review/      同学发布包、解压源码/策略、当地复测JSON与视频
├── course_presentation/    11月汇报、证据索引；不是运行入口
├── archive/
│   ├── legacy_dog_a/       旧机械本体、训练、策略、诊断
│   ├── legacy_compatibility/ 停用源码/日志实体副本
│   ├── historical_validation/ 历史V0、HUD、混合真A+2代理验收
│   ├── environment_records/ 环境冻结文档与快照
│   └── migration_backups/  历史迁移和压缩备份
├── reorganization/20261026/ 路径映射、保护清单、原文备份
├── IsaacLab/               冻结第三方；仅识别，不逐文件扫描
├── blackhorse_lightstick/  无关灯棒工程，仅目录识别
└── audits/                 本次报告
```

递归目录展开见 `DIRECTORY_TREE.txt`，文件元数据见 `FILE_INVENTORY.json`（11012项，排除第三方IsaacLab、.git、缓存、LibreOffice profile和审计输出；不解压历史大备份）。枚举不代表逐个审读全部文件。地图与战斗命名索引见 `MAP_BATTLE_RESOURCE_INDEX.txt`；checkpoint索引1695项包含历史/重复副本，不表示1695个有效策略。没有修改或执行归档迁移工具。

## 调用关系

```mermaid
flowchart TD
  LA[launch.py battle / battle-gui] --> EN[headless / battle_demo]
  EN --> RT[create_isaac_battle]
  RT --> SC[程序化TestMap + 3个运动学方块]
  RT --> BM[BattleManager]
  BM --> OB[Intel + Visibility观测]
  OB --> PO[ScriptedBattlePolicy]
  PO --> NA[SimpleNavigation / 直接速度]
  NA --> PR[ProxyAgent积分位姿]
  PO --> WE[WeaponService + PhysX射线]
  WE --> HP[HealthSystem]
  HP --> RE[死亡 / 胜负 / HUD / 日志]
  LO[独立PPO运动环境] --> CP[各版本checkpoint]
  CP -.缺少具体适配器和共享物理调度.-> PR
```

真实本体工具{ve('agents/real_dog_agent.py','class RealDogAgent')}存在；{ve('agents/real_locomotion_adapter.py','raise NotImplementedError')}仍抛出未实现异常。接口/mock验证不能代表“决策→PPO→关节→三狗同场”已打通。

## 已有证据分层

|证据|时间|适用范围|限制|
|---|---|---|---|
|当前目录smoke_summary 15 PASS|2026-10-26|三Proxy、PhysX规则专项|不是完整自主策略/三关节机器人比赛|
|归档hud_smoke_summary 6 PASS|2026-10-23|旧HUD GUI专项|本次只复验文本逻辑，需当前GUI回归|
|归档demo_summary|2026-09-20|代理比赛及多局结果|部分早期记录未完成，不能只取成功一条|
|新模型physics_gate|2026-10-26|自由机身、接触、12关节响应|不是行走验收|
|V6.2/V6.3/V7物理评估|2026-10-28～29文件记录|运动退化/不合格证据|不是本次重跑|
|同学原策略当地复测|2026-10-30文件mtime|短程前后/双转/静止、视频|单环境、未接battle；seed20261031不是执行日期|
|本次pytest|2026-11-03|13项规则、HUD文本|解析射线，无GUI/PhysX|
|本次AUDIT_PROBES.json|2026-11-03|静态模型、信息泄漏、卡墙、规则单局|纯CPU内存模型，不是Isaac比赛|

运行时进程只读检查未发现csdog/PPO/battle进程；V7状态JSON仍写DIAGNOSTIC_RUNNING、manager_alive=true，heartbeat停在10月29日，不能当作当前正在训练。未触碰任何现有任务。
''')
w('MAP_AUDIT.md',f'''# 地图与场景审计

{common}

## 数量、格式与实际选择

按“不同比赛几何”计数，当前正式源码找到 **1张基础比赛地图**：Python程序化 `TestMap`，不是独立USD地图文件。`DemoTestMap`只更改出生点，属于同一几何的第2出生配置，不应算成两张完整不同地图。归档有同源旧副本，不算新增地图。PPO平地TerrainImporter和同学训练plane是运动测试场地，不是带裁判和出生点的比赛地图。未在已扫描业务代码中找到其他接入比赛的独立地图；未解包历史tar，不能声称所有压缩备份绝对没有其他地图。

|资源|格式/内容|入口|状态|
|---|---|---|---|
|TestMap|Python边界、墙和Pose2D|battle默认create_isaac_battle|基础场景已实现，有20261026物理smoke|
|DemoTestMap|TestMap继承，仅替换3出生点|battle-gui|有历史代理demo，当前GUI需回归|
|运动平地|TerrainImporterCfg plane|单狗PPO各版本|不是比赛地图|
|旧TestMap副本|archive源码快照|不在默认PYTHONPATH|历史证据，不作当前功能计数|

证据：{ve('arena/test_map.py','class TestMap')}、{e(D+'scripts/battle/run_v0_battle_demo.py','class DemoTestMap')}、{le('env_cfg.py','terrain=TerrainImporterCfg')}。完整命名索引见 `MAP_BATTLE_RESOURCE_INDEX.txt`。

## 地图内容与完成情况

{ve('arena/test_map.py','self._bounds')} 定义x∈[-6,6]、y∈[-5,5]；地面由{ve('sim/scene.py','GroundPlaneCfg')}创建14×12m。两面内部墙：中心(0,0,.75)、尺寸(.35,3.2,1.5)；侧墙(2.6,1.6,.75)、尺寸(2.4,.35,1.5)。它们可作为遮挡/简易掩体，但没有掩体占位或战术语义。未生成四周实体围墙；边界是位置校验而非封闭碰撞。

默认出生(-4.2,-2.7)、(4.2,-2.7)、(0,3.7)，最小中心间距约7.65m，无重复。Demo出生(-4,-3)、(4,-3)、(0,-4.2)，最小约4.18m。seed打乱分配，不随机搜索有效点。当前点远离墙且适合Proxy；换真实本体后需按足迹/朝向/初始高度复核。{ve('arena/spawn_manager.py','def assign_spawns')}只查ID和数量，不查几何重叠，`zip(strict=True)`对多于3个出生点也会报错，当前恰好3点不触发此问题。

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
''')
w('REFEREE_AUDIT.md',f'''# 裁判系统审计

{common}

## 权威裁判与实际调用链

当前没有另一个必须名为referee的独立服务；规则权威是{ve('battle/battle_manager.py','class BattleManager')}组合IntelService、VisibilityService、WeaponService、HealthSystem。`runtime.create_isaac_battle`实际构造并使用这些对象；ScriptedBattlePolicy只返回BattleAction（速度/导航目标/fire），不直接扣血，HUD读取get_match_state。**职责层面裁判独立，进程/权限层面没有隔离；信息接口有实际泄漏。**

调用链：BattleManager.step → policy.act(observation) → pending_fire → _process_fire → WeaponService.fire → PhysX closest ray → apply_damage → HealthSystem → set_alive/DEATH → _evaluate_round → ROUND_END/WINNER → HUD。证据{ve('battle/battle_manager.py','pending_fire:')}、{ve('battle/battle_manager.py','def _process_fire')}、{ve('battle/battle_manager.py','def _evaluate_round')}。

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

默认{ve('config/battle_cfg.py','weapon_damage')}：HP100，伤害34，冷却1s，射程20m，前向枪口射线；视距20m、半视场60°、对准容差3°。三次有效命中可致死。GUI demo另用伤害20、冷却.9s、射程/视距22m、半FOV28°、容差1°、90s上限，不能混为同一比赛规则。

{ve('battle/weapon_service.py','def fire')}拒绝死者与冷却中请求，一次调用只处理一个closest hit；自射ID被排除，FFA没有队友机制。墙最先命中即吸收；没有弹丸飞行和穿透，多目标只命中最近对象。不要求策略指定target，避免“指定谁就扣谁”；命中方向取机器人forward。策略fire时才进该链，没有独立联网射击API。

{ve('battle/health_system.py','def apply_damage')}拒绝负伤害，HP下限0；死亡立即set_alive(false)并stop，后续step不决策、不移动，WeaponService再拦截开枪。日志有SHOT_FIRED/SHOT_HIT/DAMAGE/DEATH，死亡事件记source；无专用击杀榜，demo从事件累加命中/伤害。单帧pending_fire按字典顺序结算，先射死后者则后者无法同帧反击：是顺序裁决，未实现同时伤害语义。未发现同一发沿链重复扣血，但无外部请求ID去重（当前单进程本地调用不需要网络重试）。

死者从BattleManager暴露的intel及可见目标中排除，但其场景Collider未移除；PhysX射线可能被尸体阻挡，AnalyticRayQuery跳过死者。此差异静态确认，具体效果需物理回归，不标记为已复现的GPU故障。

## 胜负

alive≤1立即结束：1个为胜者，0个为平局；多人活到上限一律平局，不比较HP、击杀或伤害。ROUND_END与WINNER自动写日志，HUD显示赢家/平局，所有运动指令停止。没有额外清场销毁，但reset复用对象；停止程序和重置一局是不同操作。

本次默认解析单局seed42：120.0167s超时，236次射击、3次命中、3次伤害、1死亡、2存活、平局，随后reset全员100HP。它证明本次解析规则闭环，可发现当前策略问题；不代表PhysX比赛结果，也不是三狗关节运动验证。最后存活者胜出仅历史20261026 smoke第14项有PASS，本次没有冒充重新覆盖该分支。

## 五秒情报与权限漏洞

{ve('battle/intel_service.py','def update')}首次0秒播报，之后按5秒网格更新；帧跳过时推进到下个网格，不补造过去坐标。timestamp_s记录实际采样时刻，位置在两个播报间不可变、排除请求者。底层快照包含全部其他ID及alive（含死者）；BattleManager策略层立即筛除health已死目标。没有TTL/显式过期拒绝，策略持续使用最近记录并在到达后扫描。

**关键故障：{ve('battle/visibility_service.py','op, tp =')} 在判断FOV/LOS前就从真实位姿算distance_m与yaw_error_rad；无论visible是否false均返回这些数值。BattleManager把所有敌人的VisibilityResult传给策略。** 已知自己(x,y,yaw)可立即反推出墙后或背后敌人的真实位置；本次墙遮挡探针visible=false、distance=4、yaw_error=0，可精确反推(2,0)。证据 `AUDIT_PROBES.json/invisible_target_information`。

当前ScriptedBattlePolicy先过滤visible再使用这些字段，未主动利用不可见字段；但“只能通过规定接口、每5秒获取隐藏敌人位置”的约束没有被接口保证，换策略即可绕过。裁判内部读取真值正常；问题是向策略返回隐藏目标真值。还存在公开manager.agents/get_match_state可读真值，无不可信策略沙箱。若策略均为可信进程内代码，先修观测最小化就能堵住已发现漏洞；不必无依据重做分布式裁判。

## 测试与缺口

本次13个pytest包括HP死亡/reset、射击墙挡/扣血、冷却、5秒与旧位置、FOV/LOS、出生点、直线接近、HUD文本。`pytest_results.xml`记录13通过，0.02s。历史{e(D+'runs/battle/v0/20261026_102513_28328183/smoke_summary.json')}15项物理专项PASS；{e('archive/historical_validation/battle_previous/v0/20261023_104627/hud_smoke_summary.json')}6项HUD历史PASS。未测真实三狗、自伤重叠边界、尸体遮挡、同帧双方致死、公平顺序、跳帧五秒、暂停恢复与持续多局内存清理。
''')
w('MODEL_AND_RL_AUDIT.md',f'''# 模型、运动能力与PPO审计

{common}

## 最新原件与当前引用关系

本次重新解析 `model/robot.urdf`：SHA256 `20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`，与既有model_audit记录及同学原始robot.urdf一致。本次实际计算见 `AUDIT_PROBES.json/model`，不是依据文档推断。

|检查项|直接证据/结果|边界|
|---|---|---|
|文件格式|robot.urdf、robot.preview.urdf、package.xml、13个STL；派生import_v1/csdog.usd及4个配置USD|原件目录没有USD；USD在正式assets|
|四足结构|base→每腿hip_roll→hip_pitch→knee，LF/RF/LR/RR，各3转动关节，13link/12revolute|结构完整不等于能走|
|关节名|joint_{{lf,rf,lr,rr}}_{{1,2,3}}|每腿3个，不能沿用旧FL/HIP等命名|
|质量|7.6042608kg；13link均有质量/COM/inertia|物理Gate质量7.6042611kg一致；缺机械实测认证|
|惯量|本次13张量全部通过正定主子式检查|数值合法不证明CAD密度/电机真实正确|
|限位|所有关节±3.14rad、10Nm、3rad/s|宽限位；无实机极限资料，不能认证机械安全限位正确|
|足/小腿|原件knee兼含小腿/足端；每link有visual/collision|无4个独立sole link，不能将膝碰撞净力直接称足底独立测量|
|传感|全body ContactSensor，FEET筛4个knee，track_air_time|后续500Hz PhysX接触/几何指标补充，非硬件传感器|
|模型加载|20261026 physics_gate PASS，13刚体/12关节响应、自由根部重力站立|本次未运行Isaac加载，历史证据需按版本回归|

引用链：{e(D+'assets/csdog_12dof/import_v1/config.yaml','asset_path')}记录源为最新model/robot.urdf；{le('robot_cfg.py','usd_path=')}训练加载其转换USD，不是运行时直接读URDF。{e(D+'scripts/train/csdog_12dof.py','identity=')}把URDF SHA、动作顺序、维数写identity；resume会检查身份。后续多数分支继承此robot配置，V7 collision=sole时{le('phase_guided_v7/runtime.py',"if o['collision']=='sole'")}切到 `collision_sole_candidate/csdog.usda`。**训练引用最新机械来源成立；对战引用不成立。**

默认显式动作顺序是LF1/2/3、RF1/2/3、LR1/2/3、RR1/2/3，preserve_order=True。物理Gate报告运行时张量原序是LF1、LR1、RF1、RR1、LF2…，因此“URDF顺序/PhysX顺序/策略顺序”不是同一顺序，当前任务用显式匹配解决，后续适配器必须保留。

默认PD Kp25、Kd0.8、10Nm、3rad/s，自碰撞禁用，soft_joint_pos_limit_factor=.9，根部不固定。原件没有CAD装配源、质心实测、电机标定报告的充分证据，不把数值一致写成机械合理性全部通过。

## 运动能力：按版本分别判断

等级：A没有实现；B有代码未验证；C历史测试成功；D当前版本本次验证；E当前版本有问题或退化。这里“当前运动分支”指V6/V7独立实验；“同学方案”是现有可用运动成果，课程已采用但尚未部署到正式battle。没有任何一项真实物理运动被本次授予D。

|动作|正式默认/后续本地训练|同学Teleop原任务|综合状态/证据|
|---|---|---|---|
|自由机身固定PD站立|C，8秒Gate终高.3402m、0摔倒，V7原碰撞10秒静态亦稳定|C，30秒终高.389m、0摔倒|历史成功；非PPO停止能力|
|PPO零命令稳定站立|E，V7停止速度约.2126m/s、yaw .1881|E，零命令前漂.032m/s、yaw .051且四足踏步|存在故障，不能用于稳定停车瞄准|
|前进|E/部分：V6.2可约.228m/s，但有滑移；V7 .2203m/s且qualified=false|C，目标.25→实际.2609m/s，10秒1env无摔倒、四足摆动|同学短测成功；本地分支非合格四足步态|
|后退|E，V6.2原任务复测-.004m/s，基本失败；V7仍FORWARD课程无成功证据|C，-.25→-.2111m/s；-.15→-.111m/s|同学已有短程成果，未接正式对战|
|原地左转|E，V6.2 +yaw实际约.002rad/s；V7无该阶段成功记录|C但有缺陷：+.3→+.287，侧移-.078m/s|能转但不能认定严格原地稳定|
|原地右转|E，V6.2实际约+.013rad/s；V7未证实|C但有缺陷：-.3→-.348，侧移+.080m/s|同上|
|横移|本地有代码/早期测试但没有可用合格证据，V6课程vy=0|有混合命令配置与发布包历史JSON；当地独立扰动7项未覆盖横移|证据不足，不能据训练范围宣布完成|
|停止|E，V6.2与V7均漂移，同学也未合格|E|关键瓶颈|
|连续速度命令|B/部分：命令采样与Actor输入存在|固定命令测试C；连续变速/切换缺当地验证|已实现但未验证完整连续控制|
|多动作切换|V7 transition_stop评估仍漂移约.176m/s|发布mixed任务是配置；未见当地长连续切换验收|部分完成/需回归|
|摔倒检测|姿态/机身触地终止与reset代码，既有评估统计|同样有episode终止|检测存在；不等于主动起身|
|摔倒后自主恢复站起|未找到接入策略的起身动作/控制器|没有充分证据|尚未实现（训练reset/AutoPPO恢复不是机器人起身）|

运动数值来自{e('peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md','原策略固定命令测试')}及peer_perturbed_*.json；文件mtime为20261030，seed值不代表运行日期。每项1环境10秒，不能外推为长期可靠性，视频5秒与10秒测试是独立运行。同学3段前/后/转mp4已存在；本次仅确认文件，不重新渲染、不重复认证帧内容。

## 训练各代结果与退化

|分支|成果|问题/当前意义|
|---|---|---|
|最早csdog_ppo_20261026|300累计更新含smoke与官方入口验证；45维Actor/48维Critic；physicsGate通过|不是当前全部训练量；launch默认仍到该脚本，预算耗尽不能直接继续|
|Spot V2 / aligned V3|独立奖励/接触适配，V3约.254m/s前进|V3零命令约.196m/s，腿参与不均，不能宣告步态成功|
|V4|修复奖励与诊断平衡控制，另有2500轮实验|IK诊断能抬腿不代表PPO学会；5更新/2500诊断必须分开|
|V5|1500更新搜索、保存候选与评估|推荐trial003主要平移近0；部分候选能转但平移仍失败|
|V6 / V6.1|课程、物理评估和checkpoint分段保存，前进出现局部步态|2500锚点不满足完整Stage1；继续训练可丢失稀少合格片段|
|V6.2专项|300+300同源A/B、时序/奖励/滑移诊断，保存B+100快照|单点gait可高，持续性/有方向完整周期未通过；后退/转向失败|
|V6.3|A/B各300更新与完整周期指标|BLOCKED_AB_FAILED；complete_stride_ratio=0，未启动长期训练|
|AutoPPO / V7|自动实验/恢复工具、相位观测、sole对照和多种子物理指标|V7 qualified=false、FORWARD，不能据“manager_alive”称正在训练|
|同学Teleop|50维相位观测，独立sole、原任务原checkpoint短测前后/双转成功|停止/转向侧漂未解决；正式battle无引用|

主要证据：{rr('csdog_ppo_spot_v4/reports/SPOT_V4_REPAIR_REPORT.md','结论')}、{rr('csdog_ppo_tuning_v5/reports/PPO_HYPERPARAMETER_SEARCH_REPORT.md','同预算参数与结果')}、{rr('csdog_ppo_v6_2_diagnostics/FINAL_V6_2_DIAGNOSIS.md','完整验收')}、{rr('csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md')}、{rr('csdog_phase_guided_ppo_v7/TRAINING_STATUS.json','qualified')}。本地出现“有前进速度但拖滑/少腿摆动”的问题有实际日志，不宜统一描述为目前所有方案都趴地；同学方案确有短测四足运动成果。

V7最佳记录actual_speed=.2203、phase_match=.7895、complete_cycles=[0,0,0,1]、min_swing_per_env=0、support_slip=.1939，仍qualified=false。停止速度.2126、偏航.1881。最近状态heartbeat为20261029、manager_pid=161908，本次进程快照没有该训练器；不能从过时JSON判定当前活跃。

## 观测、动作、奖励和PPO

|项|最早默认任务|V6系/V7|同学Teleop|
|---|---|---|---|
|环境|ManagerBasedRLEnv 平地|继承独立课程平地|DirectRLEnv独立任务|
|Actor/Critic维数|45 / 48|48 / 48；V7相位启用50|50 / 50|
|观测|角速度、投影重力、3命令、12位置偏差/速度/上次动作；Critic加线速度|Spot风格增加线速度；V7 sin/cos时钟|线角速度、重力、3命令、12状态/历史动作、sin/cos相位|
|动作|12位置目标，scale .25，默认姿态偏置，clip1|scale .20，具体裁剪随runner；不可假设全部版本相同|clip±1 ×.35+默认角，LR/LF/RF/RR顺序|
|控制周期|dt .005×4=.02s|dt .002×10=.02s|dt .005×4=.02s|
|episode|8s/timeout、机身触地、姿态坏终止|通常20s与继承终止/评估协议|固定命令当地10s评估，非等同训练episode|
|命令|每3–5s采样，20%站立；vx±.35、vy±.22、yaw±.5|课程分布；V7当前FORWARD，stop_fraction .2|最终配置vx±.4、vy±.3、yaw±.4、45%多轴、10%静止|
|奖励|xy/yaw指数跟踪，姿态、接触、力矩、加速度、平滑、限位；可选gait/air/clearance/slip|进度/跟踪/停止/非目标轴+滑移/摆腿；V7相位支撑/释放/高度/错误支撑等|跟踪、相位支撑/释放、渐进高度、姿态/停止与滑移|
|网络|128×128×128 ELU|512×256×128 ELU|256×256×128 ELU|
|PPO基础|24步、5epochs、4mini batches、lr .001 adaptive、clip .2、γ .99、λ .95、entropy .005|lr .0001 fixed，entropy .0025；options可覆盖|24步、lr .001 adaptive、clip .2、γ .99、λ .95|
|随机化|reset基座xy/yaw、关节偏移，无完整摩擦/质量/推力DR证据|继承与选项决定，缺鲁棒全套验收|当地额外单次初始扰动；不能称完整Domain Randomization验证|

证据：{le('env_cfg.py','class PolicyObs')}、{le('ppo_cfg.py','algorithm=')}、{le('curriculum_v6/config.py','class PPOCfg')}、{le('phase_guided_v7/runtime.py','class PhaseObs')}、{e('peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md')}。表中为各分支可读默认/记录，不把配置当所有checkpoint的实际训练超参；具体run的agent/env/options/identity与日志优先。

## 足底候选与不兼容风险

本地V7候选保留13刚体/12关节/原质量，拆分sole cap与上段碰撞；两个被拒球形sole仍存档。{rr('csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md')}记录原碰撞静态也稳定，不能归因“原模型碰撞必然错误”。同学训练URDF则有17link（4个1g sole）、12转动+4固定，球形sole，限位±.65/1.4/1.8、12Nm/10rad/s、PD40/1.5，与本地10Nm/3rad/s/PD25/.8不同。机械原件同SHA并不意味着策略直接兼容。

旧Dog A、45维初版、48维V6、50维V7/同学权重均不能任意互换。即便都是50维，关节顺序、时钟、默认姿态、碰撞、驱动、动作尺度仍不同。最早resume有identity全等检查，不能外推后续所有工具都有完整身份校验。安全审计未反序列化所有权重；仅盘点1695文件和已有身份/评估证据，文件存在不代表可部署。跨同学权重维数结论来自既有权重检查与当地原任务推理证据，并非本次新加载权重。

## 可复现性与后续低风险验证方案

已有seed/options、config快照、PPO指标、checkpoint、原始npz/接触轨迹、视频和预算ledger，支持复查；恢复网络/优化器不必然恢复仿真状态，版本变更/同源源码未锁定会影响可复现。源码sha与本次mtime不能证明历史测试与当前代码逐字一致，所有物理历史成功应再做回归。

后续方案（本次不执行）：明确选定同学原任务或本地候选及身份，先检查关节映射和观测，再做1环境固定命令/停止，随后多种子连续前后转停、撞墙后恢复；记录实际速度、位置漂移、全四足周期/滑移、摔倒、饱和与命令切换。先满足停止/转向/四腿标准，再讨论训练或接三机器人，不继续盲目增加训练轮数。
''')
w('BATTLE_SYSTEM_AUDIT.md',f'''# 三机器人自主对战、HUD与集成审计

{common}

## 能否完成目标中的三狗比赛

**当前正式入口不能直接完成三只最新关节机器狗的自主对战。** 可以运行的代码链是三Proxy规则比赛；运动策略在另一套单狗/批环境任务中。具备脚本规则自主选择与开枪，不等于PPO自主战斗。三真实本体装载、各自PPO适配、共享物理步进与完整物理对战验收缺失。

## 多代理现状

{ve('runtime.py','for agent_id in')}严格构建dog_a/b/c三个独立对象，独立pose/command/alive/策略target/冷却/HP；同一场景下不同prim、红蓝绿颜色。导航字典按ID存目标，状态共享由manager统一管理，未发现直接共用一个目标变量的代码。dog_a只是代理身份，不表示自动使用旧Dog A。

{ve('sim/scene.py','kinematic_enabled=True')}配合IsaacPoseWriter.set_world_pose；Proxy按速度在Python中积分位姿。三体各有Collider，但kinematic teleport没有狗间相互避碰/动力学响应保障。本次相同坐标能被两个Proxy同时接受。真实关节机器人各自独立加载策略、接触碰撞、出生无穿插，目前证据不足。

历史{e('archive/historical_validation/battle_previous/migration_real_a/20261023_104635/dog_a_integration_summary.json')}写dog_a=RealDogAgent、b/c=Proxy，时间只有.0167s；这是旧模型混合拓扑单步接口试验，不是三真狗、不是新模型、不是一场比赛。

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

证据：{ve('battle/scripted_policy.py','def act')}、{ve('navigation/simple_navigation.py','def compute_command')}。本次默认解析单局seed42，两存活者最终在x=±4.2,y=-2.7，近3°偏角后不断射击，236发仅3次命中，120秒平局。默认3°在8.4m距离对应横向约.44m，解析目标半径.4m，因此进入fire阈值不保证打中，策略又停止继续对准。该原因与几何/轨迹相容，是明确复现的解析后端僵持；真实方块半宽.24m与PhysX时序不同，需独立回归，不能照抄同一数值当物理实测。GUI demo已用1°容差和开放三角出生，不能将其成功外推默认battle配置。

## 两条关键集成链

|链条|当前实际通路|断点|
|---|---|---|
|决策→速度/方向|ScriptedBattlePolicy→导航/override→ProxyAgent.set_velocity_command|已连通Proxy|
|速度→PPO→关节→最新机器狗|仅独立locomotion环境内有，battle工厂未使用|RealLocomotionAdapter.compute_action/step抛NotImplementedError；无CSDog具体适配器|
|三本体统一仿真|RealDogAgent注释要求adapter安排shared stepping|实际scene只创建方块，缺共享步进调度的验证|
|策略→射击请求→裁判→扣血→死亡/结果|BattleAction.fire→WeaponService→HealthSystem→_evaluate_round|解析层本次完整运行；PhysX当前全场回归未执行|

{ve('agents/real_locomotion_adapter.py','class MockRealLocomotionAdapter')}只返回12个零动作并计数；Mock/接口测试通过不能视为策略推理。真正三机器人可共享同一权重文件但各有独立观测/动作状态；不必为了“三只狗”重新训练三个模型，是否分别策略由后续方案决定。

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

{ve('ui/battle_hud.py','class BattleHUD')}说明HUD只拥有文本而非独立血量，设计正确。V0/v0.2 HUD没有全部废弃：当前BattleHUD在demo入口实际导入并build/update；历史GUI6项PASS是20261023，当前只做文本回归。旧legacy_compatibility副本不在PYTHONPATH，不是另一条正式入口。

## 当前实际可展示内容与测试范围

1. 现存同学原任务单狗前/后/转5秒视频与10秒指标，可直接播放已有视频；不能称三狗自主比赛。
2. 地图两墙+三色方块、规则射击、HP/死亡/结果，有旧代理演示与smoke证据。当前GUI代码保留，启动需独立短时回归；本次没有重新打开GUI保证现场成功。
3. 本次CPU解析规则可以重复演示一局并输出伤害/死亡/超时结果；解析几何不是Isaac场景。
4. 历史混合真A+两代理只是单步接线。旧ANYmal/旧DogA训练及视频不代替新模型能力。

历史{e('archive/historical_validation/battle_previous/v0/battle_demo/20260920_104814/demo_summary.json')}记4局完成（总16.133s）且有轮流赢家；早期104104无伤害、104154未完成，也保留。它们只证明对应历史代理配置。当前默认battle运行上限30s、规则限120s，可能因外层duration先到而结束但没裁决；退出码0不能当作“一局完成”。GUI demo默认120总活跃秒、内部90秒，支持结果停留/auto-reset。

高资源后续测试仅列方案：锁定身份与入口→1真狗替换1Proxy→确认所有agent只在同一个sim.step推进→3真狗同场静止/碰撞→固定速度→接规则→多局自主。每步用独立输出目录、不覆盖历史权重；本次全部未执行。
''')
# 统一状态矩阵；代码/测试分开，状态不是代码比例。
rows=[
('机器狗模型','URDF结构/12DOF','13link/12revolute，本次解析','本次结构/惯量通过','已完成且验证通过',e('model/robot.urdf')),
('机器狗模型','Isaac URDF→USD加载','转换闭包及训练引用','20261026 physics_gate PASS；当前未重跑','已实现但未验证',rr('csdog_ppo_20261026/reports/physics_gate.json')),
('机器狗模型','质量惯量/COM机械真实性','张量正定，总重一致','无实机/CAD校核完整证据','证据不足',e('course_presentation/model_audit_readonly.json')),
('机器狗模型','足底独立碰撞/传感','本地膝链聚合、V7候选；同学独立sole','各配置历史测试，未统一','部分完成',rr('csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md')),
('机器狗运动','稳定站立','固定PD历史成功；PPO零命令漂移','当前无新物理测试','部分完成',rr('csdog_ppo_20261026/reports/physics_gate.json')),
('机器狗运动','前进','同学Teleop短测成功，本地V7未合格','同学10秒/1env；当前battle未接','部分完成',e('peer_csdog_review/peer_perturbed_forward_025.json')),
('机器狗运动','后退','同学短测成功、本地V6.2失败','同学-.25→-.211；非本次复测','部分完成',e('peer_csdog_review/peer_perturbed_backward_025.json')),
('机器狗运动','原地旋转','同学左右转成功但侧漂','当地短测；严格原地未合格','部分完成',e('peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md')),
('机器狗运动','停止运动','所有已比对策略有漂移','V7 stop_speed .2126；同学.032','存在故障',rr('csdog_phase_guided_ppo_v7/STATUS_SUMMARY.md')),
('机器狗运动','连续速度/动作切换','命令接口存在','连续组合鲁棒性未充分验证','已实现但未验证',le('env_cfg.py','class CommandsCfg')),
('机器狗运动','横移','有采样/历史单命令配置','当地7项复测未覆盖，缺统一标准','证据不足',e('peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md')),
('机器狗运动','摔倒检测','姿态/触地终止','历史物理评估使用','已实现但未验证',le('env_cfg.py','class TerminationsCfg')),
('机器狗运动','摔倒后自主起身','未找到接入实现','无验证','尚未实现',le('env_cfg.py','class TerminationsCfg')),
('PPO训练','训练/保存/评估工具','多版本runner、日志、identity、权重','已有训练/单因素评估记录','部分完成',e(D+'scripts/train/csdog_12dof.py')),
('PPO训练','全动作运动验收','独立Gate与物理指标','本地V6.3/V7未通过','存在故障',rr('csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md')),
('地图系统','地图加载','1套程序化几何，2出生配置','历史物理smoke；本次静态','已实现但未验证',ve('sim/scene.py','def build_test_scene')),
('地图系统','障碍物碰撞','真实墙collider+Proxy中心校验','历史射线PASS，真实狗撞墙未测','部分完成',ve('arena/test_map.py','def is_position_valid')),
('地图系统','三机器人出生点','固定3点、seed分配','本次2项出生测试PASS','已完成且验证通过',ve('arena/spawn_manager.py','def assign_spawns')),
('地图系统','实体围墙/边界','仅逻辑边界','没有封闭围墙','部分完成',ve('arena/test_map.py','self._bounds')),
('地图系统','多地图切换','接口可注入，缺其他成品地图与选择器','未验证','部分完成',ve('runtime.py','arena_map:')),
('地图系统','狗间不穿插','运动学方块，无相互位置验证','本次同位置接受','存在故障',ve('agents/proxy_agent.py','def update')),
('裁判系统','射击命中','closest hit射线、方向/射程/冷却','本次解析测试与历史PhysX专项','已完成且验证通过',ve('battle/weapon_service.py','def fire')),
('裁判系统','血量管理','100HP，下限0，34伤害默认','本次规则测试/解析单局','已完成且验证通过',ve('battle/health_system.py','def apply_damage')),
('裁判系统','死亡判定','HP0→alive false→stop/fire禁用','本次HP与解析单局；真狗未接','已完成且验证通过',ve('battle/battle_manager.py','def apply_damage')),
('裁判系统','胜负判定','最后存活胜/无人或超时平局','本次超时通过，最后存活历史PASS需回归','部分完成',ve('battle/battle_manager.py','def _evaluate_round')),
('裁判系统','重置/下一局','manager reset；demo自动下一局','本次reset通过，自动多局仅历史','部分完成',e(D+'scripts/battle/run_v0_battle_demo.py','if not args.auto_reset')),
('裁判系统','暂停恢复','无显式状态机','无','尚未实现',ve('battle/battle_manager.py')),
('对战机制','5秒位置暴露','0秒起网格快照/时间戳/过滤自身','本次2个测试PASS','已完成且验证通过',ve('battle/intel_service.py','def update')),
('对战机制','限制隐藏敌人实时位置','不可见仍返回距离/方位','本次墙后位置精确反推','存在故障',ve('battle/visibility_service.py','return VisibilityResult')),
('对战机制','尸体射线一致性','解析忽略死者，物理collider保留','静态差异，未物理回归','部分完成',ve('battle/ray_query.py','if not agent.is_alive')),
('自主导航','目标追踪','直线目标接近、5秒更新','本次直线接近测试PASS','已完成且验证通过',ve('navigation/simple_navigation.py','def compute_command')),
('自主导航','障碍物绕行','没有规划器','本次24s卡墙','尚未实现',ve('navigation/simple_navigation.py')),
('自主导航','卡住重规划/脱困','无进展监控','无','尚未实现',ve('navigation/simple_navigation.py')),
('作战决策','自主射击','规则可见/对准fire','解析单局有命中/死亡；默认僵持','部分完成',ve('battle/scripted_policy.py','def act')),
('作战决策','追击/多敌选择/丢失扫描','规则策略已实现','无完整物理对抗回归','已实现但未验证',ve('battle/scripted_policy.py')),
('作战决策','主动躲避/后退/掩体','当前policy无战术逻辑','无','尚未实现',ve('battle/scripted_policy.py')),
('作战决策','战斗RL/自博弈','无接入的高层RL','无','尚未实现',ve('runtime.py')),
('系统集成','三代理规则比赛','Proxy→射击→HP→结果','本次解析单局超时平局；历史物理专项','部分完成',ve('runtime.py')),
('系统集成','三狗同时对战','scene只创建Proxy，缺具体适配器','无三真狗对战记录','尚未实现',ve('agents/real_locomotion_adapter.py','raise NotImplementedError')),
('系统集成','决策→PPO→关节动作','独立运动环境可推理，未连battle','mock不算真实链验证','部分完成',ve('agents/real_dog_agent.py')),
('可视化','HUD血量显示','读裁判快照、存活/HP','本次文本测试PASS；GUI历史需回归','部分完成',ve('ui/battle_hud.py','def update')),
('可视化','时间/赢家/平局文本','format_round_status','本次HUD文本测试PASS','已完成且验证通过',ve('ui/battle_hud.py','def format_round_status')),
('可视化','5秒倒计时/击杀列表/坐标','无专用HUD控件','无','尚未实现',ve('ui/battle_hud.py')),
('可视化','专用视角切换/重开按钮','固定镜头、CLI自动重置','专用UI无证据','尚未实现',ve('runtime.py','sim.set_camera_view')),
('可视化','完整比赛录像/回放','事件日志存在、单狗视频存在','比赛全程回放未验证','部分完成',ve('logging/battle_logger.py')),
('系统集成','完整比赛闭环','代理规则链已有；真实三狗缺失','本次只验解析规则，非最终目标','部分完成',ve('runtime.py')),
]
w('PROGRESS_MATRIX.md','''# 项目完成度矩阵

口径：状态评估当前正式工程及明确区分的外部运动成果。“已完成且验证通过”只针对该行限定的CPU规则/结构范围；不外推GUI、PhysX或三真实机器人。历史物理PASS不自动升级为本次当前物理验证。详细函数、入口、验证日期和问题见各专项报告，源码函数索引见SOURCE_SYMBOL_INDEX.md。

|模块|子功能|代码实现|测试情况|当前状态|证据位置|
|---|---|---|---|---|---|
'''+ '\n'.join('|'+ '|'.join(row)+'|' for row in rows)+'''

状态严格采用六种指定标识。每行的范围/复杂度并不相同，不将已实现行数或此表条目占比换算为项目完成百分比。“尚未实现”表示在当前有效调用链中未找到实现；与归档或同学分支某项历史成果并不冲突。
''')
w('BLOCKERS_AND_ROADMAP.md',f'''# 阻塞项、依赖关系与三人开发路线

{common}

## 当前项目的判断

最成熟的部分是：机械原件/转换与物理诊断资料；Proxy规则核心与轻量测试；单狗训练/评估/日志基础设施；同学原任务短程运动成果。地图已有可显示且可射线遮挡的基础场景，尚不是导航完整的竞技地图。裁判核心比导航成熟，主要缺口是信息最小化、边界语义与多本体集成回归。

历史独有且未接当前主链：旧Dog A训练/策略、20261023旧真A+2Proxy单步；同学Teleop前后转向虽已作11月课程成果，仍没有正式battle适配。V0与v0.2 HUD则仍被当前入口使用，不应误判成全部废弃。

当前不能直接启动一场三最新机器狗自主比赛。第一步scene只生成方块，下一步具体LocomotionAdapter还未实现；即使补接，现有策略停止/运动鲁棒性与地图卡墙都会阻碍稳定对抗。对“完整目标”最大瓶颈是 **系统集成与运动控制共同阻塞**；对“规则演示”最紧迫的是导航/瞄准和信息接口。无需先重写一套裁判。

## 关键问题（有证据与待验证严格区分）

|ID/优先级|阻塞/风险|证据|影响/依赖|
|---|---|---|---|
|B1/P0|正式battle只有Proxy，具体适配器未实现|{ve('runtime.py','agents =')}；{ve('agents/real_locomotion_adapter.py','raise NotImplementedError')}|真实三狗目标直接断链；依赖先选运动身份|
|B2/P0|运动停车不合格，本地前后转向/四腿验收失败|同学zero vx .032、V7 stop .2126；V6.2后退/转向接近0|停车射击/动作切换无法可靠；先统一验收再优化|
|B3/P0|直线导航不绕障/不脱困|本次24秒卡墙 `AUDIT_PROBES.json`|规则代理也会卡，需可通行图/局部规划及进展监测|
|B4/P0|不可见目标真值通过距离/方位泄漏|VisibilityService返回全部结果；本次可反推(2,0)|破坏5秒情报约束；先收紧观测再扩策略|
|B5/P0|默认fire角阈值允许射不中后停射僵持|本次默认解析120秒、236发3命中平局|先统一命中几何/瞄准门槛；GUI demo参数不能掩盖默认问题|
|B6/P1|狗间重叠/墙体余量/边界不是动力学约束|kinematic set_world_pose、中心margin.25、无外围墙|先体积/碰撞协议，再真实同场压力测试|
|B7/P1|解析与PhysX几何/死者遮挡不同|圆vs方块、解析略死者、物理无禁用Collider|当前静态确认差异；效果待回归|
|B8/P1|训练/策略/模型身份分叉且默认入口过旧|45/48/50维与动作/PD/sole不同，launch仍旧任务|先冻结一套部署清单，禁止直接换权重|
|B9/P1|现有验收多为专项/历史，缺当前比赛全流程证据|smoke与hud历史PASS，真实三狗无记录|需逐层gate，保留命令/版本/结果与视频|
|B10/P2|避险、战术后退、掩体选点未接策略|ScriptedBattlePolicy无对应分支|等运动/导航/信息约束可靠后实现|
|B11/P3|HUD缺倒计时/击杀列表、专用重开/视角、完整回放|BattleHUD仅HP/状态/时间/结果|比赛核心稳定后补展示与操作|

附加局部问题：SpawnManager对于多于3出生点的strict zip会报错；当前3点不触发。外层headless duration默认30而裁判上限120，正常进程退出不保证ROUND_END。顺序射击存在先手语义，暂停/恢复未实现。没有本次物理运行证据时，不把静态风险写成已复现PhysX崩溃。

## 依赖图与必须先做的工作

```mermaid
flowchart TD
  ID[明确唯一部署模型/任务/关节/观测/权重身份 B8] --> MOT[单狗前后转停与切换验收 B2]
  ID --> AD[具体PPO适配器与共享仿真步进 B1]
  MOT --> TRI[三真实本体同场固定命令]
  AD --> TRI
  GEO[统一实体尺寸/碰撞/射线语义 B6 B7] --> MAP[边界/出生/规划与脱困 B3]
  GEO --> AIM[瞄准射击几何 B5]
  OBS[隐藏信息最小化 B4] --> TACT[多敌选择/追避射策略 B10]
  TRI --> LOOP[三狗完整规则比赛闭环 B9]
  MAP --> LOOP
  AIM --> LOOP
  OBS --> LOOP
  LOOP --> TACT
  TACT --> SHOW[HUD/录制/重开/重复演示 B11]
```

地图/裁判CPU规则工作可与运动优化并行；“先所有运动训练完成才处理地图”没有必要。三真实本体接入必须先确定身份、具体适配器和共享步进，不能让每只狗的adapter各自推进全局sim一次。自主策略扩展必须先堵情报泄漏，否则验收无效。

## P0：最低可演示版本

目标：三机器人同图按简单规则移动，射击→扣血→死亡→胜负闭环；必须明确展示运动是否为规则驱动、是否真实关节。Proxy基线可作为中间验收，不冒充P0三真实机器狗完成。

已完成：基础TestMap、三Proxy、裁判/HP/日志、HUD文本、历史代理demo；同学单狗运动与视频可复用。

剩余与实施顺序：

1. 选定同学原任务作为候选或另选本地分支，记录URDF/训练URDF/USD/权重SHA、观测/动作/PD/朝向，列明未合格的stop与侧漂；不直接将同学checkpoint塞入V6/V7环境。
2. 修规则观测泄漏与默认瞄准死区，统一demo和默认比赛的规则配置说明。
3. 使用现有地图先完成可演示路径/出生方案；即使使用预设路线，也标明没有自主寻路。
4. 做具体运动适配器，1真狗→3真狗共享仿真，验证命令到关节；用低速规则运动串裁判。
5. 再进行经批准的独立有界GUI整局演示，保存完整事件、结果、视频与失败记录。

依赖：身份→适配→三狗；裁判/地图修订可并行。验收：画面确为三只12关节机器人、各自控制可区分，至少一局有射击命中/扣血/死亡/合法结果，reset后HP/冷却/策略恢复；说明预设路线与自主功能边界，不能用人工扣血凑胜者。若只有三方块或单狗视频，P0仍只是部分完成。

三人任务：建模同学负责碰撞/出生高度/外观与模型身份；强化学习同学负责选策略、动作映射、限速与stop门禁；系统同学负责裁判信息/瞄准、适配接口调度、事件/HUD整局。适配联调由运动与系统共同验收，避免一个人包揽。

## P1：可稳定运行比赛

已完成可沿用：基础规则服务、轻量测试、单狗物理评估工具、P0接口成果（完成后）。

剩余顺序：先稳定stop/左右转/前后命令切换，再统一体积与三狗碰撞、实体边界、出生校验、尸体射线/同帧结算规则；加入卡住检测与安全重置/暂停恢复；多种子多局与长于单个episode的比赛回归。这里“长于episode”不是授权长时间训练，本次未执行。

依赖P0真实关节闭环；可先在CPU层测规则边界。验收：预先约定的多种子整局全部结束，无穿墙/重叠起点/负HP/死者开枪/重复扣血，停止与追踪误差满足组内事先公布的阈值；成功率与样本数如实公布，超时平局可合法结束但不能每局都僵持。阈值应在实验前确定，不事后放宽。

分工：建模负责形体碰撞和出生/地图尺寸验证；运动负责多命令稳定与失败恢复研究；系统负责导航脱困、裁判边界、批量比赛回归与生命周期。共同审核原始轨迹，不用reward代替运动验收。

## P2：自主对战

已有：最近目标选择、5秒intel追踪、可见目标瞄准射击、到达后扫描的规则原型。

剩余顺序：修复且测试信息权限→建立地图可通行图/路径规划/动态避让→丢失目标搜索/卡住重规划→多敌选择、后退/躲避、射击时机/掩体→与已稳定低层策略联调。若需要高层战斗RL/自博弈，先构建可信比赛环境/观测/奖励/终止，再单独申请训练预算；最终自主效果可由规则导航实现，不能把“自主”自动等同“已经训练了战斗RL”。

依赖P1运动、规则与碰撞；验收：隐藏敌人只能按规定情报更新，可见敌人才返回即时观测；机器人能从墙两侧追击、换目标、失去目标后搜索，遇障碍绕行/脱困，决策确实转化PPO关节动作；完整比赛不依赖人工目标/射击/扣血。用成对基线比较胜负、卡住、无效射击与任务结束率。

分工：建模同学负责地图可通行/掩体与枪口/视线高度数据及物理回归；运动同学负责PPO速度接口与复杂命令鲁棒性/策略身份；系统同学负责规划与战术策略。场景评估/实验数据整理由建模与系统共同承担，运动同学参与高层命令可执行性审核。

## P3：最终展示

已有：HP/存活/时间/结果HUD、三色身份、事件记录、单狗视频素材；P2完成后沿用比赛核心。

剩余顺序：统一入口和版本/依赖清单→HUD暴露倒计时/击杀/位置提示→视角切换/重开/暂停恢复→完整录制与可复查事件→老师演示脚本与失败兜底、重复启动/重置验证。

依赖P1闭环、P2自主验收；展示UI可提前开发但不能以精美画面替代功能。验收：按一份运行手册从冷启动复现，清晰看到三狗、HP/时间/情报周期/结果；可连续重开多局，完整视频与日志可对应，不用历史素材冒充本次实况。每次演示注明策略/任务/权重SHA及局限。

分工：建模同学负责场景/身份标识与镜头构图、演示素材；运动同学负责部署清单和运动回归；系统同学负责HUD/操作/录制。三人各维护一套验收证据，共同彩排与交叉操作，不规定没有依据的准确工期。

## 未执行的资源消耗测试清单

先以只读核对+CPU测试冻结身份；后续需另行授权的操作包括1真狗固定命令Isaac加载/站立/前后转停、3本体碰撞、当前GUI HUD、完整单局及多局。每项须预设env数量、模拟秒数、GPU/CPU模式、输出独立目录、失败停止条件，确认没有现有任务冲突。不启动AutoPPO服务或恢复旧训练器；本次没有执行上述项目。
''')
w('FINAL_SUMMARY.md',f'''# 项目负责人总结

{common}

## 一、我们现在已经做完了什么

- **模型**：最新model/原件完整，13个连杆、12个转动关节、总质量7.60426kg，已有Isaac USD转换、自由机身站立/接触/关节响应的历史物理证据。本次结构与惯量数值检查通过。训练确实加载最新原件转换产物。
- **运动训练**：有完整PPO训练、保存、评估、诊断基础设施。不能把本地V6/V7称运动已全部成功；但同学Teleop方案已有本机前进、后退和双向转弯的10秒短测与5秒视频，11月课程汇报已采用该成果。该方案未接入正式对战，停车漂移与转向侧移仍在。
- **地图**：一套程序化比赛几何，地面、两面内部墙、三个出生点；GUI换出生点，不是第二张完整新地图。墙有碰撞/射线遮挡，暂无完整绕障和实体外围边界。
- **裁判**：当前BattleManager确实接通射击请求、射程/方向射线、冷却、扣血、死亡、超时/最后存活判定和重置。默认每5秒生成位置快照；HUD从权威血量读数据。职责独立于策略，但观测接口有泄漏，不能认定信息隔离合格。
- **对战**：三独立Proxy代理的规则比赛链已经存在；本次纯CPU解析单局产生伤害、死亡和超时平局。它不是三只关节机器狗的物理比赛。
- **可视化**：三个颜色身份、血量/存活、时间/赢家/平局HUD仍被当前GUI入口调用，有历史GUI测试；本次文本测试通过，没有重跑GUI。

直接证据：{ve('runtime.py','agents =')}、{e(D+'assets/csdog_12dof/import_v1/config.yaml')}、{e('peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md')}、{ve('battle/battle_manager.py','def step')}。本次验证见 `pytest_results.xml`（13通过）与 `AUDIT_PROBES.json`。

## 二、我们现在还没有做完什么

**当前主链尚未实现**：三只最新关节机器人同场对战工厂、具体PPO运动适配器、可靠共享仿真调度；地图路径规划/绕障/脱困；主动战术后退/躲避/掩体选择；战斗RL/自博弈；显式暂停恢复、机器人自主起身；HUD五秒倒计时/击杀列表及完整比赛回放等。

**做了一部分但不合格**：停止控制与严格原地转弯、连续动作切换、狗间/墙边碰撞保障、多地图切换、真实三狗规则回归、HUD当前GUI验证。五秒快照本身正确，但不可见目标的实时距离/方位也交给策略，破坏情报约束。默认瞄准阈值还可能造成停住不断打空。

**未确认**：长期鲁棒性、机械质量/惯量与实物一致性、所有策略权重兼容性、当前环境下一键完整GUI比赛。缺证据不能写“已完成”，也不武断否认已有短程成果。

## 三、目前实际能演示什么

可以直接展示现存同学单狗前/后/转视频及对应当地短测数据；可以展示本次CPU规则比赛结果。三色方块地图/HUD/射击与代理完整获胜演示有历史证据，当前实现仍保留，但需要短时GUI回归后才能承诺老师现场启动成功。不能把单狗视频、旧模型混合单步或三个方块当三机器狗自主对战。

当前正式命令入口是 `dogfight_rl/launch.py battle`（默认TestMap）与 `battle-gui`（DemoTestMap出生配置），都生成Proxy。默认train/evaluate仍是最早新模型任务；V7是最新本地实验分支，同学Teleop是独立运动成果，当前没有一个“升级后一键全功能主版本”。

## 四、现在能否完成一场三只机器狗的完整对战

**不能，按“当前正式入口直接运行三只最新关节机器人自主比赛”的目标判断。** 主入口创建运动学方块；具体运动适配器compute_action/step仍为NotImplementedError；地图不绕障，停车未合格。现有证据不能支持“完整自主三狗比赛已完成”。代理规则闭环与真实三狗自主闭环必须分开。

本次解析单局seed42到120.0167秒超时：236次射击、3命中、1死亡，两个存活者平局；不是Isaac Sim实测。它表明裁判链可以处理事件，也暴露默认瞄准僵持。20261026物理smoke15项PASS是专项，20260920代理demo有多局赢家，均不等于本次当前三真狗验收。

## 五、接下来最应该做的五件事

1. **确定唯一部署身份并打通真实本体适配。** 优先评估复用同学原任务，明确关节顺序/50维观测/PD/碰撞/权重；1真狗替换1代理，再到3狗共享步进，解决当前最直接断链。
2. **先解决停止、转向侧漂及动作切换验收。** 没有可靠停车，瞄准和安全控制难以稳定；本地PPO诊断指标与同学成果分别保存，不盲目追加训练。
3. **修复隐藏目标信息泄漏并统一瞄准/命中规则。** 规则CPU工作可独立推进，是可信自主比赛和代理演示的共同基础。
4. **完善地图形体碰撞、路径规划与脱困。** 当前直线追击24秒卡墙已复现；先明确尺寸、出生与边界，再接规划。
5. **建立当前版本完整比赛验收与展示入口。** 按规则→1狗→3狗→单局→多局逐层留证；再补HUD倒计时、击杀、镜头/重开和完整录制，避免只有历史成功记录。

前两项决定真实本体可执行性；第三、四项可同时在CPU规则层推进；第五项验收依赖前述结果。详见BLOCKERS_AND_ROADMAP.md的依赖图与P0–P3标准。

## 六、三个人如何分工

|角色|主要责任|必须交付/协作|
|---|---|---|
|机械建模同学|模型身份、足/腿碰撞、枪口/出生高度、地图尺寸与边界、三体碰撞回归；后期外观/镜头|交付一套确定的机器人与场景规格，同运动同学核对PD/关节，和系统同学核对射线/通行体积|
|强化学习同学|选定运动策略、观测/动作映射、前后转停/切换、多种子运动验收与部署元数据|交付能接受速度命令的具体策略适配；与系统同学共同验证共享仿真步进，不能单独背负裁判/地图/HUD|
|比赛系统同学|裁判信息最小化/瞄准、导航与脱困、生命周期、HUD/日志/整局回归|交付规则闭环和演示入口；地图数据由建模共同维护、低层适配由RL共同完成|

这是责任建议，不依据文件推断三位同学实际作者归属；姓名与既有机械/RL角色由团队映射。三人都承担验收记录和交叉演示，避免所有集成/排错落在一人身上。

## 七、项目到底完成到什么程度

**代码实现进度**：模型、运动训练基础设施、代理规则核心与HUD代码较完整；真实三本体适配、规划/战术与展示细节仍有明确缺口。

**已验证功能进度**：本次只新增13项CPU轻量测试通过、URDF结构/惯量检查、规则单局与缺陷探针；真实运动/物理/GUI依据历史记录并需回归。测试数量不是已完成目标数量。

**完整自主对战目标达成度**：尚未交付一场三最新机器狗自主比赛的完整证据，当前正式入口也缺实现。单狗运动与代理比赛是两个可复用成果，尚未完成组合。

不强给百分比：模块粒度/权重、验收阈值和物理样本数未统一，按文件/测试/代码行计数会制造精确假象。PROGRESS_MATRIX.md提供46项逐功能判断，可作为后续事先约定权重与验收口径的基础。

## 报告与边界

全部报告在本目录。未修复任何发现的问题，未训练、未启动长/短Isaac仿真、未安装依赖、未使用或保存密码。读写保护抽样为275个正式源码/配置/模型/入口文件的SHA前后对照，结果见SOURCE_INTEGRITY.json；它不代表全盘每个文件的系统级审计。
''')
w('README.md',f'''# 三机器狗自主对战项目进度审计

{common}

**结论：三Proxy规则系统和独立单狗运动成果已经存在；正式入口尚不能运行三只最新关节机器狗的完整自主比赛。** 运动成果包含同学Teleop本机前后/双转短测成功，不能只按本地V7失败抹去；也不能将它当作已经接入对战。

## 阅读顺序

1. [负责人总结](FINAL_SUMMARY.md)：已做/未做/实际演示/能否整局/五件事/三人分工/完成度。
2. [整体结构与入口](PROJECT_OVERVIEW.md)：源码、各代实验、历史与同学方案关系。
3. [模型与RL](MODEL_AND_RL_AUDIT.md)：机械原件、身份/顺序、训练、动作A–E、退化与可复现性。
4. [地图审计](MAP_AUDIT.md)：一套几何/两出生配置、物理碰撞与规划区别。
5. [裁判审计](REFEREE_AUDIT.md)：真实调用链、射击/HP/胜负/五秒与信息泄漏。
6. [对战与可视化](BATTLE_SYSTEM_AUDIT.md)：三代理/真实狗断点、自主能力、HUD与演示。
7. [功能矩阵](PROGRESS_MATRIX.md)：统一六状态，限定验证范围。
8. [阻塞与路线](BLOCKERS_AND_ROADMAP.md)：依赖图、P0–P3、验收与三人分工。

## 证据与本次验证

- `FILE_INVENTORY.json` / `DIRECTORY_TREE.txt`：递归项目业务与历史目录元数据/目录树，排除大依赖/缓存；枚举不等于逐文件语义审读。
- `MAP_BATTLE_RESOURCE_INDEX.txt`：地图/场景/出生/HUD等命名文件；同源归档不算新增地图。
- `CHECKPOINT_INVENTORY.json`：1695项权重候选文件，含重复/旧分支；未全部反序列化，不以存在证明能力。
- `SOURCE_SYMBOL_INDEX.md`：当前源码类/函数行号索引。
- `pytest_results.xml` / `TEST_EXECUTION.md`：本次13项测试通过，无GUI/GPU/PhysX。
- `audit_probes.py` / `AUDIT_PROBES.json`：本次纯CPU只读探针，信息泄漏/卡墙/重叠/解析整局/机械结构。
- `SOURCE_HASHES_BEFORE.json` / `SOURCE_INTEGRITY.json`：275个正式源码/配置/模型及入口文件前后SHA核对。
- `ENVIRONMENT_SNAPSHOT.json`：时间、进程只读快照；不把历史manager_alive作为当前进程证据。

## 判定约定

六状态严格使用：已完成且验证通过、已实现但未验证、部分完成、存在故障、尚未实现、证据不足。物理历史成功另注明日期/任务；本次通过只限实际CPU覆盖范围。证据不足的部分明确待验证，不据README计划推断完成。

报告链接为实际绝对路径及行号；默认相对路径以 `/home/zxq/robot_projects` 为根。文件修改时间是证据时间线辅助手段，不保证测试执行时刻、历史源码完全相同或日志未曾被复制。没有查证外网资料，本次结论完全来自本机文件、源码和低资源测试。

所有资源消耗较大的测试只列后续方案，未执行；本次没有为得到整局证据而擅自启动Isaac应用。用户只允许审计目录输出优先于项目一般runs输出约定；本次pytest临时目录/XML、探针和报告均在此目录。
''')
# 当前源码符号索引，给所有模块可追溯入口与行号。
idx=['# 当前业务源码类与函数索引','', '本次AST只读解析；类/函数存在并不代表调用或验证成功。','']
import ast
for p in sorted((R/D/'src').rglob('*.py')):
 try: t=ast.parse(p.read_text())
 except SyntaxError: continue
 syms=[(n.lineno,n.name,type(n).__name__) for n in ast.walk(t) if isinstance(n,(ast.ClassDef,ast.FunctionDef,ast.AsyncFunctionDef))]
 if syms:
  idx+=['## '+str(p.relative_to(R)),'']
  idx += [f'- [{name}]({p}:{line}) — {kind}，行{line}' for line,name,kind in sorted(syms)]
  idx+=['']
w('SOURCE_SYMBOL_INDEX.md','\n'.join(idx))
w('TEST_EXECUTION.md', '''# 本次执行记录

日期2026-11-03。使用冻结解释器，只执行下述7个文件的13项纯CPU测试：test_round.py、test_weapon.py、test_intel_5s.py、test_visibility.py、test_spawn.py、test_navigation.py、test_hud.py。结果13 passed in 0.02s，0失败，见pytest_results.xml。没有执行项目launch.py test全套，避免无关训练工具测试副作用。

环境变量：PYTHONDONTWRITEBYTECODE=1，PYTEST_DISABLE_PLUGIN_AUTOLOAD=1，OMP_NUM_THREADS=1，MKL_NUM_THREADS=1。参数：python -B -m pytest -q -p no:cacheprovider --basetemp=<本审计目录>/pytest_tmp --junitxml=<本审计目录>/pytest_results.xml <上述7文件绝对路径>。conftest使用AnalyticRayQuery，未启动IsaacLab AppLauncher。

另用python3 -B执行audit_probes.py，只导入轻量业务模块与标准库，MemoryLogger不写运行日志。整个探针约0.25秒：URDF结构/惯量，墙后不可见目标距离方位泄漏，24秒模拟时间的直线卡墙，两个Proxy重叠，默认seed42解析单局（120.0167模拟秒）以及0.05秒超时/reset。模拟时间通过Python循环推进，不是120秒墙钟，也不消耗GPU。

探针中的缺陷复现是发现，不是修复后的PASS；同坐标接受说明缺少互斥保障，不是已跑PhysX接触测试。完整默认解析单局有死亡并超时平局，不是三真实机器人或Isaac比赛。物理/GPU/GUI/训练/完整实战均未执行，后续方案见各专项与路线。
''')
# 保存当前环境只读状态，不调用环境更改/安装/模拟器。
ps=subprocess.run(['ps','-eo','pid,lstart,etime,pcpu,pmem,args'],capture_output=True,text=True).stdout
# 不保留本次shell命令行（可能包含大量报告正文），保留相关训练筛查与顶层快照事实。
related=[s for s in ps.splitlines() if re.search(r'(csdog|run_v0|rsl_rl|isaacsim)',s) and not any(x in s for x in ['bash -','write_audit_reports','exec_command'])]
(A/'ENVIRONMENT_SNAPSHOT.json').write_text(json.dumps({'local_time':datetime.datetime.now().isoformat(),'frozen_python_exists':(Path('/home/zxq/miniconda3/envs/dogfight/bin/python')).is_file(),'relevant_runtime_processes':related,'note':'仅进程名称筛查，不把未匹配等同于系统没有任何任务；没有kill/stop/service操作。'},ensure_ascii=False,indent=2))
# 检查相对引用/事实计数与保护哈希。
before=json.loads((A/'SOURCE_HASHES_BEFORE.json').read_text());changed=[];missing=[]
for p,h in before.items():
 q=R/p
 if not q.exists():missing.append(p)
 elif hashlib.sha256(q.read_bytes()).hexdigest()!=h:changed.append(p)
(A/'SOURCE_INTEGRITY.json').write_text(json.dumps({'checked_files':len(before),'changed':changed,'missing':missing,'result':'PASS' if not changed and not missing else 'CHANGES_DETECTED','scope':'正式src/tests/scripts/configs/model与根入口等小于4MB文件；不是全磁盘完整性证明'},ensure_ascii=False,indent=2))
# 更正摘要矩阵条数，避免维护时漂移。
f=A/'FINAL_SUMMARY.md';f.write_text(f.read_text().replace('46项逐功能判断',str(len(rows))+'项逐功能判断'))
print('九份中文报告已生成；矩阵条目',len(rows),'；保护文件',len(before),'；变化',len(changed),'；缺失',len(missing))
for p in sorted(A.glob('*.md')):print(p.name,p.stat().st_size)
