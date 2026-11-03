# 三真实 CSDog FSM 自主对战 V1 交付与验收

2026-11-03。工程根目录 `/home/zxq/robot_projects/dogfight_rl`。本文所有仿真证据均为本次在冻结 Ubuntu / Isaac Lab 2.3.2 / Isaac Sim 5.1 / CPU PhysX + RTX GUI 环境实际产生；单元测试不替代物理验收。最终结果见下方验收记录。

## 1. 先审计后开发

读取了上级及本项目 AGENTS.md、PROJECT_STRUCTURE.md、DOGFIGHT_THREE_DOG_DELIVERY.md、项目根 DOGFIGHT_V0_INTERFACE_SPEC.md，以及实际源码。精确文件名 `格式规范(1).md` 未找到；存在 `/home/zxq/robot_projects/格式规范.md` 和项目内的英文 V0 规范。上级工程说明仍有“三真实本体尚未实现”的旧文字，本次以实际代码和三狗交付文档核实。

实际复用链：`scripts/teleop/run.py → multi_runtime.py → BattleDogAgent → PolicyAdapter → 50维观测/12维动作 → 12关节位置目标 → 统一 PhysX step`。三实例已有独立 articulation、previous action、步态相位；共享只读 actor。旧循环将 C 强制 PD 站立，本次 FSM 模式取消该分支，A/B/C 均运行独立 PPO 推理。无训练、无新模型、无根节点运动替代。

地图由 `teleop/maps.py` 的注册表和 V0 MapInterface/TestMap 提供，`get_navigation_data()` 已含墙体 WallSpec，`get_bounds()`/出生点/合法性接口足够，未改地图或 V0 接口。A* 从地图对象取几何，无地图墙坐标常量。

原三狗激光显示 max_range=20，武器 range_m=20；两者原本分别配置。现由 `battle.weapon_range_m` 统一控制三狗查询与显示。旧 V0 WeaponService、HealthSystem、BattleLogger 原文件均保留。LiveBattleReferee 是现有真实本体裁判，负责结束/死亡/顺序结算。

V0 IntelService 已实现仿真时间快照，可复用。V0 VisibilityService 返回不可见目标的距离/角度，且采用固定枪口高度，不可直接给 FSM。本次新增真实本体感知适配器，在内部读取世界状态，以当前机身高度做 LOS，只有合法可见结果才携带实时位置。FSM 的输入没有 agents 或全局真实位置表。

## 2. 文件与备份

重要文件修改前备份：`runs/validation/fsm_v1_20261103/backup/`，保留原相对路径。原 Git 有大量历史迁移改动/未跟踪文件，本次未 reset、clean、提交或整理它们；原状态存于同目录 `git_before.txt`。

新增：

- `src/dogfight/fsm/navigation.py`：占据栅格 A*、线段碰撞检查、平滑、测量位置回接、独立 PathFollower。
- `src/dogfight/fsm/perception.py`：IntelService 适配、真实 LOS、不可见信息脱敏、独立观察结果。
- `src/dogfight/fsm/controller.py`：六状态 FSM、目标保持、规划节流、卡住恢复。
- `src/dogfight/fsm/visualization.py`：原生 debug draw 线段/点标记及数量诊断。
- `src/dogfight/fsm/physical_validation.py`：明确隔离的射程、导航物理专项测试摆位，不在正式比赛调用。
- `src/dogfight/fsm/__init__.py`、`configs/teleop/fsm_battle.yaml`。
- `scripts/launch_dogfight_fsm.sh`、`scripts/teleop/dogfight-fsm.desktop`、`scripts/teleop/verify_fsm_gui.py`、`scripts/teleop/summarize_fsm_validation.py`。
- `tests/test_fsm_battle.py`、本文与本次验收目录。

修改：`launch.py`、`scripts/teleop/run.py`、`teleop/{multi_runtime,combat,laser,keyboard,multi_hud,first_person,config}.py`、`configs/teleop/{default,single_dog}.yaml`。单狗默认可视激光也改为 3 米，控制链保留。原桌面快捷方式和启动脚本未修改；新增桌面 `/home/zxq/桌面/三狗自主对战.desktop` 已设执行权限及可信元数据。

## 3. 实现与参数

唯一自主配置 `configs/teleop/fsm_battle.yaml`。`controllers` 支持 keyboard/fsm/stand，默认三只均 fsm；键盘 A/B 映射保持，C 无键盘驾驶映射。原 teleop 仍 A/B keyboard、C stand，并保留原自动射击。

