"""Budgeted paired Spot v2 PPO experiment; no writes to original experiment."""
import argparse,sys,json,signal,hashlib
from pathlib import Path
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_v2'
p=argparse.ArgumentParser();p.add_argument('--experiment-dir',type=Path,default=E);p.add_argument('--settings',type=Path);p.add_argument('--stage',choices=['smoke','stage_b','stage_c'],required=True);p.add_argument('--iterations',type=int,required=True);p.add_argument('--num-envs',type=int,default=256)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.headless=True
E=a.experiment_dir.resolve()
if not E.is_relative_to(R/'runs/locomotion') or E.name=='csdog_ppo_20261026':p.error('Use an independent experiment under runs/locomotion')
if not (E/'reports/physics_gate.json').exists() or json.loads((E/'reports/physics_gate.json').read_text())['status']!='PASS':p.error('New physics/contact gate required')
if a.stage!='smoke' and not (E/'smoke/final.pt').exists():p.error('Smoke checkpoint required')
if a.stage=='smoke' and a.iterations>5:p.error('Smoke max 5')
out=E/a.stage
if out.exists():p.error('Refusing output overwrite')
from dogfight.locomotion.spot_v2.budget import Budget
budget=Budget(E,a.stage,a.iterations);out.mkdir();app=None;env=None;runner=None;status='FAILED'
def timeout(signum,frame):raise TimeoutError('Cumulative 30min training wall limit')
signal.signal(signal.SIGALRM,timeout);signal.setitimer(signal.ITIMER_REAL,budget.allowed_seconds)
try:
 app=AppLauncher(a).app
 import torch,gymnasium as gym
 from isaaclab.utils.io import dump_yaml
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.spot_v2.config import improve
 from dogfight.locomotion.spot_v2.contacts import add_sensors
 from dogfight.locomotion.spot_v2.runner import SpotWrapper,MeasuredRunner
 from dogfight.locomotion.runner import BudgetStop
 from dogfight.locomotion.ppo_cfg import CSDogPPORunnerCfg
 from dogfight.locomotion.robot_cfg import AUDIT,JOINTS
 torch.set_num_threads(4);torch.manual_seed(42);torch.backends.cuda.matmul.allow_tf32=True
 settings=dict(action_scale=.25,linear_tracking_weight=5.,angular_tracking_weight=2.5,enable_gait_reward=a.stage=='stage_c',enable_foot_slip_penalty=True,enable_air_time_reward=True,enable_foot_clearance_reward=True,enable_action_smoothness=True,enable_stand_still_penalty=True)
 if a.settings:settings.update(json.loads(a.settings.read_text()))
 if settings.get('action_scale',.25)!=.25:raise ValueError('Common Stage2 initialization requires unchanged action scale .25')
 cfg=add_sensors(improve(configure(CSDogEnvCfg(),settings),settings));cfg.scene.num_envs=a.num_envs;cfg.seed=42;cfg.log_dir=str(out)
 agent=CSDogPPORunnerCfg();agent.algorithm.entropy_coef=.002;agent.algorithm.learning_rate=.0003
 dump_yaml(str(out/'env.yaml'),cfg);dump_yaml(str(out/'agent.yaml'),agent)
 (out/'settings.json').write_text(json.dumps(settings,indent=2));(out/'identity.json').write_text(json.dumps(dict(urdf_sha256=AUDIT['sha256'],joint_order=JOINTS,action_scale=.25,actor_obs=45,critic_obs=48),indent=2))
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg);wrapped=SpotWrapper(env,clip_actions=1.)
 runner=MeasuredRunner(wrapped,agent.to_dict(),device='cuda:0',log_dir=str(out),budget=budget,output=out)
 checkpoint=R/'runs/locomotion/csdog_ppo_20261026/stage2/final.pt'
 # Same weight/normalizer initialization for B and C. Reset optimizer and exploration equally.
 runner.load(str(checkpoint),load_optimizer=False);runner.current_learning_iteration=0
 with torch.no_grad():runner.alg.policy.std.fill_(.35)
 (out/'resume_source.json').write_text(json.dumps(dict(path=str(checkpoint),sha256=hashlib.sha256(checkpoint.read_bytes()).hexdigest(),optimizer_reset=True,exploration_std_reset=.35,seed=42),indent=2))
 try:runner.learn(num_learning_iterations=a.iterations,init_at_random_ep_len=True);status='COMPLETE'
 except BudgetStop:status='TIME_LIMIT'
 runner.save(str(out/'final.pt'));print('TRAIN_RESULT',status,budget.completed,flush=True)
except BaseException:
 import traceback
 traceback.print_exc()
 raise
finally:
 signal.setitimer(signal.ITIMER_REAL,0)
 if runner is not None and status=='FAILED':
  try:runner.save(str(out/'interrupted.pt'))
  except Exception:pass
 budget.close(status)
 if env is not None:env.close()
 if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
