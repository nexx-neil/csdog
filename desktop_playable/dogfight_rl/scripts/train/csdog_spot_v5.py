"""V5 native PPO entrypoint: --iterations always means additional updates."""
from pathlib import Path
import sys,argparse,json,hashlib,os,time,signal,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--config',type=Path,required=True);p.add_argument('--iterations',type=int,required=True);p.add_argument('--num-envs',type=int,default=256);p.add_argument('--seed',type=int,default=42);p.add_argument('--experiment-name',required=True);p.add_argument('--save-interval',type=int,default=25);p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0');p.add_argument('--checkpoint',type=Path);p.add_argument('--resume',action='store_true');p.add_argument('--weights-only',action='store_true');p.add_argument('--search-ledger',type=Path);p.add_argument('--check-args',action='store_true');p.add_argument('--audit',action='store_true')
 a=p.parse_args()
 import yaml
 opt=yaml.safe_load(a.config.read_text());out=R/'runs/locomotion/csdog_ppo_tuning_v5/experiments'/a.experiment_name
 if Path(a.experiment_name).name!=a.experiment_name or a.experiment_name in ['.','..']:p.error('Use a simple unique experiment name')
 if a.iterations<1 or a.num_envs<8 or a.num_envs%8 or a.save_interval<1:p.error('Positive iterations/interval and num-envs divisible by eight required')
 if bool(a.checkpoint)!=bool(a.resume or a.weights_only) or (a.resume and a.weights_only):p.error('Checkpoint requires exactly one of --resume / --weights-only')
 if out.exists():p.error('Refusing output overwrite')
 if opt['ppo']['schedule'] not in ['fixed','adaptive'] or not 0<opt['ppo']['learning_rate']<=.001 or not 0<opt['ppo']['init_noise_std']<=1:p.error('Unsupported PPO configuration')
 if opt['commands']['distribution'] not in ['uniform','balanced'] or (opt['commands']['distribution']=='balanced' and abs(sum(opt['commands']['probabilities'])-1)>1e-6):p.error('Invalid command distribution')
 if a.checkpoint:
  from dogfight.locomotion.spot_v4.contracts import validate_identity
  a.checkpoint=validate_identity(a.checkpoint)
 if a.check_args:print(json.dumps(dict(status='ARGUMENTS_VALID',additional_updates=a.iterations,output=str(out))));return
 out.mkdir(parents=True)
 sources=list((R/'src/dogfight/locomotion/spot_v5').glob('*.py'))+[Path(__file__)]
 (out/'source_sha256.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},indent=2))
 opt['training'].update(num_envs=a.num_envs,seed=a.seed,checkpoint_interval=a.save_interval)
 raw=yaml.safe_dump(opt,sort_keys=True);(out/'config.yaml').write_text(raw);(out/'config_sha256.txt').write_text(hashlib.sha256(raw.encode()).hexdigest())
 (out/'launch.json').write_text(json.dumps({k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},indent=2))
 ledger=a.search_ledger or out/'training_budget.json'
 if not ledger.exists():ledger.write_text(json.dumps(dict(updates=0,seconds=0.,environment_steps=0)))
 data=json.loads(ledger.read_text())
 if data['updates']+a.iterations>1500 or data['seconds']>=3600:raise ValueError('Requested updates exceed this ledger remaining budget')
 import fcntl
 lock=ledger.with_suffix('.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 import torch,numpy as np,random
 torch.set_num_threads(4);torch.manual_seed(a.seed);np.random.seed(a.seed);random.seed(a.seed)
 from isaaclab.app import AppLauncher
 app=AppLauncher(headless=a.headless,device=a.device).app
 env=None;runner=None;result={};started=time.monotonic()
 try:
  import gymnasium as gym
  from isaaclab.utils.io import dump_yaml
  from dogfight.locomotion.spot_v5.config import build
  from dogfight.locomotion.spot_v5.telemetry import Runner,Wrapper,GracefulStop
  from dogfight.locomotion.spot_v5.evaluation import evaluate
  from dogfight.locomotion.spot_v4.contracts import TASK,IDENTITY
  from dogfight.locomotion.spot_v4.runtime import preflight,load_learner
  cfg,agent=build(opt,a.num_envs,a.seed,a.device);cfg.log_dir=str(out);agent.max_iterations=a.iterations;agent.save_interval=a.save_interval
  env=gym.make(TASK,cfg=cfg);(out/'preflight.json').write_text(json.dumps(preflight(env),indent=2))
  (out/'identity.json').write_text(json.dumps(dict(task=TASK,**IDENTITY),indent=2))
  dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
  wrapped=Wrapper(env,clip_actions=None)
  torch.manual_seed(a.seed);np.random.seed(a.seed);random.seed(a.seed)
  runner=Runner(wrapped,agent.to_dict(),device=a.device,log_dir=str(out),output=out,requested=a.iterations,save_interval=a.save_interval,ledger=ledger)
  initial_hash=hashlib.sha256(b''.join(v.detach().cpu().numpy().tobytes() for k,v in runner.alg.policy.state_dict().items() if k.startswith(('actor.','critic.')))).hexdigest()
  (out/'initial_network_sha256.txt').write_text(initial_hash)
  source=dict(mode='from_scratch',base_updates=0)
  if a.checkpoint:source=load_learner(runner,a.checkpoint,weights_only=a.weights_only)
  runner.base_updates=source['base_updates'];(out/'resume_info.json').write_text(json.dumps(source,indent=2))
  def stop(sig,frame):runner.stop_requested='signal_'+str(sig)
  signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
  env.unwrapped.reset(seed=a.seed)
  if a.audit:
   from dogfight.locomotion.spot_v5.audit import audit
   audit(runner,out)
  while runner.session_updates<a.iterations:
   remaining=a.iterations-runner.session_updates;n=min(a.save_interval,remaining)
   runner.current_learning_iteration=runner.total_updates
   runner.learn(n,init_at_random_ep_len=runner.session_updates==0)
   runner.current_learning_iteration=runner.total_updates
   evaluate(runner,out,runner.total_updates)
  runner.save(str(out/'final.pt'));result=dict(status='COMPLETE')
 except BaseException as exc:
  traceback.print_exc();result=dict(status='STOPPED' if type(exc).__name__=='GracefulStop' else 'FAILED',error=str(exc))
  if runner is not None:
   try:runner.save(str(out/'interrupted.pt'))
   except Exception:pass
 finally:
  result.update(completed_new_updates=runner.session_updates if runner else 0,total_updates=runner.total_updates if runner else 0,wall_seconds=time.monotonic()-started)
  (out/'result.json').write_text(json.dumps(result,indent=2));print('V5_RESULT',json.dumps(result),flush=True)
  if runner is not None and runner.writer is not None:runner.writer.close()
  if env is not None:env.close()
  app.close(wait_for_replicator=False,skip_cleanup=True)
if __name__=='__main__':main()
