"""Local, deterministic capability gate and bounded evidence-based recovery state machine.

No simulation or torch import: usable by a separate status CLI and unit tests.
"""
import copy,json,os,time
from pathlib import Path
STAGES=['FORWARD','FORWARD_BACKWARD','YAW','ALL_DIRECTIONS']
BASIC=['stop','forward','backward','yaw_positive','yaw_negative']
COMBINED=['forward_left','forward_right','backward_left','backward_right']
TRANSITIONS=['forward_stop','backward_stop','left_right','forward_backward','continuous']
BEST_NAMES=['best_forward.pt','best_forward_backward.pt','best_yaw.pt','best_all_directions.pt']
LEGS=['LF','RF','LR','RR']

def atomic_json(path,data):
    path=Path(path);tmp=path.with_name('.'+path.name+'.tmp')
    with tmp.open('w') as f:
        json.dump(data,f,indent=2,allow_nan=False);f.flush();os.fsync(f.fileno())
    os.replace(tmp,path)

def required(stage):
    return BASIC[:2] if stage==0 else BASIC[:3] if stage==1 else BASIC if stage==2 else BASIC+COMBINED+TRANSITIONS

def row_pass(r,t):
    if not r.get('valid',False) or r['fall_rate']>t['fall_rate']:return False
    if r['is_stop']:
        return r['speed_xy']<=t['stop_speed'] and r.get('yaw_abs',abs(r['yaw']))<=t['stop_yaw'] and r['tilt']<.25
    if not all(t['tracking_min']<=v<=t['tracking_max'] for v in r['tracking_ratios']):return False
    if r['lateral_speed']>t['lateral_speed'] or r['support_slip_speed']>t['support_slip']:return False
    if r['pure_yaw'] and r['speed_xy']>t['turn_translation']:return False
    if r['periodic_legs']<t['periodic_legs'] or r['gait_trial_fraction']<t['trial_pass_fraction']:return False
    return all(r[l+'_swing_ratio']>=t['swing_ratio'] for l in LEGS) and r['tilt']<.35

def assess(summary,stage,t):
    rows=summary['rows'];skills={}
    for name in required(stage):
        found=[r for r in rows if r['test']==name]
        skills[name]=bool(found) and all(row_pass(r,t) for r in found)
    return skills

def score(summary,stage,t):
    rows=[r for r in summary['rows'] if r['test'] in required(stage)]
    if not rows:return -1e6
    # Equal skill weighting, and gait/fall feasibility before tracking gains.
    by={}
    for r in rows:
        value=2*row_pass(r,t)-5*r['fall_rate']
        if not r['is_stop']:
            value+=sum(max(-1.,min(1.,v)) for v in r['tracking_ratios'])/max(1,len(r['tracking_ratios']))
            value+=.5*r['gait_trial_fraction']-min(1.,r['support_slip_speed']/.08)
        else:value-=min(1.,r['speed_xy']/.03)
        by.setdefault(r['test'],[]).append(value)
    return sum(sum(x)/len(x) for x in by.values())/len(by)

