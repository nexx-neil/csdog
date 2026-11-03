"""Train the new csdog only; explicit iteration limit required; no old checkpoint defaults."""
import argparse,sys,json,time,hashlib,signal,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--iterations',type=int,required=True);p.add_argument('--num-envs',type=int,default=128);p.add_argument('--run-name',required=True);p.add_argument('--resume',type=Path);p.add_argument('--settings',type=Path);p.add_argument('--max-seconds',type=int,default=900)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();args.headless=True
if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]*',args.run_name):p.error('run-name must be a single safe directory name')
if args.max_seconds<1:p.error('max-seconds must be positive')
from dogfight.locomotion.budget import Budget
EXPERIMENT=ROOT/'runs/locomotion/csdog_ppo_20261026'
physics=EXPERIMENT/'reports/physics_gate.json'
if not physics.is_file() or json.loads(physics.read_text())['status']!='PASS':p.error('Physics gate has not passed')
if not args.run_name.startswith('smoke'):
 gate=EXPERIMENT/'smoke_gate.json'
 if not gate.is_file() or json.loads(gate.read_text())['status']!='PASS':p.error('PPO smoke gate has not passed')
out=EXPERIMENT/args.run_name
if out.exists():p.error('output already exists; choose a new run-name')
budget=Budget(EXPERIMENT,args.run_name,args.iterations,args.max_seconds);out.mkdir()
def timeout_handler(signum,frame):
 raise TimeoutError('Single-run/cumulative wall-time limit reached')
signal.signal(signal.SIGALRM,timeout_handler)
signal.setitimer(signal.ITIMER_REAL,budget.allowed_seconds)
app=None;env=None;runner=None;status='FAILED'
try:
 app=AppLauncher(args).app
 import torch,gymnasium as gym
 from isaaclab.utils.io import dump_yaml
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.ppo_cfg import CSDogPPORunnerCfg
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 from dogfight.locomotion.runner import MeasuredWrapper,MeasuredRunner,BudgetStop
 torch.set_num_threads(4);torch.manual_seed(42);torch.backends.cuda.matmul.allow_tf32=True
 settings=json.loads(args.settings.read_text()) if args.settings else {}
 cfg=configure(CSDogEnvCfg(),settings);cfg.scene.num_envs=args.num_envs;cfg.sim.device=args.device or 'cuda:0';cfg.seed=42;cfg.log_dir=str(out)
 agent=CSDogPPORunnerCfg();agent.max_iterations=args.iterations;agent.device=cfg.sim.device
 identity={'model_id':'csdog_12dof','urdf_sha256':AUDIT['sha256'],'joint_order':JOINTS,'actor_observation_dimension':45,'critic_observation_dimension':48,'action_dimension':12,'action_scale':cfg.actions.joint_pos.scale}
 if args.resume:
  source=json.loads((args.resume.parent/'identity.json').read_text())
  if source!=identity:raise ValueError('checkpoint model/observations/actions identity incompatible')
 (out/'identity.json').write_text(json.dumps(identity,indent=2));(out/'settings.json').write_text(json.dumps(settings,indent=2))
 dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg);wrapped=MeasuredWrapper(env,clip_actions=1.)
 runner=MeasuredRunner(wrapped,agent.to_dict(),device=cfg.sim.device,log_dir=str(out),budget=budget,output=out)
 if args.resume:
  runner.load(str(args.resume));runner.current_learning_iteration+=1
  (out/'resume_source.json').write_text(json.dumps({'path':str(args.resume.resolve()),'sha256':hashlib.sha256(args.resume.read_bytes()).hexdigest()}))
 try:runner.learn(num_learning_iterations=args.iterations,init_at_random_ep_len=True);status='COMPLETE'
 except BudgetStop as exc:print(str(exc),flush=True);status='TIME_LIMIT'
 runner.save(str(out/'final.pt'))
 # A smoke gate is evidence-based, and later stages require this marker.
 if args.run_name.startswith('smoke'):
  (EXPERIMENT/'smoke_gate.json').write_text(json.dumps({'status':'PASS','run':args.run_name,'updates':budget.completed,'finite_parameters':True}))
 print('TRAIN_RESULT',json.dumps({'status':status,'updates':budget.completed,'checkpoint':str(out/'final.pt')}),flush=True)
finally:
 signal.setitimer(signal.ITIMER_REAL,0)
 if runner is not None and status=='FAILED':
  try:runner.save(str(out/'interrupted.pt'))
  except Exception:pass
 budget.close(status)
 if env is not None:env.close()
 if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
