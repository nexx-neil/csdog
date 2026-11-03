"""Offline verifiers of geometric flight; descent must not erase prior strict air."""
import numpy as np

def swing_counts(data,dt=.002,clearance=.015,duration=.06):
    n=data.shape[1];run=np.zeros((n,4),dtype=np.int32);peak=run.copy();count=run.copy()
    previous=np.zeros((n,4),dtype=bool);supported=previous.copy();ticks=int(round(duration/dt))
    for row in data:
        contact=row[:,4:8]>.5;shin=row[:,16:20]>.5
        real=(~contact)&(~shin)&(row[:,8:12]>clearance)
        run=np.where(real,run+1,0);peak=np.maximum(peak,run)
        # Max consecutive strict air persists throughout the descending phase.
        land=contact&~previous&supported&~shin&(peak>=ticks)
        count+=land;peak=np.where(contact,0,peak);supported|=contact;previous=contact
    return count

def correct_evaluation(path):
    import json
    from pathlib import Path
    p=Path(path);panel=json.loads(p.read_text());rows=panel['rows']
    for row in rows:
        npz=p.parent/f"{row['mode']}_seed{row['seed']}.npz"
        with np.load(npz) as loaded:
            a=loaded['data'];dt=float(loaded['dt'])
            strict=swing_counts(a,dt);early=swing_counts(a,dt,.004,.02)
        row['swing_count']=strict.sum(0).tolist();row['min_swing_per_env']=float(np.quantile(strict,.1,axis=0).min())
        if any(abs(x)>.04 for x in row['target_velocity']) and row['min_swing_per_env']<3:row['qualified']=False
        row['early_swing_q25']=float(np.quantile(early,.25,axis=0).min())
    m=panel['metrics'];forward=[x for x in rows if x['mode']=='forward']
    m['swing_count']=np.sum([x['swing_count'] for x in forward],axis=0).tolist();m['min_swing_per_env']=float(min(x['min_swing_per_env'] for x in forward));m['early_swing_q25']=float(min(x['early_swing_q25'] for x in forward));m['rows']=rows
    m['qualified']=bool(m['qualified'] and all(row['qualified'] for row in rows))
    # Never upgrade formal acceptance from a counter correction alone.
    panel['counter_verifier']='max-continuous-air-until-touchdown-v1'
    p.write_text(json.dumps(panel,indent=2));return m

def qualify_row(row):
    """Formal v3 acceptance. Missing physical data cannot become a PASS."""
    required={'tilt_q95','foot_speed','joint_velocity_rms'}
    if not required.issubset(row):return False
    target=row['target_velocity'];mx=abs(target[0])>.04;mz=abs(target[2])>.04
    common=(row['fall_fraction']<=.05 and row['shin_rate']<=.01 and row['support_slip']<=.08 and row['tilt_q95']<=.35)
    if mx or mz:
        return bool(common and row['tracking_quantiles'][0]>=.7 and row['tracking_quantiles'][1]<=1.35 and row['lateral_rms']<=.05 and row['phase_match_q10']>=.75 and row['min_swing_per_env']>=3 and min(row['cycle_q10'])>=2 and min(row['clearance_peak'])>=.015 and max(row['clearance_peak'])<=.06 and (mx or row['translation_rms']<=.06) and (mz or row['yaw_abs']<=.08))
    return bool(common and row['translation_rms']<=.03 and row['yaw_abs']<=.08 and row['foot_speed']<=.06 and row['joint_velocity_rms']<=.3 and min(row['contact_duty'])>=.9)
