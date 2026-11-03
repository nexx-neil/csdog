"""Compare matched arms, enforce continuation gate, and write the auditable report."""
from pathlib import Path
import hashlib,json,sys
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
LEGS=['LF','RF','LR','RR']
def run_dir(arm):return BASE/('ab_A_verified2' if arm=='A' else 'ab_B')

def load(arm,n):return json.loads((run_dir(arm)/f'eval_{n:06d}'/'summary.json').read_text())
def panel(arm,n):return json.loads((run_dir(arm)/f'eval_{n:06d}'/'evaluation_common.json').read_text())

def main():
    launches={arm:json.loads((run_dir(arm)/'launch.json').read_text()) for arm in ['A','B']}
    assert launches['A']['source_sha256']==launches['B']['source_sha256']
    for arm in ['A','B']:
        launch=launches[arm]
        assert launch['budget']==300 and launch['start_update']==2500 and launch['num_envs']==256 and launch['seed']==42
        assert launch['policy_exact'] and launch['optimizer_exact'] and launch['initial_lr']==.0001
        assert sum(1 for _ in (run_dir(arm)/'metrics.jsonl').open())==300
        assert (run_dir(arm)/'final.pt').is_file() and (run_dir(arm)/'final_gait.mp4').stat().st_size>10000
    table=[]
    for arm in ['A','B']:
        for n in [0,50,100,200,300,301]:
            m=load(arm,n);m.update(arm=arm,additional_updates='300（独立种子）' if n==301 else n);table.append(m)
    b0=load('B',0);a300=load('A',300);b300=load('B',300);bnew=load('B',301)
    persistent=[]
    for n in [100,200,300]:
        a=load('A',n);b=load('B',n)
        persistent.append(b['complete_stride_ratio']>=a['complete_stride_ratio']+.10 and min(b['complete_stride_count'])>0)
    forward_retained=b300['vx']>=.85*b0['vx'] and bnew['vx']>=.85*b0['vx']
    dynamics_safe=max(b300['fall_rate'],bnew['fall_rate'])<=.05 and b300['support_foot_slip']<=max(.12,1.2*b0['support_foot_slip'])
    stop_not_severe=b300['stop_linear_speed']<=.15 and b300['stop_yaw_rate']<=.6
    repeatable=sum(persistent)>=2 and persistent[-1] and bnew['complete_stride_ratio']>=.10 and min(bnew['complete_stride_count'])>0
    allowed=bool(repeatable and forward_retained and dynamics_safe and stop_not_severe)
    # Formal Stage1 remains the unchanged strict per-row gate plus complete strides.
    from dogfight.locomotion.curriculum_v6_3.supervisor import assess
    inv=json.loads((BASE/'checkpoint_inventory.json').read_text());thresholds=inv[0]['options']['thresholds']
    formal=all(all(assess(panel('B',n),0,thresholds).values()) for n in [100,200,300,301])
    selected=run_dir('B')/'final.pt' if allowed else None
    gate={'allowed':allowed,'formal_stage1_passed':formal,'selected_checkpoint':str(selected) if selected else None,'criteria':{'repeatable_complete_stride_improvement':repeatable,'persistent_windows':persistent,'forward_retained':forward_retained,'dynamics_safe':dynamics_safe,'stop_not_severe':stop_not_severe},'thresholds_unchanged':thresholds,'decision':'START_LONG_STAGE1' if allowed else 'BLOCKED_AB_FAILED'}
    (BASE/'CONTINUATION_GATE.json').write_text(json.dumps(gate,indent=2))
    source=inv[0]
    lines=['# V6.3 短程配对 A/B 对照','A/B均从同一个V6第2500轮完整learner恢复，Actor/Critic、17项Adam状态、std、学习率和RNG逐张量相等；仿真重置。256环境、种子42、24步/update，各300次PPO更新，即每组1,843,200环境样本。评估点0/50/100/200/300采用种子103/307/911/1301，终点另用2027/4099。','','源checkpoint：`'+source['path']+'`；SHA256 `'+source['sha256']+'`。A使用V6.2 early-swing奖励；B使用V6.3完整周期、物理滑移和条件化停止保护。网络、PPO、物理、指令分布相同。','','|组|新增更新|vx|完整周期比例|四腿周期数|有效落脚数|稳定支撑秒|滑移|停止速度|停止偏航|摔倒|动作变化RMS|','|---|---:|---:|---:|---|---|---|---:|---:|---:|---:|---:|']
    for r in table:
        lines.append(f"|{r['arm']}|{r['additional_updates']}|{r['vx']:.4f}|{r['complete_stride_ratio']:.4f}|{r['complete_stride_count']}|{r['valid_touchdown_count']}|{[round(x,2) for x in r['stable_stance_duration']]}|{r['support_foot_slip']:.4f}|{r['stop_linear_speed']:.4f}|{r['stop_yaw_rate']:.4f}|{r['fall_rate']:.4f}|{r['action_delta_rms']:.4f}|")
    lines+=['','终点独立种子逐组结果（每个forward命令档位分别列出）：','','|组|新增更新|种子|命令档位|vx|四腿完整周期|周期比例|支撑滑移|停止速度|停止偏航|','|---|---:|---:|---:|---:|---|---:|---:|---:|---:|']
    for arm in ['A','B']:
        for n in [300,301]:
            rows=panel(arm,n)['rows']
            for seed in sorted({r['seed'] for r in rows}):
                forward=[r for r in rows if r['seed']==seed and r['test']=='forward']
                stop=next(r for r in rows if r['seed']==seed and r['test']=='stop')
                for level,r in enumerate(forward):
                    lines.append(f"|{arm}|300|{seed}|{level+1}|{r['velocity'][0]:.4f}|{r['complete_stride_count']}|{r['complete_stride_ratio']:.4f}|{r['support_slip_speed']:.4f}|{stop['speed_xy']:.4f}|{stop['yaw_abs']:.4f}|")
    lines+=['','继续训练资格：**'+('通过' if allowed else '未通过')+'**。Stage 1正式验收：**'+('通过' if formal else '未通过')+'**。短程资格不会直接进入Stage 2；长期训练仍从Stage 1开始，并需连续三次完整多种子正式验收。','','判定明细：','```json',json.dumps(gate,indent=2,ensure_ascii=False),'```','','A/B视频：`ab_A_verified2/final_gait.mp4`、`ab_B/final_gait.mp4`。PPO逐轮曲线原始数据为各组`metrics.jsonl`；所有评估JSON/NPZ和checkpoint保留。若资格失败，长期训练器不会启动。']
    (BASE/'reports/V6_3_AB_COMPARISON.md').write_text('\n'.join(lines)+'\n')
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,2,figsize=(12,8),sharex=True)
    for arm,color in [('A','tab:blue'),('B','tab:orange')]:
        rows=[json.loads(x) for x in (run_dir(arm)/'metrics.jsonl').read_text().splitlines() if x.strip()]
        x=[r['total_updates']-rows[0]['total_updates']+1 for r in rows]
        for ax,key,title in [(axes[0,0],'reward_step','PPO reward/step'),(axes[0,1],'kl','KL'),(axes[1,0],'exploration_std','exploration std'),(axes[1,1],'complete_stride_count','training complete strides/update')]:
            ax.plot(x,[r.get(key,0) for r in rows],label=arm,color=color,alpha=.85);ax.set_title(title);ax.grid(alpha=.2)
    for ax in axes.flat:ax.legend()
    axes[1,0].set_xlabel('additional PPO updates');axes[1,1].set_xlabel('additional PPO updates');fig.tight_layout();fig.savefig(BASE/'reports/V6_3_PPO_CURVES.png',dpi=150);plt.close(fig)
    print(json.dumps(gate,indent=2))
if __name__=='__main__':main()