class Supervisor:
    def __init__(self,out,options,state=None):
        self.out=Path(out);self.options=options
        self.state=copy.deepcopy(state) if state else dict(stage=0,total_updates=0,environment_steps=0,training_seconds=0.,stage_updates=[0,0,0,0],training_status='RUNNING',passes=0,best_score=-1e6,best_checkpoint=None,best_summary=None,last_improvement=0,full_windows=0,repairs=0,history=[],candidate=None,weights=copy.deepcopy(options['weights']),ppo=copy.deepcopy(options['ppo']),distribution=None,speed_range=[.12,.25],diagnosis=None,quality_level=0)
    def event(self,kind,**data):
        row=dict(time=time.time(),update=self.state['total_updates'],stage=STAGES[self.state['stage']],kind=kind,**data)
        self.state['history'].append(row)
        with (self.out/'events.jsonl').open('a') as f:f.write(json.dumps(row,allow_nan=False)+'\n')
    def publish(self,summary=None):
        s=self.state;row={**s,'stage_name':STAGES[s['stage']],'heartbeat_unix':time.time()}
        if summary:s['last_evaluation']=summary;row['last_evaluation']=summary
        for field,name in [('forward_tracking_ratio','forward'),('backward_tracking_ratio','backward'),('yaw_positive_tracking_ratio','yaw_positive'),('yaw_negative_tracking_ratio','yaw_negative')]:
            source=summary or s.get('last_evaluation') or {'rows':[]}
            ratios=[v for r in source['rows'] if r['test']==name for v in r['tracking_ratios']]
            row[field]=sum(ratios)/len(ratios) if ratios else None
        row['gait_qualified']=bool(source['rows'] and all(r['is_stop'] or r['periodic_legs']==4 for r in source['rows'] if r['test'] in required(s['stage'])))
        atomic_json(self.out/'TRAINING_STATUS.json',row)
        lines=[f"# V6 {s['training_status']}",f"Stage: {STAGES[s['stage']]} | PPO updates: {s['total_updates']} | samples: {s['environment_steps']}",f"Diagnosis: {s['diagnosis']} | consecutive full passes: {s['passes']}",f"Best: {s['best_checkpoint']} | repairs: {s['repairs']}"]
        if summary:
            for name in required(s['stage']):
                rs=[r for r in summary['rows'] if r['test']==name]
                if rs:lines.append(f"{name}: tracking={[r['tracking_ratios'] for r in rs]}, falls={max(r['fall_rate'] for r in rs):.3f}, periodic legs={min(r['periodic_legs'] for r in rs)}")
        (self.out/'STATUS_SUMMARY.md').write_text('\n\n'.join(lines)+'\n')
    def diagnose(self,summary):
        rs=[r for r in summary['rows'] if r['test'] in required(self.state['stage']) and not r['is_stop']]
        if any(any(v<-.1 for v in r['tracking_ratios']) for r in rs):return 'WRONG_DIRECTION'
        if any(any(v>.5 for v in r['tracking_ratios']) and r['periodic_legs']<4 and r['support_slip_speed']>.04 for r in rs):return 'SLIDING_REWARD_EXPLOIT'
        if rs and all(max(r['tracking_ratios'],default=0)<.15 and r['periodic_legs']==0 for r in rs):return 'STANDING_LOCAL_OPTIMUM'
        if summary.get('ppo',{}).get('kl',.01)>.1:return 'PPO_UPDATE_TOO_LARGE'
        if summary.get('ppo',{}).get('kl',.01)<1e-5:return 'PPO_UPDATE_TOO_SMALL'
        return 'LEARNING_STAGNATION'
    def observe(self,summary,checkpoint,auto_recovery=True):
        """Return actions; caller performs checkpoint I/O and applies exact saved parameters."""
        s=self.state;t=self.options['thresholds'];m=self.options['monitor']
        if summary.get('full') is False:return {'action':'continue'}
        s['full_windows']+=1;s['diagnosis']=self.diagnose(summary)
        current=score(summary,s['stage'],t);skills=assess(summary,s['stage'],t)
        s['last_skills']=skills
        cand=s['candidate']
        if cand:
            if s['total_updates']-cand['start_update']<m['candidate_updates']:return {'action':'continue'}
            if cand['arm']=='control':
                cand['control_score']=current;cand['control_checkpoint']=checkpoint;cand['arm']='adjusted';cand['start_update']=s['total_updates']
                self.event('CANDIDATE_CONTROL_END',score=current,checkpoint=checkpoint)
                return dict(action='candidate_adjust',checkpoint=cand['anchor'],diagnosis=cand['diagnosis'])
            accepted=current>cand['control_score']+.02
            self.event('CANDIDATE_COMPARISON',diagnosis=cand['diagnosis'],control_score=cand['control_score'],adjusted_score=current,accepted=accepted,budget_per_arm=m['candidate_updates'],environment_steps_per_arm=m['candidate_updates']*summary['num_envs']*24,parameters_before=cand['before'],parameters_after={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range']})
            s['candidate']=None;s['last_improvement']=s['full_windows']
            if not accepted:
                for k,v in cand['before'].items():s[k]=v
                # Neither branch may replace the verified anchor if it is worse.
                target=cand['control_checkpoint'] if cand['control_score']>cand['anchor_score']+.02 else cand['anchor']
                return dict(action='rollback',checkpoint=target,reason='candidate_not_better')
        old=s['best_summary']
        if old and not s['candidate']:
            previous=assess(old,s['stage'],t)
            lost=[name for name,ok in previous.items() if ok and not skills.get(name,False)]
            old_fall=max(r['fall_rate'] for r in old['rows'] if r['test'] in required(s['stage']))
            new_fall=max(r['fall_rate'] for r in summary['rows'] if r['test'] in required(s['stage']))
            if lost or new_fall>max(.2,old_fall+.15):
                s['passes']=0;s['repairs']+=1;s['diagnosis']='POLICY_REGRESSION'
                self.event('POLICY_REGRESSION',lost=lost,rejected_checkpoint=checkpoint,restore=s['best_checkpoint'])
                if s['repairs']>m['max_repairs']:s['training_status']='BLOCKED_NEEDS_REDESIGN';return {'action':'blocked'}
                return dict(action='rollback',checkpoint=s['best_checkpoint'],reason='policy_regression',failed_skills=lost)
        actions={}
        if current>s['best_score']+.02:
            s['best_score']=current;s['best_checkpoint']=checkpoint;s['best_summary']=summary;s['last_improvement']=s['full_windows']
            actions['best']=True
        s['passes']=s['passes']+1 if all(skills.values()) else 0
        if s['passes']>=m['consecutive_passes']:
            self.event('CAPABILITY_GATE_PASSED',skills=skills,evaluation=summary['id'],thresholds=t,checkpoint=checkpoint)
            if s['stage']==3:s['training_status']='SUCCESS';return dict(action='success',**actions)
            s['stage']+=1;s['passes']=0;s['best_score']=score(summary,s['stage'],t);s['best_summary']=summary;s['best_checkpoint']=checkpoint;s['distribution']=None;s['last_improvement']=s['full_windows'];s['repairs']=0
            return dict(action='advance',**actions)
        # Quality regularization increases only after measured repeated swings, once per stage.
        motion=[r for r in summary['rows'] if r['test'] in required(s['stage']) and not r['is_stop']]
        if motion and all(r['gait_trial_fraction']>=.5 for r in motion) and s['quality_level']<=s['stage']:
            before=copy.deepcopy(s['weights'])
            for key,factor,limit in [('smoothness',1.5,-.03),('posture',1.5,-.15),('slip',1.5,-1.)]:s['weights'][key]=max(limit,s['weights'][key]*factor)
            s['quality_level']=s['stage']+1;self.event('QUALITY_REWARD_CHANGE',before=before,after=s['weights'],evidence=summary['id'])
        if s['full_windows']-s['last_improvement']>=m['stagnant_windows']:
            if not auto_recovery:s['training_status']='BLOCKED_NEEDS_REDESIGN';return {'action':'blocked'}
            if s['repairs']>=m['max_repairs']:
                s['training_status']='BLOCKED_NEEDS_REDESIGN';self.event('REPAIRS_EXHAUSTED',diagnosis=s['diagnosis']);return {'action':'blocked'}
            s['repairs']+=1;s['passes']=0
            s['candidate']=dict(arm='control',evaluation_seeds=summary.get('seeds',[103,307,911,1301]),anchor=s['best_checkpoint'],anchor_score=s['best_score'],start_update=s['total_updates'],diagnosis=s['diagnosis'],before={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range']})
            self.event('CANDIDATE_START',**s['candidate'])
            return dict(action='candidate_control',checkpoint=s['best_checkpoint'])
        return dict(action='continue',**actions)
    def adjust(self,diagnosis,summary):
        s=self.state;before={k:copy.deepcopy(s[k]) for k in ['weights','ppo','distribution','speed_range']};attempt=s['repairs']
        # One main factor per candidate. No hardware/model/threshold changes.
        if diagnosis=='SLIDING_REWARD_EXPLOIT':
            s['weights']['swing']=min(1.,s['weights']['swing']*2)
            factor='completed_swing_incentive'
        elif diagnosis in ['PPO_UPDATE_TOO_LARGE','PPO_UPDATE_TOO_SMALL']:
            factor='learning_rate';scale=.5 if diagnosis.endswith('LARGE') else 1.5
            s['ppo']['learning_rate']=max(3e-5,min(3e-4,s['ppo']['learning_rate']*scale))
        elif diagnosis=='WRONG_DIRECTION':
            from .commands import DISTRIBUTIONS
            dist=copy.deepcopy(s['distribution'] or DISTRIBUTIONS[s['stage']])
            for r in summary['rows']:
                if r['test'] in dist and any(v<0 for v in r['tracking_ratios']):dist[r['test']]*=1.5
            total=sum(dist.values());s['distribution']={k:v/total for k,v in dist.items()};factor='failed_direction_sampling'
        elif attempt==1:
            for k in ['smoothness','posture','acceleration']:s['weights'][k]*=.5
            factor='soft_motion_costs'
        elif attempt==2:factor='exploration_scale' # Actual std changed by caller, capped at .65.
        else:s['speed_range']=[.12,.18];factor='command_amplitude'
        self.event('SAFE_PARAMETER_CHANGE',factor=factor,before=before,after={k:copy.deepcopy(s[k]) for k in before},evidence=summary['id'])
        return factor
    def report(self):
        s=self.state
        text=['# CURRICULUM PPO V6 FINAL REPORT',f"Status: **{s['training_status']}**; stage: {STAGES[s['stage']]}",f"Total PPO updates: {s['total_updates']}; environment samples: {s['environment_steps']}; training seconds: {s['training_seconds']:.1f}",f"Per-stage executed updates (includes rejected branches): {s['stage_updates']}",f"Best checkpoint: {s['best_checkpoint']}",f"Diagnosis: {s['diagnosis']}","Learning state restoration includes actor, critic, optimizer, exploration, LR, RNG and supervisor. Simulation is reset on resume; PhysX solver caches are not restored and resume is not bit-exact.","No motion success is inferred from reward or update count.","## Latest evaluation",'```json',json.dumps(s.get('last_evaluation'),indent=2,ensure_ascii=False),'```',"## Gate / repair / rollback history",'```json',json.dumps(s['history'],indent=2,ensure_ascii=False),'```']
        (self.out/'CURRICULUM_PPO_V6_FINAL_REPORT.md').write_text('\n\n'.join(text)+'\n')
