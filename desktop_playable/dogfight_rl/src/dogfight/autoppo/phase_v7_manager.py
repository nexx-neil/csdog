"""V7 extension of AutoPPO, reusing SQLite, locks, serial workers and event journal.

No historical network donation. Physical improvement gates every extension.
"""
import os,json,time,uuid,hashlib,signal,subprocess,copy
from pathlib import Path
from .experiment_manager import ExperimentManager,validate_gate
from .storage import Store,atomic_json,canonical
from .config import ROOT,PYTHON
from .resource_monitor import sample
from .phase_v7_search import V7Search,early_physical_trend,prior_course_safe,strict_leg_coverage
from .checkpoint_bank import sha256

class V7Manager(ExperimentManager):
    def __init__(self,base):
        super().__init__(base)
        self.search=V7Search(self.store)
    def publish(self):
        trials=self.store.rows('SELECT * FROM trials ORDER BY created')
        running=[t for t in trials if t['status']=='RUNNING'];active=running[0] if running else None
        latest=self.store.get('latest_metrics',{})
        progress={}
        if active:
            paths=sorted((self.store.base/'trials'/active['id']).glob('*/progress.json'),key=lambda p:p.stat().st_mtime)
            if paths:progress=json.loads(paths[-1].read_text())
        total=self.store.rows('SELECT COALESCE(SUM(observed_updates),0) AS updates,COALESCE(SUM(environment_steps),0) AS steps FROM attempts WHERE trial_id IN (SELECT id FROM trials WHERE rung>=0)')[0]
        try:
            with (self.store.base/'manager.lock').open('a') as probe:
                import fcntl
                fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB);alive=False
        except BlockingIOError:alive=True
        state=self.store.get('status','READY')
        if state in ('RUNNING','ABLATION_RUNNING','LONG_ADAPTIVE_RUNNING') and not alive:state='MANAGER_NOT_RUNNING'
        effective=None
        if active:
            launches=sorted((self.store.base/'trials'/active['id']).glob('*/launch.json'),key=lambda p:p.stat().st_mtime)
            if launches:effective=json.loads(launches[-1].read_text())['options']
        row=dict(target_velocity_range=[.12,.25],effective_parameters=effective,system='CSDog AutoPPO V7',status=state,manager_alive=alive,manager_pid=self.store.get('manager_pid'),current_experiment=json.loads(active['config'])['arm'] if active else None,current_parameters=json.loads(active['config']) if active else None,curriculum=['FORWARD','FORWARD_BACKWARD','YAW','ALL_DIRECTIONS'][self.store.get('stage',0)],total_ppo_updates=total['updates'],environment_steps=total['steps'],current_progress=progress,physical_metrics=latest,best_checkpoint=self.store.get('best_checkpoint'),qualified=latest.get('qualified',False),trials=[{k:t[k] for k in ['id','status','target','progress','checkpoint','diagnosis']} for t in trials],heartbeat=time.time(),diagnosis=self.store.get('diagnosis'))
        atomic_json(self.store.base/'TRAINING_STATUS.json',row)
        text=f"# V7状态\n\n{state}；课程{row['curriculum']}；实验{row['current_experiment']}；已提交更新{total['updates']}；当前进度{progress.get('updates')}。\n\n最佳checkpoint：{row['best_checkpoint']}。物理指标：`{json.dumps(latest,ensure_ascii=False)}`。\n\n相位匹配不等于合格步态。未测数据为null/缺失，不填造值。\n"
        (self.store.base/'STATUS_SUMMARY.md').write_text(text)
        (self.store.base/'reports/V7_TRAINING_STATUS.md').write_text(text)
        return row
    def report(self):
        row=self.publish();events=self.store.rows('SELECT * FROM events ORDER BY id');atomic_json(self.store.base/'search_history.json',events)
        text='# V7等预算对照\n\n128env，seed42，24步/更新，A/B/C/D各250更新（768000环境步），随机初始化；第二轮仅在存在可信物理趋势时延长。\n\n'
        for t in self.store.rows('SELECT * FROM trials ORDER BY created'):
            c=json.loads(t['config']);text+=f"- {c['arm']}：{t['status']}，累计{t['progress']}/{t['target']}更新，checkpoint `{t['checkpoint']}`；物理结果：{t['metrics']}\n"
        text+='\n尚未完成的组不得用于宣称相位或碰撞改进。高度奖励与旧事件奖励没有独立等预算消融，不能作因果结论。\n'
        (self.store.base/'reports/V7_ABLATION_EXPERIMENT_REPORT.md').write_text(text)
        from ..locomotion.phase_guided_v7.plots import learning
        learning(self.store.base)
        from ..locomotion.phase_guided_v7.reporting import generate
        generate(self.store.base)
        return row
    def run_child(self,trial,attempt,smoke=False):
        # Reuse BaseManager's job-tree ownership and monitoring. Only substitute
        # worker entrypoint; no separate training management framework.
        cmd=[str(PYTHON),'-u',str(ROOT/'scripts/autoppo/v7.py'),'_worker','--base',str(self.store.base),'--trial',trial['id'],'--attempt',attempt]
        logfile=self.store.base/'trials'/trial['id']/(attempt+'.log')
        with logfile.open('x') as log:self.child=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True,pass_fds=(self.lock.fileno(),))
        self.store.db.execute('UPDATE attempts SET pid=? WHERE id=?',(self.child.pid,attempt));stop_at=None
        while self.child.poll() is None:
            if self.stop or (self.store.base/'STOP').exists():
                if stop_at is None:self.child.send_signal(signal.SIGTERM);stop_at=time.monotonic()
                elif time.monotonic()-stop_at>180:os.killpg(self.child.pid,signal.SIGKILL)
            self.publish();time.sleep(10)
        self.child.wait();result_path=self.store.base/'trials'/trial['id']/attempt/'result.json';self.child=None
        return json.loads(result_path.read_text()) if result_path.exists() else dict(status='FAILED',error=logfile.read_text(errors='replace')[-6000:])
    def queue(self,arm,target,source=None,rung=0,options=None,mutation=None,source_updates=0):
        c=dict(implementation='phase_guided_v7',arm=arm,seed=42,num_envs=128,stage=self.store.get('stage',0),options=options or {},mutation=mutation,source_updates=source_updates)
        digest=hashlib.sha256(canonical(dict(c,target=target,source=source)).encode()).hexdigest()
        trial=self.store.add_trial(c,rung,0,target,source,digest)
        if trial:self.store.db.execute('UPDATE trials SET rung=? WHERE id=?',(rung,trial))
        return trial
    def run(self):
        validate_gate(self.store.base)
        self.acquire();self.store.repair_orphans();self.reconcile_v7_checkpoints()
        if self.store.get('status','').startswith('BLOCKED'):self.report();return
        # Validate actual collision and software evidence, not a prefilled PASS.
        collision=json.loads((self.store.base/'collision_physics.json').read_text())
        for name in ['collision_original','collision_sole_candidate']:
            s=collision[name]['summary']
            if not (.30<s['height']<.39 and s['tilt']<.1 and s['torque_rms']<2.5 and min(s['force'])>3 and s['falls']==0):raise RuntimeError('Collision physical gate failed: '+name)
        self.store.set('manager_pid',os.getpid());self.store.set('status','ABLATION_RUNNING');self.store.event('V7_MANAGER_START')
        for sig in (signal.SIGINT,signal.SIGTERM):signal.signal(sig,lambda *a:setattr(self,'stop',True))
        if not self.store.rows('SELECT id FROM trials'):
            for arm in 'ABCD':self.queue(arm,250)
        try:
            while not self.stop and not (self.store.base/'STOP').exists():
                claimed=self.store.claim()
                if not claimed:
                    rows=self.store.rows('SELECT * FROM trials WHERE rung=0')
                    if any(t['status']!='COMPLETE' for t in rows):self.store.set('status','BLOCKED_INCOMPLETE_ABLATION');break
                    if not self.store.rows('SELECT id FROM trials WHERE rung=1'):
                        promising=[]
                        baseline=next(json.loads(t['metrics']) for t in rows if json.loads(t['config'])['arm']=='A')
                        for t in rows:
                            m=json.loads(t['metrics'])
                            strict_trend=m['actual_speed']>.06 and m['fall_fraction']<.15 and m['min_swing_per_env']>=1 and min(m['clearance_peak'])>=.008 and m['shin_rate']<.02 and m['support_slip']<.2
                            if strict_trend or early_physical_trend(m,baseline):promising.append(t)
                        promising.sort(key=lambda t:V7Search.score(json.loads(t['metrics']))+.25*json.loads(t['metrics']).get('early_swing_q25',0),reverse=True)
                        if not promising:self.store.set('status','BLOCKED_NO_PHYSICAL_TREND');self.store.set('diagnosis','All equal-budget arms lack verified four-leg movement; redesign before more updates');break
                        for t in promising[:2]:self.queue(json.loads(t['config'])['arm'],1000,t['checkpoint'],rung=1,source_updates=250)
                        continue
                    if not self.plan_long_candidate():break
                    continue
                trial,attempt=claimed;result=self.run_child(trial,attempt);now=time.time();status=result['status'];completed=result.get('updates',trial['progress']);observed=max(0,completed-trial['progress'])
                if trial['source'] and not trial['checkpoint']:observed=max(0,completed-json.loads(trial['config']).get('source_updates',250))
                with self.store.transaction():
                    self.store.db.execute('UPDATE attempts SET status=?,end=?,observed_updates=?,environment_steps=?,checkpoint=? WHERE id=?',(status,now,observed,observed*128*24,result.get('checkpoint'),attempt))
                    self.store.db.execute('UPDATE trials SET status=?,progress=?,checkpoint=?,metrics=?,diagnosis=?,updated=? WHERE id=?',('QUEUED' if status=='STOPPED' else status,completed,result.get('checkpoint'),canonical(result.get('metrics')) if result.get('metrics') else None,result.get('error'),now,trial['id']))
                    self.store.event('V7_WORKER_RESULT',trial['id'],result=result)
                if status=='COMPLETE':
                    m=result['metrics'];self.store.set('latest_metrics',m)
                    self.register_result(trial,result)
                elif status=='STOPPED':self.stop=True
                else:
                    error=result.get('error','');recoverable=any(x in error.lower() for x in ['out of memory','process_exit','timeout'])
                    if recoverable and trial['retries']<2:
                        self.store.db.execute("UPDATE trials SET status='QUEUED',retries=retries+1 WHERE id=?",(trial['id'],));self.store.event('V7_RECOVERABLE_PROCESS_RETRY',trial['id'],reason=error)
                    else:self.store.set('status','BLOCKED_WORKER_FAILURE');self.store.set('diagnosis',error);break
                self.report()
            if self.stop or (self.store.base/'STOP').exists():self.store.set('status','STOPPED')
        finally:self.report();self.store.close();self.lock.close()
        return 0

    def register_result(self,trial,result):
        m=result['metrics'];config=json.loads(trial['config']);path=result['checkpoint']
        existing=self.store.rows('SELECT id FROM checkpoints WHERE path=?',(path,));cp=existing[0]['id'] if existing else 'v7_'+uuid.uuid4().hex
        metadata=dict(path=path,options=config.get('options',{}),stage=config.get('stage',0),trial_id=trial['id'],qualified=m['qualified'],protocol='v7-geometry-500hz-v2',source=trial['source'])
        self.store.db.execute('INSERT OR IGNORE INTO checkpoints VALUES(?,?,?,?,?,?,?)',(cp,path,sha256(path),trial['id'],canonical(metadata),canonical(m),time.time()))
        stage=config.get('stage',0);prior_safe=prior_course_safe(m,stage)
        ranks=dict(best_forward=max(0.,1-abs(m['actual_speed']-.2)/.2),best_gait=m['min_swing_per_env']+strict_leg_coverage(m)+.02*m.get('early_swing_q25',0)+m['phase_match'],best_low_slip=-m['support_slip'],best_stop=-m['stop_speed']-m['stop_yaw'],best_balanced=V7Search.score(m))
        for name,value in ranks.items():
            key='v7_rank_stage'+str(stage)+'_'+name;previous=self.store.get(key,-1e30)
            if prior_safe and value>previous:
                self.store.set(key,value);self.store.db.execute('INSERT INTO bank_names VALUES(?,?) ON CONFLICT(name) DO UPDATE SET checkpoint_id=excluded.checkpoint_id',(name,cp))
        score=V7Search.score(m);old=self.store.get('v7_best_score',-1e30)
        if prior_safe and score>old+.02:
            self.store.set('v7_best_score',score);self.store.set('best_checkpoint',path);self.store.set('best_trial',trial['id']);self.store.set('stagnant_candidates',0)
        elif trial['rung']>=2:self.store.set('stagnant_candidates',self.store.get('stagnant_candidates',0)+1)
        if not m['qualified']:self.store.set('v7_passes_'+str(config.get('stage',0)),0)
        if m['qualified'] and m.get('protocol')=='v7-geometry-500hz-v3' and m.get('independent_confirmation',{}).get('qualified'):
            stage=config.get('stage',0);count=self.store.get('v7_passes_'+str(stage),0)+1;self.store.set('v7_passes_'+str(stage),count)
            if count>=3 and stage==self.store.get('stage',0):
                if stage<3:
                    self.store.set('stage',stage+1);self.store.set('v7_best_score',-1e30);self.store.set('stagnant_candidates',0);self.store.event('V7_COURSE_ADVANCED',checkpoint=path,stage=stage+1)
                else:self.store.set('status','SUCCESS');self.store.event('V7_UNIFIED_ACTOR_ACCEPTED',checkpoint=path)
        self.store.event('V7_CANDIDATE_DECISION',trial['id'],reason=V7Search.diagnose(m),parameter_change=config.get('mutation'),starting_checkpoint=trial['source'],budget=trial['target']-config.get('source_updates',0),actual_metrics=m,accepted=prior_safe and score>old+.02,checkpoint=path)
    def reconcile_v7_checkpoints(self):
        import torch
        from ..locomotion.spot_v4.contracts import finite_tree
        for trial in self.store.rows("SELECT * FROM trials WHERE status='QUEUED'"):
            candidates=[]
            for record in (self.store.base/'trials'/trial['id']).glob('*/latest.json'):
                try:
                    cp=json.loads(record.read_text());data=torch.load(cp['path'],map_location='cpu',weights_only=False);meta=data['infos']['v7']
                    if not finite_tree(data) or meta['updates']!=cp['updates']:continue
                    if meta['updates']>trial['progress']:candidates.append(cp)
                except Exception:continue
            if candidates:
                cp=max(candidates,key=lambda x:x['updates']);self.store.db.execute('UPDATE trials SET checkpoint=?,progress=? WHERE id=?',(cp['path'],cp['updates'],trial['id']));self.store.event('V7_RECOVER_COMMITTED_CHECKPOINT',trial['id'],checkpoint=cp)
    def plan_long_candidate(self):
        if sample(self.store.base)['disk_free_gib']<self.system['minimum_disk_gib']:
            self.store.set('status','BLOCKED_DISK_SPACE');return False
        if self.store.get('status')=='SUCCESS':return False
        if self.store.get('stagnant_candidates',0)>=6:
            self.store.set('status','BLOCKED_NO_PROGRESS');self.store.set('diagnosis','Six bounded gait candidates failed to improve independent physical metrics');return False
        rows=self.store.rows("SELECT * FROM trials WHERE rung>=1 AND status='COMPLETE'")
        viable=[t for t in rows if (lambda m:m['actual_speed']>.08 and m['fall_fraction']<.1 and m['min_swing_per_env']>=2 and min(m['clearance_peak'])>=.01 and m['support_slip']<.15)(json.loads(t['metrics']))]
        viable=[t for t in viable if prior_course_safe(json.loads(t['metrics']),json.loads(t['config']).get('stage',0))]
        if not viable:
            return self.diagnostic_frequency_sweep(rows)
        stage=self.store.get('stage',0)
        current=[t for t in viable if json.loads(t['config']).get('stage',0)==stage]
        if current:viable=current
        donor=max(viable,key=lambda t:V7Search.score(json.loads(t['metrics'])));m=json.loads(donor['metrics']);c=json.loads(donor['config'])
        index=self.store.get('long_candidate_index',0)
        for offset in range(8):
            options,mutation=V7Search.propose(c.get('options',{}),m,index+offset)
            options['stage']=self.store.get('stage',0)
            trial=self.queue(c['arm'],donor['progress']+250,donor['checkpoint'],rung=2,options=options,mutation=mutation,source_updates=donor['progress'])
            if trial:
                self.store.set('long_candidate_index',index+offset+1);self.store.set('status','LONG_ADAPTIVE_RUNNING')
                self.store.event('V7_BOUNDED_LONG_CANDIDATE',mutation=mutation,source=donor['checkpoint'],budget=250)
                return True
        self.store.set('status','BLOCKED_SEARCH_EXHAUSTED');self.store.set('diagnosis','No distinct targeted gait candidate remains within validated parameter bounds')
        return False

    def diagnostic_frequency_sweep(self,rows):
        # A separate finite diagnostic experiment, not an unlimited long run.
        # Includes unchanged-frequency control; all start from the SAME donor.
        if self.store.get('diagnostic_frequency_sweep_started'):
            self.store.set('status','BLOCKED_DIAGNOSTIC_NO_GAIT');self.store.set('diagnosis','Four matched-budget slip-scale/frequency candidates completed without the strict four-leg/low-slip entry evidence; inspect geometry, phase and action response before more GPU work');return False
        near=[]
        for t in rows:
            m=json.loads(t['metrics'])
            if t['progress']>=1000 and m.get('early_swing_q25',0)>=3 and m['phase_match']>=.7 and .1<m['actual_speed']<.35 and m['support_slip']<.2 and m['fall_fraction']<.1 and m['shin_rate']<.02:near.append(t)
        if not near:
            self.store.set('status','BLOCKED_NO_SUSTAINED_TREND');self.store.set('diagnosis','No second-round configuration supports repeated four-leg physical motion with a credible gait trend');return False
        donor=max(near,key=lambda t:(strict_leg_coverage(json.loads(t['metrics'])),V7Search.score(json.loads(t['metrics']))));config=json.loads(donor['config']);before=config.get('options',{}).get('frequency',1.5)
        for frequency,slip_mode in ((1.5,'raw'),(1.5,'log'),(1.,'log'),(2.,'log')):
            options=copy.deepcopy(config.get('options',{}));options.update(frequency=frequency,slip_mode=slip_mode,stage=self.store.get('stage',0))
            mutation=dict(reason='ASYMMETRIC_CLEARANCE_AND_SLIP_DIAGNOSTIC',key='frequency',before=before,after=frequency,slip_mode_before='raw',slip_mode_after=slip_mode,matched_budget_control=frequency==before and slip_mode=='raw')
            self.queue(config['arm'],donor['progress']+250,donor['checkpoint'],rung=2,options=options,mutation=mutation,source_updates=donor['progress'])
        self.store.set('diagnostic_frequency_sweep_started',True);self.store.set('status','DIAGNOSTIC_RUNNING')
        self.store.event('V7_FREQUENCY_DIAGNOSTIC_SWEEP',source=donor['checkpoint'],candidates=[dict(frequency=f,slip_mode=s) for f,s in ((1.5,'raw'),(1.5,'log'),(1.,'log'),(2.,'log'))],budget_each=250,formal_acceptance_unchanged=True)
        return True
