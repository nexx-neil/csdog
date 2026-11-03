"""Sequential read-only common physical history panel. Never runs PPO."""
from pathlib import Path
import subprocess,sys,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'runs/locomotion/csdog_curriculum_v6_1/repair_20261027'
OLD=ROOT/'runs/locomotion/csdog_curriculum_v6/train_20261027_seed42'
for name,checkpoint in [('2500','evaluated_00002500.pt'),('6000','evaluated_00006000.pt'),('7500','evaluated_00007500.pt'),('8460','interrupted.pt')]:
    target=OUT/f'history_{name}_verified'
    with (OUT/f'history_{name}_verified.log').open('x') as log:
        command=[sys.executable,'-u',str(ROOT/'scripts/evaluate/csdog_curriculum_v6_1.py'),'--checkpoint',str(OLD/checkpoint),'--output-dir',str(target),'--headless','--raw-contact']
        result=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
    if result.returncode or not (target/'provenance.json').exists():raise RuntimeError(f'Historical evaluation failed: {name}, rc={result.returncode}')
    (OUT/'history_verified_status.json').write_text(json.dumps(dict(last_completed=name)))
