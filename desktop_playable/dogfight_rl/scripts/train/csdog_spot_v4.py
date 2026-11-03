"""Manual V4 PPO entrypoint. --iterations is NEW PPO updates, never steps or episodes."""
from pathlib import Path
import argparse,json,sys,os,subprocess,signal,time,traceback,uuid,importlib.util,importlib.metadata
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))

def parser():
 p=argparse.ArgumentParser(description=__doc__,epilog='Examples: --iterations 500 --num-envs 256 --headless --experiment-name spot_v4_500; add --resume --checkpoint /absolute/path/final.pt for full learner continuation. --dry-run performs real simulation checks with ZERO PPO updates.')
 p.add_argument('--iterations',type=int,help='Number of additional PPO optimizer/rollout updates in this invocation.')
 p.add_argument('--num-envs',type=int,default=256);p.add_argument('--experiment-name')
 p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0')
 mode=p.add_mutually_exclusive_group();mode.add_argument('--resume',action='store_true');mode.add_argument('--weights-only',action='store_true',help='Initialize network only; new optimizer and update count zero.')
 p.add_argument('--checkpoint',type=Path);p.add_argument('--seed',type=int,default=42);p.add_argument('--save-interval',type=int,default=50)
 p.add_argument('--max-seconds',type=float,help='Optional training runtime cap; stop at the next completed PPO update.')
 p.add_argument('--dry-run',action='store_true',help='Initialize simulator, environment and learner; validate a checkpoint, but NEVER call learn().')
 p.add_argument('--check-args',action='store_true',help='Parse/static checks only, without simulation or output creation.')
 p.add_argument('--validation-run',action='store_true',help='Repair-session smoke only: <=32 envs and cumulative <=5 updates. Normal manual runs have no fixed iteration cap.')
 return p

def prepare(a):
 from dogfight.locomotion.spot_v4.contracts import output_path,validate_identity,ROOT,AUDIT,IDENTITY
 if a.iterations is None:
  if a.dry_run:a.iterations=0
  else:raise ValueError('--iterations is required for training')
 if a.iterations<0 or (not a.dry_run and a.iterations<1):raise ValueError('--iterations must be positive')
 if a.num_envs<1 or a.save_interval<1:raise ValueError('--num-envs and --save-interval must be positive')
 if a.max_seconds is not None and a.max_seconds<=0:raise ValueError('--max-seconds must be positive')
 if (a.resume or a.weights_only) and a.checkpoint is None:raise ValueError('--resume/--weights-only requires --checkpoint')
 if a.checkpoint is not None and not (a.resume or a.weights_only):raise ValueError('Choose --resume or --weights-only explicitly for --checkpoint')
 if a.checkpoint:a.checkpoint=validate_identity(a.checkpoint)
 out=output_path(a.experiment_name)
 for module in ['isaacsim','isaaclab','isaaclab_tasks','rsl_rl']:
  if importlib.util.find_spec(module) is None:raise RuntimeError(f'Required module unavailable: {module}; use the frozen dogfight interpreter')
 for filename in [R/'assets/csdog_12dof/import_v1/csdog.usd',R.parent/'model/robot.urdf']:
  if not filename.is_file():raise FileNotFoundError(f'Robot asset missing: {filename}')
 import hashlib
 if hashlib.sha256((R.parent/'model/robot.urdf').read_bytes()).hexdigest()!=IDENTITY['urdf_sha256']:raise ValueError('Raw robot identity SHA changed')
 versions={k:importlib.metadata.version(k) for k in ['isaacsim','rsl-rl-lib','torch']}
 if not versions['isaacsim'].startswith('5.1.0') or versions['rsl-rl-lib']!='3.1.2':raise RuntimeError(f'Frozen environment version mismatch: {versions}')
 if a.validation_run and not a.dry_run:
  ledger=R/'runs/locomotion/csdog_ppo_spot_v4/codex_validation_budget.json'
  data=json.loads(ledger.read_text())
  if a.num_envs>32 or a.iterations+data['completed_updates']>5:raise ValueError('Repair validation capped at 5 cumulative PPO updates and 32 environments')
 return out,versions

