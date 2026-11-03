"""Detached process manager. All policy decisions remain inside the Python trainer."""
from pathlib import Path
import argparse,json,os,signal,subprocess,sys,time,datetime
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.locomotion.curriculum_v6_1.supervisor import atomic_json
TRAIN=ROOT/'scripts/train/csdog_curriculum_v6_1.py'

def verified_pid(out):
    try:pid=int((out/'pid').read_text());args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
    except (ValueError,OSError):return None
    if not any(x.endswith(b'/csdog_curriculum_v6_1.py') for x in args):return None
    try:
        index=args.index(b'--experiment-name')
        if args[index+1].decode()!=out.name:return None
    except (ValueError,IndexError):return None
    return pid

def newest(out):
    import torch
    from dogfight.locomotion.spot_v4.contracts import finite_tree,IDENTITY
    choices=[]
    for p in out.glob('*.pt'):
        try:
            d=torch.load(p,map_location='cpu',weights_only=False);m=d['infos']['curriculum_v6']
            if not d.get('optimizer_state_dict') or m.get('schema')!=6 or m.get('identity')!=IDENTITY:continue
            if not finite_tree(d):continue
            if 'std' in d['model_state_dict'] and not (d['model_state_dict']['std']>0).all():continue
            if not all(torch.isfinite(t).all() for t in d['model_state_dict'].values()):continue
            choices.append((m['state']['total_updates'],p.stat().st_mtime,p))
        except Exception:continue
    if not choices:raise RuntimeError('No complete valid checkpoint')
    return max(choices)[2]

def launch(out,args):
    if out.exists():raise RuntimeError('Output exists; choose a fresh run name')
    if '--experiment-name' not in args:args+=['--experiment-name',out.name]
    if args[args.index('--experiment-name')+1]!=out.name:raise RuntimeError('Run name mismatch')
    if out.parent!=ROOT/'runs/locomotion/csdog_curriculum_v6_1':raise RuntimeError('Run must be directly under V6.1 runs')
    log=out.parent/(out.name+'.training.log');out.parent.mkdir(parents=True,exist_ok=True)
    with log.open('x') as f:
        watcher=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'_watch','--run-dir',str(out),'--',*args],cwd=ROOT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
    atomic_json(out.parent/(out.name+'.service.json'),dict(watcher_pid=watcher.pid,log=str(log),run_dir=str(out),args=args))
    print(json.dumps(dict(watcher_pid=watcher.pid,run_dir=str(out),log=str(log))))

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('action',choices=['status','stop','run','resume','_watch']);p.add_argument('--run-dir',type=Path,required=True);p.add_argument('--new-name')
    raw=sys.argv[1:];i=raw.index('--') if '--' in raw else len(raw);a=p.parse_args(raw[:i]);args=raw[i+1:];out=a.run_dir.resolve()
    if a.action=='status':
        s=json.loads((out/'TRAINING_STATUS.json').read_text());pid=verified_pid(out)
        print((out/'STATUS_SUMMARY.md').read_text());print(json.dumps(dict(pid=pid,process_alive=bool(pid),heartbeat_age_s=round(time.time()-s['heartbeat_unix'],1),substage=s.get('substage'),score_version=s.get('score_version'),continuation_gate=json.loads((out/'CONTINUATION_GATE.json').read_text()) if (out/'CONTINUATION_GATE.json').exists() else None)));return
    if a.action=='stop':
        pid=verified_pid(out)
        if not pid:print('No matching live training process; no signal sent.');return
        (out/'STOP').touch()
        # Trainer checks STOP at chunk boundaries; signal handler stops at each PPO boundary.
        status=json.loads((out/'TRAINING_STATUS.json').read_text())
        if (out/'initial.pt').exists():os.kill(pid,signal.SIGTERM)
        print(f'Safe stop requested for PID {pid}; await interrupted.pt and INTERRUPTED status.');return
    if a.action=='resume':
        gate=out/'CONTINUATION_GATE.json'
        if gate.exists() and not json.loads(gate.read_text()).get('allowed',False):p.error('Continuation safety gate rejected this run. Preserve the verified historical checkpoint; repair and revalidate before long training.')
        if verified_pid(out):raise RuntimeError('Current run is still alive; safely stop it first')
        cp=newest(out)
        import torch
        meta=torch.load(cp,map_location='cpu',weights_only=False)['infos']['curriculum_v6'];s=meta['state']
        new=out.parent/(a.new_name or 'train_resume_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        launch(new,['--resume','--checkpoint',str(cp),'--num-envs',str(s['num_envs']),'--seed',str(s['seed']),'--headless','--iterations','unlimited','--auto-curriculum','--auto-recovery','--variant',meta['options'].get('variant','improved')]);return
    if a.action=='run':launch(out,args);return
    child=subprocess.Popen([sys.executable,'-u',str(TRAIN),*args],cwd=ROOT,stdin=subprocess.DEVNULL)
    requested=False
    while child.poll() is None:
        time.sleep(30)
        status=out/'TRAINING_STATUS.json'
        if status.exists():
            try:s=json.loads(status.read_text())
            except (OSError,ValueError):continue
            if time.time()-s['heartbeat_unix']>1800 and not requested:
                (out/'STOP').touch();os.kill(child.pid,signal.SIGTERM);requested=True
    if out.exists() and (out/'TRAINING_STATUS.json').exists():
        s=json.loads((out/'TRAINING_STATUS.json').read_text())
        if s['training_status']=='RUNNING':
            s.update(training_status='BLOCKED_NEEDS_REDESIGN',diagnosis=f'UNCLEAN_CHILD_EXIT:{child.returncode}')
            atomic_json(out/'TRAINING_STATUS.json',s);(out/'STATUS_SUMMARY.md').write_text(f"BLOCKED: unclean child exit {child.returncode}; inspect training log.\n")
    atomic_json(out.parent/(out.name+'.watchdog_result.json'),dict(pid=child.pid,returncode=child.returncode))
if __name__=='__main__':main()
