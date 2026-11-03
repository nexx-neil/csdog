"""Targeted gait-only search; no parameter splicing or broad random reward changes."""
import copy
from .search_optimizer import SearchOptimizer
from ..locomotion.phase_guided_v7.kernel import DEFAULTS
BOUNDS=dict(frequency=(1.,2.),clearance_target=(.018,.035),stance_weight=(.8,2.),release_weight=(.3,1.),slip_weight=(.1,.8),tracking_weight=(3.,6.),stop_fraction=(.15,.35),entropy_coef=(.001,.008))
class V7Search(SearchOptimizer):
    @staticmethod
    def diagnose(m):
        if m['fall_fraction']>.1:return 'FALLING'
        if m.get('stop_speed',0)>.03 or m.get('stop_yaw',0)>.08 or m.get('stop_foot_speed',0)>.06 or m.get('stop_min_contact_duty',1)<.9:return 'STOP_DRIFT'
        if m['actual_speed']<0:return 'WRONG_DIRECTION'
        if max(m['clearance_peak'])>.06 and min(m['clearance_peak'])<.015:return 'ASYMMETRIC_LIFT'
        if min(m['clearance_peak'])<.008:return 'NO_LIFT'
        if max(m['clearance_peak'])>.06:return 'TOO_HIGH'
        if m['min_swing_per_env']<1:return 'ONLY_SOME_LEGS'
        if m['support_slip']>.08:return 'SLIP'
        if m['actual_speed']<.14:return 'IN_PLACE'
        if m['phase_match']<.75:return 'PHASE_MISMATCH'
        if m.get('course',0)>0 and any(row.get('tracking_ratio',1)<.7 for row in m.get('rows',[]) if row['mode'] not in ('stop','transition_stop')):return 'NEW_DIRECTION'
        return 'REFINE'
    @staticmethod
    def propose(options,m,index):
        o=dict(DEFAULTS,**copy.deepcopy(options));reason=V7Search.diagnose(m)
        mapping=dict(ASYMMETRIC_LIFT=[('frequency',-.25),('clearance_target',-.003),('stance_weight',.2)],NEW_DIRECTION=[('entropy_coef',.001),('tracking_weight',.5)],FALLING=[('frequency',-.25),('stance_weight',.2)],STOP_DRIFT=[('stop_fraction',.05)],WRONG_DIRECTION=[('tracking_weight',.5)],NO_LIFT=[('release_weight',.15),('clearance_target',-.003),('entropy_coef',.001)],TOO_HIGH=[('clearance_target',-.003),('release_weight',-.1)],ONLY_SOME_LEGS=[('stance_weight',.2),('frequency',-.25)],SLIP=[('slip_weight',.1)],IN_PLACE=[('tracking_weight',.5)],PHASE_MISMATCH=[('frequency',-.25),('stance_weight',.2)],REFINE=[('frequency',.25),('frequency',-.25),('clearance_target',.003),('slip_weight',.1)])
        choices=mapping[reason];key,delta=choices[index%len(choices)];delta*=1+index//len(choices);before=o.get(key,.0025);lo,hi=BOUNDS[key];after=min(hi,max(lo,before+delta))
        if after==before:after=min(hi,max(lo,before-delta))
        o[key]=after
        return o,dict(reason=reason,key=key,before=before,after=after)
    @staticmethod
    def score(m):
        base=4*max(0.,1-abs(m['actual_speed']-.2)/.2)+min(2,m['min_swing_per_env']/3)+m['phase_match']-5*m['support_slip']-5*m['fall_fraction']-5*m.get('stop_speed',0)-m.get('stop_yaw',0)
        if m.get('course',0)>0:
            moving=[r for r in m.get('rows',[]) if r['mode'] not in ('stop','transition_stop')]
            if moving:
                # New command skills must influence inheritance; forward-only
                # ranking would repeatedly roll back genuine backward progress.
                tracking=sum(max(0.,1-abs(r['tracking_ratio']-1)) for r in moving)/len(moving)
                gait=sum(min(1.,r['min_swing_per_env']/3) for r in moving)/len(moving)
                base=4*tracking+2*gait+m['phase_match']-5*m['support_slip']-5*m['fall_fraction']-5*m.get('stop_speed',0)-m.get('stop_yaw',0)
        return base

def early_physical_trend(m,baseline):
    """Continuation budget only; never a walking acceptance criterion."""
    return bool(m.get('early_swing_q25',0)>=1 and m['phase_match']>=.60
                and m['actual_speed']>.06 and m['fall_fraction']<.10
                and m['shin_rate']<.02 and m['support_slip']<min(.30,.95*baseline['support_slip'])
                and all(.10<d<.95 for d in m['contact_duty']))

def prior_course_safe(m,stage):
    if stage==0:return True
    required={'forward','stop','transition_stop'}
    if stage>=2:required.add('backward')
    if stage>=3:required.update(('yaw_positive','yaw_negative'))
    rows=[r for r in m.get('rows',[]) if r['mode'] in required]
    return required.issubset({r['mode'] for r in rows}) and all(r.get('qualified',False) for r in rows)

def strict_leg_coverage(m):
    """Fractional per-leg strict flight coverage, separate from formal min gate."""
    counts=m.get('swing_count')
    if not counts:return min(1.,m['min_swing_per_env']/3)
    seeds=max(1,len([r for r in m.get('rows',[]) if r['mode']=='forward']))
    n=m.get('num_envs',128)
    return sum(min(1.,count/(n*seeds*3)) for count in counts)/4
