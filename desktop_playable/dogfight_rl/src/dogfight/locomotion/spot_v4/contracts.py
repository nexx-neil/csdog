"""Static launch/checkpoint contracts. Importing this module never starts Isaac Sim."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[4]
RUNS=ROOT/'runs/locomotion'
JOINTS=[f'joint_{leg}_{j}' for leg in ['lf','rf','lr','rr'] for j in [1,2,3]]
AUDIT_PATH=ROOT/'configs/locomotion/csdog_ppo/model_audit.json'
AUDIT=json.loads(AUDIT_PATH.read_text())
IDENTITY=dict(joint_order=JOINTS,actor_obs=48,critic_obs=48,network=[512,256,128],urdf_sha256=AUDIT['sha256'],action_scale=.2,clip_actions=None,actuator='explicit_pd_delay0')
TASK='Dogfight-CSDog-Spot-Flat-v4'
def output_path(name):
 if not name or not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',name):raise ValueError('--experiment-name must be one safe directory name')
 path=RUNS/name
 if path.exists() or path.is_symlink():raise FileExistsError(f'Refusing overwrite: {path}; choose a new experiment name')
 return path
def validate_identity(checkpoint):
 checkpoint=Path(checkpoint).resolve()
 if not checkpoint.is_file():raise FileNotFoundError(f'Checkpoint not found: {checkpoint}')
 meta=checkpoint.parent/'identity.json'
 if not meta.is_file():raise ValueError('Checkpoint lacks identity.json; cannot verify model and joint mapping')
 identity=json.loads(meta.read_text())
 for key,expected in IDENTITY.items():
  if identity.get(key)!=expected:raise ValueError(f'Incompatible checkpoint {key}: expected {expected!r}, got {identity.get(key)!r}')
 return checkpoint
def completed_updates(state):
 info=state.get('infos') or {}
 if isinstance(info,dict) and 'spot_v4' in info:return int(info['spot_v4']['completed_updates'])
 return int(state['iter'])+1
def finite_tree(value):
 import torch
 if torch.is_tensor(value):return bool(torch.isfinite(value).all())
 if isinstance(value,dict):return all(finite_tree(v) for v in value.values())
 if isinstance(value,(list,tuple)):return all(finite_tree(v) for v in value)
 return True
