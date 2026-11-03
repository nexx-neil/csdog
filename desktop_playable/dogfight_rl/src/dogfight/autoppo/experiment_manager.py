"""Persistent serial search service. Holds an inherited lock for the entire job tree."""
from pathlib import Path
import copy,json,fcntl,os,signal,subprocess,time,hashlib,uuid
import yaml
from .config import ROOT,BASE,PYTHON,default_options
from .storage import Store,atomic_json,canonical
from .search_optimizer import SearchOptimizer
from .checkpoint_bank import CheckpointBank
from .motion_evaluator import score,metrics,safe,qualified
from .recovery_manager import RecoveryManager
from .curriculum_manager import CurriculumManager
from .resource_monitor import sample,prune_temporary

STAGES=['FORWARD','FORWARD_BACKWARD','YAW','ALL_DIRECTIONS']

def source_hashes():
    files=list((ROOT/'src/dogfight/autoppo').glob('*.py'))+list((ROOT/'src/dogfight/locomotion').rglob('*.py'))+list((ROOT/'scripts/autoppo').glob('*.py'))+list((ROOT/'configs/autoppo').glob('*.yaml'))+list((ROOT/'tests').glob('test_autoppo*.py'))
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}

def validate_gate(base):
    gate_path=Path(base)/'reports/VALIDATION_GATE.json'
    if not gate_path.exists():raise RuntimeError('BLOCKED: validation gate is missing')
    gate=json.loads(gate_path.read_text())
    required=['gait','reward_timing','physical_evaluation','checkpoint_protection','search','recovery','ppo_smoke']
    if not all(gate.get('checks',{}).get(k)== 'PASS' for k in required):raise RuntimeError('BLOCKED: a required validation check did not pass')
    if gate.get('source_hashes')!=source_hashes():raise RuntimeError('BLOCKED: implementation changed after validation')
    for item in gate.get('evidence',[]):
        p=Path(item['path'])
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('BLOCKED: validation evidence changed')
    return gate