|参数|实际值|
|---|---|
|battle.weapon_range_m|3.0 m，三狗武器和渲染唯一权威值；旧 range_m 仅兼容读取|
|血量/伤害/冷却/超时|100 / 20 / 1.0 s / 180 s|
|intel_period_s|5.0，0秒首发，随后5秒网格更新|
|vision_max_range_m / vision_fov_deg|6.0 / 140.0|
|decision_period_s / visual_period_s|0.10 / 0.20 s|
|grid_resolution_m|0.20 m|
|body_radius_m / tracking_margin_m|0.40 / 0.20 m；规划膨胀0.60，跟踪检查0.40机身包络|
|min_plan_interval_s / replan_target_delta_m|1.0 s / 0.50 m|
|终点 / 中间路点接近误差|0.35 / 0.12 m；切点必须检查到下一点的线段；经过路点法平面且距离≤0.50米时也可切换，以避免转向侧移造成绕点|
|max_speed / max_yaw_rate / vy|0.25 m/s / 0.30 rad/s / 0|
|搜索角速度 / 朝向增益 / 死区|0.25 rad/s / 1.2 / 0.025 rad|
|前进朝向阈值 / 射击瞄准阈值|0.45 / 0.08 rad|
|ATTACK 进入 / 退出距离|2.5 / 2.8 m，范围内停止向前冲撞|
|目标保持余量|0.60 m|
|卡住阈值 / 最小位置进展|4 s / 0.12 m|
|恢复|后退0.15 m/s×0.8s，再转向2s；无进展时最多3次，实际恢复进展后可重新计数|
|路线高度 / 线宽|0.10 m / 4像素|
|物理/控制|0.005 / 0.02 s；CPU PhysX，GPU RTX渲染|

A* 使用八邻域、欧氏启发、禁止切角；处理起终点阻塞、相同、无连接、不可达和地图非法区域。平滑线段必须碰撞检查。额外漂移余量和机身包络分离：机器人只进入规划余量而机身仍合法时，可从测得当前位置经碰撞验证线段回接栅格；机身实际阻塞仍报告 start_blocked，不投影或移动机器人。

PATROL 原地慢转，无随机巡逻。SEARCH 使用最新合法快照或最后视野位置；CHASE 使用合法实时视野位置及 A*；ATTACK 有范围/角度滞回并输出开火请求；RECOVER 有限后退/转向后重规划；DEAD 清除目标、路径和火力。可见最近目标优先，当前可见目标在0.6米余量内保持；无可见目标时保留有效记忆目标，失效才选择最近合法记忆。公共死亡ID不包含位置。

感知每5秒生成冻结记录；两个快照之间不会更新坐标。看不见时 Sighting 的位置、距离、角度均为 None；FSM 只保留之前合法记录。暂停时比赛时间和感知定时不前进；结束停止感知/规划；重置同时清空历史、FSM、情报、可见性、路径、冷却、血量、计时和路线。日志 AUTONOMY_RESET 记录 PPO steps=0。

FSM 只给速度与火力请求；裁判仍调用 WeaponService，冷却合格才射击，PhysX 最近非自身碰撞体决定命中，HealthSystem 扣血，裁判判死亡/胜负。三狗发射者及显示共用相同范围与排除自身/最近命中规则，适配器额外拒绝负值或超距离结果；死狗尸体也阻挡光束。显示为常亮瞄准光束，亮线不等于每帧开火。有效射程从实际枪口起算，不从机器人中心起算。

## 4. 实时路线与 HUD

采用本机已有 `isaacsim.util.debug_draw` 3.1 扩展（不安装依赖），为三狗一次批量绘制红/蓝/绿线段和当前位置/目标/路点标记。线条提高0.10米、宽4像素；标记8/12/6像素。没有创建USD路线实体，导航prim数量和碰撞schema均为0。

每0.2秒先 clear_lines/clear_points，再绘制当前三狗路线；数组替换，不追加历史线。已过路段从索引移除，起线连接实时机身位置。原先USD BasisCurves在Fabric/RTX下出现旧几何残留，日志显示隐藏但屏幕未隐藏，因此弃用；对应截图不作为Gate E通过证据。

