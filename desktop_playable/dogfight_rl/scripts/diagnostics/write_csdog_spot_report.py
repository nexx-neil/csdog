"""Write the Spot report using preserved measured data."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_v2';O=E/'reports'
def load(p):return json.loads(p.read_text())
labels=['Stage2','B','C'];dirs=['baseline_final','evaluation_b','evaluation_c']
evals=[load(E/d/('summary_validated.json' if d=='evaluation_b' else 'summary.json')) for d in dirs]
metrics={s:[json.loads(x) for x in (E/s/'metrics.jsonl').read_text().splitlines()] for s in ['stage_b','stage_c']}
budget=load(E/'training_budget.json');gate=load(O/'physics_gate.json');old=load(O/'old_reward_contributions.json')
actuator={};comparison=[]
for label,d,rows in zip(labels,dirs,evals):
 data=np.load(E/d/'diagnostics.npz');mask=data['valid']&(data['t'][:,None]>=1.);p=data['projected_joint_force']
 actuator[label]=dict(all_physical_states_finite=all(np.isfinite(data[k]).all() for k in ['q','qd','torque','projected_joint_force','velocity','foot_height','raw_action']),projected_force_limit_fraction=float((abs(p[mask])>=9.9).mean()),projected_force_peak=float(abs(p[mask]).max()),pd_estimate_peak=float(abs(data['torque'][mask]).max()),joint_speed_peak=float(abs(data['qd'][mask]).max()))
 for row in rows:comparison.append(dict(stage=label,**row))
(O/'actuator_validation.json').write_text(json.dumps(actuator,indent=2));(O/'comparison.json').write_text(json.dumps(comparison,indent=2))
with (O/'comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
import torch
checkpoints={}
def finite(v):
 if torch.is_tensor(v):return bool(torch.isfinite(v).all())
 if isinstance(v,dict):return all(finite(x) for x in v.values())
 if isinstance(v,(list,tuple)):return all(finite(x) for x in v)
 return True
for stage in ['smoke','stage_b','stage_c']:
 path=E/stage/'final.pt';ck=torch.load(path,map_location='cpu',weights_only=False)
 checkpoints[stage]=dict(path=str(path),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),all_saved_tensors_finite=finite(ck))
(O/'checkpoint_validation.json').write_text(json.dumps(checkpoints,indent=2))
text=f"""# SPOT_LOCOMOTION_IMPROVEMENT_REPORT

日期：2026-10-26。实验目录：{E}

**已实际完成基线诊断、接触接口修复、物理和奖励门禁、5次smoke、B/C各150次PPO更新、评估和视频。防滑、裁剪和部分方向控制改善，但没有形成正常交替步态，左移摔倒、斜向退化；不建议开始长训练。Spot GaitReward已正确接入，本轮没有证据证明其促成Trot。**

## 1. 原始问题分析

首先审查旧TRAINING_EXPERIMENT_REPORT、各evaluation目录的summary/trajectory、奖励设置、训练日志和TensorBoard，并抽取两段旧视频检查。索引见old_experiment_review.json、old_reward_contributions.json、old_stage1_review.png、old_stage2_review.png。旧阶段完整文件SHA256预先封存。

原无限平面复测vx=0.31589、vy=-0.08389m/s，复现旧结果。为取得可靠接触点而更换地面后，同一Stage2策略vx=0.31543、vy=-0.08517，原问题仍存在。所有正式B/C比较使用相同的新地面。baseline、baseline_box保留接触接口失败数据，**不用于步态奖励或比较**。

