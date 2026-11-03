"""Seal reviewed current static files after documented reorganization edits.

Do not run this to hide regressions; validate the baseline/edit backups and review changes first.
"""
from pathlib import Path
import json
from operations import R,E,sha,dump
paths=[]
for p in (R/'dogfight_rl').rglob('*'):
 if p.is_file() and not any(x in ('.git','__pycache__','.pytest_cache','runs') for x in p.relative_to(R/'dogfight_rl').parts):paths.append(p)
for name in ['AGENTS.md','DOGFIGHT_ENVIRONMENT.md','PROJECT_STRUCTURE.md','REORGANIZATION_MANIFEST.md','REORGANIZATION_REPORT.md']:
 p=R/name
 if p.is_file():paths.append(p)
for name in ['manifest.json','changes.json','created.json','moves_done.json','file_mapping.csv','checkpoint_index.json',
             'deduplication_candidates.json','operations.py','rollback.py','check_static.py','build_indexes.py','seal_current.py']:
 paths.append(E/name)
dump('current_files.json',[dict(path=str(p.relative_to(R)),sha256=sha(p)) for p in sorted(set(paths))])
print('Sealed',len(set(paths)),'static current files and evidence indexes; runtime outputs excluded.')
