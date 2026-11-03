"""Low-token local status/stop/watchdog CLI. Watchdog owns a detached training child."""
from pathlib import Path
import argparse,json,os,signal,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.locomotion.curriculum_v6.supervisor import atomic_json

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['status','stop','run']);p.add_argument('--run-dir',type=Path,required=True)
    raw=sys.argv[1:];split=raw.index('--') if '--' in raw else len(raw)
    a=p.parse_args(raw[:split]);a.training_args=raw[split+1:]
    out=a.run_dir.resolve()
    if a.action=='status':
        print((out/'STATUS_SUMMARY.md').read_text());return
    if a.action=='stop':
        status=json.loads((out/'TRAINING_STATUS.json').read_text())
        if status['training_status']!='RUNNING':print(status['training_status']);return
        (out/'STOP').touch();pid=int((out/'pid').read_text())
        cmdline=Path(f'/proc/{pid}/cmdline')
        if not cmdline.exists():print('Training process has exited; STOP recorded.');return
        args=cmdline.read_bytes().split(b'\0')
        if not any(x.endswith(b'/csdog_curriculum_v6.py') for x in args) or out.name.encode() not in args:raise RuntimeError('PID no longer identifies this run; refusing to signal')
        os.kill(pid,signal.SIGTERM);return
    args=a.training_args
    if args and args[0]=='--':args=args[1:]
    if out.exists():p.error('run directory already exists')
    # Log is outside the child run, so child can atomically claim a fresh directory.
    out.parent.mkdir(parents=True,exist_ok=True)
    log=out.parent/(out.name+'.training.log')
    with log.open('x') as f:
        child=subprocess.Popen([sys.executable,str(ROOT/'scripts/train/csdog_curriculum_v6.py'),*args],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT,start_new_session=True)
        while child.poll() is None:
            time.sleep(30)  # Local only; no Codex polling loop.
            status=out/'TRAINING_STATUS.json'
            if status.exists():
                try:heartbeat=json.loads(status.read_text()).get('heartbeat_unix',time.time())
                except (ValueError,OSError):continue
                if time.time()-heartbeat>1800:
                    os.kill(child.pid,signal.SIGTERM)
                    try:child.wait(timeout=120)
                    except subprocess.TimeoutExpired:os.kill(child.pid,signal.SIGKILL);child.wait()
                    break
    status=out/'TRAINING_STATUS.json'
    if status.exists():
        s=json.loads(status.read_text())
        if s['training_status']=='RUNNING':
            s['training_status']='BLOCKED_NEEDS_REDESIGN';s['diagnosis']=f'CHILD_EXIT_WITHOUT_CLEAN_CHECKPOINT: {child.returncode}'
            atomic_json(status,s)
            (out/'STATUS_SUMMARY.md').write_text(f"V6 BLOCKED: child exit {child.returncode}. Resume latest intact checkpoint; see {log}.\n")
            from dogfight.locomotion.curriculum_v6.supervisor import Supervisor
            Supervisor(out,json.loads((ROOT/'configs/locomotion/curriculum_v6/default.json').read_text()),s).report()
    atomic_json(out.parent/(out.name+'.watchdog_result.json'),dict(pid=child.pid,returncode=child.returncode,log=str(log)))
if __name__=='__main__':main()
