"""CSDog AutoPPO Lab management. Importing/status never starts Isaac Sim."""
from pathlib import Path
import argparse,json,os,subprocess,sys,time,fcntl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE,PYTHON
from dogfight.autoppo.storage import Store,atomic_json

def verified_manager(base):
    try:
        row=json.loads((base/'manager_process.json').read_text());pid=int(row['pid'])
        args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
        return pid if b'_daemon' in args and str(base).encode() in args and any(x.endswith(b'/autoppo.py') for x in args) else None
    except (OSError,ValueError,KeyError):return None

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['start','status','stop','resume','report','_daemon','_worker'])
    p.add_argument('--base',type=Path,default=BASE);p.add_argument('--trial');p.add_argument('--attempt');p.add_argument('--smoke',action='store_true')
    a=p.parse_args();base=a.base.resolve();base.mkdir(parents=True,exist_ok=True)
    if a.action=='_worker':
        if not a.trial or not a.attempt:p.error('_worker requires trial/attempt')
        from dogfight.autoppo.train_runner import worker
        return worker(base,a.trial,a.attempt,a.smoke)
    from dogfight.autoppo.experiment_manager import ExperimentManager,validate_gate
    if a.action=='_daemon':
        try:ExperimentManager(base).run();return 0
        except BaseException as e:
            atomic_json(base/'MANAGER_ERROR.json',dict(error=repr(e),time=time.time()))
            raise
    if a.action=='status':
        path=base/'TRAINING_STATUS.json';row=json.loads(path.read_text()) if path.exists() else dict(status='NOT_STARTED')
        row['verified_manager_pid']=verified_manager(base)
        if row.get('status')=='RUNNING' and row['verified_manager_pid'] is None:row['status']='MANAGER_NOT_RUNNING'
        print(json.dumps(row,indent=2));return 0
    if a.action=='stop':
        (base/'STOP').touch()
        print(json.dumps(dict(status='STOP_REQUESTED',manager_pid=verified_manager(base),message='Worker saves at a completed PPO update; committed checkpoint and SQLite queue are retained.')));return 0
    if a.action=='report':
        manager=ExperimentManager(base)
        try:manager.report()
        finally:manager.store.close()
        print(base/'AUTOPPO_EXPERIMENT_REPORT.md');return 0
    validate_gate(base)
    pid=verified_manager(base)
    if pid:print(json.dumps(dict(status='ALREADY_RUNNING',manager_pid=pid)));return 0
    store=Store(base)
    try:
        state=store.get('status','READY')
        if state.startswith('BLOCKED') or state=='SUCCESS':raise RuntimeError('Refusing restart of terminal state '+state+'; redesign/revalidation required')
    finally:store.close()
    # Probe the inherited lock as well as PID; an orphan worker may still hold it.
    with (base/'manager.lock').open('a') as probe:
        try:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            print(json.dumps(dict(status='JOB_TREE_STILL_RUNNING',manager_pid=pid)));return 0
    if a.action=='resume' or a.action=='start':(base/'STOP').unlink(missing_ok=True)
    unit=Path.home()/'.config/systemd/user/csdog-autoppo-lab.service'
    if unit.exists() and base==BASE:
        subprocess.run(['systemctl','--user','start','csdog-autoppo-lab.service'],check=True)
    else:
        env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4',PYTHONUNBUFFERED='1')
        with (base/'manager.log').open('a') as log:
            subprocess.Popen([str(PYTHON),'-u',str(Path(__file__).resolve()),'_daemon','--base',str(base)],cwd=ROOT,
                stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True,env=env)
    for _ in range(20):
        pid=verified_manager(base)
        if pid:print(json.dumps(dict(status='MANAGER_STARTED',manager_pid=pid)));return 0
        time.sleep(.5)
    raise RuntimeError('Manager startup not verified; inspect manager.log / MANAGER_ERROR.json')
if __name__=='__main__':raise SystemExit(main())
