"""Independent raw-500 Hz event funnel for the completed matched experiment."""
from pathlib import Path
import csv,json
import numpy as np
from scipy.spatial.transform import Rotation

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
LEGS=['LF','RF','LR','RR']

def spans(a):
    e=np.r_[0,np.flatnonzero(np.diff(a.astype(int)))+1,len(a)]
    return [(l,r) for l,r in zip(e[:-1],e[1:]) if a[l]]

def main():
    events=[]
    for arm,directory in [('A','ab_A_verified2'),('B','ab_B')]:
        for p in sorted((BASE/directory/'eval_000300').glob('physics_seed*.npz')):
            d=np.load(p);dt=float(d['dt']);seed=int(p.stem.split('seed')[1]);n,m=d['contact'].shape[:2]
            quat=d['root_quaternion'];rot=Rotation.from_quat(quat[:,:,[1,2,3,0]].reshape(-1,4))
            delta=d['foot_position']-d['root_position'][:,:,None,:]
            relative=np.stack([rot.inv().apply(delta[:,:,j].reshape(-1,3)).reshape(n,m,3) for j in range(4)],2)
            gravity=rot.inv().apply(np.broadcast_to([0.,0.,-1.],(n*m,3))).reshape(n,m,3)
            for i in range(m):
                speed=float(d['command'][-1,i,0])
                if speed<.04:continue
                support=d['contact'][:,i]&~d['shin'][:,i]
                for j,leg in enumerate(LEGS):
                    c=d['contact'][:,i,j];strict=~c&(d['clearance'][:,i,j]>.015)&(d['raw_force'][:,i,j]<1)&~d['shin'][:,i,j]
                    slip=np.linalg.norm(d['patch_velocity'][:,i,j,:2],axis=-1)
                    for l,r in spans(~c):
                        if l*dt<=1.3 or l==0 or r>=n:continue
                        prior=l-1
                        while prior>=0 and support[prior,j]:prior-=1
                        end=r
                        while end<n and support[end,j]:end+=1
                        air=max([(b-a)*dt for a,b in spans(strict[l:r])],default=0.)
                        exc=float(relative[r,i,j,0]-relative[l,i,j,0])
                        checks=[(l-1-prior)*dt>=.04-1e-6,air>=.06-1e-6,(r-l)*dt<=.6+1e-6,exc>.02,not d['shin'][l:r+1,i,j].any(),bool((support[l:r].sum(-1)>=2).all()),float(d['force'][r,i,j])<80,float(d['root_velocity'][r,i,0])>.25*speed,np.linalg.norm(gravity[r,i,:2])<.35,int(support[r].sum())>=2]
                        stable=(end-r)*dt>=.06-1e-6 and float(slip[r:min(end,r+round(.06/dt))].mean())<=.08
                        events.append(dict(arm=arm,seed=seed,speed=speed,trial=i,leg=leg,flight_s=(r-l)*dt,strict_air_s=air,excursion=exc,post_stance_s=(end-r)*dt,post_slip=float(slip[r:end].mean()) if end>r else 0.,prior_support=checks[0],strict_swing=checks[1],flight_limit=checks[2],forward_placement=checks[3],no_shin=checks[4],support_coverage=checks[5],impact=checks[6],body_progress=checks[7],tilt=checks[8],landing_support=checks[9],valid_landing=all(checks),stable_after_landing=all(checks) and stable))
    with (BASE/'reports/V6_3_AB_RAW_EVENTS.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(events[0]));w.writeheader();w.writerows(events)
    lines=['# V6.3 失败分析','独立重算终点原始500 Hz子集：4个种子，每个前进速度各4次试验，剔除前1.3秒。未改变验收阈值。下列各条件列独立计数，不能相加；最后两列要求所有条件同时成立。','','|组|腿|离地片段|连续60ms真实摆动|前摆>20mm|之前支撑40ms|全飞行≥2支撑足|无小腿接触|有效落脚|稳定周期|','|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for arm in ['A','B']:
        for leg in LEGS:
            es=[e for e in events if e['arm']==arm and e['leg']==leg]
            count=lambda k:sum(e[k] for e in es)
            lines.append(f"|{arm}|{leg}|{len(es)}|{count('strict_swing')}|{count('forward_placement')}|{count('prior_support')}|{count('support_coverage')}|{count('no_shin')}|{count('valid_landing')}|{count('stable_after_landing')}|")
    lines+=['','B的滑移代价改善了接触点速度，但没有产生合格落脚序列。全评估面板的LR有效摆动由A的4907次降为B的15次；旧离地占比无法表达该退化。B终点动作变化RMS为1.338，A为0.770，平滑性明显恶化。停止平移0.0835m/s、偏航0.3525rad/s，仍超过正式0.03/0.08门槛。','','本次同时改变完整周期引导、滑移积分与停止反馈，因此不能把滑移改善或步态失败唯一归因于某一项。生产状态机的有效落脚、支撑质量与周期奖励在短程训练中几乎始终未激活，奖励测试通过只证明支付与反重复机制，不证明学习信号足够。','','下一项最值得验证：固定此次已验证的事件支付机制和正式阈值，先从原始轨迹统计“前摆/持续离地/前置支撑/双足支撑”中最早阻断的条件，再用单因素短程对照检验渐进式前摆引导是否能让LR与RR形成真实向前落脚。滑移权重保持对照隔离，避免同时增强多个约束。暂不增大稀疏周期信用，不放宽正式验收，不自动启动长期训练。','','原始逐事件证据：`V6_3_AB_RAW_EVENTS.csv`。该独立子集是诊断补充；继续训练资格仍使用全部256环境、6个评估种子与生产状态机的统一结果。']
    lines+=['','门槛风险：RF在A、B的原始飞行子集中，满足“全飞行至少两足支撑”的次数均为零；B的LF仅17/1879次满足。该条件为防止四腿异常腾空新增，可能同时拒绝短暂单足支撑的合理协调运动。不能把零周期完全归因于PPO不会运动。下一次应单独验证有持续时间限制的支撑安全条件，重评历史模型，再做单因素对照；正式滑移、停止和四腿周期门槛保持不变。B的LR真实连续摆动及LF向前落脚减少则是独立的动作退化证据。']
    (BASE/'reports/V6_3_FAILURE_ANALYSIS.md').write_text('\n'.join(lines)+'\n')
    report=BASE/'reports/V6_3_AB_COMPARISON.md'
    with report.open('a') as f:f.write('\n失败归因与下一项验证见 `V6_3_FAILURE_ANALYSIS.md`，独立500 Hz事件数据见 `V6_3_AB_RAW_EVENTS.csv`。\n')
    print('\n'.join(lines[:14]))

if __name__=='__main__':main()
