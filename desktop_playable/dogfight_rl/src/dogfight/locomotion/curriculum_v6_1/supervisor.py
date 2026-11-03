"""Versioned continuous ranking, strict V6 capability gates and bounded repairs."""
import copy, hashlib, json, math
from ..curriculum_v6.supervisor import (
    Supervisor as V6Supervisor, atomic_json, assess, required, row_pass,
    STAGES, BASIC, COMBINED, TRANSITIONS, BEST_NAMES, LEGS)
SCORE_VERSION='v6.1-continuous-2'
SEEDS=[103,307,911,1301]

def protocol(summary):
    return dict(score_version=SCORE_VERSION,contact_version=summary.get('contact_version','v6-raw'),
                seeds=summary.get('seeds'),seconds=summary.get('seconds'),num_envs=summary.get('num_envs'))

def score(summary,stage,t):
    by={}
    for r in summary['rows']:
        if r['test'] not in required(stage):continue
        if not r.get('valid') or not all(math.isfinite(float(r[k])) for k in ['fall_rate','speed_xy','support_slip_speed','tilt']):return -1e6
        value=-8*r['fall_rate']
        if r['is_stop']:
            value-=.35*math.log1p(r['speed_xy']/t['stop_speed'])
            value-=.15*math.log1p(r.get('yaw_abs',abs(r['yaw']))/t['stop_yaw'])
        else:
            ratios=r['tracking_ratios']
            if not ratios:return -1e6
            progress=sum(max(-1.,min(1.,x)) for x in ratios)/len(ratios)
            # Task progress remains dominant; low slip cannot make standing win.
            value+=2*progress-1.5*max(0.,.7-min(ratios))
            value+=.5*r['gait_trial_fraction']+.25*r['periodic_legs']/4
            value-=.35*math.log1p(r['support_slip_speed']/t['support_slip'])
            value-=.25*max(0.,r['tilt']-.25)
        by.setdefault(r['test'],[]).append(value)
    if set(by)!=set(required(stage)):return -1e6
    return sum(sum(v)/len(v) for v in by.values())/len(by)

def compact(summary):
    result=copy.deepcopy(summary)
    for r in result['rows']:
        r.pop('feet',None)
    return result

def motion_safe(summary,reference=None):
    rows=[r for r in summary['rows'] if r['test']=='forward']
    if not rows or not all(r.get('valid') and r['fall_rate']<=.05 and
            r['tracking_ratios'] and all(.7<=x<=1.5 for x in r['tracking_ratios']) and r['tilt']<.35 for r in rows):return False
    stops=[r for r in summary['rows'] if r['test']=='stop']
    if not stops or any(r['fall_rate']>.05 for r in stops):return False
    if reference:
        old=[r for r in reference['rows'] if r['test']=='forward']
        if len(rows)!=len(old):return False
        for r,o in zip(rows,old):
            if r['velocity'][0]<.85*o['velocity'][0]:return False
            if r['gait_trial_fraction']+.25<o['gait_trial_fraction']:return False
        previous_stops=[r for r in reference['rows'] if r['test']=='stop']
        for r,o in zip(stops,previous_stops):
            if r['speed_xy']>max(.05,1.5*o['speed_xy']):return False
            if r.get('yaw_abs',abs(r['yaw']))>max(.16,1.5*o.get('yaw_abs',abs(o['yaw']))):return False
    return True

