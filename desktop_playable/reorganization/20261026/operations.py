"""Guarded move/edit helpers for this reorganization; no compatibility imports."""
from pathlib import Path
import hashlib,json,os,shutil
R=Path(__file__).resolve().parents[2]; E=Path(__file__).resolve().parent
M=json.loads((E/'manifest.json').read_text())
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def dump(name,data):
 p=E/name;tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');tmp.replace(p)
def write(path,content):
 p=R/path if not isinstance(path,Path) else path
 rel=str(p.relative_to(R)); changes=json.loads((E/'changes.json').read_text()); created=json.loads((E/'created.json').read_text())
 if p.exists():
  if p.read_text()==content:return
  if not any(x['path']==rel for x in changes) and rel not in created:
   backup=E/'originals'/rel;backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,backup)
   changes.append(dict(path=rel,before=sha(p),backup=str(backup.relative_to(R))))
 else:
  if rel not in created:created.append(rel);dump('created.json',created)
 p.parent.mkdir(parents=True,exist_ok=True);p.write_text(content)
 for x in changes:
  if x['path']==rel:x['after']=sha(p)
 dump('changes.json',changes)
def move_all():
 done=json.loads((E/'moves_done.json').read_text())
 for move in M['moves']:
  if move in done:continue
  a=R/move['old'];b=R/move['new']; assert a.exists() and not b.exists(),(a,b)
  b.parent.mkdir(parents=True,exist_ok=True);assert a.stat().st_dev==b.parent.stat().st_dev
  os.rename(a,b);done.append(move);dump('moves_done.json',done)
 # Every original file has reached its planned location without content changes.
 for x in M['files']:
  p=R/x['new'];assert p.is_file() and p.stat().st_size==x['size'] and sha(p)==x['sha256'],x
 dump('move_verification.json',dict(status='PASS',files=len(M['files'])))
if __name__=='__main__':move_all()