- 前进的有效支撑点滑速0.2568m/s；1秒后LF/RR在5秒内各切换接触约249次，RF/LR长期支撑，整膝碰撞体离地仅0～4.2mm。这是约25Hz浅层抖动，不是正常摆动。旧速度奖励允许拖地位移，整膝air-time和末端平均点高度不能验证真正离地。
- 后退、右移、右转的平均裁剪动作与静止余弦相似度分别0.979、0.986、0.993。右转指令实际为-0.4rad/s，裁剪比例约87.5%，大量均值超出动作边界。裁剪压缩了有效指令差异，策略具有明显偏置。关节脉冲均响应，未发现命令漏送或右转符号反写；这些证据不等于排除一切物理不对称。
- 零指令仍有大量非默认目标，vy约+0.119m/s。旧静止惩罚弱，且未专门约束实际平移和yaw，偏置动作继续产生漂移。
- 原探索std逐关节约0.434～0.817；确定性原始输出峰值超过3，说明饱和不只是探索噪声。完整逐关节依据见baseline_root_cause_data.json和baseline_final/diagnostics.npz。

## 2. 物理模型与接触修复

原URDF、STL、机器人USD、质量/惯量、12个驱动自由度、关节映射、PD25/0.8及10Nm/3rad/s上限均未修改。视觉与碰撞引用相同STL，origin为零，导入碰撞使用convexHull；见geometry_audit.json。没有新增足部质量或固定关节。实际机器人质量{gate['mass']:.7f}kg。

GPU PhysX实际打印：GPU contact filter for collider ... is not supported。无限平面和静态箱体的net_force有效，但筛选接触点为空。新环境采用顶面z=0、原摩擦0.8/0.7的固定运动学箱体地面；运动学地面不参与机器人质量，不移动。为各膝部建立单体ContactSensor，筛选与此地面的真实manifold；没有修改机器人根部速度或位置模拟行走。

采用方案C：逐个接触点按距末端帽区中心35mm内、距地面20mm内分类，汇总真实法向力。有远端区域外接触或缓冲溢出时，否决该腿有效支撑并关闭该环境gait。整膝力仍单独保存。35mm末端区域是保守几何代理，不冒充独立foot刚体传感器；混合胫部接触宁可漏判。平地验证可靠，复杂地形仍需重新验证。

世界系足端和接触斑速度均为v_COM + omega × (point_world - COM_world)。滑移用真实接触斑速度；摆动诊断另存末端点速度。门禁用link原点速度和相应杆臂独立交叉验证，误差小于1e-4m/s。

Clearance改用整根小腿/足端凸包的最低表面高度，由STL凸包顶点和刚体位姿计算，任何小腿部位拖地均不能获得抬升奖励。目标35→30mm，核宽15mm，约22cm小腿长度的14%。固定机身几何可达上界约61mm，见reachability.json；这不是负载条件下的动力学保证，也没有据此扩大动作范围。

有效接触时钟精度为20ms，来源是50Hz实际manifold分类，不是Spot独立足部传感器的200Hz数据。没有向官方传感器写入伪造接触。适配器把这些明确标注的时钟提供给官方六个时间核。无力且不足10mm离地的模糊近地状态禁止gait，避免把高频卸载当成摆动。

## 3. 阶段A物理与控制器验证

4环境、8秒自由浮动站立，无NaN/Inf和摔倒。最终根高约0.3403m，tilt约0.0077，四足法向力约16.45/16.56/20.48/21.10N，总和接近体重；有效接触持续超过6秒。12关节脉冲全部响应，最小变化约0.017rad。已知时钟的官方同步/反同步核方向断言、静止air/clearance为0、滑移惩罚非负以及动态奖励有限值检查均通过。详情physics_gate.json。

必须区分网络clip[-1,1]、目标位置软限位±2.826、驱动力10Nm与速度3rad/s。所有确定性评估目标未触及位置限位。ImplicitActuator的applied_torque/computed_torque是PD近似估计，不能当作实测电机力矩。另记录PhysX get_dof_projected_joint_forces的真实关节轴投影作用力；它也不等于纯电机驱动力，以下仅作力矩诊断。

|阶段|PhysX轴投影峰值 Nm|PD估计峰值 Nm|速度峰值 rad/s|
|---|---:|---:|---:|
"""
for label in labels:
 a=actuator[label];text+=f"|{label}|{a['projected_force_peak']:.3f}|{a['pd_estimate_peak']:.3f}|{a['joint_speed_peak']:.3f}|\n"
text+="""\n部分速度短暂越过3rad/s，应如实记录求解后读数，未擅自放宽上限。没有根据PD估计10Nm就宣称真实电机长期饱和。

