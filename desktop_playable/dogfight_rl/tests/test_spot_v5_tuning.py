"""Pure command/reward tests without starting Kit, executing the actual function AST."""
import ast
from pathlib import Path
from types import SimpleNamespace
import torch
R=Path(__file__).resolve().parents[1]
def function(name):
 tree=ast.parse((R/'src/dogfight/locomotion/spot_v5/config.py').read_text())
 nodes=[n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name]
 namespace={'torch':torch};exec(compile(ast.Module(body=[nodes[0]],type_ignores=[]),'<v5>','exec'),namespace)
 return namespace[name]
def test_balanced_real_sampling():
 import yaml
 options=yaml.safe_load((R/'csdog_ppo_tuning_v5/configs/baseline.yaml').read_text())['commands'];n=50000
 fake=SimpleNamespace(device='cpu',cfg=SimpleNamespace(v5_options=options),vel_command_b=torch.zeros(n,3),is_standing_env=torch.zeros(n,dtype=torch.bool))
 torch.manual_seed(42);function('_resample_command')(fake,torch.arange(n));v=fake.vel_command_b
 assert torch.allclose(fake.sample_counts/n,torch.tensor(options['probabilities']),atol=.008)
 backward=(v[:,0]<0)&(v[:,1]==0)&(v[:,2]==0);right=(v[:,1]<0)&(v[:,0]==0)&(v[:,2]==0)
 assert backward.any() and right.any()
 assert ((v[backward,0]>=-.30)&(v[backward,0]<=-.12)).all()
 assert ((v[right,1]>=-.20)&(v[right,1]<=-.10)).all()
 assert (v[fake.is_standing_env]==0).all()
def test_translation_gate_keeps_yaw_and_stop():
 command=torch.tensor([[.2,0,0],[-.2,0,0],[0,.2,0],[0,-.2,0],[0,0,.4],[0,0,0]])
 env=SimpleNamespace(command_manager=SimpleNamespace(get_command=lambda _:command))
 assert function('translating')(env).tolist()==[True,True,True,True,False,False]
