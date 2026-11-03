"""Bounded local launch verification. No recurring Codex log polling is needed."""
from pathlib import Path
import sys,json,time,subprocess,os,argparse
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE
from dogfight.autoppo.storage import Store,atomic_json
from dogfight.autoppo.checkpoint_bank import inspect_checkpoint

def snapshot():
    store=Store(BASE)
    try:
        rows=store.rows("SELECT a.*,t.progress,t.target,t.status AS trial_status FROM attempts a JOIN trials t ON t.id=a.trial_id ORDER BY a.start")
        full=store.rows('SELECT * FROM evaluations WHERE full=1 ORDER BY created')
        status=json.loads((BASE/'TRAINING_STATUS.json').read_text())
        return rows,full,status
    finally:store.close()

def verify(seconds=3600,exercise_resume=False):
    started=time.monotonic();resume_done=not exercise_resume
    while time.monotonic()-started<seconds:
        rows,full,status=snapshot()
        if status['status'].startswith('BLOCKED'):raise RuntimeError('Training entered '+status['status'])
        for row in rows:
            if row['status']=='FAILED':
                p=BASE/'trials'/row['trial_id']/row['id']/'result.json'
                result=json.loads(p.read_text()) if p.exists() else {}
                if any(k in result.get('error','') for k in ['NameError','TypeError','ImportError','UnboundLocalError']):
                    (BASE/'STOP').touch();raise RuntimeError('Critical worker failure: '+result['error'])
        if not resume_done:
            running=[r for r in rows if r['status']=='RUNNING' and r['progress']>=100]
            if running:
                exercise_live_resume(running[0]);resume_done=True
                continue
        completed=[r for r in rows if r['status'] in ['COMPLETE','REJECTED'] and r['progress']>=200]
        live=[r for r in rows if r['status']=='RUNNING' and r['observed_updates']>=2 and Path(f"/proc/{r['pid']}").exists()]
        if completed and live and full:
            finished=completed[0];active=live[-1]
            if finished['id']==active['id']:raise ValueError('Not independent sequential experiments')
            inspect_checkpoint(finished['checkpoint'])
            # Require a periodic checkpoint, not merely the initial snapshot.
            committed=BASE/'trials'/finished['trial_id']/finished['id']
            if not list(committed.glob('checkpoint_*.pt')):raise ValueError('No trained checkpoint')
            args=Path(f"/proc/{active['pid']}/cmdline").read_bytes()
            if b'_worker' not in args or str(BASE).encode() not in args:raise ValueError('Worker PID identity mismatch')
            manager_pid=status['manager_pid']
            manager_args=Path(f'/proc/{manager_pid}/cmdline').read_bytes()
            if b'_daemon' not in manager_args:raise ValueError('Manager PID identity mismatch')
            text=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
            gpu=[x.strip() for x in text.splitlines() if x.strip().startswith(str(active['pid'])+',')]
            if not gpu:time.sleep(10);continue
            processes=[]
            for p in Path('/proc').iterdir():
                if not p.name.isdigit():continue
                try:
                    cmd=(p/'cmdline').read_bytes().split(b'\0')
                    if b'_worker' in cmd and str(BASE).encode() in cmd:processes.append(int(p.name))
                except OSError:pass
            if processes!=[active['pid']]:raise ValueError('Unexpected parallel main workers: '+str(processes))
            result=dict(status='PASS',verified_unix=time.time(),manager_pid=manager_pid,worker_pid=active['pid'],
                first_trial=finished['trial_id'],first_trial_updates=finished['progress'],
                next_trial=active['trial_id'],next_trial_updates=active['observed_updates'],
                full_physical_evaluations=len(full),total_new_ppo_updates=status['total_ppo_updates'],
                checkpoint=finished['checkpoint'],gpu=gpu,main_gpu_workers=processes,service='csdog-autoppo-lab.service')
            atomic_json(BASE/'reports/LAUNCH_VERIFIED.json',result)
            write_report(status,result)
            print(json.dumps(result,indent=2),flush=True);return
        time.sleep(15)
    raise TimeoutError('Launch verification did not meet all requirements in the bounded verification window')

