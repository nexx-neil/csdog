"""Assemble the aligned experiment report from actual immutable measurements."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';O=E/'reports'
def read(p):return json.loads(p.read_text())
labels=['Stage2 common','V2-B common','V2-C common','V3-120','V3-220']
folders=['comparison_stage2','comparison_v2_b','comparison_v2_c','evaluation_first','evaluation_second'];ev=[]
for folder in folders:
 d=np.load(E/folder/'diagnostics.npz');rows=read(E/folder/'summary.json')
 for i,row in enumerate(rows):
  sl=slice(i*4,(i+1)*4);valid=d['valid'][:,sl]&(d['t'][:,None]>=1.)
  row['height_max']=d['foot_height'][:,sl][valid].max(0).tolist() if valid.any() else None
  row['valid_samples']=int(valid.sum());row['falls']=int(d['fall'][:,sl].any(0).sum())
 (E/folder/'summary_validated.json').write_text(json.dumps(rows,indent=2,allow_nan=False));ev.append(rows)
comparison=[dict(policy=label,**row) for label,rows in zip(labels,ev) for row in rows]
(O/'comparison.json').write_text(json.dumps(comparison,indent=2,allow_nan=False))
with (O/'comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(comparison[0]));w.writeheader();w.writerows(comparison)
metrics={s:[json.loads(x) for x in (E/s/'metrics.jsonl').read_text().splitlines()] for s in ['first','second']}
budget=read(E/'training_budget.json');gate=read(O/'physics_gate.json');fixture=read(E/'fixture/summary_validated.json');zero=read(O/'zero_command_reward_diagnosis.json')
total=sum(x['completed_updates'] for x in budget['runs']);seconds=sum(x['seconds'] for x in budget['runs'])
text=f"""# SPOT_ALIGNMENT_EXPERIMENT_REPORT

日期：2026-10-26。实验目录：{E}

**实际完成官方配置审查、动态驱动/接触诊断、独立48维任务、5次smoke、从头120次训练、评估后唯一一次两类调整及100次续训，共{total}/230次更新、训练运行{seconds:.2f}秒。出现约3Hz的单腿真实摆动和前进能力，但仍不是正常四足交替步态，零速漂移和方向控制不合格。暂不建议500～1500次长训练；没有启动长训练。**

本轮没有完全修复承载/平衡问题。500Hz下基础站立和夹具驱动通过，浮动开环抬腿未通过。不能把基础物理门禁写成完整步态动力学通过。

## 1. NVIDIA官方对齐情况

