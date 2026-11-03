"""Produce the launch gate only from completed, inspected local test evidence."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import BASE,PYTHON
from dogfight.autoppo.storage import atomic_json
from dogfight.autoppo.checkpoint_bank import sha256,inspect_checkpoint
from dogfight.autoppo.experiment_manager import source_hashes,validate_gate
from dogfight.autoppo.stride import PROTOCOL

def main():
    reports=BASE/'reports';smoke=BASE/'smoke_validation_final_02';audit=BASE/'physical_audit_final'
    passed=json.loads((smoke/'SMOKE_PASS.json').read_text())
    if passed.get('status')!='PASS' or passed.get('new_updates')!=4 or passed.get('sequential_jobs')!=2 or not passed.get('full_learner_restore_verified'):raise RuntimeError('Final PPO smoke incomplete')
    launches=[]
    for cp in passed['checkpoints']:
        data,meta=inspect_checkpoint(cp);folder=Path(cp).parent
        launch=json.loads((folder/'launch.json').read_text());launches.append(launch)
        rows=[json.loads(x) for x in (folder/'metrics.jsonl').read_text().splitlines()]
        if len(rows)!=2 or not all(r['actor_parameter_delta_l2']>0 for r in rows):raise ValueError('PPO updates did not change actor')
        panel=json.loads((folder/'eval_00000002/evaluation_common.json').read_text())
        if panel['protocol']!=PROTOCOL or not list((folder/'eval_00000002').glob('stride_events_seed*.csv')):raise ValueError('Physical event evaluation missing')
        if not (folder/'smoke_gait.mp4').is_file() or not (folder/'ppo_curves.png').is_file():raise ValueError('Smoke video/curves missing')
    if launches[0]['optimizer_exact_restored'] or not launches[1]['optimizer_exact_restored']:raise ValueError('Restoration modes were not distinguished')
    done=json.loads((audit/'DONE.json').read_text())
    if done['status']!='PASS' or set(done['results'])!={'v63_B300','v6_2500','v62_B100'}:raise ValueError('Historical physical panel incomplete')
    for name in done['results']:
        panel=json.loads((audit/name/'evaluation_common.json').read_text())
        if panel['protocol']!=PROTOCOL or panel['seeds']!=[103,307]:raise ValueError('Historical evaluation protocol mismatch')
    log=reports/'validation_tests_final.log'
    env=os.environ.copy();env.update(PYTHONPATH=str(ROOT/'src'),OPENBLAS_NUM_THREADS='1')
    with log.open('x') as out:
        subprocess.run([str(PYTHON),'-m','pytest','tests/test_autoppo_system.py','tests/test_autoppo_gait.py','tests/test_curriculum_v6_3.py','-q','-p','no:cacheprovider'],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)
    inventory=json.loads((reports/'protected_checkpoints.json').read_text());changed=[]
    for row in inventory:
        p=Path(row['path'])
        if not p.is_file() or p.stat().st_size!=row['bytes'] or sha256(p)!=row['sha256']:changed.append(str(p))
    protection=dict(status='PASS' if not changed else 'FAIL',files=len(inventory),changed=changed,verified_unix=time.time())
    atomic_json(reports/'CHECKPOINT_PROTECTION_FINAL.json',protection)
    if changed:raise ValueError('Historical checkpoint protection failed')
    files=[log,smoke/'SMOKE_PASS.json',audit/'DONE.json',reports/'CHECKPOINT_PROTECTION_FINAL.json',ROOT/'configs/autoppo/csdog-autoppo-lab.service']
    gate=dict(status='PASS',created_unix=time.time(),checks={k:'PASS' for k in ['gait','reward_timing','physical_evaluation','checkpoint_protection','search','recovery','ppo_smoke']},
        source_hashes=source_hashes(),evidence=[dict(path=str(p),sha256=sha256(p)) for p in files],
        protocol=PROTOCOL,smoke_new_updates=4,simulation_success_is_not_robot_motion_success=True)
    atomic_json(reports/'VALIDATION_GATE.json',gate);validate_gate(BASE)
    print(json.dumps(dict(status='VALIDATION_GATE_PASS',protected_checkpoints=len(inventory),smoke_updates=4,protocol=PROTOCOL)))
if __name__=='__main__':main()
