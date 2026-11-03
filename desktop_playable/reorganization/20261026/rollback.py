"""Preview guarded rollback; --apply preserves generated files in a quarantine directory."""
from pathlib import Path
import argparse,hashlib,json,os,shutil
R=Path(__file__).resolve().parents[2];E=Path(__file__).resolve().parent

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()

def empty_tree(path):
 if path.is_dir():
  for child in list(path.iterdir()):
   if child.is_dir():empty_tree(child)
  path.rmdir()  # refuses any unexpected file; never removes user data

def main():
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
 m=json.loads((E/'manifest.json').read_text());changes=json.loads((E/'changes.json').read_text())
 created=json.loads((E/'created.json').read_text());done=json.loads((E/'moves_done.json').read_text())
 edits={x['path']:x for x in changes};bad=[]
 for row in m['files']:
  p=R/row['new'];expected=edits.get(row['new'],{}).get('after',row['sha256'])
  if not p.is_file() or sha(p)!=expected:bad.append('changed/missing: '+str(p))
 for x in changes:
  p=R/x['path'];backup=R/x['backup']
  if not p.is_file() or sha(p)!=x['after']:bad.append('later edit: '+str(p))
  if not backup.is_file() or sha(backup)!=x['before']:bad.append('invalid backup: '+str(backup))
 seal=E/'current_files.json'
 if seal.exists():
  for x in json.loads(seal.read_text()):
   p=R/x['path']
   if not p.is_file() or sha(p)!=x['sha256']:bad.append('later edit to current source: '+str(p))
 known={x['new'] for x in m['files']}|set(created)
 for p in (R/'dogfight_rl').rglob('*'):
  if not p.is_file() or '.git' in p.parts or 'runs' in p.relative_to(R/'dogfight_rl').parts:continue
  if str(p.relative_to(R)) not in known:bad.append('unrecorded project file: '+str(p))
 print(json.dumps(dict(status='BLOCKED' if bad else 'READY',moves=len(done),restore_originals=len(changes),
   preserve_generated_files=len(created),failures=bad),ensure_ascii=False,indent=2))
 if bad:return 1
 if not args.apply:return 0
 # Never overwrite or discard generated work. New run outputs stay in runs.
 from datetime import datetime
 quarantine=E/('rollback_generated_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
 assert not quarantine.exists()
 for rel in created:
  p=R/rel
  if p.is_file():
   dest=quarantine/rel;dest.parent.mkdir(parents=True,exist_ok=True);os.rename(p,dest)
 for x in changes:
  shutil.copy2(R/x['backup'],R/x['path'])
 for x in reversed(done):
  a=R/x['old'];b=R/x['new']
  if a.exists():empty_tree(a)
  a.parent.mkdir(parents=True,exist_ok=True);os.rename(b,a)
 for row in m['files']:
  p=R/row['old'];assert p.is_file() and sha(p)==row['sha256'],p
 (E/'rollback_result.json').write_text(json.dumps(dict(status='RESTORED',preserved_generated=str(quarantine)),indent=2)+'\n')
 return 0
if __name__=='__main__':raise SystemExit(main())