V 默认开启，按键重复不会反复切换；隐藏只影响显示。死亡、结束、重置、规划失败均清除旧线；失败时仍可显示候选目标点，但无有效路径或当前跟踪路点。ATTACK 可保留目标标记。HUD 每0.2秒刷新状态、目标、导航XY、距离、可见性、规划状态。左侧总览和右侧三第一视角布局保留，右侧标题显示实际FSM状态。

status/trace 中 route_visuals 记录 enabled、每狗显示状态/顶点数、line_count、point_count、prim_count 和 physics_schemas；可核对隐藏及比赛结束时绘制缓冲区归零。此模式独占本入口的 debug draw buffers，不与其他调试绘制模块混用。

激光采用固定高度1米的非碰撞USD圆柱，通过每帧 transform scale 设置真实长度；隐藏时缩放为0。避免运行时修改几何 height 在Fabric下缓存旧长度。查询最大值、最近命中点、圆柱transform长度和端点一致，物理专项同时记录 rendered_length_m。保持旧激光模块接口。

日志包括状态变化、目标变化、规划原因及全部路点、可见/丢失、Intel、射击距离、伤害、死亡和比赛结果。10Hz navigation_trace.jsonl 持续保存；原 trace.json 环形记录仍保留。

## 5. 启动与测试命令

从任意工作目录均可：

```bash
/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_fsm.sh
/home/zxq/miniconda3/envs/dogfight/bin/python /home/zxq/robot_projects/dogfight_rl/launch.py fsm_battle
# 原双键盘与单狗
/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh
/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh --config configs/teleop/single_dog.yaml
```

启动默认锁停，点击左侧后按 C 开始；Space 暂停，C 继续，R 重置并锁停，Esc 安全退出，V 路线开关。窗口失焦/输入轮询长暂停仍锁停；活狗姿态异常会安全暂停，死亡尸体倒下不会暂停比赛。PPO零指令仍可能漂移，暂停不是物理刹车。

本次实际执行的验收命令（工作目录工程根）：

```bash
/home/zxq/miniconda3/envs/dogfight/bin/python -B launch.py test
/home/zxq/miniconda3/envs/dogfight/bin/python -B launch.py fsm_battle --preflight
DOGFIGHT_NO_DIALOG=1 scripts/launch_dogfight_fsm.sh --scenario range-check
DOGFIGHT_NO_DIALOG=1 scripts/launch_dogfight_fsm.sh --scenario fsm-recovery --duration 35
DOGFIGHT_NO_DIALOG=1 scripts/launch_dogfight_fsm.sh --scenario navigation-check
DISPLAY=:1 XAUTHORITY=/run/user/1000/gdm/Xauthority /home/zxq/miniconda3/envs/dogfight/bin/python -B scripts/teleop/verify_three_dog_gui.py
/home/zxq/miniconda3/envs/dogfight/bin/python -B scripts/teleop/verify_fsm_gui.py --battle
/home/zxq/miniconda3/envs/dogfight/bin/python -B launch.py battle --duration 3
```

GUI 验收器通过 gio 启动桌面文件，再向真实 Isaac 窗口发 XTest 键盘事件，用 ffmpeg X11 捕获截图；没有使用 Matplotlib、假UI或根位姿驱动来代替GUI验收。专项的 reset 摆位只用于明确测试初始化；自主比赛使用原三个出生点，不注入驾驶或敌人位置。

## 6. 实际证据与 Gate 结果

最终原生绘制版本已完成真实GUI对战、截图检查和日志审计；下列 PASS 仅覆盖写明的测试范围，早期失败不计入通过。

所有 run 下路径前缀均为 `/home/zxq/robot_projects/dogfight_rl/runs/battle/teleop/`。

