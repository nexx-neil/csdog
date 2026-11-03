"""Read-only validation of current syntax, model assets, metadata and original hashes."""
from pathlib import Path
import ast,json,subprocess,sys,tomllib,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[2];P=R/'dogfight_rl';E=Path(__file__).resolve().parent
sys.path.insert(0,str(E));from operations import sha
result={'python_files':0,'shell_files':0,'urdf_mesh_references':0,'errors':[]}
for base in [P/'src',P/'scripts',P/'tests']:
 for p in base.rglob('*.py'):
  ast.parse(p.read_text(),filename=str(p));result['python_files']+=1
 for p in base.rglob('*.sh'):
  subprocess.run(['bash','-n',str(p)],check=True);result['shell_files']+=1
for p in [P/'launch.py',P/'setup.py']:
 ast.parse(p.read_text(),filename=str(p));result['python_files']+=1
for p in [P/'pyproject.toml',P/'configs/battle/extension.toml']:
 tomllib.loads(p.read_text())
# All original URDFs remain byte-preserved; resolve their package URIs explicitly.
for base in [R/'model',R/'archive/legacy_dog_a/assets',R/'archive/legacy_compatibility/assets']:
 for p in base.rglob('*.urdf'):
  for mesh in ET.parse(p).getroot().iter('mesh'):
   uri=mesh.attrib['filename']
   if uri.startswith('package://csdog_urdf/'):
    target=R/'model'/uri.removeprefix('package://csdog_urdf/')
   elif uri.startswith('package://fix_new.SLDASM/'):
    target=R/'archive/legacy_dog_a/assets/original/fix_new.SLDASM'/uri.removeprefix('package://fix_new.SLDASM/')
   else:target=p.parent/uri
   result['urdf_mesh_references']+=1
   if not target.is_file():result['errors'].append('mesh missing: '+str(target))
manifest=json.loads((E/'manifest.json').read_text());changes={x['path']:x for x in json.loads((E/'changes.json').read_text())}
for x in manifest['files']:
 p=R/x['new'];expected=changes.get(x['new'],{}).get('after',x['sha256'])
 if not p.is_file() or sha(p)!=expected:result['errors'].append('hash mismatch: '+x['new'])
result['original_files_verified']=len(manifest['files'])
result['status']='FAIL' if result['errors'] else 'PASS'
(E/'static_validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(result,ensure_ascii=False,indent=2));raise SystemExit(bool(result['errors']))