class Supervisor(V6Supervisor):
    def __init__(self,out,options,state=None):
        super().__init__(out,options,state)
        s=self.state
        if s.get('score_version')!=SCORE_VERSION:
            s['legacy_best']={k:copy.deepcopy(s.get(k)) for k in ['best_checkpoint','best_score','best_summary']}
            s.update(best_checkpoint=None,best_score=-1e6,best_summary=None,rankings=[],score_version=SCORE_VERSION,passes=0,ranking_protocol=None,ranking_reference=None)
        s.setdefault('rankings',[]);s.setdefault('attempts',[]);s.setdefault('substage','1A');s.setdefault('last_repair_window',0)
        s.setdefault('failed_factors',['completed_swing_incentive:0.15->0.30'])
    def publish(self,summary=None):
        if summary:summary=compact(summary)
        if self.state.get('last_evaluation'):self.state['last_evaluation']=compact(self.state['last_evaluation'])
        super().publish(summary)
        p=self.out/'STATUS_SUMMARY.md'
        p.write_text(p.read_text().replace('# V6 ', '# V6.1 ')+f"\nInternal Stage 1: {self.state['substage']} | score: {SCORE_VERSION}\n")
    def report(self):
        super().report()
        src=self.out/'CURRICULUM_PPO_V6_FINAL_REPORT.md'
        if src.exists():src.rename(self.out/'CURRICULUM_PPO_V6_1_FINAL_REPORT.md')
    def register(self,summary,checkpoint):
        """Every valid complete evaluation is registered, including rejected candidate arms."""
        if not summary.get('full') or score(summary,self.state['stage'],self.options['thresholds'])<=-1e6:return False
        s=self.state;entry=dict(checkpoint=str(checkpoint),summary=compact(summary),protocol=protocol(summary))
        if s.get('ranking_protocol') is None:s['ranking_protocol']=entry['protocol']
        s['rankings']=[x for x in s['rankings'] if not (x['checkpoint']==str(checkpoint) and x['protocol']==entry['protocol'])]+[entry]
        if entry['protocol']!=s['ranking_protocol']:
            self.event('SEPARATE_EVALUATION_PROTOCOL',checkpoint=str(checkpoint),protocol=entry['protocol'])
            return False
        comparable=[x for x in s['rankings'] if x['protocol']==s['ranking_protocol']]
        if s.get('ranking_reference') is None:s['ranking_reference']=compact(summary)
        def prerequisites(x):return s['stage']==0 or all(assess(x['summary'],s['stage']-1,self.options['thresholds']).values())
        def rank_key(x):return (prerequisites(x),motion_safe(x['summary'],s['ranking_reference']),score(x['summary'],s['stage'],self.options['thresholds']))
        winner=max(comparable,key=rank_key)
        before=s['best_checkpoint'];old=s['best_score']
        s['best_checkpoint']=winner['checkpoint'];s['best_summary']=copy.deepcopy(winner['summary'])
        s['best_score']=score(winner['summary'],s['stage'],self.options['thresholds'])
        if before!=s['best_checkpoint'] and s['best_score']>old+.02:s['last_improvement']=s['full_windows']
        atomic_json(self.out/'ranking.json',dict(score_version=SCORE_VERSION,stage=s['stage'],protocol=entry['protocol'],best_checkpoint=s['best_checkpoint'],entries=[dict(checkpoint=x['checkpoint'],evaluation=x['summary']['id'],prior_stage_qualified=prerequisites(x),continuation_safe=motion_safe(x['summary'],s['ranking_reference']),score=score(x['summary'],s['stage'],self.options['thresholds'])) for x in sorted(comparable,key=rank_key,reverse=True)]))
        return before!=s['best_checkpoint'] and s['best_checkpoint']==str(checkpoint)
    def observe(self,summary,checkpoint,auto_recovery=True):
        s=self.state;m=self.options['monitor'];t=self.options['thresholds']
        if not summary.get('full'):return dict(action='continue')
        if s['candidate'] and protocol(summary)!=s['candidate']['protocol']:raise RuntimeError('CANDIDATE_PROTOCOL_MISMATCH')
        if s.get('ranking_protocol') and protocol(summary)!=s['ranking_protocol']:raise RuntimeError('RANKING_PROTOCOL_MISMATCH')
        old=copy.deepcopy(s.get('best_summary'));anchor=s.get('best_checkpoint')
        s['full_windows']+=1;best=self.register(summary,checkpoint)
        current=score(summary,s['stage'],t);skills=assess(summary,s['stage'],t)
        s['last_skills']=skills;s['diagnosis']=self.diagnose(summary)
        result=dict(action='continue',best=best)
        cand=s['candidate']
        if cand:
            if protocol(summary)!=cand['protocol']:raise RuntimeError('CANDIDATE_PROTOCOL_MISMATCH')
            if s['total_updates']-cand['start_update']<m['candidate_updates']:return result
            if cand['arm']=='control':
                cand.update(control_score=current,control_checkpoint=checkpoint,control_summary=compact(summary),arm='adjusted',start_update=s['total_updates'])
                self.event('CANDIDATE_CONTROL_END',checkpoint=checkpoint,score=current)
                return dict(result,action='candidate_adjust',checkpoint=cand['anchor'],diagnosis=cand['diagnosis'])
            accepted=current>cand['control_score']+.02 and motion_safe(summary,cand['control_summary'])
            attempt=dict(diagnosis=cand['diagnosis'],factor=cand.get('factor'),before=cand['before'],after={k:copy.deepcopy(s[k]) for k in cand['before']},anchor=cand['anchor'],control_checkpoint=cand['control_checkpoint'],adjusted_checkpoint=checkpoint,control_score=cand['control_score'],adjusted_score=current,accepted=accepted,evaluation=summary['id'],budget=m['candidate_updates'])
            s['attempts'].append(attempt);self.event('CANDIDATE_COMPARISON',**attempt)
            if not accepted and cand.get('factor'):s['failed_factors'].append(cand['factor'])
            s['candidate']=None;s['last_repair_window']=s['full_windows']
            if not accepted:
                for k,v in cand['before'].items():s[k]=v
                return dict(result,action='rollback',checkpoint=s['best_checkpoint'],reason='candidate_not_better')
        previous_skills=assess(old,s['stage'],t) if old else {}
        lost=[k for k,v in previous_skills.items() if v and not skills.get(k)]
        falls=[r['fall_rate'] for r in summary['rows'] if r['test'] in required(s['stage'])]
        old_falls=[r['fall_rate'] for r in old['rows'] if r['test'] in required(s['stage'])] if old else []
        regression=(bool(old) and motion_safe(old) and not motion_safe(summary,old)) or bool(lost) or (old_falls and max(falls)>max(.2,max(old_falls)+.15))
        if old and protocol(old)==protocol(summary) and regression:
            s['repairs']+=1;s['passes']=0
            self.event('POLICY_REGRESSION',rejected_checkpoint=checkpoint,restore=anchor,lost=lost)
            if s['repairs']>m['max_repairs']:return self.block('REGRESSION_REPAIRS_EXHAUSTED')
            return dict(result,action='rollback',checkpoint=anchor,reason='policy_regression',failed_skills=lost)
        self.update_internal(summary)
        s['passes']=s['passes']+1 if all(skills.values()) else 0
        if s['passes']>=m['consecutive_passes']:
            self.event('CAPABILITY_GATE_PASSED',checkpoint=checkpoint,skills=skills,thresholds=t)
            if s['stage']==3:s['training_status']='SUCCESS';return dict(result,action='success')
            s['stage']+=1;s['passes']=0;s['distribution']=None;s['repairs']=0;s['last_improvement']=s['full_windows']
            self.register(summary,checkpoint)
            return dict(result,action='advance')
        since=s['full_windows']-max(s['last_improvement'],s['last_repair_window'])
        if since>=m['stagnant_windows']:
            if not auto_recovery or s['repairs']>=m['max_repairs']:return self.block('REPAIRS_EXHAUSTED')
            s['repairs']+=1
            s['candidate']=dict(arm='control',evaluation_seeds=summary['seeds'],protocol=protocol(summary),anchor=s['best_checkpoint'],anchor_score=s['best_score'],start_update=s['total_updates'],diagnosis=s['diagnosis'],before={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range','substage']})
            self.event('CANDIDATE_START',**s['candidate'])
            return dict(result,action='candidate_control',checkpoint=s['best_checkpoint'])
        return result
    def update_internal(self,summary):
        s=self.state
        if not summary.get('full') or s['stage']!=0 or self.options.get('variant')!='improved':return
        motion=[r for r in summary['rows'] if r['test']=='forward']
        previous=s['substage']
        if motion_safe(summary):
            s['substage']='1B'
            if motion and all(r['gait_trial_fraction']>=.8 and r['periodic_legs']==4 for r in motion):s['substage']='1C'
        else:s['substage']='1A'
        if previous!=s['substage']:self.event('INTERNAL_CURRICULUM',before=previous,after=s['substage'],evidence=summary['id'])
    def block(self,reason):
        self.state.update(training_status='BLOCKED_NEEDS_REDESIGN',diagnosis=reason)
        self.event('BLOCKED',reason=reason);return dict(action='blocked')
    def adjust(self,diagnosis,summary):
        s=self.state;before={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range','substage']}
        failed=s['failed_factors'];motion=[r for r in summary['rows'] if r['test']=='forward']
        if diagnosis=='SLIDING_REWARD_EXPLOIT':
            if not self.options.get('contact_validated'):raise RuntimeError('CONTACT_DIAGNOSIS_REQUIRED')
            stops=[r for r in summary['rows'] if r['test']=='stop']
            if s.get('substage')=='1C' and any(r['speed_xy']>.03 or r.get('yaw_abs',abs(r['yaw']))>.08 for r in stops):
                factor='stop_sampling:0.30';s['distribution']={'forward':.7,'stop':.3}
            elif motion and min(r['gait_trial_fraction'] for r in motion)>=.8:
                factor='support_slip:1.5';s['weights']['slip']*=1.5
            else:
                factor='continuous_swing:1.5';s['weights']['gait_guide']=max(.15,s['weights']['gait_guide']*1.5)
        elif diagnosis.startswith('PPO_UPDATE_'):
            factor='learning_rate:0.5' if diagnosis.endswith('LARGE') else 'learning_rate:1.5'
            s['ppo']['learning_rate']*=.5 if diagnosis.endswith('LARGE') else 1.5
        else:
            from ..curriculum_v6.commands import DISTRIBUTIONS
            dist=copy.deepcopy(s['distribution'] or DISTRIBUTIONS[s['stage']])
            if diagnosis=='WRONG_DIRECTION':
                factor='failed_direction_sampling:1.5'
                for r in summary['rows']:
                    if r['test'] in dist and any(v<0 for v in r['tracking_ratios']):dist[r['test']]*=1.5
            else:
                factor='stop_sampling:2.0';dist['stop']*=2
            total=sum(dist.values());s['distribution']={k:v/total for k,v in dist.items()}
        signature=factor+':'+hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()[:12]
        if factor in failed or signature in failed:
            for k,v in before.items():s[k]=v
            raise RuntimeError('FAILED_REPAIR_WOULD_REPEAT:'+factor)
        if s['candidate']:s['candidate']['factor']=factor
        self.event('SAFE_PARAMETER_CHANGE',factor=factor,signature=signature,before=before,after={k:copy.deepcopy(s[k]) for k in before},evidence=summary['id'])
        return factor
