"""Derive flight/landing/stance evidence from every saved raw physical tick."""
from pathlib import Path
import sys,json,csv
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
LEGS=['LF','RF','LR','RR']
def spans(a):
    edges=np.r_[0,np.flatnonzero(np.diff(a.astype(int)))+1,len(a)]
    return [(l,r) for l,r in zip(edges[:-1],edges[1:]) if a[l]]
def main():
    import matplotlib;matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    rows=[];legrows=[];metrics={}
    for name in ['v6_2500','v62_B100','v62_B300']:
        dest=OUT/'history'/name;metrics[name]=json.loads((dest/'summary.json').read_text())
        for p in sorted(dest.glob('physics_seed*.npz')):
            d=np.load(p);dt=float(d['dt']);seed=int(p.stem.split('seed')[1]);n=len(d['contact'])
            q=d['root_quaternion'];delta=d['foot_position']-d['root_position'][:,:,None,:]
            rot=Rotation.from_quat(q[:,:,[1,2,3,0]].reshape(-1,4))
            relative=np.stack([rot.inv().apply(delta[:,:,j].reshape(-1,3)).reshape(n,12,3) for j in range(4)],axis=2)
            for i in range(12):
                speed=float(d['command'][-1,i,0]);valid=(np.arange(n)*dt>1.3)&(d['episode'][:,i]>1)
                for j,leg in enumerate(LEGS):
                    c=d['contact'][:,i,j];strict=(~c)&(d['clearance'][:,i,j]>.015)&(d['raw_force'][:,i,j]<1)&~d['shin'][:,i,j]
                    durations=[(r-l)*dt for l,r in spans(strict&valid)]
                    support=c&valid;slip=np.linalg.norm(d['patch_velocity'][:,i,j,:2],axis=-1)
                    legrows.append(dict(checkpoint=name,seed=seed,trial=i,speed=speed,leg=leg,strict_air_ratio=float(strict[valid].mean()),max_height=float(d['clearance'][valid,i,j].max()),max_strict_air=max(durations,default=0),strict_segments_ge60=sum(v>=.06-1e-6 for v in durations),support_duty=float(c[valid].mean()),longest_support=max([(r-l)*dt for l,r in spans(support)],default=0),support_slip=float(slip[support].mean()) if support.any() else 0,shin_ratio=float(d['shin'][valid,i,j].mean())))
                    for l,r in spans((~c)&valid):
                        if l==0 or r>=n or not c[l-1] or not c[r]:continue
                        end=r
                        while end<n and c[end]:end+=1
                        air=max([(b-a)*dt for a,b in spans(strict[l:r])],default=0)
                        exc=float(relative[r,i,j,0]-relative[l-1,i,j,0])
                        rows.append(dict(checkpoint=name,seed=seed,trial=i,speed=speed,leg=leg,liftoff_s=l*dt,touchdown_s=r*dt,flight_s=(r-l)*dt,max_height=float(d['clearance'][l:r,i,j].max()),continuous_strict_air_s=air,forward_placement=exc,post_stance_s=(end-r)*dt,post_stance_slip=float(slip[r:end].mean()),post_stance_force=float(d['force'][r:end,i,j].mean()),shin=bool(d['shin'][l:end,i,j].any()),valid_swing=bool(air>=.06-1e-6),directional_touchdown=bool(air>=.06-1e-6 and exc>.02),stable_support=bool((end-r)*dt>=.06-1e-6 and slip[r:end].mean()<=.08)))
            if seed==103:
                fig,axs=plt.subplots(4,1,figsize=(13,9),sharex=True)
                for j,leg in enumerate(LEGS):
                    ix=8;t=np.arange(n)*dt;axs[j].plot(t,d['clearance'][:,ix,j]*1000,label='mesh clearance mm');axs[j].plot(t,relative[:,ix,j,0]*1000,label='body relative x mm');axs[j].fill_between(t,0,15,where=d['contact'][:,ix,j],alpha=.2);axs[j].set_ylabel(leg);axs[j].legend(loc='upper right')
                axs[-1].set_xlabel('physical seconds; 0.25 m/s, seed103, trial0');fig.tight_layout();fig.savefig(dest/'foot_cycles.png');plt.close(fig)
    for filename,data in [('physical_flights.csv',rows),('physical_legs.csv',legrows)]:
        with (OUT/'reports'/filename).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(data[0]));w.writeheader();w.writerows(data)
    text=['# V6.3 历史步态统一物理分析','三模型均重新运行真实PhysX，无PPO更新；同256环境、2ms/20ms、相同reset扰动、确定性Actor、12秒、种子103/307/911/1301。保留原16任务面板，主分析为0.18、0.25m/s与停止。每种子各主命令4次完整500Hz原始轨迹，全部环境保存500Hz状态机的控制步累计量。没有合并接触间隙。','完整周期定义：先连续有效distal支撑40ms，卸载后单次飞行内连续真实15mm/60ms离地，600ms内向前落脚>20mm，无小腿接触/冲击>80N，再连续支撑60ms且该支撑段平均真实接触点速度≤0.08m/s。完整周期指标比历史离地片段指标更严格；旧门槛全部保留并独立报告，历史模型全部重新评估。','|模型|vx|滑移|旧步态比例|完整周期比例|四腿完整周期数|停止速度|停止偏航|','|---|---:|---:|---:|---:|---|---:|---:|']
    for name,m in metrics.items():text.append(f"|{name}|{m['vx']:.4f}|{m['support_foot_slip']:.4f}|{m['legacy_gait_fraction']:.4f}|{m['complete_stride_ratio']:.4f}|{m['complete_stride_count']}|{m['stop_linear_speed']:.4f}|{m['stop_yaw_rate']:.4f}|")
    text+=['','下表为500Hz原始子集（四种子×每速度四次试验），前1.3秒剔除。向前位移以机身坐标变换计算；原始实际关节/目标关节、力、足部速度、根姿态、接触/离地均在physics_seed*.npz。','|模型|速度|腿|最长严格离地ms均值|峰值高度mm均值|≥60ms段数|方向合格落脚数|随后稳定支撑数|支撑滑移均值|支撑占比|','|---|---:|---|---:|---:|---:|---:|---:|---:|---:|']
    for name in metrics:
        for speed in [.18,.25]:
            for leg in LEGS:
                ls=[r for r in legrows if r['checkpoint']==name and abs(r['speed']-speed)<1e-4 and r['leg']==leg];fs=[r for r in rows if r['checkpoint']==name and abs(r['speed']-speed)<1e-4 and r['leg']==leg]
                avg=lambda k:np.mean([r[k] for r in ls])
                text.append(f"|{name}|{speed}|{leg}|{avg('max_strict_air')*1000:.1f}|{avg('max_height')*1000:.1f}|{sum(r['strict_segments_ge60'] for r in ls)}|{sum(r['directional_touchdown'] for r in fs)}|{sum(r['directional_touchdown'] and r['stable_support'] for r in fs)}|{avg('support_slip'):.3f}|{avg('support_duty'):.3f}|")
    text+=['','退化的高度、时长、方向与支撑证据必须按上表逐腿比较。离地不等于有效摆动；有效摆动不等于向前落脚；向前落脚也不等于稳定支撑。支撑抖动/短接触全部保留于physical_flights.csv，不通过滤波制造步态。','B100的旧比例即使较高，仍需检查四腿方向落脚和支撑。支撑滑移不下降，是因为旧指标没有要求向前落脚后的稳定支撑，原progress/tracking又可通过滑动获得。是否存在原地垂直抬腿，以方向合格落脚数而非峰值高度判定。没有证据把长期支撑或所有失败都归因于单腿静止，支撑占比和逐事件时长提供直接核对。','继续训练起点预先选择V6第2500轮：保护前进与较好停止能力。B100和B300保留为诊断模型；不能用旧100%覆盖其高滑移和更差停止。三模型的视频为history/<模型>/gait.mp4，同视角、同速度、同种子、12秒，含真实速度/接触/高度/完整周期计数。','恢复方式：完整恢复Actor/Critic、17项Adam状态、std、学习率和RNG，未重新初始化优化器；仿真episode及求解器缓存重置，非逐位连续物理恢复。完整来源与SHA在checkpoint_inventory.json。']
    (OUT/'reports/V6_3_HISTORICAL_GAIT_ANALYSIS.md').write_text('\n'.join(text)+'\n')
if __name__=='__main__':main()
