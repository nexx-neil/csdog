"""Independent per-flight audit of immutable 500 Hz physical trajectories."""
from pathlib import Path
import csv
import json
import numpy as np
from scipy.spatial.transform import Rotation

LEGS = ('LF', 'RF', 'LR', 'RR')
REASONS = ('INSUFFICIENT_SUPPORT', 'INSUFFICIENT_SWING_HEIGHT',
           'SWING_DURATION_TOO_SHORT', 'NO_FORWARD_FOOT_DISPLACEMENT',
           'INVALID_TOUCHDOWN', 'EXCESSIVE_STANCE_SLIP', 'SHANK_GROUND_CONTACT',
           'CONTACT_CHATTER', 'STATE_MACHINE_RESET', 'OTHER')

def spans(signal):
    edges = np.r_[0, np.flatnonzero(np.diff(signal.astype(int))) + 1, len(signal)]
    return [(int(a), int(b)) for a, b in zip(edges[:-1], edges[1:]) if signal[a]]

def longest(signal):
    return max((b-a for a,b in spans(signal)), default=0)

def audit_file(path, output, plot=True):
    """All independent rejection reasons, including an explicit right-censored result.

    Keep the formal V6.3 2-support requirement. Never bridge contact gaps.
    """
    path, output = Path(path), Path(output)
    output.mkdir(parents=True, exist_ok=True)
    with np.load(path) as f:
        d = {k:f[k] for k in f.files}
    dt = float(d['dt'])
    if not np.isclose(dt,.002):
        raise ValueError('Formal audit requires 500 Hz data')
    n,m = d['contact'].shape[:2]
    q = d['root_quaternion']
    rot = Rotation.from_quat(q[:,:,[1,2,3,0]].reshape(-1,4))
    delta = d['foot_position'] - d['root_position'][:,:,None,:]
    x = np.stack([rot.inv().apply(delta[:,:,j].reshape(-1,3)).reshape(n,m,3)[:,:,0]
                  for j in range(4)], -1)
    tilt = np.linalg.norm(rot.inv().apply(np.broadcast_to([0.,0.,-1.],(n*m,3))).reshape(n,m,3)[:,:,:2],axis=-1)
    contact,shin = d['contact'],d['shin']
    support = contact & ~shin
    total = support.sum(-1)
    slip = np.linalg.norm(d['patch_velocity'][...,:2],axis=-1)
    events=[]
    for i in range(m):
        # Full raw recorder includes stop trials as well. Stop is retained in plots,
        # but flight statistics describe only translational movement candidates.
        for j,leg in enumerate(LEGS):
            c = contact[:,i,j]
            for l,r in spans(~c):
                if l == 0 or l*dt <= 1.3 or abs(d['command'][l,i,0]) <= .04:
                    continue
                stop = min(r,n-1)
                cmd = float(d['command'][l,i,0]); direction=np.sign(cmd)
                pre=l-1
                while pre>=0 and support[pre,i,j]: pre-=1
                end=r
                while end<n and support[end,i,j]: end+=1
                strict=(~c[l:r])&(d['clearance'][l:r,i,j]>.015)&(d['raw_force'][l:r,i,j]<1)&~shin[l:r,i,j]
                low=total[l:r,i]<2
                zero=total[l:r,i]==0
                post=slip[r:min(end,r+round(.06/dt)),i,j]
                excursion=float((x[stop,i,j]-x[l,i,j])*direction)
                reset=(r==n or np.any(d['episode'][l:stop+1,i]<=1)
                       or np.any(np.diff(d['episode'][l:stop+1,i])<0)
                       or np.any(np.sign(d['command'][l:stop+1,i,0])!=direction))
                conditions={
                    'INSUFFICIENT_SUPPORT': bool(low.any() or total[stop,i]<2),
                    'INSUFFICIENT_SWING_HEIGHT': bool(d['clearance'][l:r,i,j].max(initial=0)<=.015),
                    'SWING_DURATION_TOO_SHORT': longest(strict)*dt < .06-1e-6,
                    'NO_FORWARD_FOOT_DISPLACEMENT': excursion <= .02,
                    'INVALID_TOUCHDOWN': bool(r==n or (l-1-pre)*dt<.04-1e-6 or (r-l)*dt>.6+1e-6
                                              or d['force'][stop,i,j]>=80 or tilt[stop,i]>=.35
                                              or d['root_velocity'][stop,i,0]*direction<=.25*abs(cmd)),
                    'EXCESSIVE_STANCE_SLIP': bool(len(post) and post.mean()>.08),
                    'SHANK_GROUND_CONTACT': bool(shin[l:stop+1,i,j].any()),
                    'CONTACT_CHATTER': bool((end-r)*dt<.06-1e-6 or (r-l)*dt<.06-1e-6),
                    'STATE_MACHINE_RESET': bool(reset), 'OTHER': False,
                }
                deficient=np.flatnonzero(low)
                row=dict(source=str(path),trial=i,leg=leg,start_tick=l,end_tick=r,
                         command=cmd,flight_s=(r-l)*dt,strict_air_s=longest(strict)*dt,
                         prior_support_s=(l-1-pre)*dt,post_support_s=(end-r)*dt,
                         excursion_m=excursion,first_60ms_slip=float(post.mean()) if len(post) else None,
                         insufficient_support_s=float(low.sum()*dt),longest_support_gap_s=longest(low)*dt,
                         zero_support_s=float(zero.sum()*dt),
                         first_deficit_tick=l+int(deficient[0]) if len(deficient) else None,
                         # Raw net force is independent of distal manifold classification.
                         raw_force_disagreement_ticks=int(((d['raw_force'][l:r,i]>1).sum(-1)[low]>=2).sum()),
                         all_feet_clear_ticks=int((d['clearance'][l:r,i][zero].min(-1)>.004).sum()),
                         touchdown_force=float(d['force'][stop,i,j]),
                         complete_cycle=not any(conditions.values()),**conditions)
                row['reasons']='|'.join(k for k,v in conditions.items() if v)
                events.append(row)
    if events:
        with (output/'events.csv').open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(events[0]));w.writeheader();w.writerows(events)
    summary={}
    for leg in LEGS:
        e=[r for r in events if r['leg']==leg]
        gaps=[r['longest_support_gap_s'] for r in e if r['INSUFFICIENT_SUPPORT']]
        summary[leg]=dict(candidates=len(e),complete_cycles=sum(r['complete_cycle'] for r in e),
            rejections={k:sum(r[k] for r in e) for k in REASONS},
            longest_support_gap_s_percentiles=np.percentile(gaps,[0,25,50,75,100]).tolist() if gaps else [],
            raw_force_disagreement_ticks=sum(r['raw_force_disagreement_ticks'] for r in e),
            zero_support_s=sum(r['zero_support_s'] for r in e),
            all_feet_clear_ticks=sum(r['all_feet_clear_ticks'] for r in e))
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    if plot:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        movers=np.flatnonzero(abs(d['command'][-1,:,0])>.04)
        i=int(movers[0]) if len(movers) else 0
        a,b=round(2/dt),min(n,round(4/dt));t=np.arange(a,b)*dt
        fig,axes=plt.subplots(5,1,figsize=(14,12),sharex=True)
        for j,leg in enumerate(LEGS):
            axes[0].step(t,contact[a:b,i,j]*.7+j,where='post',label=leg)
            axes[1].plot(t,d['clearance'][a:b,i,j]*1000,label=leg)
            axes[2].plot(t,x[a:b,i,j]*1000,label=leg)
            axes[3].plot(t,d['raw_force'][a:b,i,j],label=leg)
        axes[4].step(t,total[a:b,i],where='post',label='support feet')
        axes[4].plot(t,d['root_position'][a:b,i,2],label='root z (m)')
        for ax,label in zip(axes,['Contact','Mesh clearance (mm)','Foot body x (mm)','Raw net force (N)','Support / root z']):
            ax.set_ylabel(label);ax.legend(loc='upper right');ax.grid(alpha=.2)
        axes[-1].set_xlabel('Physical time (s)')
        fig.suptitle(f'{path.parent.parent.name}/{path.name}, trial {i}, command {d["command"][-1,i,0]:.2f} m/s')
        fig.tight_layout();fig.savefig(output/'contact_height_trajectory.png');plt.close(fig)
    return summary

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('raw',type=Path,nargs='+');p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    results={}
    for path in a.raw:
        key=path.parent.parent.name+'_'+path.parent.name+'_'+path.stem
        results[key]=audit_file(path,a.output/key)
    (a.output/'all_summaries.json').write_text(json.dumps(results,indent=2)+'\n')
    for key,s in results.items():
        print(key,{leg:(v['candidates'],v['complete_cycles'],v['longest_support_gap_s_percentiles']) for leg,v in s.items()},flush=True)
if __name__=='__main__':main()
