> 当前默认入口已扩展为三只真实机器狗，最新操作与验收见 [三狗交付说明](DOGFIGHT_THREE_DOG_DELIVERY.md)。下文保留原单狗阶段记录；复现单狗需加 `--config configs/teleop/single_dog.yaml`。

# DOGFIGHT V0.2 — RealDog Teleop Integration 交付说明

日期：2026-11-03。真实机器人、原PPO与现有TestMap已经集成；不含训练、伤害或三真实狗比赛。最后人工双击和全部输入安全验收以本文件末尾最终状态为准。

## 启动

- 桌面：`/home/zxq/桌面/机器狗对战环境.desktop`，已可执行且metadata::trusted=true。
- 包装器：`/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh`。
- 命令：`/home/zxq/robot_projects/dogfight_rl/scripts/launch_dogfight_teleop.sh`；或 `/home/zxq/miniconda3/envs/dogfight/bin/python -B /home/zxq/robot_projects/dogfight_rl/launch.py teleop --map test_map --robot dog_a`。
- 启动后点击仿真视口，按C解锁，再按住运动键。失焦会锁停；松开Space不会解锁。
- 模型：`assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf`及其转换USD。
- 权重：`assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt`（iter1043）。
- 日志：`runs/battle/teleop/launcher/`；每次独立运行身份、status、metrics、trace在`runs/battle/teleop/<时间_UUID>/`。
- 默认原TestMap地面/两墙/三个出生点，遥控模式追加配置控制的四周边界墙；一只dog_a，没有Proxy替身。

## 文件与职责

`launch.py`只新增teleop分派及该模式的exec信号传递；修改前备份见`runs/validation/teleop_v02_current.txt`指向目录的backup/launch.py。原有src文件SHA未变，旧裁判/WeaponService/HUD/三Proxy工厂未改写。

新增`src/dogfight/teleop/`：config核对资源/ABI/哈希；policy负责Actor恢复和50维观测/12关节目标；agent继承V0 RealDogAgent补充body-frame枪口；maps注册与创建现有TestMap及边界；keyboard输入/锁停/焦点/超时；laser全命中物理查询排除自身并绘制红色无碰撞圆柱；hud低频状态文本；runtime统一200Hz物理/50Hz策略调度。

新增`scripts/teleop/run.py`、桌面启动模板与XTest验证工具；`configs/teleop/default.yaml`、`configs/robots/dog_a_teleop.yaml`；正式模型/权重副本及IMPORT_MANIFEST/identity；`assets/ui/dogfight_teleop.svg`；`tests/test_teleop_v02.py`。详细接入前审计见`docs/TELEOP_POLICY_AUDIT.md`。

正常运动只写关节位置目标；根节点写入只用于初始出生和明确reset，不用位姿赋值伪造行走。适配器不推进世界，裁判不接触关节。激光无HP/冷却/弹药，damage_enabled强制false。

## 键盘

|键|功能|
|---|---|
|W / S|前进 / 后退，默认±.25m/s|
|A / D|左转 / 右转，默认±.3rad/s；可与W/S组合|
|Q / E|强制旋转模式，覆盖W/S令期望vx=0；不保证PPO实际零平移|
|Space|急停锁定，持续输出零命令|
|C|解锁并清除旧运动键；需重新按运动键|
|R|恢复地图出生点，重置动作历史和相位，保持锁停，按C继续|
|Esc|退出；退出清零命令|
|松手/冲突键|松手对应轴立即清零；W+S、A+D、Q+E冲突安全归零|

焦点丢失/输入异常/超时清除命令并锁停。所谓停止是零速度命令，不是物理瞬间刹车。原PPO零命令仍踏步漂移，不能将其称作安全硬刹车或实机急停。

## 实际测试证据

