"""Unified deterministic physical panel. Reuse existing rollout and thresholds."""
from pathlib import Path
import numpy as np
from .stride import observe,PROTOCOL
from .gait_audit import REASONS,audit_file
from ..locomotion.curriculum_v6_3 import evaluation as legacy
from ..locomotion.curriculum_v6.evaluation import CASES
from ..locomotion.curriculum_v6.supervisor import atomic_json

brief=legacy.brief

def evaluate(runner,out,full=True,seeds=None,raw=True):
    out=Path(out)
    o=observe(runner.env.unwrapped);o.events=[]
    step=runner.env.step
    def measured(action):
        o.record_events=bool(full)
        try:return step(action)
        finally:o.record_events=False
    runner.env.step=measured
    saved=legacy.observe;legacy.observe=observe
    try:panel=legacy.evaluate(runner,out,full=full,seeds=seeds,raw=raw)
    finally:
        legacy.observe=saved;runner.env.step=step;o.record_events=False
    panel['protocol']=panel['stride_protocol']=PROTOCOL
    panel['yaw_protocol']='fixed-body-tangent-physical-stride-v1'
    enrich(panel,out)
    if full:export_events(o,panel,out)
    if raw:
        for p in out.glob('physics_seed*.npz'):audit_file(p,out/(p.stem+'_events'))
    return panel


def enrich(panel,out):
    out=Path(out)
    for seed in panel['seeds']:
        with np.load(out/f'evaluation_common_seed{seed}.npz') as d:
            reps=panel['num_envs']//len(CASES)
            seed_rows=[r for r in panel['rows'] if r['seed']==seed];cursor=0
            for i,(name,_) in enumerate(CASES):
                ix=list(range(i*reps,(i+1)*reps));c=d['command'][:,ix]
                changes=np.any(np.diff(c,axis=0)!=0,axis=(1,2));age=np.zeros(len(c));age[0]=.02
                for k in range(1,len(c)):age[k]=.02 if changes[k-1] else age[k-1]+.02
                case_rows=[]
                while cursor<len(seed_rows) and seed_rows[cursor]['test']==name:
                    case_rows.append(seed_rows[cursor]);cursor+=1
                for row in case_rows:
                    row['case_index']=i
                    row['target_sequence']=[list(v) for v in CASES[i][1]]
                    moving=np.linalg.norm(c,axis=-1)>.04
                    mask=d['valid'][:,ix]&(age[:,None]>1.3)&(~moving if row['is_stop'] else moving)
                    row['candidate_count']=(d['candidate_count'][:,ix]*mask[:,:,None]).sum((0,1)).tolist()
                    a=(d['reason_count'][:,ix]*mask[:,:,None,None]).sum((0,1))
                    row['rejection_counts']={reason:a[:,j].tolist() for j,reason in enumerate(REASONS)}
                    row['rejection_counts_all']={reason:d['reason_count'][:,ix].sum((0,1))[:,j].tolist() for j,reason in enumerate(REASONS)}
                    row['illegal_shank_fraction']=float(d['shin'][:,ix][mask].any(-1).mean()) if mask.any() else 1.
    panel['formal_acceptance']='unchanged V6.3 thresholds; first landing window fixed at 60ms'
    atomic_json(out/'evaluation_common.json',panel);atomic_json(out/'summary.json',brief(panel))
    return panel


def export_events(observer,panel,out):
    import torch,csv
    if not observer.events:return
    per_seed=round(panel['seconds']/.002)
    if len(observer.events)!=per_seed*len(panel['seeds']):raise ValueError('Physical event recorder tick count mismatch')
    # Whole-panel bitfields preserve every environment/leg/physical-tick event;
    # raw mesh/force/pose trajectories remain a separate diagnostic subset.
    for i,seed in enumerate(panel['seeds']):
        data=torch.stack(observer.events[i*per_seed:(i+1)*per_seed]).cpu().numpy()
        np.savez_compressed(out/f'stride_events_seed{seed}.npz',dt=.002,events=data,reasons=np.array(REASONS))
        indices=np.argwhere(data.any(-1))
        with (out/f'stride_events_seed{seed}.csv').open('w') as f:
            w=csv.writer(f);w.writerow(['physical_tick','time_s','environment','leg','candidate','complete_cycle','reasons'])
            for tick,env,leg in indices:
                candidate,bits,complete=data[tick,env,leg]
                w.writerow([int(tick),float((tick+1)*.002),int(env),['LF','RF','LR','RR'][leg],int(candidate),int(complete),'|'.join(reason for j,reason in enumerate(REASONS) if int(bits)&(1<<j))])
    observer.events=[]