|Gate|结果|本次证据与范围|
|---|---|---|
|A 原有功能|PASS 已测范围|`20261103_142456_88e19daf` 由原桌面文件 gio 启动，15组实际XTest采样检查A/B全部原按键、全局停止/解锁/重置/Esc、三路视口；验收文件 `runs/validation/fsm_v1_20261103/teleop_gui_acceptance.json`。单狗 `20261103_160019_c433f170` GUI+CPU PhysX 5秒，真实PPO前进，旧相机保留。模型和权重manifest校验通过，23项保护资源摘要无变化。原Proxy `battle --duration 3` 成功；四周墙穷举 NOT TESTED。|
|B 有限射程|PASS|`20261103_163023_6e149374/physical_range_checks.json`：名义2米目标HP80，超3米HP100，约2米墙挡射且目标HP100，两狗串列仅第一狗HP80。最近命中距离/圆柱transform渲染长度分别1.567962/3.000000/2.014299/1.567962米，逐项一致。实际GUI夹具截图 `range_*.png`；这些初始夹具截图不作为最终布局验收证据。|
|C 情报/视野|PASS 已测范围|最终GUI事件0、5、10、15、20、25、30秒Intel（浮点误差约1e-12，额外0来自R重置）；5次可见、3次丢失。射程专项用真实PhysX LOS：墙后visible=false，开放目标visible=true。单元测试核对4.99秒冻结、5秒更新、FOV/距离/死亡与不可见字段None、最后合法观察保留。|
|D A*和真实跟踪|PASS 已测范围|`20261103_143808_abd016cd/physical_navigation_result.json`：A由(-2,0)绕现有中央墙到(2,0)附近，32.5秒、误差0.347397米、最低根高0.3961米，实际PPO，无根位姿修正；同目录 `physical_navigation_trace.jsonl`、`physical_navigation_500.png`、`physical_navigation_1500.png`。最终比赛28次成功规划/3次明确失败，所有有效路段经0.40米包络复核均合法。起终点非法/相同/不可达/切角/目标变化/规划节流有单元测试；不可达是单元地图测试，不冒充本地图GUI。|
|E GUI路线|PASS 已测范围|最终 `20261103_164416_cec1d1f6` 的 `fsm_routes_on.png`、`fsm_routes_off.png`、`fsm_routes_restored.png`、`fsm_reset.png`、`fsm_match_20.png`、`fsm_result.png`。已逐张核对原生绘制版本可显示三色路线、目标/路点，V后无路线、恢复正常、重置/死亡/结束无旧线。实际缓冲区最多8线/9点，隐藏及结束归零，0导航prim/0碰撞schema；没有逐帧增殖对象。整轮含截图44.10模拟秒/46.64墙钟秒，接近实时；未做独立绘制开销基准或多小时主动比赛内存压力测试。|
|F 三狗真实PPO|PASS 已测范围|最终比赛 A/B/C 控制器均fsm，独立策略steps=1632/1632/1142，实际位置反馈运动；采样连续位移最大0.038米/0.1秒（剔除明确R重置）。真实绕墙见D。`20261103_163643_92147a7d` 实际CPU PhysX无GUI阻挡夹具，A以PPO撞到真实B尸体，35模拟秒内NAV_STUCK在6.7、18.6、28.0、32.1秒触发四个恢复事件；B/C为夹具站立，不能冒充三狗同时PPO，该项由最终完整GUI比赛证明。|
|G 自主对战|PASS|最终 `20261103_164416_cec1d1f6`：31.52比赛秒dog_b获胜、剩80HP；A/C死亡，15次发射、11次真实伤害、2次死亡、1次ROUND_END。无需驾驶按键，三狗原出生点、独立PPO、FSM请求开火、PhysX命中、HealthSystem扣血。三路第一视角右侧停靠且主相机保留。|

最终整轮：

- `runs/battle/teleop/20261103_164416_cec1d1f6/metrics.json`：真实结果和策略步数。
- 同目录 `combat_events/events.jsonl`：所有情报、状态、规划、射击、伤害、死亡与结果事件。
- 同目录 `navigation_trace.jsonl`、`trace.json`：10Hz连续位置、实际速度、命令、FSM、路径；原trace仍为有界环形数据。
- 同目录 `fsm_gui_acceptance.json`：桌面启动、真实按键、暂停、重置、截图清单。
- 同目录 `validation_summary.json`：路径/射程复核、0碰撞调试对象、绘制计数、三狗PPO、保护摘要。生成命令：`python -B scripts/teleop/summarize_fsm_validation.py runs/battle/teleop/20261103_164416_cec1d1f6`，所有断言通过。此前 `162802` 轮末帧尚有5Hz标记清理延迟，最终版本在round_over立即刷新，该断言已重新通过。
- `runs/validation/fsm_v1_20261103/unit_final.log`：192项单元测试通过（11.89秒）；`preflight_final.log`：冻结策略预检通过。
- `runs/validation/fsm_v1_20261103/proxy_regression.log`、`teleop_gui_regression.log`：原入口回归命令输出。
- `runs/validation/fsm_v1_20261103/protected_assets_after.json`：23项模型/策略相关资源摘要；最终核对0项变化，manifest校验每次启动执行。

