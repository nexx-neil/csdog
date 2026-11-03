"""Build the experiment report from measured artifacts; no estimated performance values."""
from pathlib import Path
import json,numpy as np
ROOT=Path(__file__).resolve().parents[2];EXP=ROOT/'runs/locomotion/csdog_ppo_20261026';OUT=EXP/'reports'
s=json.loads((OUT/'comparison.json').read_text());ev=[json.loads((EXP/f'evaluation_stage{i}_final/summary.json').read_text()) for i in [1,2]]
audit=json.loads((ROOT/'configs/locomotion/csdog_ppo/model_audit.json').read_text());physics=json.loads((OUT/'physics_gate.json').read_text());env=json.loads((OUT/'environment.json').read_text())
a=s['stage1'];b=s['stage2'];names={'stop':'静止','forward':'前进','backward':'后退','left':'左移','right':'右移','left_turn':'左转','right_turn':'右转','diagonal':'斜向'}
def line(row):
 v=row['actual_mean_velocity'];return f"({v[0]:+.3f}, {v[1]:+.3f}, {row['actual_mean_yaw_rate']:+.3f})"
rows=['|测试|目标 vx/vy/wz|第一阶段实测 vx/vy/wz|第二阶段实测 vx/vy/wz|平移误差1→2 m/s|yaw误差1→2 rad/s|摔倒1/2|','|---|---|---|---|---|---|---|']
for x,y in zip(ev[0]['tests'],ev[1]['tests']):rows.append(f"|{names[x['test']]}|{tuple(x['target'])}|{line(x)}|{line(y)}|{x['linear_error']:.3f} → {y['linear_error']:.3f}|{x['yaw_error']:.3f} → {y['yaw_error']:.3f}|{x['falls']}/4、{y['falls']}/4|")
extra=['|测试|路程1→2 m|姿态RMS1→2|支撑滑移1→2 m/s|限幅后动作变化平方1→2|第二阶段限幅比例|','|---|---|---|---|---|---|']
for x,y in zip(ev[0]['tests'],ev[1]['tests']):extra.append(f"|{names[x['test']]}|{x['mean_travel_distance']:.3f} → {y['mean_travel_distance']:.3f}|{x['tilt_rms']:.3f} → {y['tilt_rms']:.3f}|{x['contact_slip_speed']:.3f} → {y['contact_slip_speed']:.3f}|{x['processed_action_delta_mean_square']:.3f} → {y['processed_action_delta_mean_square']:.3f}|{100*y['action_clip_fraction']:.1f}%|")
base=audit['links']['base']['collision_bounds'];dimensions=(np.array(base[1])-base[0]).tolist()
text=f'''# 新12自由度机器狗 PPO 短程训练实验报告

日期：2026-10-26。正式代码位于 `/home/zxq/robot_projects/dogfight_rl/src/dogfight/locomotion`，配置在 `dogfight_rl/configs/locomotion/csdog_ppo`，本实验根目录为 `dogfight_rl/runs/locomotion/csdog_ppo_20261026`。

**已完成独立任务、真实动力学门禁、PPO更新、两轮短程训练、独立评估及两阶段视频。策略已形成前进、较弱后退/左移/斜向能力，但右移、右转和零指令停止仍不合格，动作饱和/滑移明显。推荐 stage2/final.pt 仅用于后续研发，不用于真实硬件或三真实本体对战。没有继续长训练。**

## 环境审查与工程保护

- Ubuntu22.04.5，RTX4070 Laptop，8188MiB显存；初始使用约638MiB。驱动580.178.04，CUDA可用。
- 解释器 `{env['executable']}`；Python3.11.16；PyTorch {env['torch']}、CUDA runtime {env['cuda']}；Isaac Sim {env['packages']['isaacsim']}；RSL-RL {env['packages']['rsl-rl-lib']}。
- IsaacLab源码tag v2.3.2，commit `37ddf626871758333d6ed89cf64ad702aef127d0`；分发版本0.54.2是另一个版本字段。环境检查见 environment.log / environment.json。
- 未改官方源码、未安装/升级依赖、未移动或修改 archive 旧任务、未覆盖任何旧checkpoint；原始model保持SHA256。现有入口、当前目录说明和模型接入元数据的必要修改前，原文保存在 protection；旧整理清单和封存记录不改，使用新任务独立修订链验证。
- `official_trainer.log` 记录未修改的官方 `scripts/reinforcement_learning/rsl_rl/train.py` 实际运行本项目新注册任务，16环境、1次PPO更新并保存 model_0.pt；输出仅在本实验 official_validation 内。它是对官方入口的实测，不把 --help 误作训练通过。该1次计入总预算。

## 参考的 NVIDIA 方法与源码版本

具体文件和许可证见 src/dogfight/locomotion/THIRD_PARTY_NOTICES.md，BSD-3-Clause全文已保留。源码版本统一为上述本地冻结commit。

- [ANYmal-C Flat](https://github.com/isaac-sim/IsaacLab/tree/37ddf626871758333d6ed89cf64ad702aef127d0/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/anymal_c)：采用平地速度跟踪、ManagerBasedRLEnv的模块化观测/动作/奖励/重置/终止、24步rollout、Actor/Critic三层128单元ELU网络和RSL-RL PPO。
- 基础奖励直接复用官方MDP函数：xy/wz指数跟踪、垂直速度/roll-pitch角速度/投影重力惩罚、关节力矩/加速度、动作变化、非法接触及关节限位。
- [Spot](https://github.com/isaac-sim/IsaacLab/tree/37ddf626871758333d6ed89cf64ad702aef127d0/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot)：GaitReward直接复用官方类；LF/RR和RF/LR时序同步，其余足对反同步。使用接触与腾空时间差的指数核，门限控制移动时启用。保留为弱可选先验，两轮训练均未启用，避免多奖励同时强制步态。
- 足端抬升/滑移借鉴Spot思路，针对本模型改成真实STL末端点。未复制Spot的质量、PD、动作尺度、足端高度或奖励数值。[NVIDIA方法说明](https://developer.nvidia.com/blog/closing-the-sim-to-real-gap-training-spot-quadruped-locomotion-with-nvidia-isaac-lab/)。
- PPO使用现有RSL-RL3.1.2；算法库没有复制。新增runner只做有限值检查、JSON指标、预算和checkpoint保护。

## 模型检查和独立标定

原始资产为工作区model/robot.urdf、robot.preview.urdf、13个STL及package.xml。主URDF摘要 `{audit['sha256']}`，未修改任何原始几何、质量、惯量数据。自动审查见 configs/locomotion/csdog_ppo/model_audit.json。

- 13个link，12个revolute可驱动关节；LF/RF/LR/RR各3关节，固定关节0。每关节类型、旋转轴、原点、限位与逐link质量/惯量正定性已检查。
- 总质量 {audit['mass_kg']:.7f}kg，base质量 {audit['links']['base']['mass']:.5f}kg；base碰撞Mesh包围盒尺寸约 {dimensions[0]:.3f}×{dimensions[1]:.3f}×{dimensions[2]:.3f}m。大腿连接向量长度约0.19m，膝部远端约0.22m；精确几何以逐关节原点/STL与审查JSON为准。
- 关节命名 joint_lf/rf/lr/rr_1,2,3，URDF声明顺序LR/LF/RF/RR；Isaac运行时顺序按关节层分组，和声明不同。动作与关节观测通过名称显式映射为LF/RF/LR/RR每腿1→2→3，绝不按12维数量套旧Dog A映射。
- 关节1绕±X，2/3轴接近±Y并带CAD原始小Z分量；完整轴数值保留。URDF每关节限位±3.14rad、effort10Nm、velocity3rad/s。没有假定这些就是实测硬件额定值。
- +X按前腿所在正X定义前向，+Y左、+Z上；新模型根部姿态无需旧Dog A的−π/2偏移。
- 没有独立foot刚体，四个link_*_knee同时包含小腿和足端。自动取每个STL远端帽区平均点，用FK数值求站姿，使足端落在(±0.215,±0.160,−0.350)m。膝部刚体原点不是足端，不能直接用它作抬脚高度。
- 静态仿真标定：初始root高度0.355m，PD Kp25Nm/rad、Kd0.8Nm·s/rad；驱动限制10Nm/3rad/s；动作偏移最大±0.25rad。原始URDF限位不改。地面摩擦0.8/0.7，自碰撞关闭，重力开启，不固定根部。

实际动力学门禁：4环境从0.435m释放，root稳定至 {physics['final_z']:.4f}m；8秒站立0摔倒，稳定阶段最大投影重力xy范数 {physics['maximum_settled_tilt']:.4f}；四足最终接触力约 {[round(v,1) for v in physics['final_contact_forces']]}N，合计接近重量；12个低幅关节控制均有响应，最小 {min(physics['joint_pulse_response_rad']):.4f}rad。导入质量 {physics['total_mass']:.7f}kg，与URDF一致。根部下落和接触数据见 [physics_gate.json](physics_gate.json)，不是固定在空中站立。无需单独站立神经网络。

USD在 assets/csdog_12dof/import_v1，转换器显式import_inertia_tensor=True，保留原惯量；convex hull碰撞，全部转换依赖一起保留。

## 新任务实现与参数

Gym注册 `Dogfight-CSDog-Velocity-Flat-v0`。仿真200Hz、策略50Hz，8秒episode，平面地形。训练时没有摄像机，视频评估单独启用渲染。

- 指令为机身系[vx,vy,wz]，范围±0.35m/s、±0.22m/s、±0.5rad/s。每3～5秒重采样；stop、纯vx、纯vy、纯yaw、组合速度各20%。正负方向均匀抽样，包含实际非零yaw。
- 12维连续动作先clip到[−1,1]，再 `q_target=q_default+0.25*a`，由新PD执行；不直接写根速度或根位置以制造运动。
- Actor45维：角速度3(×0.25)、投影重力3、指令3、关节偏移12、关节速度12(×0.05)、上次动作12。Critic额外获得机身线速度3，共48维；该线速度属于仿真特权观测，Actor不使用，真实迁移仍须处理IMU/编码器噪声与估计。
- 官方PPO：clip0.2、5epochs、4minibatches、初始lr0.001/KL自适应、gamma0.99、GAE0.95、entropy系数0.005、grad_norm1、探索std0.7。网络[128,128,128]ELU，Actor/Critic独立，不复制旧网络权重。
- 首轮仅基础跟踪/稳定/正则；静止关节偏移惩罚−0.15，防止零指令下无意义关节偏离。四个可选奖励开关全关。
- 随机化限于reset xy±0.1m、yaw±π、关节±0.025rad；先不启用质量/COM/摩擦随机化和推搡，也不加传感噪声。本轮是工程与短学习验证，不是sim-to-real训练完成。
- 终止：超时、base非法接触>8N或projected_gravity_z>−0.65。足端接触传感器track_air_time开启。

## 执行预算、checkpoint与日志

|运行|环境数|新增PPO迭代|说明|
|---|---:|---:|---|
|新任务smoke|32|3|有限值、更新、重置、checkpoint通过|
|Stage1|256|150|从零训练|
|官方原训练入口验证|16|1|未修改官方train.py，独立1次更新|
|Stage2|256|146|从Stage1/final.pt恢复，保持观测/动作兼容|
|总计||**300**|正式两阶段296，所有测试训练也计入上限|

三个新任务进程累计wall time（包含其App启动/环境初始化）为 **{s['new_task_wall_seconds']:.2f}秒**；官方脚本报告其训练1.07秒。两轮分别约101.71/103.93秒，均远低于单次900秒和累计2400秒上限。全任务开发/录像时间不当作训练时间。预算账本 training_budget.json 以文件锁防并发；按更新记录消耗，迭代结束检查时限，SIGALRM另作单次硬时限。周期checkpoint每25轮保存，最后final.pt保留，异常尝试保存interrupted.pt。已实测额外1次请求被预算拒绝，未启动环境，见 budget_rejection.log。

训练记录reward、episode length、xy/yaw误差、摔倒/timeout、动作变化、value/surrogate loss、entropy、lr和nvidia-smi显存。Stage1峰值 {a['max_gpu_memory_mib']}MiB，Stage2 {b['max_gpu_memory_mib']}MiB；因此32环境smoke后选择256，无OOM。模型/优化器所有保存张量有限，checkpoint_validation.json记录obs指令列权重不为零；不是忘记将yaw指令送入网络。

保留 [Stage1 checkpoint](../stage1/final.pt)、[Stage2 checkpoint](../stage2/final.pt)、smoke及官方验证权重、全部周期checkpoint、配置快照、来源SHA。Stage1 final的iter=149表示150次，Stage2 iter=295表示主策略累计296次，不能把零基下标当迭代总数。推荐后续研发以Stage2为起点，不复制第三个“推荐权重”；recommended_checkpoint.json记录现有路径与SHA。

## 第一轮评估、优化依据和第二轮结果

评估使用相同seed734、同一默认站姿/PD/摩擦，8种固定指令，每项4次重复、6秒，去掉首1秒计算速度误差；不在测试间给根部速度，只有每个独立试验开始时正常reset。重复初始条件相同，32个短trial不是随机鲁棒性或长期稳定性证明。另做12秒连续变向→零指令测试。

第一轮主要保持静态倾斜姿态，前/后平均速度接近0；左转有间歇响应，其他方向失败。零指令也有漂移。只改变两组奖励，完整差异见 [PARAMETER_CHANGE.md](PARAMETER_CHANGE.md)：

1. 跟踪组：linear 3.0→5.0，angular 1.5→2.5，提高速度目标相对正则的比重。
2. 足部组：air_time 0→0.2，clearance 0→0.15，目标足端高度0.035m，鼓励真实离地。gait/slip继续关闭。

没有改站姿、关节映射、PD、动作尺度/维度、观测、PPO网络，兼容恢复Stage1。未一次性调整大量物理参数掩盖模型问题。

{chr(10).join(rows)}

第二轮平移改善明显：前进vx接近0.3但伴随负vy漂移，后退约半目标速度；左移和斜向有初步效果。右移方向仍错误，右转没有有效负yaw。左转平均0.150rad/s，虽然绝对yaw误差略改善，却伴随约0.14m/s侧向漂移，不是合格原地转向。零指令下侧向漂移恶化。

{chr(10).join(extra)}

姿态指标为投影重力xy范数RMS，维度无量纲，不冒充roll/pitch角度。路程是整个试验累计真实平移路径，包含初期姿态调整；不是目标方向的有效前进距离。详细根部位置、速度、关节角度、限幅比例、动作变化、转矩/关节速度与有效样本在 evaluation_stage1_final / evaluation_stage2_final。接触力是整根小腿+足的汇总，无法严格区分足底/胫部触地；拖腿指标low_swing仅代理量，不能代替接触点和人工视频分类。

额外诊断修正了一个速度坐标细节：Isaac Lab body_lin_vel_w 是COM速度，足端速度必须用 COM→足端杆臂计算 omega×r。该修正不影响本次训练（slip关闭、clearance只取位置），但影响滑移/拖腿代理指标；因此重新评估并保留*_final为权威结果，早期evaluation_*和*_detailed数据保留作诊断历史，不用于最终滑移比较。

### 汇总对比

|指标|Stage1|Stage2|
|---|---:|---:|
|主策略累计更新|150|296|
|最后记录Mean Reward|{a['last_mean_reward']:.3f}|{b['last_mean_reward']:.3f}|
|最后10轮Mean Reward|{a['last10_mean_reward']:.3f}|{b['last10_mean_reward']:.3f}|
|最后10轮episode平均时长|{a['last10_episode_seconds']:.3f}s|{b['last10_episode_seconds']:.3f}s|
|8指令平均平移误差|{a['eval_mean_linear_error']:.3f}m/s|{b['eval_mean_linear_error']:.3f}m/s|
|8指令平均yaw误差|{a['eval_mean_yaw_error']:.3f}rad/s|{b['eval_mean_yaw_error']:.3f}rad/s|
|固定试验摔倒率|0/32|0/32|
|训练已结束episode中的摔倒比例|{100*a['training_fall_fraction_of_completed_episodes']:.3f}%|{100*b['training_fall_fraction_of_completed_episodes']:.3f}%|
|连续变向后停止阶段实际速度|{a['continuous_stop_error']:.3f}m/s|{b['continuous_stop_error']:.3f}m/s|
|平均限幅后动作变化平方|{a['mean_processed_action_delta']:.3f}|{b['mean_processed_action_delta']:.3f}|

两阶段reward权重不同，46不可以直接和25比较为“性能提高约一倍”。各阶段曲线有上升趋势，但初始随机episode长度造成最早几个日志回报偏低，物理评估才是主要证据。Stage2平均yaw误差和停止表现变差，不掩盖策略局部退化。频繁动作饱和（第二轮不同任务约55%～91%）与大幅限幅后动作切换，说明存在靠抖动/滑移获得速度奖励的风险，尚未形成可部署的自然步态。

## 视频、曲线与复现入口

- [第一阶段24秒视频](../videos/stage1/all_directions.mp4)
- [第二阶段24秒视频](../videos/stage2/all_directions.mp4)
- 两者800×608、25fps、H.264；分别含8指令，每项3秒，跟随近距离相机、地面参考线、目标/实测速度文字。视频配置/物理与数值评估相同，但视频为单环境且每指令3秒，不是6秒批量统计样本本身。来源checkpoint与SHA见各video_provenance.json。已抽帧确认能清楚看到整只机器人和四足。
- [训练曲线](training_curves.png)：Reward、episode length、速度误差、动作变化、显存。
- [独立评估对比](evaluation_comparison.png)、[PPO损失/Entropy/lr](ppo_diagnostics.png)。
- [完整逐方向CSV](comparison.csv)、comparison.json、所有原始trajectory/continuous_commands.json保留。

使用说明见实验README和当前工程 docs/LOCOMOTION_PPO.md。保留历史训练命令和实际机器解释器，不提供声称已经验证的长训练结果。本轮预算已封顶，额外训练请求明确拒绝；评估/回放仍可独立运行。

## 验收边界与下一步建议

通过：真实浮动本体、重力/四足接触/PD/关节映射、独立Gym注册、官方RSL训练入口、smoke参数更新、两阶段训练、固定/连续指令评估、4个可选奖励有限值门禁、checkpoint有限值、实际视频；39项轻量回归通过。没有观察到持续NaN/Inf或OOM。官方库和旧工程不修改，当前完整性通过独立任务修订链核验，见最终验证记录。

尚未达到：可靠右移/右转、零速稳定停止、低滑移/低动作冲击、长期鲁棒性、sim-to-real、真实三本体对战。两轮很短，不能据此否定PPO；但也不建议直接无诊断地开展长时间训练。

下一轮应先围绕1～2组问题做有预算的短对比：降低动作饱和/目标频繁翻转（显式有界输出或更合理探索尺度、动作/加速度约束），再强化零指令与负vy/负yaw的验收和采样。接触点空间分类/足底辨别需改进，防止把小腿拖滑当作正常步态。之后再考虑弱gait先验对比和域随机化。不得继续本轮训练来凑出更好数字；本轮已停止。
'''
text+='''
## 最终工程复核

- regression_final.log：39项测试通过，包含新模型映射/标定、300迭代与2400秒保护；未删对战规则断言。
- environment_final.log：冻结环境检查通过；static_final.json记录IsaacLab Git工作树仍clean。
- integrity_final.json：全部3,783个既有文件/历史修订链、新任务修改前保护和30个新增静态文件核验通过；52处原始新模型Mesh引用有效，0软链接、0正式源码硬链接。旧模型资产、源码、权重和模型原件未被改写。
- 初次完整性复核发现pytest在本次新建测试临时目录产生12个current软链接，原失败记录保留为integrity_test_cache_failure.json。只移除这些测试指针，目标数据完整保留，见test_temp_link_cleanup.json；没有跳过资源检查或删历史文件，再次核验通过。
- TensorBoard已实测读取事件并短时启动HTTP服务，返回200，验证后自动停止；无训练进程继续运行。
- 新任务来源/修改前原文在protection，未覆盖此前reorganization历史封存。artifact_manifest.json保存实验产物哈希；recommended_checkpoint.json只引用已有权重。
'''
(OUT/'TRAINING_EXPERIMENT_REPORT.md').write_text(text)
# Reference an existing checkpoint; do not manufacture a duplicate recommended.pt.
cp=EXP/'stage2/final.pt'
import hashlib
(EXP/'recommended_checkpoint.json').write_text(json.dumps({'path':str(cp),'sha256':hashlib.sha256(cp.read_bytes()).hexdigest(),'deployment_ready':False,'reason':'Best translational progress in this short campaign; rightward motion, negative yaw and stopping fail.'},indent=2))
print('Report generated from measured data.')
