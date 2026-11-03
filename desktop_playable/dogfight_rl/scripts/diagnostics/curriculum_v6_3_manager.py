"""Detached V6.3 service manager with verified status, safe stop, and full resume."""
from pathlib import Path
import argparse,datetime,json,os,signal,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'runs/locomotion/csdog_curriculum_ppo_v6_3'
TRAIN=ROOT/'scripts/train/csdog_curriculum_v6_3.py'
ACTIVE=BASE/'ACTIVE_RUN'
PYTHON=Path('/home/zxq/miniconda3/envs/dogfight/bin/python')

def atomic_text(path,text):
    tmp=path.with_name('.'+path.name+'.tmp');tmp.write_text(text);os.replace(tmp,path)

def active_run():
    if not ACTIVE.exists():raise RuntimeError('No V6.3 active run has been registered')
    out=Path(ACTIVE.read_text().strip()).resolve()
    if out.parent!=BASE or not out.exists():raise RuntimeError('ACTIVE_RUN is invalid: '+str(out))
    return out

def continuation_gate():
    path=BASE/'CONTINUATION_GATE.json'
    if not path.exists():raise RuntimeError('V6.3 A/B continuation gate has not been evaluated')
    gate=json.loads(path.read_text())
    if not gate.get('allowed'):raise RuntimeError('V6.3 A/B continuation gate failed; long training is prohibited')
    return gate

def verified_pid(out):
    try:
        pid=int((out/'pid').read_text());args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
    except (OSError,ValueError):return None
    if not any(x.endswith(b'/csdog_curriculum_v6_3.py') for x in args):return None
    try:
        target=Path(args[args.index(b'--output')+1].decode())
        if not target.is_absolute():target=Path(f'/proc/{pid}/cwd').resolve()/target
        return pid if target.resolve()==out else None
    except (ValueError,IndexError):return None

def newest(out):
    import torch
    choices=[]
    for p in out.glob('*.pt'):
        try:
            d=torch.load(p,map_location='cpu',weights_only=False);m=d['infos']['curriculum_v6']
            if m['options'].get('schema')!=6.3 or not d.get('optimizer_state_dict'):continue
            tensors=list(d['model_state_dict'].values())
            if not all(torch.isfinite(v).all() for v in tensors):continue
            choices.append((m['state']['total_updates'],p.stat().st_mtime,p))
        except Exception:continue
    if not choices:raise RuntimeError('No complete V6.3 learner checkpoint found')
    return max(choices)[2]

def launch(name,checkpoint):
    gate=continuation_gate()
    if not ACTIVE.exists() and checkpoint.resolve()!=Path(gate['selected_checkpoint']).resolve():
        raise RuntimeError('First long run must use the checkpoint selected by the A/B gate')
    out=(BASE/name).resolve()
    if out.parent!=BASE or out.exists():raise RuntimeError('Use a fresh simple run name under '+str(BASE))
    log=BASE/(name+'.training.log')
    cmd=[str(PYTHON),'-u',str(Path(__file__).resolve()),'_watch','--name',name,'--checkpoint',str(checkpoint)]
    with log.open('x') as f:
        watcher=subprocess.Popen(cmd,cwd=ROOT,stdin=subprocess.DEVNULL,stdout=f,stderr=subprocess.STDOUT,start_new_session=True,close_fds=True)
    atomic_text(ACTIVE,str(out)+'\n')
    (BASE/(name+'.service.json')).write_text(json.dumps({'watcher_pid':watcher.pid,'run_dir':str(out),'log':str(log),'checkpoint':str(checkpoint)},indent=2))
    print(json.dumps({'watcher_pid':watcher.pid,'run_dir':str(out),'log':str(log)}))

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=['status','stop','run','resume','_watch']);p.add_argument('--name');p.add_argument('--checkpoint',type=Path)
    a=p.parse_args()
    if a.action=='status':
        if not ACTIVE.exists():
            path=BASE/'CONTINUATION_GATE.json'
            gate=json.loads(path.read_text()) if path.exists() else None
            ab=BASE/'ab_B';ab_status=json.loads((ab/'TRAINING_STATUS.json').read_text()) if (ab/'TRAINING_STATUS.json').exists() else {}
            m=ab_status.get('physical_metrics') or {}
            pid=verified_pid(ab) if ab.exists() else None
            print(json.dumps({'training':bool(pid),'pid':pid,'ppo_updates':ab_status.get('total_updates'),'stage':'STAGE1_AB' if ab.exists() else 'PRE_AB','forward_speed':m.get('vx'),'complete_stride_ratio':m.get('complete_stride_ratio'),'complete_stride_count':m.get('complete_stride_count'),'support_foot_slip':m.get('support_foot_slip'),'stop_linear_speed':m.get('stop_linear_speed'),'stop_yaw_rate':m.get('stop_yaw_rate'),'gait_qualified':ab_status.get('gait_qualified'),'continuation_gate':gate,'best_checkpoint':None,'best_gait_checkpoint':None,'best_balanced_checkpoint':None,'best_stage_qualified_checkpoint':None,'latest_ab_checkpoint':str(ab/'final.pt') if (ab/'final.pt').exists() else None},indent=2));return
        out=active_run();status=json.loads((out/'TRAINING_STATUS.json').read_text());pid=verified_pid(out);m=status.get('physical_metrics') or {}
        result={'training':bool(pid),'pid':pid,'ppo_updates':status.get('total_updates'),'stage':status.get('stage_name'),'forward_speed':m.get('vx'),'complete_stride_ratio':m.get('complete_stride_ratio'),'complete_stride_count':m.get('complete_stride_count'),'support_foot_slip':m.get('support_foot_slip'),'stop_linear_speed':m.get('stop_linear_speed'),'stop_yaw_rate':m.get('stop_yaw_rate'),'gait_qualified':status.get('gait_qualified'),'best_gait_checkpoint':status.get('best_gait_checkpoint'),'best_balanced_checkpoint':status.get('best_balanced_checkpoint'),'best_stage_qualified_checkpoint':status.get('best_stage_qualified_checkpoint'),'heartbeat_age_s':round(time.time()-status['heartbeat_unix'],1)}
        print(json.dumps(result,indent=2));return
    if a.action=='stop':
        if not ACTIVE.exists():print('No registered V6.3 long trainer; no signal sent.');return
        out=active_run();pid=verified_pid(out)
        if not pid:print('No verified live V6.3 trainer; no signal sent.');return
        (out/'STOP').touch();os.kill(pid,signal.SIGTERM)
        print(f'Safe stop requested for PID {pid}; trainer will atomically write interrupted.pt and Supervisor state.');return
    if a.action=='run':
        if not a.name or not a.checkpoint:p.error('run requires --name and --checkpoint')
        launch(a.name,a.checkpoint.resolve());return
    if a.action=='resume':
        continuation_gate()
        old=active_run()
        if verified_pid(old):raise RuntimeError('Training is still live; stop it safely before resume')
        checkpoint=newest(old);name=a.name or ('long_resume_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))
        launch(name,checkpoint);return
    if not a.name or not a.checkpoint:p.error('_watch requires --name and --checkpoint')
    out=(BASE/a.name).resolve()
    child=subprocess.Popen([str(PYTHON),'-u',str(TRAIN),'--mode','long','--arm','B','--checkpoint',str(a.checkpoint.resolve()),'--output',str(out)],cwd=ROOT,stdin=subprocess.DEVNULL)
    while child.poll() is None:time.sleep(30)
    (BASE/(a.name+'.watchdog_result.json')).write_text(json.dumps({'child_pid':child.pid,'returncode':child.returncode},indent=2))

if __name__=='__main__':main()
