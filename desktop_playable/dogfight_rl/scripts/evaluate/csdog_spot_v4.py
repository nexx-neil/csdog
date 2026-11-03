"""Load a compatible V3/V4 checkpoint; evaluate 8 commands and continuous stopping with real physics."""
from pathlib import Path
import argparse,sys,json,os,uuid,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
def worker(path):
 launch=json.loads(Path(path).read_text());a=argparse.Namespace(**launch['args']);out=Path(path).parent
 if os.environ.get('CSDOG_V4_WORKER_TOKEN')!=launch['token']:raise RuntimeError('Use public evaluation CLI')
 app=None;env=None;result={}
 try:
  import torch,numpy as np,gymnasium as gym
  torch.set_num_threads(4)
  from isaaclab.app import AppLauncher
  app=AppLauncher(headless=a.headless,device=a.device,enable_cameras=a.video and not a.dry_run).app
  from dogfight.locomotion.spot_v4.config import V4EnvCfg,V4PPOCfg
  from dogfight.locomotion.spot_v4.contracts import TASK
  from dogfight.locomotion.spot_v4.runtime import preflight,load_learner
  from dogfight.locomotion.spot_v4.evaluation import rollout,summarize,TESTS
  from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
  from rsl_rl.runners import OnPolicyRunner
  cfg=V4EnvCfg();cfg.scene.num_envs=1 if a.video else 8*a.replicates;cfg.seed=a.seed;cfg.sim.device=a.device;cfg.episode_length_s=100.
  cfg.events.reset_joints.params['position_range']=(0.,0.);cfg.events.reset_base.params['pose_range']={}
  cfg.viewer.eye=(1.05,1.1,.65);cfg.viewer.lookat=(0.,0.,.16);cfg.viewer.resolution=(960,720)
  env=gym.make(TASK,cfg=cfg,render_mode='rgb_array' if a.video and not a.dry_run else None);b=env.unwrapped
  checks=preflight(env);w=RslRlVecEnvWrapper(env,clip_actions=None)
  runner=OnPolicyRunner(w,V4PPOCfg().to_dict(),device=a.device,log_dir=None)
  source=load_learner(runner,Path(a.checkpoint),weights_only=True,restore_rng=False);policy=runner.get_inference_policy(device=a.device)
  (out/'provenance.json').write_text(json.dumps(dict(checkpoint=source,preflight=checks,seed=a.seed,settle_seconds=1.,video=a.video,seconds=a.seconds,replicates=1 if a.video else a.replicates,no_root_motion_injection=True),indent=2))
  if a.dry_run:result=dict(status='DRY_RUN_PASS',ppo_updates=0,source_updates=source['source_checkpoint_updates'])
  else:
   summaries=[]
   if a.video:
    import imageio.v2 as imageio
    from pxr import UsdGeom,Gf
    import omni.usd
    stage=omni.usd.get_context().get_stage()
    for i in range(-12,13):
     for axis in [0,1]:
      cube=UsdGeom.Cube.Define(stage,f'/World/Reference_{axis}_{i+12}');cube.CreateSizeAttr(1.)
      xf=UsdGeom.Xformable(cube);xf.AddTranslateOp().Set(Gf.Vec3d(i*.25 if axis==0 else 0.,i*.25 if axis==1 else 0.,.001));xf.AddScaleOp().Set(Gf.Vec3f(.002 if axis==0 else 6.,.002 if axis==1 else 6.,.001));cube.CreateDisplayColorAttr([Gf.Vec3f(.6,.6,.6)])
    with imageio.get_writer(str(out/'all_directions.mp4'),fps=25,codec='libx264',quality=8) as writer:
     for name,command in TESTS:
      d=rollout(w,policy,torch.tensor([command],device=b.device),a.seconds,a.seed,writer,'V4 '+Path(a.checkpoint).parent.name+' '+name)
      np.savez_compressed(out/(name+'_trajectory.npz'),**d);summaries.append(summarize(d,[0],name))
   else:
    commands=torch.tensor([c for _,c in TESTS for _ in range(a.replicates)],device=b.device)
    d=rollout(w,policy,commands,a.seconds,a.seed);np.savez_compressed(out/'diagnostics.npz',**d)
    for i,(name,_) in enumerate(TESTS):summaries.append(summarize(d,list(range(i*a.replicates,(i+1)*a.replicates)),name))
   sequence=torch.tensor([[[x,y,z]]*b.num_envs for x,y,z in [(.3,0,0),(-.3,0,0),(0,.2,0),(0,0,-.4),(.2,.1,0),(0,0,0)]],device=b.device)
   continuous=rollout(w,policy,sequence,12.,a.seed);np.savez_compressed(out/'continuous_commands.npz',**continuous)
   mask=(continuous['t'][:,None]>10.5)&continuous['valid'];speed=np.linalg.norm(continuous['velocity'][:,:,:2],axis=-1)
   stopping=dict(linear_speed=float(speed[mask].mean()) if mask.any() else None,yaw_speed=float(abs(continuous['yaw'][mask]).mean()) if mask.any() else None,valid_samples=int(mask.sum()),fallen_trials=int(continuous['fall'].any(0).sum()))
   (out/'continuous_stop.json').write_text(json.dumps(stopping,indent=2,allow_nan=False));(out/'summary.json').write_text(json.dumps(summaries,indent=2,allow_nan=False))
   result=dict(status='EVALUATION_PASS',ppo_updates=0,checkpoint_updates=source['source_checkpoint_updates'],summary=str(out/'summary.json'),video=str(out/'all_directions.mp4') if a.video else None)
 except BaseException as exc:traceback.print_exc();sys.stderr.flush();result=dict(status='FAILED',error=str(exc),ppo_updates=0)
 finally:
  (out/'result.json').write_text(json.dumps(result,indent=2));print('RESULT',json.dumps(result),flush=True)
  if env is not None:
   try:env.close()
   except Exception:pass
  if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
def main():
 from dogfight.locomotion.spot_v4.contracts import validate_identity,RUNS
 from dogfight.locomotion.spot_v4.cli import supervise
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path);p.add_argument('--video',action='store_true');p.add_argument('--headless',action='store_true');p.add_argument('--device',default='cuda:0');p.add_argument('--seconds',type=float,default=6.);p.add_argument('--replicates',type=int,default=4);p.add_argument('--seed',type=int,default=734);p.add_argument('--dry-run',action='store_true')
 a=p.parse_args()
 try:
  a.checkpoint=validate_identity(a.checkpoint)
  if a.seconds<=1 or a.replicates<1:raise ValueError('--seconds must exceed 1 and --replicates must be positive')
  if a.output_dir is None:
   from datetime import datetime
   a.output_dir=RUNS/('spot_v4_eval_'+datetime.now().strftime('%Y%m%d_%H%M%S'))
  out=a.output_dir.resolve()
  if not out.is_relative_to(RUNS.resolve()) or out.exists():raise ValueError('Use a new evaluation output inside runs/locomotion; existing outputs cannot be overwritten')
 except Exception as exc:p.error(str(exc))
 out.mkdir(parents=True);launch=out/'launch_parameters.json';launch.write_text(json.dumps(dict(args={k:str(v) if isinstance(v,Path) else v for k,v in vars(a).items()},token=uuid.uuid4().hex),indent=2))
 return supervise(Path(__file__),launch,out,'evaluation.log')
if __name__=='__main__':
 if len(sys.argv)==3 and sys.argv[1]=='--_worker':worker(sys.argv[2])
 else:raise SystemExit(main())