单狗5秒只覆盖release与W的实际执行、相机和基本姿态，不声称其全部键位本次逐一复测；完整原A/B键位另有上表真实双键盘GUI验证。180秒超时及边界规则单元通过，但两轮有效自主比赛均提前决出胜者，完整180秒GUI超时场景 NOT TESTED。人工双击 NOT TESTED，实际通过 gio 启动同一个 .desktop 文件及其绝对路径脚本。

物理专项函数在主交互循环之前执行，通用metrics的frames可能为0；专项结果以 `physical_range_checks.json` / `physical_navigation_result.json` 及专项轨迹为准，不能将通用默认minimum_root_z=100解读为物理测量。

## 7. 已发现并修正的问题、范围与后续替换

失败记录全部保留（含尚未完成最终GUI验收的轮次）：

- `20261103_143940_893a902f`：真实比赛26.92秒dog_b获胜，但USD路线隐藏/死亡清理画面残留，Gate E FAIL；其对战证据有效，不能代表整体验收通过。
- `20261103_160609_42108440`：桌面锁屏，键盘未进入Isaac，计时保持0；GUI验收 NOT TESTED，不把登录界面截图作为路线证据。解锁后另起新轮。

- `20261103_141855_8003ff6c`：首次感知日志 timestamp_s 重复参数导致启动失败，已修正。
- `20261103_142237_cb38327b`：射程测试夹具将第三狗置于墙内，合法性检查正确拒绝；调整为地图出生点。
- `20261103_142302_2fc2d44e`：首个物理 tick 将自定义夹具摆位还原为资产初始状态，2米夹具失败；加入实际物理预热后重新reset，通过版本见验收表。
- `20261103_142742_19ba60c9`：尸体倒下误触发全局姿态锁停，比赛停于34.84秒，FAIL；已限制为活狗姿态保护。
- `20261103_142936_955662f7`、`20261103_143141_aef48332`、`20261103_143359_ac240d19`：PPO绕墙跟踪进入安全膨胀边界而失败。逐步修正路点切换、独立机身/漂移余量及回接检查；不把这些失败写为PASS。
- `20261103_143517_3899927f`：已真实绕过中央墙，但中间点震荡，90秒时距终点1.699米，FAIL；增加经过路点平面的接受条件后，`20261103_143808_abd016cd` 在32.5秒内以0.347米误差到达，PASS。

PPO 停车/转向侧移仍存在，路径只是速度闭环引导；不提供精准刹车、精确原地转动或主动动态避障。存活狗严重倒地仍会安全暂停，需要用户评估后重置，不能保证所有比赛均不倒地。尸体保留碰撞，可能造成卡住或堵路，恢复是有限尝试。

没有开发随机巡逻、战术、动态避障、新训练/强化学习、ROS、SLAM或新地图。没有给出长时间多轮可靠性、全部外围墙方向和人工双击的穷举承诺。实际自动桌面启动不等于人工双击验收；180秒超时判定有单元测试，若实际比赛提前决出胜者，不声称完整180秒GUI测试通过。

更换地图需注册 MapInterface，提供 bounds、合法性、轴对齐 WallSpec 几何及三个合法出生点；当前栅格处理平面轴对齐墙体，旋转墙/不规则几何应先扩展地图导航表示和碰撞检查。调整栅格、机身包络、漂移余量必须重新进行真实绕墙测试。

更换PPO沿用机器人注册表，但必须匹配50观测/12动作、关节顺序、PD、动作缩放与频率，更新匹配manifest；共享只读网络不共享策略历史。模型/权重校验沿用原manifest，`protected_assets_after.json` 保存本次资源摘要；未训练、未修改模型、权重或冻结框架/环境。单狗/GPU旧可视模式保留，三狗真实扣血仍要求CPU PhysX，不能用GPU tensor位置未同步的查询冒充命中。

## 8. 最终桌面交付状态

已再次实际通过新增桌面文件启动同一绝对路径脚本，最终run为 `runs/battle/teleop/20261103_164848_a27927cb`，PID 48141。窗口保留，Space锁停，比赛时间0，三狗100HP且命令均为0，导航默认显示，三路第一视角存在。最终截图 `fsm_handoff_paused.png`，启动/按键记录 `fsm_gui_acceptance.json`；即时核查 `runs/validation/fsm_v1_20261103/final_handoff.json`。按C开始自主比赛，V切换路线，Esc安全退出。该PID表示本次交付检查时状态，不保证以后进程一直存活。