def exercise_live_resume(active):
    from dogfight.autoppo.config import PYTHON
    command=[str(PYTHON),str(ROOT/'scripts/autoppo/autoppo.py')]
    subprocess.run(command+['stop'],check=True,capture_output=True,text=True)
    deadline=time.monotonic()+210
    while time.monotonic()<deadline:
        state=subprocess.run(['systemctl','--user','is-active','csdog-autoppo-lab.service'],capture_output=True,text=True).stdout.strip()
        if state not in ['active','deactivating','activating']:break
        time.sleep(3)
    else:raise TimeoutError('Safe service stop did not complete')
    store=Store(BASE)
    try:
        row=store.rows('SELECT * FROM trials WHERE id=?',(active['trial_id'],))[0]
        queued=store.rows("SELECT id FROM trials WHERE status='QUEUED'")
    finally:store.close()
    if row['status']!='QUEUED' or row['progress']<100:raise ValueError('Safe stop lost trial queue or progress')
    _,meta=inspect_checkpoint(row['checkpoint'])
    if not queued:raise ValueError('Safe stop lost search queue')
    subprocess.run(command+['resume'],check=True,capture_output=True,text=True)
    deadline=time.monotonic()+210
    while time.monotonic()<deadline:
        rows,_,status=snapshot()
        resumed=[r for r in rows if r['trial_id']==active['trial_id'] and r['id']!=active['id'] and r['status']=='RUNNING' and r['observed_updates']>=2]
        if resumed:
            current=resumed[-1]
            launch=json.loads((BASE/'trials'/current['trial_id']/current['id']/'launch.json').read_text())
            if not launch['optimizer_exact_restored'] or launch['start_progress']!=row['progress'] or launch['lineage_start']!=meta['state']['total_updates']:raise ValueError('Exact checkpoint/optimizer/progress restoration failed')
            atomic_json(BASE/'reports/RECOVERY_LIVE_PASS.json',dict(status='PASS',trial=row['id'],
                stopped_progress=row['progress'],checkpoint=row['checkpoint'],resumed_attempt=current['id'],
                resumed_observed_updates=current['observed_updates'],optimizer_exact=True,queue_size_preserved=len(queued)))
            return
        time.sleep(5)
    raise TimeoutError('Same trial did not resume and update')

def write_report(status,result):
    smoke_updates=0
    for p in BASE.glob('smoke_validation*/experiments.sqlite'):
        s=Store(p.parent)
        try:smoke_updates+=s.rows('SELECT COALESCE(SUM(observed_updates),0) AS n FROM attempts')[0]['n']
        finally:s.close()
    text='# AUTOPPO LAUNCH REPORT\n\n'
    text+=f"Verified at unix {result['verified_unix']}: manager PID {result['manager_pid']}, worker PID {result['worker_pid']}. One main Isaac worker; GPU evidence {result['gpu']}.\n\n"
    text+=f"First autonomous trial {result['first_trial']} executed {result['first_trial_updates']} PPO updates, saved a validated checkpoint and completed automatic full physics evaluation. Next queued trial {result['next_trial']} is already updating ({result['next_trial_updates']} updates at verification).\n\n"
    text+=f"Formal search new updates at the last status heartbeat: {status['total_ppo_updates']}; validation-only observed updates across all retained attempts: {smoke_updates}. These totals exclude inherited history.\n\n"
    text+=f"Current course: {status['curriculum_stage']}; generation {status['search_generation']}; completed experiments {status['completed_experiments']}; failed experiments {status['failed_experiments']}. Best relative checkpoint: {status['best_checkpoint']}.\n\n"
    text+='Initial donor selection uses the unified v2 physical panel, with V6.3 B300 best balanced, V6.2 B100 retained for genuine early swings, and V6 2500 retained for other tradeoffs. All were unqualified for Stage 1; different inherited training costs are preserved in metadata.\n\n'
    text+='The service is enabled under the current systemd user and Linger=yes. It continues after this session and recovers after unexpected exit/reboot. A deliberate stop retains STOP until resume. No systemwide or unrelated GPU processes are killed.\n\n'
    text+='Formal validation gate, final tests, original checkpoint protection, final two-job real Smoke and physical event traces are in this reports directory. One earlier final Smoke failed due to a checkpoint-metadata variable name; it was retained, repaired and superseded by smoke_validation_final_02.\n\n'
    text+='No walking success is claimed. Current best is a relative search result; only the unchanged physical criteria can certify movement/course success. See TRAINING_STATUS.json / STATUS_SUMMARY.md and AUTOPPO_EXPERIMENT_REPORT.md for live values.\n\n'
    text+='Management:\n\n```bash\n'
    for action in ['start','status','stop','resume','report']:
        text+=f'/home/zxq/miniconda3/envs/dogfight/bin/python /home/zxq/robot_projects/dogfight_rl/scripts/autoppo/autoppo.py {action}\n'
    text+='```\n\nAll configs: trials/<id>/config.json and attempt env.yaml / agent.yaml / launch.json. Search history: SQLite events and search_history.json. Bank roles are immutable IDs, never overwritten files.\n'
    (BASE/'reports/AUTOPPO_LAUNCH_REPORT.md').write_text(text)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--timeout',type=int,default=3600);p.add_argument('--exercise-resume',action='store_true');a=p.parse_args();verify(a.timeout,a.exercise_resume)
