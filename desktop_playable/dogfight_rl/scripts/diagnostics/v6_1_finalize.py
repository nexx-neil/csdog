"""Local fail-closed post-experiment selection, video, detached launch and verification."""
from pathlib import Path
import json,subprocess,sys,time,os,datetime
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/locomotion/csdog_curriculum_v6_1/repair_20261027';RUNS=OUT.parent
sys.path.insert(0,str(ROOT/'src'))
from dogfight.locomotion.curriculum_v6_1.supervisor import atomic_json

def run(args,log):
    with log.open('x') as f:r=subprocess.run([sys.executable,'-u',*map(str,args)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(f'Command failed ({r.returncode}): {log}')

def main():
    while True:
        p=OUT/'experiment_verified_status.json'
        if p.exists():
            status=json.loads(p.read_text())
            if status.get('status')=='BLOCKED':raise RuntimeError('Experiment prerequisite failed: '+str(status))
            if status.get('phase')=='AB_COMPLETE':break
        time.sleep(20)
    run([ROOT/'scripts/diagnostics/v6_1_comparison_report.py'],OUT/'comparison_report.log')
    decision=json.loads((OUT/'ab_selection.json').read_text())
    # Always retain a real physical video of the improved configuration, even if it loses.
    run([ROOT/'scripts/evaluate/csdog_curriculum_v6_1.py','--checkpoint',RUNS/'ab_B_verified_20261027/final.pt','--output-dir',OUT/'optimized_B_video','--headless','--video'],OUT/'optimized_B_video.log')
    if not decision['selected_arm']:
        atomic_json(OUT/'launch_verification.json',dict(status='BLOCKED_BOTH_ARMS_REGRESSED',training_started=False,reason=decision))
        (OUT/'BLOCKED.md').write_text('# BLOCKED\n\nBoth 500-update endpoints failed continuation safety relative to the verified initialization. No long training was started. Preserve the original historical checkpoint; see V6_1_AB_COMPARISON.md.\n')
        run([ROOT/'scripts/diagnostics/v6_1_repair_report.py'],OUT/'repair_report.log')
        return
    import torch
    from dogfight.locomotion.spot_v4.contracts import finite_tree
    cp=Path(decision['checkpoint']);data=torch.load(cp,map_location='cpu',weights_only=False);meta=data['infos']['curriculum_v6'];source=meta['state']['total_updates']
    name='train_20261027_seed42';target=RUNS/name
    if target.exists():name='train_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_seed42';target=RUNS/name
    started=time.time()
    run([ROOT/'scripts/diagnostics/curriculum_v6_1_supervisor.py','run','--run-dir',target,'--','--resume','--checkpoint',cp,'--iterations','unlimited','--auto-curriculum','--auto-recovery','--num-envs',str(meta['state']['num_envs']),'--seed',str(meta['state']['seed']),'--headless','--experiment-name',name,'--variant',decision['variant']],OUT/'long_launch.log')
    atomic_json(OUT/'long_training_target.json',dict(run_dir=str(target),source_checkpoint=str(cp),launch_unix=started))
    deadline=time.monotonic()+2400
    while time.monotonic()<deadline:
        time.sleep(20)
        status_path=target/'TRAINING_STATUS.json'
        if not status_path.exists():continue
        s=json.loads(status_path.read_text())
        if s['training_status'] in ['BLOCKED_NEEDS_REDESIGN','INTERRUPTED']:raise RuntimeError('Long trainer stopped: '+str(s['diagnosis']))
        periodic=sorted(target.glob('checkpoint_*.pt'))
        if s['total_updates']<source+100 or not periodic:continue
        pid=int((target/'pid').read_text());args=Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0');args=[x.decode() for x in args if x]
        if not any(x.endswith('/csdog_curriculum_v6_1.py') for x in args) or name not in args:raise RuntimeError('Training PID identity mismatch')
        latest=periodic[-1];checkpoint=torch.load(latest,map_location='cpu',weights_only=False)
        if not finite_tree(checkpoint) or not checkpoint.get('optimizer_state_dict'):raise RuntimeError('Invalid durable learner')
        if checkpoint['infos']['curriculum_v6']['state']['total_updates']<source+100:continue
        rows=[json.loads(x) for x in (target/'metrics.jsonl').read_text().splitlines()]
        if len(rows)<100 or rows[-1]['total_updates']<=rows[0]['total_updates']:continue
        gpu=subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,used_memory','--format=csv,noheader,nounits'],text=True)
        memory=[x for x in gpu.splitlines() if x.split(',')[0].strip()==str(pid)]
        if not memory:raise RuntimeError('Training PID has no GPU allocation')
        train_pids=[]
        for proc in Path('/proc').iterdir():
            if not proc.name.isdigit():continue
            try:a=(proc/'cmdline').read_bytes().split(b'\0')
            except OSError:continue
            if any(x.endswith(b'/scripts/train/csdog_curriculum_v6.py') or x.endswith(b'/scripts/train/csdog_curriculum_v6_1.py') for x in a):train_pids.append(int(proc.name))
        if train_pids!=[pid]:raise RuntimeError('Duplicate training process: '+str(train_pids))
        service=json.loads((RUNS/(name+'.service.json')).read_text());watcher=service['watcher_pid']
        if os.getsid(pid)!=os.getsid(watcher) or os.getsid(pid)==os.getsid(os.getpid()):raise RuntimeError('Trainer is not in an independent detached session')
        changed=[f for f,h in json.loads((target/'source_sha256.json').read_text()).items() if __import__('hashlib').sha256(Path(f).read_bytes()).hexdigest()!=h]
        if changed:raise RuntimeError('Training source changed after launch: '+str(changed))
        evidence=dict(status='RUNNING_VERIFIED',training_started=True,run_dir=str(target),pid=pid,watcher_pid=watcher,session_id=os.getsid(pid),cwd=os.readlink(f'/proc/{pid}/cwd'),command=args,stage=s['stage_name'],substage=s['substage'],total_updates=s['total_updates'],source_updates=source,source_checkpoint=str(cp),durable_checkpoint=str(latest),log=service['log'],gpu=memory,metrics_rows=len(rows),first_update=rows[0]['total_updates'],last_update=rows[-1]['total_updates'],optimizer_verified=True,exploration_verified=bool((checkpoint['model_state_dict']['std']>0).all()),source_changed=changed,unique_training_pids=train_pids,heartbeat_age_s=time.time()-s['heartbeat_unix'])
        atomic_json(OUT/'launch_verification.json',evidence)
        run([ROOT/'scripts/diagnostics/v6_1_repair_report.py'],OUT/'repair_report.log')
        atomic_json(OUT/'FINALIZATION_STATUS.json',dict(status='COMPLETE',run_dir=str(target)))
        return
    raise RuntimeError('Long trainer did not produce 100 updates and a durable checkpoint within startup timeout')
if __name__=='__main__':
    try:main()
    except BaseException as e:
        atomic_json(OUT/'FINALIZATION_STATUS.json',dict(status='BLOCKED',error=repr(e)))
        (OUT/'BLOCKED.md').write_text('# BLOCKED\n\n'+repr(e)+'\n\nNo unverified long-training success is claimed. Inspect local logs and complete prerequisite evidence.\n')
        if not (OUT/'V6_1_REPAIR_REPORT.md').exists():(OUT/'V6_1_REPAIR_REPORT.md').write_text('# V6.1 repair: prerequisite blocked\n\n'+repr(e)+'\n\nV6 was already interrupted at8460 updates; original checkpoints are preserved. See unit_tests_verified.log, history_verified_status.json and experiment_verified_status.json.\n')
        raise
