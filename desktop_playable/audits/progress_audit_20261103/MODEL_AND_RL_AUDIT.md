# 模型、运动能力与PPO审计

审计日期：2026-11-03（Asia/Shanghai）。本次只读分析与低资源CPU规则测试；未启动Isaac Sim、GPU仿真、训练、模型转换或安装依赖。所有新文件均在本审计目录。

## 最新原件与当前引用关系

本次重新解析 `model/robot.urdf`：SHA256 `20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`，与既有model_audit记录及同学原始robot.urdf一致。本次实际计算见 `AUDIT_PROBES.json/model`，不是依据文档推断。

|检查项|直接证据/结果|边界|
|---|---|---|
|文件格式|robot.urdf、robot.preview.urdf、package.xml、13个STL；派生import_v1/csdog.usd及4个配置USD|原件目录没有USD；USD在正式assets|
|四足结构|base→每腿hip_roll→hip_pitch→knee，LF/RF/LR/RR，各3转动关节，13link/12revolute|结构完整不等于能走|
|关节名|joint_{lf,rf,lr,rr}_{1,2,3}|每腿3个，不能沿用旧FL/HIP等命名|
|质量|7.6042608kg；13link均有质量/COM/inertia|物理Gate质量7.6042611kg一致；缺机械实测认证|
|惯量|本次13张量全部通过正定主子式检查|数值合法不证明CAD密度/电机真实正确|
|限位|所有关节±3.14rad、10Nm、3rad/s|宽限位；无实机极限资料，不能认证机械安全限位正确|
|足/小腿|原件knee兼含小腿/足端；每link有visual/collision|无4个独立sole link，不能将膝碰撞净力直接称足底独立测量|
|传感|全body ContactSensor，FEET筛4个knee，track_air_time|后续500Hz PhysX接触/几何指标补充，非硬件传感器|
|模型加载|20261026 physics_gate PASS，13刚体/12关节响应、自由根部重力站立|本次未运行Isaac加载，历史证据需按版本回归|

引用链：[dogfight_rl/assets/csdog_12dof/import_v1/config.yaml:1](/home/zxq/robot_projects/dogfight_rl/assets/csdog_12dof/import_v1/config.yaml:1)记录源为最新model/robot.urdf；[dogfight_rl/src/dogfight/locomotion/robot_cfg.py:12](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/robot_cfg.py:12)训练加载其转换USD，不是运行时直接读URDF。[dogfight_rl/scripts/train/csdog_12dof.py:37](/home/zxq/robot_projects/dogfight_rl/scripts/train/csdog_12dof.py:37)把URDF SHA、动作顺序、维数写identity；resume会检查身份。后续多数分支继承此robot配置，V7 collision=sole时[dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py:65](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py:65)切到 `collision_sole_candidate/csdog.usda`。**训练引用最新机械来源成立；对战引用不成立。**

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

运动数值来自[peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md:9](/home/zxq/robot_projects/peer_csdog_review/PEER_CSDOG_RUNTIME_TEST.md:9)及peer_perturbed_*.json；文件mtime为20261030，seed值不代表运行日期。每项1环境10秒，不能外推为长期可靠性，视频5秒与10秒测试是独立运行。同学3段前/后/转mp4已存在；本次仅确认文件，不重新渲染、不重复认证帧内容。

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

主要证据：[dogfight_rl/runs/locomotion/csdog_ppo_spot_v4/reports/SPOT_V4_REPAIR_REPORT.md:5](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_spot_v4/reports/SPOT_V4_REPAIR_REPORT.md:5)、[dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/PPO_HYPERPARAMETER_SEARCH_REPORT.md:49](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_tuning_v5/reports/PPO_HYPERPARAMETER_SEARCH_REPORT.md:49)、[dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/FINAL_V6_2_DIAGNOSIS.md:72](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_ppo_v6_2_diagnostics/FINAL_V6_2_DIAGNOSIS.md:72)、[dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_curriculum_ppo_v6_3/STATUS_SUMMARY.md:1)、[dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/TRAINING_STATUS.json:127](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/TRAINING_STATUS.json:127)。本地出现“有前进速度但拖滑/少腿摆动”的问题有实际日志，不宜统一描述为目前所有方案都趴地；同学方案确有短测四足运动成果。

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

证据：[dogfight_rl/src/dogfight/locomotion/env_cfg.py:32](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/env_cfg.py:32)、[dogfight_rl/src/dogfight/locomotion/ppo_cfg.py:10](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/ppo_cfg.py:10)、[dogfight_rl/src/dogfight/locomotion/curriculum_v6/config.py:67](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/curriculum_v6/config.py:67)、[dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py:25](/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion/phase_guided_v7/runtime.py:25)、[peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md:1](/home/zxq/robot_projects/peer_csdog_review/PEER_CSDOG_PPO_COMPARISON.md:1)。表中为各分支可读默认/记录，不把配置当所有checkpoint的实际训练超参；具体run的agent/env/options/identity与日志优先。

## 足底候选与不兼容风险

本地V7候选保留13刚体/12关节/原质量，拆分sole cap与上段碰撞；两个被拒球形sole仍存档。[dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md:1](/home/zxq/robot_projects/dogfight_rl/runs/locomotion/csdog_phase_guided_ppo_v7/reports/SOLE_COLLISION_COMPARISON.md:1)记录原碰撞静态也稳定，不能归因“原模型碰撞必然错误”。同学训练URDF则有17link（4个1g sole）、12转动+4固定，球形sole，限位±.65/1.4/1.8、12Nm/10rad/s、PD40/1.5，与本地10Nm/3rad/s/PD25/.8不同。机械原件同SHA并不意味着策略直接兼容。

旧Dog A、45维初版、48维V6、50维V7/同学权重均不能任意互换。即便都是50维，关节顺序、时钟、默认姿态、碰撞、驱动、动作尺度仍不同。最早resume有identity全等检查，不能外推后续所有工具都有完整身份校验。安全审计未反序列化所有权重；仅盘点1695文件和已有身份/评估证据，文件存在不代表可部署。跨同学权重维数结论来自既有权重检查与当地原任务推理证据，并非本次新加载权重。

## 可复现性与后续低风险验证方案

已有seed/options、config快照、PPO指标、checkpoint、原始npz/接触轨迹、视频和预算ledger，支持复查；恢复网络/优化器不必然恢复仿真状态，版本变更/同源源码未锁定会影响可复现。源码sha与本次mtime不能证明历史测试与当前代码逐字一致，所有物理历史成功应再做回归。

后续方案（本次不执行）：明确选定同学原任务或本地候选及身份，先检查关节映射和观测，再做1环境固定命令/停止，随后多种子连续前后转停、撞墙后恢复；记录实际速度、位置漂移、全四足周期/滑移、摔倒、饱和与命令切换。先满足停止/转向/四腿标准，再讨论训练或接三机器人，不继续盲目增加训练轮数。