本机IsaacLab commit 37ddf626871758333d6ed89cf64ad702aef127d0；读取Spot flat_env_cfg.py、agents/rsl_rl_ppo_cfg.py、mdp/rewards.py、isaaclab_assets/robots/spot.py。逐项原文AST、行号和SHA在official_source_audit.json；[官方固定版本配置](https://github.com/isaac-sim/IsaacLab/tree/37ddf626871758333d6ed89cf64ad702aef127d0/source/isaaclab_tasks/isaaclab_tasks/manager_based/locomotion/velocity/config/spot)。

完整A/B/C/D对齐表：SPOT_CONFIGURATION_COMPARISON.md。独立任务Dogfight-CSDog-Spot-Aligned-Flat-v3，不覆盖原任务。主要完全对齐：

- Actor和Critic均512/256/128、ELU，不启用观测归一化。
- Actor/Critic均48维，顺序为机身系线速度3、角速度3、投影重力3、机身速度命令3、显式LF/RF/LR/RR每腿1/2/3关节偏移12、关节速度12、上次动作12。全部scale1，定义的噪声实际enable_corruption=False。
- 500Hz物理、decimation10、50Hz策略、20秒episode、10秒保持的Uniform命令、10%静止命令。
- 官方PPO：24步rollout、5epochs、4minibatches、clip .2、初始lr .001自适应、gamma .99、lam .95、value_loss .5、clipped value、entropy .0025、desired_KL .01、grad_norm1、初始每关节std1。
- 12维关节位置动作、scale .2、wrapper不裁剪，与官方clip_actions=None一致。高斯采样和log_prob全部使用原RSL；没有另写PPO，也没有错误的有界分布变换。
- 完整SpotRewardsCfg作为基线，不再用ANYmal奖励再零散叠加。

仍需保留差异：7.6kg模型的质量/几何/关节映射和13刚体、无独立foot、无实测膝传动表、10Nm/3rad/s、Kp25/Kd.8、延迟未知故设0；低速命令±.35/±.22/±.5；尺寸缩放的跟踪std和足高；gait权重2及平移门控；V2运动学箱体地面与摩擦.8/.7；轻量reset；自碰撞False、求解器8/2；保留base接触和倾倒终止，关闭官方大幅质量/摩擦/reset速度/push随机化。本轮简单平地，不复制SpotFlat实际使用的起伏地形，更不复制官方20000次训练默认值。

唯一优化轮将std重置.4、smoothness权重改-.2，属于有记录的偏离，不宣称最终策略所有超参数仍完全官方。

## 2. 旧实验复审与问题定位

已读取两份旧报告、Stage1/2和V2-B/C的agent/env/settings、指标时序、足部诊断与视频资料。沿用此前结论，未无意义重跑200Hz原始诊断：

- Stage2以约25Hz浅层接触抖动、拖滑获得前进；Actor无直接线速度，clip1压缩不同命令的有效目标。
- V2防滑/平滑降低了滑移和裁剪，却仍缺真实摆动，斜向常停住并长悬一腿。gait奖励贡献低，不能把布尔对角一致率当作Trot。
- 摔倒增加不能简单归因于GaitReward：V2-B没有gait也在原评估左移4/4摔倒，C同样4/4。基础防滑/动作/静止约束改变与载荷/策略分布同样相关；单种子没有独立因果证据。
- 本轮Actor加线速度、网络扩大和频率/驱动改变后，第一轮仍学成静止；说明网络容量或观测缺项并不是全部根因。

## 3. 动力学、电机及接触检查

### 实际测试范围

未使用PPO进行12关节逐个0.15rad阶跃、四腿高度调整、四条腿分别主动抬起和前后摆动、协调小幅运动、8N持续0.1秒真实侧向力扰动恢复。另测试有支撑位移的抬腿、较大回收、Kp25/50/75和Kd.2/.4/.8的独立敏感性，始终保留10Nm/3rad/s。原URDF、质量和惯量没改，没有宣称任何更大硬件额定参数。

基础站立无摔倒、无NaN/Inf，四足法向力总和{gate['standing_force']:.3f}N，质量{gate['mass']:.7f}kg，与重力一致。20ms策略采样之外另记录2ms物理子步，降低Kd未解决问题，没有证据支持靠增加电机上限修复。

**负载限制必须保留：** 无平衡反馈的浮动IK抬腿中，身体下沉/倾斜，支撑关节偏离目标约0.1～0.4rad，转矩裁剪可达约5%～10%；主动脚仍在地面。增加刚度、降低阻尼以及由静态支撑转矩标定的等效servo偏置没有可靠改善，全部未采纳到训练配置。仅有三腿支撑位移的参考也没有修复这个问题，较大回收还会摔倒/速度越限。

固定基座夹具只用于隔离电机和运动学：四腿实际抬升约48mm，跟踪RMSE {fixture['target_tracking_rmse']:.5f}rad，转矩峰值{fixture['torque_peak']:.3f}Nm。不是浮动行走视频，不参与PPO成绩。原绝对FK诊断遗漏环境网格平移，旧记录保留；用夹具中无根运动的足端位移独立交叉验证，最大误差{max(fixture['fk_displacement_errors_m']):.3g}m，见fixture/summary_validated.json。关节可动、FK正确，但不证明负载下必然迈步。PPO优化轮随后确实在浮动模型学到一条腿离地，说明不存在全局关节锁死；全身承载协调仍未解决。

基础门禁scope明确写在physics_gate.json：站立、接触、48维观测、奖励有限、无负载驱动通过；unassisted_floating_lift_passed=False。没有将失败检测改写成成功。dynamic_controller_diagnostics.png、各dynamics/unload/pd_probe/kp_probe目录保留完整目标、实际q、误差、转矩、速度、力和失败记录。

### 驱动信号含义

官方Spot髋部是45Nm DelayedPD 60/1.5、0～4个物理步延迟，膝为实测传动曲线RemotizedPD。CSDog无对应实测数据，因此只采用零延迟显式PD25/.8及原10Nm/3rad/s。不能把Spot曲线套到直接驱动腿。

显式PD的applied_torque是写入PhysX的实际指令转矩，可统计指令饱和；另存PhysX轴投影关节作用力，两者意义不同。旧隐式applied_torque只是近似估计，原生历史数值不能直接与新真实指令转矩比较。统一比较下所有策略用相同显式驱动，避免混淆。

网络输出裁剪、目标位置限位、转矩限幅、速度限幅分开记录。无wrapper clip不等于神经网络输出已变小，最终raw常超过±1。实际速度可有数值越限，不能把配置3rad/s写成每帧严格满足3。

### 接触可信度

复用V2四个单体ContactSensor对固定运动学箱体地面的真实manifold；静态平面GPU筛选限制没有被忽略。按距帽区中心35mm和地面位置保守分区，混合胫部接触/溢出否决。足端与接触斑速度均在世界系用v_COM+omega×r，最低表面高度由整膝STL凸包计算。原碰撞几何不改，没有新增机器人质量或隐形足垫。

分类是保守代理，不能声称有独立foot触觉；Python有效接触时钟仍50Hz/20ms，不因物理500Hz就声称时钟500Hz。gait几何可信门限5mm与最终严格摆动>15mm分开。不能用接触力瞬间低于阈值直接证明正常摆腿。

## 4. 奖励实现与实际贡献

详见SPOT_REWARD_ALIGNMENT.md：14个Spot条目全部接入。速度/机身/关节/动作函数直接用官方实现；脚部时间、高度、滑移以及Gait输入按上述真实结构适配。源码joint_acc/joint_vel虽然传入髋关节asset_cfg，函数实际未索引joint_ids，V3保留全12关节的实际官方行为并披露。Gait是六核相乘，尚需可信离地模式；末期命令适用覆盖约40%、几何模式可信覆盖约73%，两者交集没有单独记录，不能把边际比例相乘当精确覆盖率。实际gait贡献约0.1，相对速度奖励合计约5偏小；静止/滑动吸引态与支撑负载问题仍存在。本轮没有V3同预算无gait消融，不能将局部改善单独归因于gait。

速度权重5/5，std .25/.5；gait2、std .1、max_err .2，仅合适平移启用，纯转向/低速横移/静止不强迫Trot；air_time dense模式5、mode .25；clearance .5、target .03/std .0045/tanh2；slip-.5；air variance-1；base motion-2/orientation-3；joint pos-.7、stand scale5、threshold .1；joint vel-.01、acc-1e-4、torque-5e-4。

首轮smoothness实际约-3.3，和线/yaw奖励合计约+5相比很重。优化只改std .4与smoothness-.2，未改gait/驱动/接触/动作尺度/指令分布。Reward由约17升至约97不能解读为性能提高数倍：奖励权重变了，主要依赖独立物理评估。

**实测静止漏洞：** 官方joint_position_penalty在body速度超过阈值后，即使指令为0，也不再使用5倍静止系数。V3将阈值缩为.1，优化轮零命令有{zero['220 updates']['fraction_escaping_stand_multiplier']*100:.1f}%稳态样本越过它。记录状态上的真实关节惩罚均值约{zero['220 updates']['actual_joint_pos_penalty']:.3f}，若保持5倍则约{zero['220 updates']['hypothetical_command_only_penalty']:.3f}。后者是离线代数，不是新仿真或因果消融。该条件可能奖励持续漂移以规避静止约束，不能只归咎于训练太短；下一轮应先改为零命令保持静止倍率或做清晰迟滞。本轮两类调整已用完，未偷偷再改奖励和续训。图见zero_command_reward_mask.png。

## 5. 短程训练与检查点

"""
text+='|阶段|起点|环境数|新增更新|累计主策略更新|运行秒数|\n|---|---|---:|---:|---:|---:|\n'
for row in budget['runs']:
 stage=row['name'];text+=f"|{stage}|{'随机初始化' if stage!='second' else 'first/final.pt兼容恢复'}|{32 if stage=='smoke' else 256}|{row['completed_updates']}|{220 if stage=='second' else 120 if stage=='first' else 5}|{row['seconds']:.2f}|\n"
text+=f"""
累计训练运行{seconds:.2f}秒，含App启动/环境初始化；物理诊断、评估和录像另计，没有PPO更新。主策略从头120+100=220次，smoke5次另算，累计{total}/230次，预留5未使用。seed42；每30次实际完成更新保存update_0030/0060/0090/0120，最终保存final.pt。没有0基下标误计，旧Stage2/V2从未加载到48维新网络。TensorBoard、metrics、env/agent YAML、identity、来源SHA、参数更新记录均保留。

smoke真实更新、checkpoint有限、48维顺序/坐标检查通过；45项回归通过。预算同时限制阶段5/120/100/5、总230和1200秒，并用文件锁/独立账本/SIGALRM保护，旧预算未解锁。

## 6. 视频与稳态步态质量

四种策略用统一脚本csdog_spot_aligned_v3.py、相同seed734、默认姿态/root=.36、500Hz/50Hz、显式PD25/.8、10Nm/3rad/s、地面摩擦.8/.7。网络和观测按各策略原生合同重建：旧45维/128网络/clip1/scale.25，新48维/512网络/无clip/scale.2，绝不强塞不兼容checkpoint。命令为静止、±.3m/s前后、±.2m/s横向、±.4rad/s旋转、(.2,.1)斜向；每项6秒、4次重复，去掉首1秒，首次摔倒后排除。重复条件相同不是随机鲁棒性结论。另有12秒连续变向→停止。

优化轮前进vx约0.254、vy约+0.068，平面速度跟踪误差约0.119m/s；支撑滑速约0.155m/s。均值摆动占比约6.3%，但不能据此宣称四腿学会走路：

- 一条代表性trial去掉起步首秒，LF/RF/LR/RR真实最低表面峰值约11.8/15.6/32.6/7.2mm。
- 第一条代表性trial中稳态真实摆动比例约0/0.4%/24%/0，主要左后腿反复摆动，单次约0.06～0.10秒。
- 膝动作主频约3Hz，和旧25Hz浅抖相比出现了较慢、真实的单腿抬升；其他三腿大量低抬升/拖滑。对角布尔一致率约0.54仍是代理，不能证明两对对角足协调。
- 早期汇总height_max包含起步瞬态，曾显示四腿都超过15mm。最终summary_validated.json和gait_quality_detail.json统一去掉首秒，明确纠正这个描述，不把瞬态当成稳态步态。
- 没有足够依据把根部有效位移拆分为“迈步百分比/滑移百分比”，这里只报告足端和支撑滑速代理，视频辅助判断。

最终零命令速度约0.196m/s，较首轮0.004明显恶化。前进/斜向有早期能力，但后退只约-.033m/s、右移方向仍错误、左/右转约+.074/-.098rad/s并夹杂平移。固定测试本次两轮均0/32摔倒，仅是短程样本。

## 7. 与旧版本统一条件对照

**下表是新500Hz显式驱动共同测试平台，不是旧策略原生200Hz隐式驱动成绩。** 更换物理驱动导致分布偏移，旧策略明显退化，不能据此声称新网络/算法优于旧策略。旧主策略约296次，V2-B/C各在其基础上150次（各约446次），V3仅120/220次；训练预算也不相等，无法作因果优劣结论。

"""
def mean(rows,key):
 vals=[r[key] for r in rows if r[key] is not None];return float(np.mean(vals)) if vals else None
text+='|指标（统一平台）|'+'|'.join(labels)+'|\n|---|'+'---:|'*5+'\n'
for title,func in [
 ('前进平移误差 m/s',lambda r:r[1]['linear_error']),('后退平移误差 m/s',lambda r:r[2]['linear_error']),
 ('左右横移平均误差 m/s',lambda r:mean([r[3],r[4]],'linear_error')),('左右旋转平均yaw误差 rad/s',lambda r:mean([r[5],r[6]],'yaw_error')),
 ('平均支撑滑速 m/s',lambda r:mean(r,'slip')),('真实摆动比例',lambda r:mean(r,'air_fraction')),
 ('对角支撑代理',lambda r:mean(r,'diagonal_support')),('实际wrapper裁剪比例',lambda r:mean(r,'clip')),
 ('raw超过±1比例',lambda r:mean(r,'raw_outside_unit_fraction')),('电机指令转矩饱和比例',lambda r:mean(r,'torque_limit')),
 ('零指令平移误差 m/s',lambda r:r[0]['linear_error'])]:
 vals=[func(rows) for rows in ev];text+='|'+title+'|'+'|'.join(f'{x:.4f}' if x is not None else '无存活样本' for x in vals)+'|\n'
text+='|摔倒/32|'+'|'.join(f"{sum(x['falls'] for x in rows)}/32" for rows in ev)+'|\n'
text+='\n逐方向实际vx/vy/wz：\n\n|方向|'+'|'.join(labels)+'|\n|---|'+'---|'*5+'\n'
for i,name in enumerate(['stop','forward','backward','left','right','left_turn','right_turn','diagonal']):
 def fmt(r):return '/'.join(f'{x:+.3f}' for x in [*r['velocity'][:2],r['yaw']]) if r['velocity'] is not None else '无存活样本'
 text+='|'+name+'|'+'|'.join(fmt(rows[i]) for rows in ev)+'|\n'
text+='\n原生历史条件参考（不混入统一平台排名）：\n\n|策略/原生物理|前进vx m/s|零速漂移 m/s|摔倒/32|\n|---|---:|---:|---:|\n'
native_paths=[R/'runs/locomotion/csdog_ppo_spot_v2/baseline_final/summary.json',R/'runs/locomotion/csdog_ppo_spot_v2/evaluation_b/summary_validated.json',R/'runs/locomotion/csdog_ppo_spot_v2/evaluation_c/summary.json']
for label,p in zip(['Stage2 /200Hz隐式','V2-B /200Hz隐式','V2-C /200Hz隐式'],native_paths):
 rows=read(p);text+=f"|{label}|{rows[1]['velocity'][0]:.3f}|{rows[0]['linear_error']:.3f}|{sum(r['falls'] for r in rows)}/32|\n"
text+="""\n原生旧策略能更快前进，但存在拖腿；共同驱动平台下旧策略失效不代表此前速度是伪造。模型/驱动改变与网络、观测、奖励一起变化，本轮是系统验证，非单因素消融。新版本实际clip=0由取消wrapper裁剪定义造成，不是证明raw输出学得更温和；应结合raw越界、目标/转矩/速度和步态判断。

连续停止与完整逐方向指标见各continuous_stop.json、comparison.csv/json；空存活集合记null，不伪造停止成功。

## 8. 数据、曲线、视频绝对路径

每个evaluation/comparison目录均有foot_contact_timeline.png、foot_height_curves.png、action_saturation.png、velocity_tracking.png、gait_metrics.json和完整diagnostics.npz。首次摔倒后的样本不画成步态周期。reports/training_curves.png记录Reward/速度误差/Gait/滑移/离地/std/转矩饱和；dynamic_controller_diagnostics.png与zero_command_reward_mask.png解释根因。

所有主视频相同相机、960×720、25fps、8方向各4秒、32秒总长，显示阶段、目标/实际速度、支撑状态和地面参考。画面来自实际浮动PhysX策略执行，没有直接移动根节点制造运动。夹具数据有明确标签，不混入这些视频。

"""
for name in ['stage2','v2_b','v2_c','first','second']:
 text+=f"- {name}: {E/'videos'/name/'all_directions.mp4'}\n"
text+=f"- V3最终2倍慢放: {E/'videos/second/all_directions_slow2x.mp4'}\n"
text+="""\n每个新的唯一checkpoint策略都有可视评估：smoke和中间30/60/90更新用4秒前进→停止短片，两个主阶段final用完整32秒视频。first/update_0120.pt与first/final.pt模型张量相同，共享已核验同策略视频，不伪称不同策略。checkpoint_visualization_manifest.json记录每个checkpoint、实际模型digest和视频映射；checkpoint_validation.json记录全部保存张量有限性。慢放只改变实际录像时间轴，不生成动作或新仿真状态。

## 9. 下一阶段建议

- 当前浮动模型基本站立、接触和无负载关节动作可信，PPO也确实能学到左后腿抬起，模型不是完全不能动。但加载支撑误差、转矩限制和全身协调仍未解决，不能宣称动力学问题已修复。
- PPO有有效早期学习迹象：优化轮由静止到前进/斜向、动作主频降低到约3Hz并产生真实单腿摆动。但没有形成正常四足交替，支撑滑移仍高，方向/停止严重不足。
- Spot对齐纠正了观测、网络、输出裁剪定义、仿真频率和奖励体系；没有自动解决载荷与策略吸引态。不能用Reward上升掩盖零速和后退失败。
- 明显奖励风险已发现：零指令通过漂移越过速度阈值可规避5倍站姿惩罚；dense air-time也可能奖励浅层接触切换，gait布尔协调代理可能被部分脚短促卸载抬高。先修复这些条件，并继续采用真实几何/接触验证。
- **目前不建议直接500～1500次训练。** 下一轮先用独立短预算检查零指令倍率/迟滞、负载下多腿支撑与足端空间、合适站姿及必要的目标变化约束；不要盲目增加电机额定值或放大动作范围。只有四腿真实摆动、停止与方向验收出现稳定改善后，再评估500～1500次的价值。本轮绝不执行它。

## 10. 工程保护与可复现性

不修改Isaac Sim5.1.0、IsaacLab2.3.2、RSL-RL3.1.2，不安装/升级核心依赖；PPO库和官方源码不改。原URDF、STL、USD质量/惯量、旧Stage2/V2全部checkpoint、评估、视频和两本旧预算完整保留，SHA核验见protection/integrity_after.json。

权威新源码在src/dogfight/locomotion/spot_aligned_v3；新增train/evaluate/diagnostic入口独立命名。共享V2接触实现只读复用，没有复制兼容源码树。V3配置快照、seed42、每次源文件SHA、唯一调整差异和失败诊断均保留。包含的calibration.py仅是失败候选的证据，默认训练不导入它。

训练入口scripts/train/csdog_spot_aligned_v3.py显式要求stage/iterations，默认根目录本实验且拒绝覆盖已存在输出；--experiment-dir可指定新的csdog_ppo_spot_aligned_v3前缀独立实验，仍需该目录自己的门禁；不可将旧45维策略强行加载到48维新任务。评估入口scripts/evaluate/csdog_spot_aligned_v3.py按--kind stage2/v2/v3重建各网络，使用相同共同平台。训练用源版本以SHA核验保存在protection/training_source_versions，之后仅增加独立实验路径参数，未改变本次训练数学或默认配置。所有剩余工作均为只读分析和录像，无训练进程继续运行。
"""
(O/'SPOT_ALIGNMENT_EXPERIMENT_REPORT.md').write_text(text)
print(O/'SPOT_ALIGNMENT_EXPERIMENT_REPORT.md')
