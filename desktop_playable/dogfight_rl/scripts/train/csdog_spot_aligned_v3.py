"""Strictly budgeted Spot aligned PPO; incompatible old checkpoints cannot be loaded."""
from pathlib import Path
import argparse,sys,json,signal,hashlib,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3'
p=argparse.ArgumentParser();p.add_argument('--experiment-dir',type=Path,default=E);p.add_argument('--stage',choices=['smoke','first','second','validation'],required=True);p.add_argument('--iterations',type=int,required=True);p.add_argument('--num-envs',type=int,default=256);p.add_argument('--settings',type=Path);p.add_argument('--resume',type=Path)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.headless=True
E=a.experiment_dir.resolve()
if E.parent!=R/'runs/locomotion' or not E.name.startswith('csdog_ppo_spot_aligned_v3'):p.error('Independent aligned-v3 experiment directory required')
gate=E/'reports/physics_gate.json'
if not gate.exists() or json.loads(gate.read_text())['status']!='PASS':p.error('V3 dynamic/contact gate required')
if a.stage not in ['smoke','validation'] and not (E/'smoke/final.pt').exists():p.error('Smoke must pass first')
if a.stage=='second' and (not (E/'evaluation_first/summary.json').exists() or a.resume is None):p.error('Evaluate first and specify compatible checkpoint before targeted second stage')
out=E/a.stage
if out.exists():p.error('Refusing output overwrite')
from dogfight.locomotion.spot_aligned_v3.budget import Budget
budget=Budget(E,a.stage,a.iterations);out.mkdir();app=None;env=None;runner=None;status='FAILED'
def timeout(*unused):raise TimeoutError('V3 cumulative 20-minute training runtime limit')
signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,budget.allowed_seconds)
try:
 app=AppLauncher(a).app
 import torch,gymnasium as gym
 from isaaclab.utils.io import dump_yaml
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,AlignedPPOCfg,configure
 from dogfight.locomotion.spot_aligned_v3.runner import Wrapper,Runner
 from dogfight.locomotion.runner import BudgetStop
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 torch.set_num_threads(4);torch.manual_seed(42);torch.backends.cuda.matmul.allow_tf32=True
 settings=json.loads(a.settings.read_text()) if a.settings else {}
 cfg=configure(AlignedEnvCfg(),settings);cfg.scene.num_envs=a.num_envs;cfg.seed=42;cfg.log_dir=str(out)
 agent=AlignedPPOCfg();agent.max_iterations=a.iterations
 if 'init_noise_std' in settings:agent.policy.init_noise_std=float(settings['init_noise_std'])
 identity=dict(task='Dogfight-CSDog-Spot-Aligned-Flat-v3',joint_order=JOINTS,actor_obs=48,critic_obs=48,network=[512,256,128],urdf_sha256=AUDIT['sha256'],action_scale=.2,clip_actions=None,actuator='implicit' if settings.get('implicit_actuator',False) else 'explicit_pd_delay0')
 if a.resume:
  old=json.loads((a.resume.parent/'identity.json').read_text())
  if old!=identity:raise ValueError('Incompatible checkpoint identity: no forced migration')
 (out/'settings.json').write_text(json.dumps(settings,indent=2));(out/'identity.json').write_text(json.dumps(identity,indent=2))
 dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
 sources=list((R/'src/dogfight/locomotion/spot_aligned_v3').glob('*.py'))+[Path(__file__)]
 (out/'source_sha256.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2))
 env=gym.make(identity['task'],cfg=cfg);w=Wrapper(env,clip_actions=None)
 runner=Runner(w,agent.to_dict(),device='cuda:0',log_dir=str(out),budget=budget,output=out)
 initial=torch.cat([p.detach().flatten() for p in runner.alg.policy.actor.parameters()]).clone()
 if a.resume:
  runner.load(str(a.resume));runner.current_learning_iteration+=1
  if 'reset_noise_std' in settings:
   with torch.no_grad():runner.alg.policy.std.fill_(float(settings['reset_noise_std']))
   runner.alg.optimizer.state.pop(runner.alg.policy.std,None)
  (out/'resume_source.json').write_text(json.dumps(dict(path=str(a.resume),sha256=hashlib.sha256(a.resume.read_bytes()).hexdigest()),indent=2))
 try:runner.learn(num_learning_iterations=a.iterations,init_at_random_ep_len=True);status='COMPLETE'
 except BudgetStop:status='TIME_LIMIT'
 runner.save(str(out/'final.pt'))
 final=torch.cat([p.detach().flatten() for p in runner.alg.policy.actor.parameters()])
 assert torch.isfinite(final).all() and not torch.equal(initial,final)
 (out/'parameter_update.json').write_text(json.dumps(dict(actor_l2_change=float((final-initial).norm()),all_parameters_finite=all(bool(torch.isfinite(p).all()) for p in runner.alg.policy.parameters())),indent=2))
 print('TRAIN_RESULT',status,budget.completed,flush=True)
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:
 signal.setitimer(signal.ITIMER_REAL,0)
 if runner is not None and status=='FAILED':
  try:runner.save(str(out/'interrupted.pt'))
  except Exception:pass
 budget.close(status)
 if env is not None:env.close()
 if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
