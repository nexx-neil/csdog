"""Record the new task as an explicit amendment, never rewrite historical migration evidence."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[2];R=ROOT.parent;EXP=ROOT/'runs/locomotion/csdog_ppo_20261026'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
old={x['path']:x['sha256'] for x in json.loads((R/'reorganization/20261026/current_files.json').read_text())}
changes=json.loads((EXP/'protection/changed_files.json').read_text())
for row in changes:
 assert sha(R/row['backup'])==row['before'],row
 assert old[row['path']]==row['before'],row
 row['after']=sha(R/row['path'])
(EXP/'protection/changed_files.json').write_text(json.dumps(changes,indent=2)+'\n')
new=[]
for p in ROOT.rglob('*'):
 rel=p.relative_to(ROOT)
 if not p.is_file() or any(x in ('.git','__pycache__','.pytest_cache','runs') for x in rel.parts):continue
 name=str(p.relative_to(R))
 if name not in old:new.append({'path':name,'sha256':sha(p),'size':p.stat().st_size})
manifest={'purpose':'User-authorized new csdog PPO task, separate from archived Dog A','old_seal_unchanged':True,'changes':changes,'new_files':new}
(EXP/'protection/task_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
# Hash experiment outputs too; exclude this generated index and disposable pytest temp files.
artifacts=[]
for p in EXP.rglob('*'):
 if p.is_file() and p.name!='artifact_manifest.json' and 'pytest_tmp' not in p.parts and '__pycache__' not in p.parts:
  artifacts.append({'path':str(p.relative_to(R)),'sha256':sha(p),'size':p.stat().st_size})
(EXP/'artifact_manifest.json').write_text(json.dumps(artifacts,indent=2)+'\n')
print(json.dumps({'protected_current_edits':len(changes),'new_task_static_files':len(new),'experiment_artifacts':len(artifacts)}))
