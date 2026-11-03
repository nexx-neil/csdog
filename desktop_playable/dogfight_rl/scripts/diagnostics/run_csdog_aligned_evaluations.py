"""Sequential read-only evaluations and real videos; never invokes a trainer."""
from pathlib import Path
import subprocess,json,sys,time
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';PY=Path('/home/zxq/miniconda3/envs/dogfight/bin/python');script=R/'scripts/evaluate/csdog_spot_aligned_v3.py'
jobs=[]
old=[('stage2','stage2',R/'runs/locomotion/csdog_ppo_20261026/stage2/final.pt'),('v2_b','v2',R/'runs/locomotion/csdog_ppo_spot_v2/stage_b/final.pt'),('v2_c','v2',R/'runs/locomotion/csdog_ppo_spot_v2/stage_c/final.pt')]
for name,kind,checkpoint in old:jobs.append((name+'_metrics',kind,checkpoint,E/('comparison_'+name),[]))
for name,kind,checkpoint in old+[('second','v3',E/'second/final.pt')]:jobs.append((name+'_video',kind,checkpoint,E/'videos'/name,['--video']))
for stage,filename in [('smoke','final.pt')]+[(s,f'update_{n:04d}.pt') for s in ['first','second'] for n in [30,60,90]]:
 jobs.append((stage+'_'+Path(filename).stem+'_video','v3',E/stage/filename,E/'videos'/stage/Path(filename).stem,['--video','--video-case','forward_stop']))
results=[]
for name,kind,checkpoint,out,extra in jobs:
 expected=out/('provenance.json' if '--video' in extra else 'summary.json')
 if expected.exists():
  results.append(dict(job=name,status='ALREADY_COMPLETE',output=str(out)));continue
 command=[str(PY),str(script),'--kind',kind,'--checkpoint',str(checkpoint),'--output-dir',str(out)]+extra
 start=time.monotonic()
 with (E/'reports'/(name+'.log')).open('w') as log:
  result=subprocess.run(command,cwd=R,stdout=log,stderr=subprocess.STDOUT)
 okay=expected.exists() and result.returncode==0
 results.append(dict(job=name,status='PASS' if okay else 'FAIL',seconds=time.monotonic()-start,output=str(out),command=command))
 (E/'reports/evaluation_jobs.json').write_text(json.dumps(results,indent=2))
 print(name,'PASS' if okay else 'FAIL',flush=True)
 if not okay:sys.exit(1)
print('ALL_READONLY_EVALUATIONS_COMPLETE',flush=True)
