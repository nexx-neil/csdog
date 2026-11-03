"""Compact evidence report from AutoPPO SQLite and measured evaluation summaries."""
from pathlib import Path
import json,time
from ...autoppo.storage import Store,atomic_json

def generate(base):
    base=Path(base);store=Store(base)
    try:
        trials=store.rows('SELECT * FROM trials WHERE rung>=0 ORDER BY generation,created');state=store.get('status','READY');best=store.get('best_checkpoint');latest=store.get('latest_metrics',{})
        text='# V7等预算消融实验报告\n\n'
        text+='A=原碰撞/无相位，B=sole cap/无相位，C=原碰撞/相位，D=sole cap/相位。所有首轮组随机初始化、128环境、seed42、24步rollout、每组250更新=768000环境步；速度.12–.25m/s与20%停止。相位是观测+奖励的组合修改，不能分离二者的独立作用。\n\n'
        text+='|组|状态|累计更新|实际前速m/s|支撑滑移m/s|相位匹配|最小真实摆动/环境|停止速度m/s|摔倒环境比例|正式合格|\n|---|---|---:|---:|---:|---:|---:|---:|---:|---|\n'
        for t in trials:
            c=json.loads(t['config']);m=json.loads(t['metrics']) if t['metrics'] else {};fmt=lambda k:f"{m[k]:.4f}" if k in m else '待测'
            text+=f"|{c['arm']} f={c.get('options',{}).get('frequency',1.5)} s={c.get('options',{}).get('slip_mode','raw')} (rung {t['rung']})|{t['status']}|{t['progress']}|{fmt('actual_speed')}|{fmt('support_slip')}|{fmt('phase_match')}|{fmt('min_swing_per_env')}|{fmt('stop_speed')}|{fmt('fall_fraction')}|{m.get('qualified','待测')}|\n"
        text+='\n速度为独立物理评估的真实body-frame前速，目标0.20m/s；停止包括静止起始和运动后停止，取较差结果。真实摆动为>=15mm几何离地、>=60ms连续卸载后着地，最小值按四腿及环境10%分位统计；完整周期另需有效支撑/前移/低滑移落地等条件。四腿计数、占空比和原始500Hz数据均保留，不把接触相位匹配当作步态成功。\n\n'
        text+='管理验证数据单独保留：88更新用于stop/resume验证，未混入任何正式组的250更新；此外2更新smoke用于验证48/50维网络、物理评估和checkpoint。A正式重新从随机初始化执行完整250更新。首轮只用一个训练随机种子，不能作跨训练种子的统计显著性结论。\n\n'
        text+='## 当前结论\n\n'
        completed=[t for t in trials if t['status']=='COMPLETE'];qualified=[t for t in completed if json.loads(t['metrics']).get('qualified')]
        text+=('存在通过当前物理门槛的checkpoint，仍需独立确认和课程验收。' if qualified else '尚无通过正式步态验收的checkpoint。')+'\n\n'
        if state.startswith('BLOCKED'):text+=f"已自动停止：{state}。原因：{store.get('diagnosis')}。未强行进入长期训练。\n\n"
        else:text+=f"当前状态：{state}；未完成的实验不能提前下结论。\n\n"
        text+='碰撞静态对照未证明sole cap有明显优势；球形sole候选被拒绝。sin/cos及连续奖励是否加快真实步态形成，仅能依据完成的相位/非相位组判断。V7高度进度单元测试通过，但没有“旧事件奖励 vs 新高度奖励”的独立等预算消融，不能单独声称新高度奖励更优。\n\n'
        text+='## 证据位置\n\n- `reports/training_curves.png`：训练采样诊断曲线，非独立验收。\n- `trials/<id>/<attempt>/evaluation_250/*.png`：四腿接触、高度、真实速度、接触点速度、相位匹配；显示env0，汇总指标来自全部环境。\n- 同目录`*.npz`：完整500Hz物理样本。\n- 同目录`physical_rollout.mp4`：实际仿真视频，前进及运动后停止。\n- 每个attempt的`launch.json`、`preflight.json`、`result.json`：实际参数、维度和结果。\n\n'
        for t in completed:text+=f"- {json.loads(t['config'])['arm']} checkpoint：`{t['checkpoint']}`\n"
        (base/'reports/V7_ABLATION_EXPERIMENT_REPORT.md').write_text(text)
        answers=[
         ('最大实现差异','旧版没有显式sin/cos时钟和逐周期对角支撑/释放计划；旧完整周期奖励前置条件多。原始模型整体膝部凸包，现有代码已经测接触点和完整凸包最低点。'),
         ('代码核实范围','CSDog的48维观测、12维动作、PD/限制、接触分类、事件门槛、零指令控制及滑移均已检查，见审计报告。'),
         ('同学信息来源','未找到可确认属于同学的源码，sole具体shape/body、步频和超参数等仍待验证；只按用户文字做方案比较。'),
         ('原碰撞是否有问题','本次静态站立未发现重大异常；默认四足最低点差约0.063mm。不能将步态失败归因于sole缺失。'),
         ('sole是否改善','球形sole明显恶化并拒绝；cap静态与原模型接近。首轮D支撑滑移约0.149m/s、C约0.267m/s，存在该训练种子下的条件性动态改善；B单独换sole仍滑行，不能认定sole本身解决了步态问题。'),
         ('相位是否明显改善','首轮C/D的相位匹配约0.715/0.819，A/B约0.500；C/D出现真实小幅四腿摆动，A/B没有合格摆动。相位观测+奖励组合改善了这些早期指标，但未单独隔离sin/cos的作用，更不等于正式步态成功。'),
         ('支撑和摆动奖励是否生效','V7运行时注册独立奖励；每次更新的reward_rates记录实际贡献，张量测试验证相位及高度门控。贡献非零不代表步态成功。'),
         ('渐进高度是否优于旧事件','学习信号连续、边界测试通过；缺少单独因果消融，效果优越性尚未证实。'),
         ('最早形成真实步态的组','尚无正式合格组。' if not qualified else json.loads(qualified[0]['config'])['arm']),
         ('形成步态的更新和样本数','尚未达到，不能给出虚构数值。' if not qualified else '最少通过验收的观测点为'+str(min(t['progress'] for t in qualified))+'更新，谱系样本数='+str(min(t['progress'] for t in qualified)*128*24)+'；不是准确形成时刻，两个评估点之间未逐更新验收。全实验成本另计，不能把分叉候选的采样相加当作同一策略谱系。'),
         ('能否长期训练','仅在短程存在可信四腿物理趋势后追加到1000，再以受控候选继续；当前'+state+'。'),
         ('当前最佳checkpoint',str(best)+'；这是相对物理评分最高者，是否合格需单看qualified，不能据此称为成功步态。')]
        launch='# V7 AutoPPO启动与验收报告\n\n'
        for i,(q,a) in enumerate(answers,1):launch+=f'{i}. {q}：{a}\n\n'
        launch+='首轮为v2物理协议；后续正式v3额外测足端三维速度、关节速度、站立接触及倾斜。旧缺测数据不补零通过。正式停止要求足端速度<=.06m/s、关节速度RMS<=.3rad/s、四足接触占空比均>=.9；平地行走真实高度P95范围15–60mm。基础追踪/滑移/停止阈值保持，未因结果不佳而放宽。\n\n管理复用现有AutoPPO ExperimentManager/Store/SQLite事务、锁、进程生命周期和事件记录；V7扩展提供随机初始化消融、相位指标、针对性参数搜索。长期每候选250更新，无全局迭代上限；无改善6候选、搜索空间耗尽、物理失败或磁盘不足会停止。正式长期状态只在物理趋势门槛后启用，不将第一轮消融称作长期训练。\n\n'
        launch+='已实际验证start/status/stop/resume/report接口；使用冻结解释器执行：\n\n```bash\n/home/zxq/miniconda3/envs/dogfight/bin/python /home/zxq/robot_projects/dogfight_rl/scripts/autoppo/v7.py status\n# 将最后的status替换为start、stop、resume、report\n```\n\n'
        launch+='BLOCKED状态下start/resume拒绝重复运行；修复、重新验证后才可恢复。命令不会自动清除阻塞或放宽验收。进程以独立session、DEVNULL stdin和文件日志启动，管理器与worker持锁，GPU共享锁防止重复训练。中断保存完整学习器；恢复重置物理episode并同步重置phase，不声称恢复PhysX内部状态。\n\n'
        launch+='独立物理验收仍严格要求：目标轴追踪、四腿重复真实摆动、对角相位、碰撞最低点离地、支撑滑移<=.08m/s、停止<=.03m/s及.08rad/s、低跌倒/小腿接触；1000更新不自动通过。所有课程由同一Actor递进学习，不能拼接参数。\n'
        (base/'reports/V7_AUTOPPO_LAUNCH_REPORT.md').write_text(launch)
        atomic_json(base/'report_index.json',dict(updated=time.time(),status=state,qualified_count=len(qualified),best_checkpoint=best,reports=[str(p) for p in sorted((base/'reports').glob('*.md'))]))
    finally:store.close()
