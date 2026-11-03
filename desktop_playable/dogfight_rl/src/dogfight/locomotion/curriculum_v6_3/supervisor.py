"""Extend the repaired V6.1 supervisor; preserve its rollback/candidate/course engine."""
import copy,math
from contextlib import contextmanager
from ..curriculum_v6_1 import supervisor as base
from ..curriculum_v6.supervisor import assess as legacy_assess,required
from .evaluation_version import VERSION
atomic_json=base.atomic_json
base_score=base.score;base_safe=base.motion_safe;base_protocol=base.protocol

def assess(panel,stage,t):
    skills=legacy_assess(panel,stage,t)
    for name in required(stage):
        rows=[r for r in panel['rows'] if r['test']==name and not r['is_stop']]
        # The V6.3 directional placement state machine is defined for vx tasks.
        # Pure yaw keeps the original four-leg 500 Hz periodic-contact gate.
        translation=name in {'forward','backward','forward_left','forward_right','backward_left','backward_right','forward_stop','backward_stop','forward_backward','continuous'}
        if translation:
            skills[name]=skills[name] and all(r.get('complete_stride_ratio',0)>=t['trial_pass_fraction'] and r.get('complete_stride_legs',0)==4 for r in rows)
    return skills

def score(panel,stage,t):
    # Keep motion/stop/slip continuous ranking; replace the permissive old gait bonus.
    p=copy.deepcopy(panel)
    for r in p['rows']:
        r['gait_trial_fraction']=r.get('complete_stride_ratio',0)
        r['periodic_legs']=r.get('complete_stride_legs',0)
    return base_score(p,stage,t)

def motion_safe(panel,reference=None):
    if not base_safe(panel,reference):return False
    if reference:
        current=[r for r in panel['rows'] if r['test']=='forward'];old=[r for r in reference['rows'] if r['test']=='forward']
        for r,o in zip(current,old):
            if r.get('complete_stride_ratio',0)+.10<o.get('complete_stride_ratio',0):return False
            if r['support_slip_speed']>max(.12,o['support_slip_speed']*1.3):return False
    return True

def protocol(panel):return dict(base_protocol(panel),stride_protocol=panel.get('stride_protocol'))

def brief(panel):
    forward=[r for r in panel['rows'] if r['test']=='forward'];stops=[r for r in panel['rows'] if r['test']=='stop']
    avg=lambda rows,key:sum(float(r[key]) for r in rows)/max(1,len(rows))
    sum4=lambda key:[sum(float(r[key][j]) for r in forward) for j in range(4)]
    return dict(vx=sum(float(r['velocity'][0]) for r in forward)/max(1,len(forward)),support_foot_slip=avg(forward,'support_slip_speed'),complete_stride_ratio=avg(forward,'complete_stride_ratio'),complete_stride_count=sum4('complete_stride_count'),valid_touchdown_count=sum4('valid_touchdown_count'),stable_stance_duration=sum4('stable_stance_duration'),legacy_gait_fraction=avg(forward,'gait_trial_fraction'),stop_linear_speed=avg(stops,'speed_xy'),stop_yaw_rate=avg(stops,'yaw_abs'),fall_rate=max([float(r['fall_rate']) for r in forward+stops],default=1.),action_delta_rms=avg(forward,'action_delta_rms'))

@contextmanager
def extend():
    names={'assess':assess,'score':score,'motion_safe':motion_safe,'protocol':protocol,'SCORE_VERSION':VERSION}
    old={k:getattr(base,k) for k in names}
    for k,v in names.items():setattr(base,k,v)
    try:yield
    finally:
        for k,v in old.items():setattr(base,k,v)

class Supervisor(base.Supervisor):
    def __init__(self,out,options,state=None):
        with extend():super().__init__(out,options,state)
        for key in ['best_gait_checkpoint','best_balanced_checkpoint','best_stage_qualified_checkpoint']:
            self.state.setdefault(key,None)
    def register(self,panel,checkpoint):
        if panel.get('stride_protocol')!=VERSION:raise ValueError('V63_COMMON_PHYSICAL_PROTOCOL_REQUIRED')
        with extend():best=super().register(panel,checkpoint)
        s=self.state;entries=[e for e in s['rankings'] if e['protocol']==s['ranking_protocol']]
        def gait(e):
            rs=[r for r in e['summary']['rows'] if r['test']=='forward']
            return (sum(r.get('complete_stride_ratio',0) for r in rs)/max(1,len(rs)),sum(sum(r.get('complete_stride_count',[0]*4)) for r in rs))
        if entries:
            safe=[e for e in entries if motion_safe(e['summary'],s.get('ranking_reference'))]
            s['best_gait_checkpoint']=max(entries,key=gait)['checkpoint']
            s['best_balanced_checkpoint']=max(safe or entries,key=lambda e:score(e['summary'],s['stage'],self.options['thresholds']))['checkpoint']
            qualified=[e for e in entries if all(assess(e['summary'],s['stage'],self.options['thresholds']).values())]
            if qualified:s['best_stage_qualified_checkpoint']=max(qualified,key=lambda e:score(e['summary'],s['stage'],self.options['thresholds']))['checkpoint']
        return best
    def observe(self,panel,checkpoint,auto_recovery=True):
        with extend():return super().observe(panel,checkpoint,auto_recovery)
    def update_internal(self,panel):
        # V6.3 quality signals apply from Stage1; no reward switch based on old air ratio.
        self.state['substage']='1B'
    def adjust(self,diagnosis,panel):
        # Finite, non-repeating single-factor candidates from an unchanged anchor.
        s=self.state;before={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range','substage']}
        choices=[('physical_slip:1.25','physical_slip',1.25),('stop_feedback:1.25','stop_feedback',1.25),('stride_credit:1.25','stride_credit',1.25)]
        tried=set(s['failed_factors'])|{a.get('factor') for a in s['attempts']}
        for factor,key,scale in choices:
            if factor not in tried:
                s['weights'][key]=max(-1.5,min(1.5,s['weights'][key]*scale))
                if s['candidate']:s['candidate']['factor']=factor
                self.event('SAFE_PARAMETER_CHANGE',factor=factor,before=before,after={k:copy.deepcopy(s[k]) for k in before},evidence=panel['id']);return factor
        raise RuntimeError('ALL_DEFINED_SAFE_CANDIDATES_EXHAUSTED')
    def publish(self,summary=None):
        super().publish(summary)
        p=self.out/'TRAINING_STATUS.json'
        if not p.exists():return
        import json
        s=json.loads(p.read_text());panel=summary or self.state.get('last_evaluation')
        if panel:
            s['physical_metrics']=brief(panel);s['gait_qualified']=all(assess(panel,self.state['stage'],self.options['thresholds']).values())
        s['score_version']=VERSION;atomic_json(p,s)
        (self.out/'STATUS_SUMMARY.md').write_text(f"V6.3 {s['training_status']} | Stage {s['stage']+1} {s['stage_name']} | PPO {s['total_updates']}\n\nMetrics: {s.get('physical_metrics')}\n\nBest gait: {s.get('best_gait_checkpoint')}\n\nBest balanced: {s.get('best_balanced_checkpoint')}\n\nBest qualified: {s.get('best_stage_qualified_checkpoint')}\n")
