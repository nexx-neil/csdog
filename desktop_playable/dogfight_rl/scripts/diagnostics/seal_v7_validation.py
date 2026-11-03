"""Run current-code tests and a real normalized PPO/physics smoke, then seal AutoPPO gate."""
from pathlib import Path
import sys,subprocess,json,hashlib,time,fcntl
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.autoppo.config import PYTHON
from dogfight.autoppo.experiment_manager import source_hashes
from dogfight.autoppo.storage import atomic_json
BASE=ROOT/'runs/locomotion/csdog_phase_guided_ppo_v7'
with (BASE/'manager.lock').open('a') as probe:fcntl.flock(probe,fcntl.LOCK_EX|fcntl.LOCK_NB)
start_hash=source_hashes()
tests=['tests/test_phase_guided_v7.py','tests/test_phase_v7_search.py','tests/test_phase_v7_manager.py','tests/test_phase_v7_trace.py','tests/test_autoppo_system.py','tests/test_autoppo_gait.py']
with (BASE/'regression_tests.log').open('w') as log:
 result=subprocess.run([str(PYTHON),'-m','pytest','-q',*tests],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,env=__import__('os').environ|{'PYTHONPATH':str(ROOT/'src')})
if result.returncode:raise RuntimeError('Current-source unit/regression tests failed')
smoke=BASE/('validation_'+time.strftime('%Y%m%d_%H%M%S'))
with (BASE/'normalized_smoke.log').open('w') as log:
 result=subprocess.run([str(PYTHON),'-u',str(ROOT/'scripts/autoppo/v7.py'),'smoke','--base',str(smoke),'--arm','D','--updates','2','--slip-mode','log'],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
if result.returncode:raise RuntimeError('PPO smoke process failed')
proof=smoke/'smoke/D/result.json';r=json.loads(proof.read_text())
if r['status']!='COMPLETE' or r['updates']!=2:raise RuntimeError('PPO smoke did not complete two updates and physical evaluation')
preflight=json.loads((proof.parent/'preflight.json').read_text());assert preflight['actor_obs']==50 and preflight['action_dim'] if 'action_dim' in preflight else preflight['actor_obs']==50
import torch
from dogfight.locomotion.spot_v4.contracts import finite_tree
cp=torch.load(r['checkpoint'],map_location='cpu',weights_only=False);assert finite_tree(cp) and (cp['model_state_dict']['std']>0).all()
protected=json.loads((BASE/'protected_assets_sha256.json').read_text());assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in protected.items())
collision=json.loads((BASE/'collision_physics.json').read_text())
for x in collision.values():assert len(x['joints'])==12 and len(x['bodies'])==13 and x['summary']['tilt']<.1 and x['summary']['falls']==0
if source_hashes()!=start_hash:raise RuntimeError('Source changed during verification; refusing seal')
evidence=[BASE/'regression_tests.log',proof,proof.parent/'preflight.json',Path(r['checkpoint']),BASE/'collision_physics.json',BASE/'collision_geometry.json',BASE/'protected_assets_sha256.json',ROOT/'assets/csdog_12dof/collision_sole_candidate/csdog.usda',BASE/'LAUNCH_RUNTIME_VERIFIED.json']
evidence += [ROOT/p for p in tests]
gate=dict(schema='V7-validation-not-policy-qualification',checks={k:'PASS' for k in ['gait','reward_timing','physical_evaluation','checkpoint_protection','search','recovery','ppo_smoke']},source_hashes=start_hash,evidence=[dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in evidence],normalized_smoke=str(proof),physical_policy_qualified=False,meaning='Pipeline checks passed. No claim that a policy has passed walking acceptance.')
atomic_json(BASE/'reports/VALIDATION_GATE.json',gate)
print(json.dumps(dict(status='V7_PIPELINE_VALIDATED',smoke=str(proof),gate=str(BASE/'reports/VALIDATION_GATE.json'))),flush=True)
