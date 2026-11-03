"""V7 commands backed by the existing AutoPPO Store and ExperimentManager."""
from pathlib import Path
import sys,argparse,json,os,subprocess,time,fcntl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import PYTHON
from dogfight.autoppo.storage import Store,atomic_json
BASE=ROOT/'runs/locomotion/csdog_phase_guided_ppo_v7'

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['start','resume','stop','status','report','_daemon','_worker','smoke']);p.add_argument('--base',type=Path,default=BASE);p.add_argument('--arm',choices=list('ABCD'),default='C');p.add_argument('--trial');p.add_argument('--attempt');p.add_argument('--updates',type=int,default=2);p.add_argument('--slip-mode',choices=['raw','log'],default='raw');a=p.parse_args();base=a.base.resolve();base.mkdir(parents=True,exist_ok=True)
 if a.action in ('_worker','smoke'):
  from dogfight.locomotion.phase_guided_v7.train import worker
  if a.action=='smoke':return worker(base/'smoke',a.arm,a.updates,smoke=True,options_override={'slip_mode':a.slip_mode})
  from dogfight.autoppo.experiment_manager import validate_gate
  validate_gate(base)
  store=Store(base);trial=store.rows('SELECT * FROM trials WHERE id=?',(a.trial,))[0];c=json.loads(trial['config']);store.close()
  return worker(base,c['arm'],trial['target'],trial['checkpoint'] or trial['source'],out=base/'trials'/a.trial/a.attempt,options_override=c.get('options'))
 from dogfight.autoppo.phase_v7_manager import V7Manager
 if a.action=='_daemon':return V7Manager(base).run()
 if a.action=='stop':(base/'STOP').touch();print('STOP_REQUESTED');return 0
 if a.action in ('status','report'):
  m=V7Manager(base)
  try:r=m.report() if a.action=='report' else m.publish()
  finally:m.store.close()
  if a.action=='report':
   from dogfight.locomotion.phase_guided_v7.reporting import generate
   generate(base)
  print(json.dumps(r,indent=2));return 0
 from dogfight.autoppo.experiment_manager import validate_gate
 validate_gate(base)
 # Acquiring the same lock prevents duplicate manager trees, including orphan workers.
 with (base/'manager.lock').open('a') as probe:
  try:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
  except BlockingIOError:print('ALREADY_RUNNING');return 0
 store=Store(base);state=store.get('status','READY');store.close()
 if state.startswith('BLOCKED'):raise RuntimeError('Revalidation required: '+state)
 (base/'STOP').unlink(missing_ok=True)
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='4',PYTHONUNBUFFERED='1')
 with (base/'manager.log').open('a') as f:
  proc=subprocess.Popen([str(PYTHON),'-u',str(Path(__file__).resolve()),'_daemon','--base',str(base)],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True,env=env)
 print(json.dumps(dict(manager_pid=proc.pid,mode='bounded_ablation_first',log=str(base/'manager.log'))));return 0
if __name__=='__main__':raise SystemExit(main())
