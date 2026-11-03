"""Build present-day indexes and deletion recommendations; never remove content."""
from pathlib import Path
import collections,csv,json,os
from operations import R,E,write,sha,dump
m=json.loads((E/'manifest.json').read_text());done=json.loads((E/'moves_done.json').read_text())
p=R/'dogfight_rl/docs/environment';dest=R/'archive/environment_records/project_environment_docs'
if p.exists():
 move=dict(old=str(p.relative_to(R)),new=str(dest.relative_to(R)),category='historical_environment_document')
 m['moves'].append(move)
 for row in m['files']:
  if row['new'].startswith(move['old']+'/'):row['new']=move['new']+row['new'][len(move['old']):];row['category']=move['category']
 dump('manifest.json',m);dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();os.rename(p,dest)
 done.append(move);dump('moves_done.json',done)
changes={x['path']:x for x in json.loads((E/'changes.json').read_text())}
rows=[];checkpoints=[];groups=collections.defaultdict(list)
for row in m['files']:
 p=R/row['new'];digest=changes.get(row['new'],{}).get('after',row['sha256']);assert p.is_file() and sha(p)==digest,p
 entry=dict(path=row['new'],old=row['old'],size=p.stat().st_size,sha256=digest,category=row['category'])
 rows.append(entry)
 # Exclude backup tarballs, caches and edit-protection copies from deletion advice.
 if 'migration_backups/' not in row['new'] and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts:
  groups[(digest,p.stat().st_size)].append(entry)
 if p.suffix.lower() in ['.pt','.pth','.onnx']:
  model='ANYmal-C' if any(x in row['new'] for x in ['external_home','external_isaaclab']) else 'legacy_dog_a'
  checkpoints.append({**entry,'model':model,'status':'archived_not_new_model_policy',
   'reproduction_notes':'See archive/legacy_dog_a/README.md and complete run/config/source archive; old paths resolve via manifest.'})
def rank(row):
 p=row['path']
 return (0 if p.startswith('dogfight_rl/src/') else 1 if 'legacy_dog_a/' in p else 2 if 'historical_validation/' in p else 3 if 'environment_records/' in p else 4,p)
candidates=[]
for (digest,size),items in groups.items():
 if len(items)<2 or size==0:continue
 items.sort(key=rank)
 # Only exact duplicates among preserved originals; approval and historical-reference review still required.
 removable = [x['path'] for x in items[1:] if 'legacy_compatibility/' in x['path']
              or Path(x['path']).suffix.lower() in ['.pt','.pth','.onnx']
              or 'environment_records/' in x['path'] or 'historical_validation/training_copies/' in x['path']]
 if not removable:continue
 candidates.append(dict(sha256=digest,size=size,retain_candidate=items[0]['path'],
   delete_candidates=removable,potential_bytes=size*len(removable),
   decision='REVIEW_ONLY: preserve provenance, archive snapshot completeness and resource dependencies; update historical indexes before any deletion'))

candidates.sort(key=lambda x:x['potential_bytes'],reverse=True)
dump('checkpoint_index.json',checkpoints)
dump('deduplication_candidates.json',dict(status='PROPOSAL_ONLY_NOT_DELETED',potential_bytes=sum(x['potential_bytes'] for x in candidates),groups=candidates))
with (E/'file_mapping.csv').open('w') as f:
 writer=csv.DictWriter(f,fieldnames=['old','new','category','size','sha256']);writer.writeheader()
 for row in m['files']:writer.writerow({key:row[key] for key in writer.fieldnames})
lines=['# 项目整理迁移清单','', '2026-10-26 实际迁移记录；不恢复已主动删除的 path_migration/20261025，不伪造旧证据。','',
 f"覆盖 {len(m['files'])} 个原始普通文件（含未跟踪文件）；逐文件原路径、新路径、迁移前大小、SHA256 见 [JSON](reorganization/20261026/manifest.json) 与 [CSV](reorganization/20261026/file_mapping.csv)。",'',
 '全部在同一文件系统设备上，用 os.rename 移动。大型日志和备份没有复制。修改前原文按需保存在 reorganization/20261026/originals；changes.json 记录前后摘要；created.json 记录新增文件；moves_done.json 记录实际顺序。', '',
 'Git 迁移前状态、完整未提交二进制diff、IsaacLab状态均已保存。Git已有大量修改/未跟踪文件，不执行提交/clean/reset。', '',
 '回滚：先 `python -B reorganization/20261026/rollback.py` 只读检查；确认没有项目进程/后续编辑后，显式 `--apply` 反序恢复。新增文件先移至 rollback_generated 时间目录，不删除；新run保留。检测哈希变化会拒绝回滚。回滚本轮未应用，避免撤销已完成的整理。', '',
 '首次移动验收发现同名 scripts/configs 目标被后续快照移动携带，已完整反序恢复并调整顺序，再次逐文件校验通过。见 stage_note.txt；没有丢失数据。','',
 '| 原路径 | 新路径 | 分类 |','|---|---|---|']
lines += [f"| `{x['old']}` | `{x['new']}` | {x['category']} |" for x in m['moves']]
write(R/'REORGANIZATION_MANIFEST.md','\n'.join(lines)+'\n')
print(json.dumps(dict(files=len(rows),moved_files=sum(x['old']!=x['new'] for x in m['files']),move_operations=len(done),
 checkpoint_files=len(checkpoints),duplicate_groups=len(candidates),potential_duplicate_bytes=sum(x['potential_bytes'] for x in candidates)),indent=2))