## 4. NVIDIA Spot机制迁移

本机IsaacLab commit 37ddf626871758333d6ed89cf64ad702aef127d0已核验，官方源码未修改。优先阅读本机flat_env_cfg.py和mdp/rewards.py；[对应官方源码](https://github.com/isaac-sim/IsaacLab/blob/37ddf626871758333d6ed89cf64ad702aef127d0/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot/mdp/rewards.py)。

- GaitReward继承官方类，原样调用2个同步核和4个反同步核，LF/RR、RF/LR。修改接触时钟与显式索引，增加命令/几何门控。std=.025秒平方、max_err=.2秒、弱权重.35。仅平移>.15、|vx|>.10、|wz|<.35适用；静止、纯旋转和低速横移不强制Trot。没有预设完整关节轨迹。
- 防滑沿用官方支撑时水平速度范数之和，并非示意公式的平方。接触和速度替换为有效末端manifold和真实接触斑速度，不处罚正常摆动水平速度。
- Air time参考Spot时序，但改为摆动峰值>20mm、持续0.10～0.40秒并真正落地后奖励；短抖动、长悬腿和静止不获奖励。不是直接照搬Spot air_time_reward。
- Clearance用整膝最低碰撞表面、无整膝接触和摆动速度门控，纠正中心高度满足但表面拖地。
- 直接复用Spot action_smoothness_penalty，提高action_rate，并惩罚raw输出超过0.9的部分。动作尺度仍±0.25rad。B/C共同重置std=.35、entropy=.002、初始lr=.0003、重置优化器，从同一Stage2网络权重初始化。
- 保留RSL原始Gaussian采样与原始动作log_prob；clip只是环境执行映射，没有引入有界分布或错误的tanh概率公式。
- Stand still参考Spot默认关节偏差，加实际xy/yaw速度及关节速度项；移动指令关闭该项，避免直接压制运动。

六项独立开关均在spot_v2/config.py；B仅关闭gait，C开启六项。奖励权重独立配置，包含action_rate_weight、action_smoothness_weight、raw_saturation_weight。原任务注册与旧源码未改，新入口显式配置同一Gym任务。

## 5. 奖励权重与实际贡献

实际贡献为加权奖励率。旧Stage2取末10次episode归一化日志，新B/C取末10次rollout均值，采样分布不同，只作量级诊断。

|奖励|旧权重|B权重|C权重|旧贡献|B贡献|C贡献|
|---|---:|---:|---:|---:|---:|---:|
"""
weights={'track_lin_vel_xy_exp':(5,5,5),'track_ang_vel_z_exp':(2.5,2.5,2.5),'lin_vel_z_l2':(-1,-1,-1),'ang_vel_xy_l2':(-.08,-.08,-.08),'flat_orientation_l2':(-2.5,-2.5,-2.5),'dof_torques_l2':(-.0002,-.0002,-.0002),'dof_acc_l2':(-1e-7,-1e-7,-1e-7),'action_rate_l2':(-.005,-.02,-.02),'undesired_contacts':(-1,-1,-1),'dof_pos_limits':(-1,-1,-1),'stand_deviation':(-.15,-.4,-.4),'gait':(0,0,.35),'foot_air_time':(.2,.4,.4),'foot_clearance':(.15,.2,.2),'foot_slip':(0,-.6,-.6),'spot_smoothness':(0,-.06,-.06),'raw_saturation':(0,-.3,-.3)}
for term,w in weights.items():
 vals=[old.get('Episode_Reward/'+term,0.)]+[float(np.mean([x.get('contribution_'+term,0.) for x in metrics[s][-10:]])) for s in ['stage_b','stage_c']]
 text+=f"|{term}|{w[0]:g}|{w[1]:g}|{w[2]:g}|"+'|'.join(f'{v:.6g}' for v in vals)+'|\n'
text+="""\nC的gait贡献远小于速度跟踪，真正离地样本太少。不能放宽真实性判定把浅层抖动算作正常步态，也不能据此宣称Spot机制无效。

## 6. 两组实验与预算

"""
text+=f"新实验共{sum(x['completed_updates'] for x in budget['runs'])}次更新，累计训练wall time（含启动/初始化）{sum(x['seconds'] for x in budget['runs']):.2f}秒。smoke=5，B=150，C=150；剩余15未用。独立320次/1800秒账本，旧300次账本未改。B/C均seed42、256环境、24步rollout、相同checkpoint及优化器/std重置，仅gait不同。单种子短程结果不代表统计显著性。\n\n"
text+='|方向|目标vx/vy/wz|Stage2实测|B实测|C实测|摔倒 Stage2/B/C（各4次）|\n|---|---|---|---|---|---|\n'
for i in range(8):
 row=evals[0][i];fmt=lambda r:'/'.join(f'{x:+.3f}' for x in [*r['velocity'][:2],r['yaw']])
 text+=f"|{row['test']}|{'/'.join(str(x) for x in row['target'])}|{fmt(evals[0][i])}|{fmt(evals[1][i])}|{fmt(evals[2][i])}|{evals[0][i]['falls']}/{evals[1][i]['falls']}/{evals[2][i]['falls']}|\n"
text+='\n|指标（8方向均值）|Stage2|B|C|\n|---|---:|---:|---:|\n'
for key,name in [('linear_error','平移误差 m/s'),('yaw_error','yaw误差 rad/s'),('slip','有效支撑点滑速 m/s'),('clip','确定性输出裁剪比例'),('action_delta','限幅后动作变化均方'),('tilt','投影重力xy范数')]:
 text+='|'+name+'|'+'|'.join(f'{np.mean([r[key] for r in ev]):.4f}' for ev in evals)+'|\n'
text+="""\n固定评估每项6秒、4次相同初始条件、seed734、去掉首1秒；重复不是随机鲁棒性试验。摔倒后样本不参与速度统计。B/C左移速度0.58/0.64是倒下前失控运动，不能算成功。均4/32摔倒，超过基线0/32，未满足摔倒率目标。

前进支撑点滑速约0.257→0.143/0.141，但前进仍无>15mm摆动。C后退更快却带+0.306rad/s偏航。B/C斜向基本停住并持续抬一腿：离地比例0.25不是交替迈步。对角接触一致率可被浅层抖动或长期支撑抬高，只是代理量。

连续命令为前进→后退→左移→右转→斜向→静止，每段2秒。B在停止瞬态10.24～10.26秒摔倒，10.5秒后无存活样本，停止指标为null。同条件基线连续测试无摔倒，停止平移0.1203m/s、yaw0.1289rad/s。C无摔倒，停止窗口平移约0.0625m/s、yaw约0.0522rad/s，仍非完全停止。固定零指令平移：基线0.120、B0.052、C0.068m/s。

## 7. 训练曲线与诊断数据

reports/training_curves.png包含实际Reward、xy/yaw误差、滑移、裁剪和对角支撑代理曲线。baseline_final、evaluation_b、evaluation_c各包含：

- foot_contact_timeline.png
- foot_height_curves.png
- joint_action_diagnostics.png
- foot_slip_diagnostics.png

各diagnostics.npz完整保存四足整膝最低高度、帽区点高度、接触点、有效/整膝接触力、接触/腾空时间、足端/接触斑世界速度、12关节裁剪前后动作、目标/实际角度、速度、PD估计及PhysX轴投影力、根部速度位置和目标命令。gait_metrics.json保存每腿接触段时长、离地比例、落脚数与周期自相关代理；持续悬腿或高速浅抖不能以代理值证明正常步态。comparison.csv/json及逐更新metrics/TensorBoard均保留。

42项回归通过，三个最终checkpoint全部保存张量有限。B初次汇总把自动reset后的再次摔倒累计成20，权威summary_validated.json按初始trial计为4/4；原数据未删。原continuous_stop空集合统计产生NaN，已给出continuous_stop_validated.json的null；不是物理状态NaN。所有物理时序有限。图表和gait_metrics已排除首次摔倒后的自动reset样本，避免把重复倒地误画成周期步态。

## 8. 实际运动视频

三段主视频相同相机、seed、站姿、每方向4秒、总32秒、25fps、960×720；独立reset，标注目标/实际速度与真实支撑状态。均为实际PhysX仿真，没有根部运动注入。接触调试另附12.16秒视频。

"""
for stage in ['baseline','stage_b','stage_c']:
 text+=f"- {stage}: {E/'videos'/stage/'all_directions.mp4'}\n"
text+=f"- 接触调试（真实膝凸包橙色线框、接触斑绿色法向力标记，无物理作用）: {E/'videos/contact_debug_v2/all_directions.mp4'}\n"
text+="""\n## 9. 最终判断与建议

1. **尚未形成正常步态。** 长期支撑、25Hz高频抖动、单腿悬空仍存在，不能把目标vx或一腿抬起称作正常行走。
2. **防滑和动作控制部分有效。** 前进滑移、平均裁剪与动作突变下降，右移/右转及固定零速改善；左移摔倒和斜向退化不可忽略。
3. **GaitReward成效尚未验证。** 官方核和真实时钟已验证，但真正摆动样本太少、实际贡献低。C比B的局部速度改善不能证明Trot形成。
4. **不建议直接长训练。** 先比较平滑/限速关节目标生成对高频反馈循环的影响；重新以碰撞表面校准reset高度（root=.355的默认站姿约2.6mm穿地），检查瞬态；有依据地比较弯膝站姿。不要随意修改惯量、放大动作范围或盲目提高gait。
5. 在新预算中先解决左移倾倒及斜向一腿悬空的吸引态；针对air/clearance贡献近零，先建立真实摆动样本，再验证gait门控范围与权重。
6. 当前几何分类是平地保守代理。若推进复杂地形，应进一步评估独立足底碰撞表示，同时验证固定连接导入、质量/惯量和小腿接触。没有证据表明原模型根本不能迈步，但本轮没有学会。

## 10. 工程保护与复现

环境仍为Isaac Sim5.1.0、IsaacLab2.3.2、RSL-RL3.1.2，PPO、12维关节位置动作、3维速度指令。没有升级/安装依赖、修改原URDF或官方源码、覆盖旧checkpoint/视频/预算。保护核验见protection/integrity_after.json。训练用源码另以SHA验证备份在protection/training_sources；训练后仅将相同默认权重暴露为配置项、增加独立实验路径/可选settings文件参数，见post_training_changes.json。

新增代码仅在src/dogfight/locomotion/spot_v2和新增scripts入口，没有建立兼容源码树或重写PPO。许可证沿用上层NVIDIA BSD全文和官方引用。全部失败/修复日志、设置快照、seed、checkpoint SHA、预算、原始时序和视频provenance保留。

入口为scripts/diagnostics/csdog_spot_gate.py、scripts/train/csdog_spot_v2.py、scripts/evaluate/csdog_spot_v2.py。训练可用--settings传入JSON独立权重与开关；显式指定--stage smoke/stage_b/stage_c、--iterations 5/150/150、--num-envs 32/256/256；评估显式指定--checkpoint、--output-dir，新策略加--improved。解释器为/home/zxq/miniconda3/envs/dogfight/bin/python。已存在输出会拒绝覆盖；再现实验在物理门禁和训练入口均指定--experiment-dir runs/locomotion/NEW_RUN，使用独立目录/新预算，不解锁本次或旧预算。没有后台训练继续运行。
"""
(O/'SPOT_LOCOMOTION_IMPROVEMENT_REPORT.md').write_text(text)
print(O/'SPOT_LOCOMOTION_IMPROVEMENT_REPORT.md')