|Gate|状态及范围|证据|
|---|---|---|
|A 环境/资源|PASS：冻结Python3.11、IsaacSim5.1/IsaacLab2.3.2、原权重50→256→256→128→12与LR/LF/RF/RR映射实际加载|teleop_preflight.log、各run/identity.json|
|B 真实狗|PASS：自由根部、真实12关节接触、无运动根位姿覆盖，运动面板最低根高约.376m、最大倾斜代理.275|20261103_105844_698b07ff/metrics.json|
|C 运动遥控|物理脚本面板PASS；GUI最后验收另见末尾。前后/左右/四组合/QE/锁停解锁均有数据；严格无漂移不合格|teleop_motion.log、keyboard_gui_events_retry.log及最终桌面记录|
|D 地图碰撞|PASS（8秒中央墙试验）：未穿越中央墙，最大水平接触约43.9N；松手命令归零。四条外围墙逐方向压力测试NOT TESTED|20261103_110046_4b110d33/metrics.json、trace.json|
|E 常亮激光|PASS已测范围：GUI红线可见，实际PhysX墙命中截断，随朝向变化，无自身命中，无伤害；多视角穷举NOT TESTED|teleop_gui_first.png、墙试验trace及桌面截图|
|F 地图独立|PASS：运行入口实际消费create_selected_map配置；pytest注册替代桩并切换边界/接口|test_teleop_v02.py地图测试|
|G 权重选择|PASS：配置权重、manifest/hash/维数/映射检查；错误维数、顺序、哈希、缺文件明确拒绝|teleop_delivery_pytest.log|
|H 旧系统|PASS：launch.py battle --duration 1、battle-gui --duration 3 --result-hold 0均实际启动，退出0；不宣称重测完整胜者比赛|teleop_proxy_regression.json与对应日志|
|I 桌面|快捷方式、权限、trusted、gio launch实际窗口已验证；人工鼠标双击NOT TESTED。最终输入/退出复核见末尾|desktop_launch_acceptance.json、桌面启动日志|

测试日志除run名外均在`runs/validation/`。CPU全套最近163项通过（12.02秒），不能替代上述物理/GUI证据。初次raycast_all回调结构不匹配已修；Space默认时间轴暂停曾造成退出等待，相关失败日志保留；后续GUI回调字符串兼容修订正在最终复核，不以早期退出0掩盖失败。

## 运动测量与局限

3秒窗口：W平均vx约+.251，位移.749m；S平均vx约−.206，位移.618m；A平均yaw+.280、转角+.837rad、平移.203m；D平均yaw−.329、转角−.963rad、平移.218m。W+Q/W+E发出vx=0而仍有上述平移。零命令2秒平移约.058m；撞墙后松手1秒平移约.104m。不能宣称完全停车或严格原地旋转。

GUI样本32.5模拟秒约38.5墙钟秒（实时因子约.84），策略步长仍.02秒，图形约25Hz；一次8GB GPU观察约5.4GB占用。启动/材质编译和桌面已有任务影响速度，不修改电源/驱动以追求虚假帧率。Kit用户Documents目录缺失等非物理插件错误在日志中保留；不为此创建项目外目录或重装环境。

## 后续换权重/地图/更多机器人

权重修改`configs/robots/dog_a_teleop.yaml`的checkpoint、policy_manifest与policy_version。保留原版本，为新权重建立独立文件夹和identity.json，包含真实SHA及完整contract。必须同50维顺序、12维动作/关节顺序、PD/姿态/模型碰撞、相位/频率、网络和归一化；不兼容任务需要新适配器，不能只改数字或伪造manifest。重启生效，不热替换。

地图在`src/dogfight/teleop/maps.py`向MAPS注册实现V0 MapInterface的工厂，然后修改`configs/teleop/default.yaml`的map.name。当前程序化渲染消费get_navigation_data中的walls（WallSpec）、get_bounds和get_spawn_points。新USD地图可在地图层扩展几何加载，不改机器人/PPO/裁判。boundary_walls在地图配置中控制。

dog_b/c未来各加独立机器人配置、权重manifest，并在default.yaml的robots登记；单狗入口已按ID创建prim。真正三狗仍需扩展runtime为多个Agent先更新关节目标，再统一一次世界步进；不能每狗各sim.step。本次不创建空目录或宣称三真狗集成已完成。

## 回滚

关闭本次遥控窗口，确认无本次进程后，将备份launch.py恢复到正式入口即可撤回新增命令；新模块/资源可保留但不再被入口调用。不要运行历史全项目迁移回滚、git reset/clean，不覆盖任何训练成果。原同学资产与model原件未修改。

## 最终验收状态

待最后桌面入口键盘/退出复核写入；在此之前不能称全项完成。

## 右侧第一视角更新（2026-11-03）

已增加默认开启的右侧独立第一视角，左侧主相机保留。详细配置、备份和GUI证据见[第一视角说明](docs/FIRST_PERSON_VIEW.md)。界面为同一Isaac进程的双视口，不改变策略或模型；原键位继续使用。
