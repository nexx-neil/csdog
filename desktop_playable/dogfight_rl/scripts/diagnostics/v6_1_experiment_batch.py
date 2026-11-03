"""Fail-closed ordered smoke and 500+500 PPO experiment driver."""
from pathlib import Path
import sys,subprocess,json,time
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'runs/locomotion/csdog_curriculum_v6_1/repair_20261027';RUNS=OUT.parent

def run(command,log):
    if log.exists():log=log.with_name(log.stem+'_'+str(time.time_ns())+log.suffix)
    with log.open('x') as f:r=subprocess.run([sys.executable,'-u',*map(str,command)],cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
    if r.returncode:raise RuntimeError(f'Command failed rc={r.returncode}; log={log}')

def main():
    while True:
        status=OUT/'history_verified_status.json'
        if status.exists() and json.loads(status.read_text()).get('last_completed')=='8460':break
        # This is a local dependency wait; no repeated Codex log reading.
        time.sleep(15)
    import numpy as np
    old=ROOT/'runs/locomotion/csdog_curriculum_v6/train_20261027_seed42'
    for name,cp in [('2500','evaluated_00002500.pt'),('6000','evaluated_00006000.pt'),('7500','evaluated_00007500.pt'),('8460','interrupted.pt')]:
        raw=np.load(OUT/f'history_{name}_verified/physics_500hz.npz')
        # CASES index14 is forward .25; index15 is backward .25.
        if list(raw['indices'][-4:])!=[224,225,226,227] and not (OUT/f'contact_forward_{name}/provenance.json').exists():
            run([ROOT/'scripts/evaluate/csdog_curriculum_v6_1.py','--checkpoint',old/cp,'--output-dir',OUT/f'contact_forward_{name}','--headless','--raw-contact','--contact-probe'],OUT/f'contact_forward_{name}.log')
    if not (OUT/'contact_report_verified.log').exists():run([ROOT/'scripts/diagnostics/v6_1_contact_report.py'],OUT/'contact_report_verified.log')
    chosen=json.loads((OUT/'history_selection.json').read_text())['checkpoint'];config=OUT/'experiment_config.json'
    common=['--resume','--checkpoint',chosen,'--config',str(config),'--num-envs','256','--seed','42','--headless']
    run([ROOT/'scripts/train/csdog_curriculum_v6_1.py',*common,'--experiment-name','repair_smoke_verified_20261027','--iterations','2','--smoke-test'],OUT/'smoke_verified.log')
    smoke=RUNS/'repair_smoke_verified_20261027'
    if json.loads((smoke/'TRAINING_STATUS.json').read_text())['training_status']!='SMOKE_PASSED':raise RuntimeError('Smoke did not pass')
    for name,variant in [('ab_A_verified_20261027','control'),('ab_B_verified_20261027','improved')]:
        (OUT/'experiment_verified_status.json').write_text(json.dumps(dict(phase=name,status='RUNNING')))
        run([ROOT/'scripts/train/csdog_curriculum_v6_1.py',*common,'--experiment-name',name,'--experiment-updates','500','--variant',variant],OUT/(name+'.log'))
        state=json.loads((RUNS/name/'TRAINING_STATUS.json').read_text())
        if state['training_status']!='EXPERIMENT_COMPLETE':raise RuntimeError(f'{name}: {state["training_status"]}')
        with (RUNS/name/'metrics.jsonl').open() as f:metrics=[json.loads(x) for x in f]
        if len(metrics)!=500:raise RuntimeError('Experiment update budget mismatch')
    (OUT/'experiment_verified_status.json').write_text(json.dumps(dict(phase='AB_COMPLETE',status='COMPLETE')))
if __name__=='__main__':
    try:main()
    except BaseException as e:
        (OUT/'experiment_verified_status.json').write_text(json.dumps(dict(status='BLOCKED',error=repr(e))))
        raise
