"""Safety, continuous motion objectives and Pareto ranking; reward is never an input."""
import math
from ..locomotion.curriculum_v6.supervisor import required,row_pass

def metrics(panel,stage=0):
    rows=[r for r in panel['rows'] if r['test'] in required(stage)]
    if not rows:raise ValueError('Empty physical evaluation')
    moving=[r for r in rows if not r['is_stop']];stop=[r for r in rows if r['is_stop']]
    avg=lambda rs,key:sum(float(r.get(key,0)) for r in rs)/max(1,len(rs))
    ratios=[v for r in moving for v in r['tracking_ratios']]
    cycles=[sum(r.get('complete_stride_count',[0]*4)[j] for r in moving) for j in range(4)]
    f=[r for r in rows if r['test']=='forward' and not r['is_stop']]
    replicates=sum(r['replicates'] for r in moving)
    swings=[sum(r.get('valid_swing_count',[0]*4)[j] for r in moving)/max(1,replicates) for j in range(4)]
    rejection={}
    for r in moving:
        for key,values in r.get('rejection_counts',{}).items():rejection[key]=rejection.get(key,0)+sum(values)
    return dict(forward_velocity=sum(r['velocity'][0] for r in f)/max(1,len(f)),
        tracking=min(ratios,default=0.),tracking_error=avg(moving,'forward_tracking_error'),
        complete_stride_count=cycles,min_complete_per_trial=min(cycles)/max(1,replicates),gait_fraction=avg(moving,'complete_stride_ratio'),
        real_swing_count_per_trial=swings,early_swing_min_per_trial=min(swings),
        touchdown_count=sum(sum(r.get('valid_touchdown_count',[0]*4)) for r in moving)/max(1,replicates),
        stable_support_seconds=sum(sum(r.get('stable_stance_duration',[0]*4)) for r in moving)/max(1,replicates),
        support_slip=avg(moving,'support_slip_speed'),stop_linear_speed=avg(stop,'speed_xy'),
        stop_yaw_rate=avg(stop,'yaw_abs'),fall_rate=max(r['fall_rate'] for r in rows),
        illegal_contact=max(r.get('illegal_shank_fraction',0) for r in rows),
        rejection_counts=rejection,protocol=panel['protocol'],seeds=panel['seeds'],seconds=panel['seconds'])

def safe(m):
    numeric=[v for v in m.values() if isinstance(v,(int,float))]
    return (all(math.isfinite(x) for x in numeric) and m['fall_rate']<=.05
            and m.get('illegal_contact',0)<=.01 and m['tracking']>=0)

def continuation_safe(m):
    numeric=[v for v in m.values() if isinstance(v,(int,float))]
    return (all(math.isfinite(x) for x in numeric) and m['fall_rate']<=.15
            and m.get('illegal_contact',0)<=.1 and m['tracking']>=-.1)

def objectives(m):
    # Do not saturate penalties at the acceptance threshold: going from .4 to
    # .1 slip/stop remains visible while each objective remains separate.
    return (min(1.,m['tracking']),m['gait_fraction'],math.log1p(m.get('min_complete_per_trial',min(m['complete_stride_count']))),
            math.log1p(m.get('early_swing_min_per_trial',0)),-m['tracking_error'],-m['support_slip'],-m['stop_linear_speed'],
            -m['stop_yaw_rate'],-m['fall_rate'],-m.get('illegal_contact',0))

def score(m):
    if not safe(m):return -1e6
    # A stationary policy must not beat a moving anchor merely by having zero
    # slip and stop drift. This is search utility, never formal qualification.
    motion_deficit=max(0.,.7-m['tracking'])/.7
    return (min(1.,m['tracking'])-3*motion_deficit+2*m['gait_fraction']+.15*math.log1p(m.get('min_complete_per_trial',min(m['complete_stride_count'])))
            +.08*math.log1p(m.get('early_swing_min_per_trial',0))*max(0.,min(1.,m['tracking']))
            +.03*math.log1p(m['touchdown_count'])+.02*math.log1p(m['stable_support_seconds'])
            -.6*math.log1p(m['support_slip']/.08)-.5*math.log1p(m['stop_linear_speed']/.03)
            -.5*math.log1p(m['stop_yaw_rate']/.08)-3*m['fall_rate']-m.get('illegal_contact',0))

def dominates(a,b):
    if safe(a)!=safe(b):return safe(a)
    x,y=objectives(a),objectives(b)
    return all(v>=w for v,w in zip(x,y)) and any(v>w for v,w in zip(x,y))

def pareto(entries):
    return [a for a in entries if not any(a is not b and dominates(b['metrics'],a['metrics']) for b in entries)]

def qualified(panel,stage,thresholds):
    if stage>=2 and panel.get('yaw_protocol')!='fixed-body-tangent-physical-stride-v1':return False
    for name in required(stage):
        rows=[r for r in panel['rows'] if r['test']==name]
        if not rows or not all(row_pass(r,thresholds) for r in rows):return False
        for r in rows:
            if not r['is_stop']:
                if r.get('complete_stride_ratio',0)<thresholds['trial_pass_fraction'] or r.get('complete_stride_legs',0)!=4:return False
                if r.get('illegal_shank_fraction',1)>.01:return False
    return True