class ExperimentManager:
    def __init__(self,base=BASE):
        self.store=Store(base);(self.store.base/'reports').mkdir(exist_ok=True);self.system=yaml.safe_load((ROOT/'configs/autoppo/system.yaml').read_text())
        self.search=SearchOptimizer(self.store);self.bank=CheckpointBank(self.store)
        self.curriculum=CurriculumManager(self.store,default_options()['thresholds'])
        self.lock=None;self.stop=False;self.child=None
    def acquire(self):
        self.lock=(self.store.base/'manager.lock').open('a')
        try:fcntl.flock(self.lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise RuntimeError('An AutoPPO manager or its worker already holds the lab lock')
    def initialize(self,audit):
        if self.store.get('initialized'):return
        audit=Path(audit)
        results=json.loads((audit/'results.json').read_text())
        if not (audit/'DONE.json').exists():raise RuntimeError('Historical physical evaluation incomplete')
        imported={r['metadata'].get('historical_name') for r in self.bank.entries()}
        for name,result in results.items():
            if name in imported:continue
            panel=json.loads((audit/name/'evaluation_common.json').read_text())
            m=metrics(panel,0)
            self.bank.register(result['checkpoint'],m,options=default_options(),extra=dict(historical_name=name,initialization_only=True))
        self.store.set('initialized',True);self.store.set('stage',0);self.store.set('generation',0)
        self.store.set('status','READY');self.store.set('stagnant_batches',0)
        best=self.bank.names().get('best_balanced')
        if not best:raise RuntimeError('No safe evaluated historical donor')
        self.store.set('best_metrics',best['metrics']);self.store.set('generation_best_score',score(best['metrics']))
    def publish(self):
        active=self.store.rows("SELECT * FROM trials WHERE status='RUNNING'")
        trials=self.store.rows('SELECT id,status,progress,target,rung,generation,stage,score,diagnosis,checkpoint FROM trials ORDER BY created')
        names=self.bank.names();best=names.get('best_balanced');m=best['metrics'] if best else {}
        totals=self.store.rows('SELECT COALESCE(SUM(observed_updates),0) AS updates,COALESCE(SUM(environment_steps),0) AS steps,COALESCE(SUM(wall_seconds),0) AS seconds FROM attempts')[0]
        attempts=self.store.rows("SELECT pid,trial_id,id,start FROM attempts WHERE status='RUNNING'")
        status=self.store.get('status','READY');stage=self.store.get('stage',0)
        row=dict(system='CSDog AutoPPO Lab',status=status,curriculum_stage=STAGES[stage],
             search_generation=self.store.get('generation',0),active_trial=active[0]['id'] if active else None,
             total_ppo_updates=totals['updates'],environment_steps=totals['steps'],completed_gpu_worker_seconds=totals['seconds'],
             historical_lineage_excluded_from_new_work_totals=True,best_checkpoint=best['path'] if best else None,
             forward_velocity=m.get('forward_velocity'),complete_stride_count=m.get('complete_stride_count'),
             support_slip=m.get('support_slip'),stop_linear_speed=m.get('stop_linear_speed'),stop_yaw_rate=m.get('stop_yaw_rate'),
             completed_experiments=sum(t['status'] in ['COMPLETE','PROMOTED','ELIMINATED'] for t in trials),
             failed_experiments=sum(t['status']=='FAILED' for t in trials),trials=trials,
             checkpoint_bank={k:{'id':v['id'],'path':v['path'],'metrics':v['metrics']} for k,v in names.items()},
             manager_pid=os.getpid() if self.lock else self.store.get('manager_pid'),active_processes=attempts,
             heartbeat_unix=time.time(),resources=sample(self.store.base),diagnosis=self.store.get('diagnosis'))
        atomic_json(self.store.base/'TRAINING_STATUS.json',row)
        text=f"# CSDog AutoPPO Lab\n\n{status} | Stage {stage+1}: {STAGES[stage]} | Generation {row['search_generation']}\n\n"
        text+=f"Active trial: {row['active_trial']} | completed experiments: {row['completed_experiments']} | new PPO updates: {totals['updates']} | samples: {totals['steps']}\n\n"
        text+=f"Best: {row['best_checkpoint']}\n\nForward {row['forward_velocity']} m/s; cycles {row['complete_stride_count']}; slip {row['support_slip']} m/s; stop {row['stop_linear_speed']} m/s / {row['stop_yaw_rate']} rad/s.\n\n"
        text+='Best is a relative ranking, not a claim of qualified walking.\n'
        (self.store.base/'STATUS_SUMMARY.md').write_text(text)
        return row
    def donors(self):
        names=self.bank.names();result=[];seen=set()
        stage=self.store.get('stage',0)
        order=([f'best_stage_{stage}','best_stage_qualified'] if stage else [])+['best_balanced','best_gait','best_low_slip','best_stop','best_forward']
        for name in order:
            d=names.get(name)
            if d and d['id'] not in seen:
                if stage and name not in [f'best_stage_{stage}','best_stage_qualified'] and not (d.get('stage')==stage and d.get('prior_stage_qualified')):continue
                result.append(d);seen.add(d['id'])
        return result[:3]
    def new_generation(self):
        generation=self.store.get('generation',0)+1;stage=self.store.get('stage',0)
        with self.store.transaction():
            self.store.set('generation',generation);self.store.set('generation_stage',stage)
            self.store.set('generation_building',True)
            self.store.set('batch_start_score',score(self.store.get('best_metrics')))
        self.complete_generation()
    def complete_generation(self):
        generation=self.store.get('generation');stage=self.store.get('generation_stage')
        existing=self.store.rows('SELECT id FROM trials WHERE generation=?',(generation,))
        missing=self.system['population']-len(existing)
        ids=[]
        if missing>0:
            ids=self.search.generate(generation,stage,self.donors(),self.store.get('diagnosis'),count=missing,seed_offset=len(existing))
        with self.store.transaction():
            self.store.set('generation_building',False)
            self.store.event('SEARCH_BATCH_START',generation=generation,trials=[r['id'] for r in existing]+ids,stage=stage)
    def adopt_result(self,trial,attempt,result):
        now=time.time();trial_id=trial['id'];config=json.loads(trial['config'])
        status=result['status']
        if status in ['COMPLETE','REJECTED']:
            m=result['metrics'];panel=result['panel'];diagnosis=RecoveryManager.diagnose(m,self.store.get('best_metrics'))
            self.store.db.execute("UPDATE trials SET status=?,metrics=?,score=?,diagnosis=?,updated=? WHERE id=?",('COMPLETE' if status=='COMPLETE' else 'FAILED',canonical(m),score(m),diagnosis,now,trial_id))
            previous_ok=config['stage']==0 or qualified(panel,config['stage']-1,config['options']['thresholds'])
            donor=self.bank.register(result['checkpoint'],m,trial_id,panel=panel,options=config['options'],
                    extra=dict(parent_checkpoint=trial['source'],restoration_mode=result.get('restore_mode',config['restore_mode']),
                               trial_progress=result['progress'],generation=trial['generation'],seed=config['seed'],
                               reproducible_config=config,attempt=attempt,prior_stage_qualified=previous_ok))
            old=self.store.get('best_metrics')
            # Only compatible protocols may be compared; initial donors already
            # have this exact physical protocol. Preserve prior-stage qualifications.
            previous_ok=config['stage']==0 or qualified(panel,config['stage']-1,config['options']['thresholds'])
            if safe(m) and previous_ok and (old is None or (m['protocol']==old['protocol'] and score(m)>score(old)+.02)):
                self.store.set('best_metrics',m);self.store.set('best_trial',trial_id)
                self.store.event('RELIABLE_IMPROVEMENT',trial_id,before=old,after=m,checkpoint=donor['path'])
            self.store.set('diagnosis',diagnosis)
            advanced=self.curriculum.observe(panel,result['checkpoint'])
            if advanced:
                self.store.set('stagnant_batches',0)
                new_stage=self.store.get('stage')
                if new_stage!=config['stage']:
                    self.store.set('best_metrics',metrics(panel,new_stage))
                    self.store.db.execute("UPDATE trials SET status='ELIMINATED',diagnosis='COURSE_ADVANCED' WHERE status='QUEUED' AND stage<?",(new_stage,))
        elif status=='INTERRUPTED':
            self.store.db.execute("UPDATE trials SET status='QUEUED',updated=? WHERE id=?",(now,trial_id))
            self.store.set('status','STOPPED')
        else:
            reason=RecoveryManager.process_failure(result.get('error','PROCESS_EXIT'))
            retry=trial['retries']<self.system['max_process_retries'] and reason in ['PROCESS_EXIT','GPU_OOM']
            if reason=='GPU_OOM' and config['num_envs']<=64:retry=False
            self.store.set('diagnosis',reason)
            if reason in ['CONTACT_DETECTION_ERROR','CHECKPOINT_INCOMPATIBLE']:
                self.store.set('status','BLOCKED_NEEDS_REDESIGN')
            self.store.db.execute('UPDATE trials SET status=?,retries=retries+1,diagnosis=?,updated=? WHERE id=?',
                                 ('QUEUED' if retry else 'FAILED',reason,now,trial_id))
            if reason=='GPU_OOM' and retry:
                # Same immutable trial config is not silently changed. Failed
                # attempt is retained; create a new hashed lower-memory branch.
                self.store.db.execute("UPDATE trials SET status='FAILED' WHERE id=?",(trial_id,))
                config['num_envs']=max(64,config['num_envs']//2)
                config['mutation']=dict(group='resource',key='num_envs',reason='GPU_OOM',before=json.loads(trial['config']))
                digest=hashlib.sha256(canonical(config).encode()).hexdigest()
                target=trial['target']*json.loads(trial['config'])['num_envs']//config['num_envs']
                self.store.add_trial(config,trial['generation'],trial['stage'],target,trial['source'],digest)
            self.store.event('PROCESS_FAILURE_CLASSIFIED',trial_id,reason=reason,retry=retry,error=result.get('error'))
    def finish_rung(self):
        generation=self.store.get('generation')
        if self.store.get('generation_stage',self.store.get('stage',0))!=self.store.get('stage',0):
            self.new_generation();return True
        rows=self.store.rows('SELECT * FROM trials WHERE generation=?',(generation,))
        rung=max(r['rung'] for r in rows)
        cohort=[r for r in rows if r['rung']==rung and r['status']=='COMPLETE']
        if rung<2 and cohort:
            count=self.system['survivors'][rung]
            chosen=self.search.select(cohort,count)
            # An increasing minimum per-leg cycle rate can earn a grace place,
            # independent of whether it already satisfies the formal gate.
            for r in cohort:
                history=self.store.rows('SELECT metrics FROM evaluations WHERE trial_id=? AND full=1 ORDER BY created',(r['id'],))
                rates=[json.loads(v['metrics']).get('min_complete_per_trial',0) for v in history]
                if len(rates)>1 and rates[-1]>rates[-2] and r['id'] not in chosen and len(chosen)<count+1:chosen.append(r['id'])
            with self.store.transaction():
                for r in cohort:
                    if r['id'] in chosen:
                        envs=json.loads(r['config'])['num_envs'];target=self.system['budgets'][rung+1]*256//envs
                        self.store.db.execute("UPDATE trials SET status='QUEUED',rung=rung+1,target=? WHERE id=?",(target,r['id']))
                    else:self.store.db.execute("UPDATE trials SET status='ELIMINATED' WHERE id=?",(r['id'],))
                self.store.event('SUCCESSIVE_HALVING',generation=generation,rung=rung,survivors=chosen)
            return True
        current=score(self.store.get('best_metrics'));start=self.store.get('batch_start_score',current)
        stagnant=0 if current>start+.02 else self.store.get('stagnant_batches',0)+1
        self.store.set('stagnant_batches',stagnant)
        self.store.event('SEARCH_BATCH_COMPLETE',generation=generation,improvement=current-start,stagnant_batches=stagnant)
        atomic_json(self.store.base/'reports'/f'batch_{generation:04d}.json',dict(generation=generation,improvement=current-start,stagnant_batches=stagnant,experiments=[{k:r.get(k) for k in ['id','status','progress','score','diagnosis']} for r in rows]))
        if stagnant>=self.system['max_stagnant_batches']:
            self.store.set('status','BLOCKED_NEEDS_REDESIGN');self.report();return False
        # A useful elite gets another bounded 500-update window; if it ceases to
        # improve, bounded new batches are generated instead of infinite replay.
        improving=[r for r in cohort if r.get('score',-1e6)>start+.02]
        if improving and self.store.get('generation_stage')==self.store.get('stage'):
            elite=max(improving,key=lambda r:r['score'])
            with self.store.transaction():
                self.store.db.execute("UPDATE trials SET status='QUEUED',target=target+? WHERE id=?",(self.system['elite_extension'],elite['id']))
                self.store.set('batch_start_score',current)
                self.store.event('ELITE_BOUNDED_EXTENSION',elite['id'],budget=self.system['elite_extension'])
            return True
        self.new_generation();return True
    def run_child(self,trial,attempt,smoke=False):
        cmd=[str(PYTHON),'-u',str(ROOT/'scripts/autoppo/autoppo.py'),'_worker','--base',str(self.store.base),'--trial',trial['id'],'--attempt',attempt]
        if smoke:cmd.append('--smoke')
        logfile=self.store.base/'trials'/trial['id']/(attempt+'.log')
        with logfile.open('x') as log:
            self.child=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,
                start_new_session=True,close_fds=True,pass_fds=(self.lock.fileno(),) if self.lock else ())
        self.store.db.execute('UPDATE attempts SET pid=? WHERE id=?',(self.child.pid,attempt))
        stop_at=None
        while self.child.poll() is None:
            if self.stop or (self.store.base/'STOP').exists():
                if stop_at is None:self.child.send_signal(signal.SIGTERM);stop_at=time.monotonic()
                elif time.monotonic()-stop_at>self.system['stop_grace_seconds']:
                    # Own process group only; no pkill or broad GPU cleanup.
                    os.killpg(self.child.pid,signal.SIGKILL)
            self.publish();time.sleep(15)
        self.child.wait();result_path=self.store.base/'trials'/trial['id']/attempt/'result.json'
        if result_path.exists():result=json.loads(result_path.read_text())
        else:
            text=logfile.read_text(errors='replace')[-16000:]
            result=dict(status='INTERRUPTED' if stop_at is not None else 'FAILED',error=text)
            self.store.db.execute("UPDATE attempts SET status=?,end=?,wall_seconds=? WHERE id=?",('CRASHED',time.time(),time.time()-self.store.rows('SELECT start FROM attempts WHERE id=?',(attempt,))[0]['start'],attempt))
        self.child=None
        return result
    def reconcile_checkpoints(self):
        from .checkpoint_bank import inspect_checkpoint
        for trial in self.store.rows("SELECT * FROM trials WHERE status='QUEUED'"):
            directory=self.store.base/'trials'/trial['id'];directory.mkdir(parents=True,exist_ok=True)
            if not (directory/'config.json').exists():atomic_json(directory/'config.json',json.loads(trial['config']))
            if not trial['checkpoint']:continue
            try:
                inspect_checkpoint(trial['checkpoint']);continue
            except Exception:pass
            records=self.store.rows("SELECT data FROM events WHERE trial_id=? AND kind='CHECKPOINT_COMMITTED' ORDER BY id DESC",(trial['id'],))
            selected=None
            for row in records:
                item=json.loads(row['data'])
                try:
                    _,meta=inspect_checkpoint(item['checkpoint'])
                    if meta['state']['total_updates']==item['lineage_updates']:selected=item;break
                except Exception:continue
            with self.store.transaction():
                self.store.db.execute('UPDATE trials SET checkpoint=?,progress=? WHERE id=?',
                    (selected['checkpoint'] if selected else None,selected['progress'] if selected else 0,trial['id']))
                self.store.event('TORN_CHECKPOINT_RECOVERY',trial['id'],invalid=trial['checkpoint'],selected=selected,
                    lost_uncommitted_progress=trial['progress']-(selected['progress'] if selected else 0))
    def run(self):
        validate_gate(self.store.base);self.acquire()
        self.store.repair_orphans();self.reconcile_checkpoints()
        if self.store.get('status','').startswith('BLOCKED') or self.store.get('status')=='SUCCESS':
            self.report();self.store.close();self.lock.close();return
        if not self.store.get('initialized'):self.initialize(self.store.base/'physical_audit_final')
        self.store.set('status','RUNNING');self.store.set('manager_pid',os.getpid());atomic_json(self.store.base/'manager_process.json',dict(pid=os.getpid(),start=time.time()))
        def stop(sig,frame):self.stop=True;(self.store.base/'STOP').touch()
        for sig in [signal.SIGTERM,signal.SIGINT]:signal.signal(sig,stop)
        if self.store.get('generation_building'):self.complete_generation()
        elif not self.store.rows('SELECT id FROM trials'):self.new_generation()
        try:
            while not self.stop and not (self.store.base/'STOP').exists():
                free=sample(self.store.base)['disk_free_gib']
                if free<self.system['minimum_disk_gib']:
                    removed=prune_temporary(self.store.base)
                    if sample(self.store.base)['disk_free_gib']<self.system['minimum_disk_gib']:
                        self.store.set('status','BLOCKED_DISK_SPACE');self.store.event('DISK_SPACE_BLOCK',removed=removed);break
                claimed=self.store.claim()
                if claimed:
                    trial,attempt=claimed;result=self.run_child(trial,attempt);self.adopt_result(trial,attempt,result)
                elif not self.finish_rung():break
                if self.store.get('status')=='SUCCESS' or self.store.get('status','').startswith('BLOCKED'):break
                self.publish()
            if self.stop or (self.store.base/'STOP').exists():self.store.set('status','STOPPED')
        finally:self.publish();self.report();self.store.close();self.lock.close()
    def report(self):
        row=self.publish()
        events=self.store.rows('SELECT * FROM events ORDER BY id')
        atomic_json(self.store.base/'search_history.json',events)
        text=(self.store.base/'STATUS_SUMMARY.md').read_text()+'\n## Experiments\n\n|Trial|State|Updates|Target|Rung|Diagnosis|\n|---|---|---:|---:|---:|---|\n'
        for t in row['trials']:text+=f"|{t['id']}|{t['status']}|{t['progress']}|{t['target']}|{t['rung']}|{t['diagnosis']}|\n"
        text+='\nImmutable configs: `trials/<trial>/config.json`. Full search decisions: `search_history.json` and SQLite events.\n'
        (self.store.base/'AUTOPPO_EXPERIMENT_REPORT.md').write_text(text)
        if row['status'].startswith('BLOCKED'):(self.store.base/'reports/BLOCKED.md').write_text(text)
        return row