def worker(launch_path):
 import fcntl,hashlib,random
 launch_path=Path(launch_path);launch=json.loads(launch_path.read_text());a=argparse.Namespace(**launch['args']);out=launch_path.parent
 if os.environ.get('CSDOG_V4_WORKER_TOKEN')!=launch['token']:raise RuntimeError('Worker must be launched through the public CLI')
 lock=(out/'.worker.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 if (out/'result.json').exists() or (out/'progress.json').exists():raise RuntimeError('Refusing to rerun an existing worker output')
 app=None;env=None;runner=None;validation_lock=None;status='FAILED';result={};exit_error=None
 try:
  import torch,numpy as np
  if not torch.cuda.is_available():raise RuntimeError('CUDA unavailable; activate the frozen dogfight environment and verify driver/GPU availability')
  if not a.device.startswith('cuda:') or not a.device[5:].isdigit() or int(a.device[5:])>=torch.cuda.device_count():raise ValueError(f'Invalid CUDA device {a.device}; available GPUs: {torch.cuda.device_count()}')
  torch.cuda.set_device(a.device)
  torch.set_num_threads(4);torch.manual_seed(a.seed);np.random.seed(a.seed);random.seed(a.seed)
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=a.headless,device=a.device,enable_cameras=False).app
  import gymnasium as gym
  from isaaclab.utils.io import dump_yaml
  from dogfight.locomotion.spot_v4.config import V4EnvCfg,V4PPOCfg
  from dogfight.locomotion.spot_v4.contracts import TASK,IDENTITY
  from dogfight.locomotion.spot_v4.runtime import preflight,load_learner
  from dogfight.locomotion.spot_v4.runner import Runner,Wrapper,GracefulStop
  gym.spec(TASK)
  cfg=V4EnvCfg();cfg.scene.num_envs=a.num_envs;cfg.seed=a.seed;cfg.sim.device=a.device;cfg.log_dir=str(out)
  agent=V4PPOCfg();agent.seed=a.seed;agent.device=a.device;agent.max_iterations=a.iterations;agent.save_interval=a.save_interval
  (out/'identity.json').write_text(json.dumps(dict(task=TASK,**IDENTITY),indent=2));(out/'settings.json').write_text(json.dumps(dict(version='spot_v4',seed=a.seed,stop_logic='command_only_ramp_0.25s'),indent=2))
  dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
  env=gym.make(TASK,cfg=cfg);checks=preflight(env)
  (out/'preflight.json').write_text(json.dumps(checks,indent=2));wrapped=Wrapper(env,clip_actions=None)
  runner=Runner(wrapped,agent.to_dict(),device=a.device,log_dir=str(out),output=out,requested=a.iterations,save_interval=a.save_interval,max_seconds=a.max_seconds)
  resume_info=dict(mode='from_scratch',source_checkpoint_updates=0,base_updates=0,optimizer_restored=False,learning_rate=runner.alg.learning_rate)
  if a.checkpoint:resume_info=load_learner(runner,Path(a.checkpoint),weights_only=a.weights_only)
  runner.base_updates=resume_info['base_updates']
  (out/'resume_info.json').write_text(json.dumps(resume_info,indent=2))
  print(f"UPDATES: source={resume_info['source_checkpoint_updates']}, base={runner.base_updates}, requested_new={a.iterations}, proposed_final={runner.base_updates+a.iterations}; mode={resume_info['mode']}",flush=True)
  sources=list((R/'src/dogfight/locomotion/spot_v4').glob('*.py'))+[Path(__file__)]
  (out/'source_sha256.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2))
  if a.dry_run:status='DRY_RUN_PASS'
  else:
   if a.validation_run:
    ledger=R/'runs/locomotion/csdog_ppo_spot_v4/codex_validation_budget.json'
    validation_lock=ledger.with_suffix('.lock').open('a');fcntl.flock(validation_lock,fcntl.LOCK_EX|fcntl.LOCK_NB);data=json.loads(ledger.read_text())
    if data['completed_updates']+a.iterations>5:raise ValueError('Repair validation cap exceeded')
    data['runs'].append(dict(experiment=out.name,requested_updates=a.iterations,completed_updates=0));ledger.write_text(json.dumps(data,indent=2));runner.validation_budget=ledger
   def stop(signum,frame):
    runner.stop_requested=signal.Signals(signum).name
    print('Stop requested; saving after the next completed PPO update.',flush=True)
   signal.signal(signal.SIGINT,stop);signal.signal(signal.SIGTERM,stop)
   before={k:v.detach().clone() for k,v in runner.alg.policy.actor.state_dict().items()}
   try:
    runner.learn(num_learning_iterations=a.iterations,init_at_random_ep_len=True);status='COMPLETE'
   except GracefulStop as exc:status='INTERRUPTED';result['stop_reason']=str(exc)
   checkpoint=out/('final.pt' if status=='COMPLETE' else 'interrupted.pt');runner.save(str(checkpoint))
   changed=any(not torch.equal(v,runner.alg.policy.actor.state_dict()[k]) for k,v in before.items())
   if not changed:raise RuntimeError('PPO completed without changing actor parameters')
   result.update(checkpoint=str(checkpoint),actor_parameters_changed=changed)
  result.update(status=status,base_updates=runner.base_updates,requested_updates=a.iterations,completed_new_updates=runner.session_updates,total_updates=runner.total_updates,proposed_final_updates=runner.base_updates+a.iterations,learning_rate=runner.alg.learning_rate,dry_run=a.dry_run,optimizer_restored=resume_info['optimizer_restored'],simulation_state_restored=False)
 except BaseException as exc:
  traceback.print_exc();sys.stderr.flush();exit_error=str(exc)
  try:
   import torch
   oom=isinstance(exc,torch.cuda.OutOfMemoryError) or 'out of memory' in str(exc).lower()
  except Exception:oom=False
  if oom:exit_error='GPU OOM. Reduce --num-envs (for example 256 -> 128); no automatic retry or extra PPO updates.'
  result.update(status='FAILED',error=exit_error)
  if runner is not None:
   result.update(completed_new_updates=runner.session_updates,total_updates=runner.total_updates)
   try:runner.save(str(out/'failed_boundary.pt'))
   except Exception:pass
 finally:
  (out/'result.json').write_text(json.dumps(result,indent=2))
  print('RESULT',json.dumps(result),flush=True)
  if validation_lock:fcntl.flock(validation_lock,fcntl.LOCK_UN);validation_lock.close()
  if env is not None:
   try:env.close()
   except Exception:pass
  if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)

def main():
 p=parser();a=p.parse_args()
 try:out,versions=prepare(a)
 except Exception as exc:p.error(str(exc))
 values={k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()}
 if a.check_args:
  print(json.dumps(dict(status='ARGUMENTS_VALID',output=str(out),additional_ppo_updates=a.iterations,versions=versions,args=values),indent=2));return 0
 out.mkdir(parents=True,exist_ok=False);token=uuid.uuid4().hex
 launch=out/'launch_parameters.json';launch.write_text(json.dumps(dict(args=values,token=token,versions=versions),indent=2))
 from dogfight.locomotion.spot_v4.cli import supervise
 return supervise(Path(__file__),launch,out,'train.log')
if __name__=='__main__':
 if len(sys.argv)==3 and sys.argv[1]=='--_worker':worker(sys.argv[2])
 else:raise SystemExit(main())
