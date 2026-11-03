"""Fixed-command physical policy evaluation and optional close-camera video, no training."""
from pathlib import Path
import argparse,sys,json,hashlib
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--video',action='store_true');p.add_argument('--seconds',type=float,default=6.);p.add_argument('--replicates',type=int,default=4)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args();args.headless=True;args.enable_cameras=args.video
if not args.output_dir.resolve().is_relative_to(ROOT):p.error('Evaluation output must stay inside dogfight_rl')
if args.seconds<=1. or args.replicates<1:p.error('Use seconds>1 and at least one replicate')
if args.output_dir.exists():p.error('Refusing to overwrite evaluation output')
args.output_dir.mkdir(parents=True);app=AppLauncher(args).app
try:
 import torch,numpy as np,gymnasium as gym
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 from dogfight.locomotion.ppo_cfg import CSDogPPORunnerCfg
 from dogfight.locomotion.mdp import feet_kinematics
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 from rsl_rl.runners import OnPolicyRunner
 tests=[('stop',(0.,0.,0.)),('forward',(0.3,0.,0.)),('backward',(-0.3,0.,0.)),('left',(0.,0.2,0.)),('right',(0.,-0.2,0.)),('left_turn',(0.,0.,0.4)),('right_turn',(0.,0.,-0.4)),('diagonal',(0.2,0.1,0.))]
 settings=json.loads((args.checkpoint.parent/'settings.json').read_text());identity=json.loads((args.checkpoint.parent/'identity.json').read_text())
 assert identity['urdf_sha256']==AUDIT['sha256'] and identity['joint_order']==JOINTS
 cfg=configure(CSDogEnvCfg(),{**settings,'no_reset_noise':True});cfg.scene.num_envs=1 if args.video else len(tests)*args.replicates;cfg.episode_length_s=100.;cfg.sim.device=args.device or 'cuda:0';cfg.seed=734
 cfg.viewer.resolution=(800,600)
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg,render_mode='rgb_array' if args.video else None);base=env.unwrapped
 wrapped=RslRlVecEnvWrapper(env,clip_actions=1.);agent=CSDogPPORunnerCfg();runner=OnPolicyRunner(wrapped,agent.to_dict(),device=cfg.sim.device,log_dir=None);runner.load(str(args.checkpoint));policy=runner.get_inference_policy(device=cfg.sim.device)
 def set_command(values):
  term=base.command_manager.get_term('base_velocity');term.vel_command_b[:]=values;term.is_standing_env[:]=False;term.time_left[:]=1000.
 def rollout(commands,duration,sequence=False,writer=None,title=''):
  obs=wrapped.get_observations();robot=base.scene['robot'];rows=[];alive=torch.ones(base.num_envs,dtype=torch.bool,device=base.device)
  previous=robot.data.root_pos_w[:,:2].clone();start=previous.clone();distance=torch.zeros(base.num_envs,device=base.device)
  for step in range(round(duration/base.step_dt)):
   if sequence:
    command=commands[min(int(step*base.step_dt/2.),len(commands)-1)]
    cmd=torch.tensor(command,device=base.device).expand(base.num_envs,-1)
   else:cmd=commands
   set_command(cmd);obs=wrapped.get_observations() # command must be reflected immediately in actor input
   with torch.inference_mode():action=policy(obs)
   obs,reward,done,extra=wrapped.step(action)
   pos=robot.data.root_pos_w[:,:2].clone();valid=alive&~done.bool();distance+=(pos-previous).norm(dim=-1)*valid;previous=pos.clone()
   fp,fv=feet_kinematics(base);sensor=base.scene['contact_forces'];fi=sensor.find_bodies(['link_lf_knee','link_rf_knee','link_lr_knee','link_rr_knee'],preserve_order=True)[0]
   contact=sensor.data.net_forces_w[:,fi].norm(dim=-1)>2.
   sample=dict(step=step,time=step*base.step_dt,command=cmd.cpu().tolist(),velocity=robot.data.root_lin_vel_b[:,:2].cpu().tolist(),yaw_rate=robot.data.root_ang_vel_b[:,2].cpu().tolist(),
    position=pos.cpu().tolist(),tilt=robot.data.projected_gravity_b[:,:2].norm(dim=-1).cpu().tolist(),valid=valid.cpu().tolist(),fall=(alive&done.bool()).cpu().tolist(),
    foot_slip=((fv[:,:,:2].norm(dim=-1)*contact).sum(-1)/contact.sum(-1).clamp_min(1)).cpu().tolist(),
    low_swing=((~contact)&(fp[:,:,2]<0.015)&(fv[:,:,:2].norm(dim=-1)>0.1)).float().mean(-1).cpu().tolist(),action_delta=0. if step==0 else (action-last_action).square().mean(-1).cpu().tolist())
   processed=base.action_manager.action.clone()
   sample.update(processed_action_delta=0. if step==0 else (processed-last_processed).square().mean(-1).cpu().tolist(),
    action_clip_fraction=(action.abs()>1.).float().mean(-1).cpu().tolist(),joint_velocity_max=robot.data.joint_vel.abs().max(-1).values.cpu().tolist(),
    torque_rms=robot.data.applied_torque.square().mean(-1).sqrt().cpu().tolist(),joint_position=robot.data.joint_pos.cpu().tolist())
   rows.append(sample);alive&=~done.bool();last_action=action.clone();last_processed=processed
   if writer is not None and step%2==0:
    from PIL import Image,ImageDraw
    image=Image.fromarray(env.render());draw=ImageDraw.Draw(image);actual=robot.data.root_lin_vel_b[0,:2].tolist();yaw=float(robot.data.root_ang_vel_b[0,2]);target=cmd[0].tolist()
    draw.rectangle((0,0,800,65),fill=(20,20,20));draw.text((12,10),f'{title} | target vx={target[0]:+.2f} vy={target[1]:+.2f} wz={target[2]:+.2f}',fill='white');draw.text((12,32),f'actual vx={actual[0]:+.2f} vy={actual[1]:+.2f} wz={yaw:+.2f} | t={step*base.step_dt:.2f}s',fill='white')
    writer.append_data(np.asarray(image))
  return rows,distance.cpu().tolist()
 if args.video:
  import imageio.v2 as imageio
  from pxr import UsdGeom,Gf
  import omni.usd
  # Visual-only ground ruler; no collisions or forces are added.
  stage=omni.usd.get_context().get_stage()
  for i in range(-8,9):
   for axis in [0,1]:
    cube=UsdGeom.Cube.Define(stage,f'/World/Ruler_{axis}_{i+8}');cube.CreateSizeAttr(1.)
    xf=UsdGeom.Xformable(cube);xf.AddTranslateOp().Set(Gf.Vec3d(i*0.25 if axis==0 else 0.,i*0.25 if axis==1 else 0.,0.001));xf.AddScaleOp().Set(Gf.Vec3f(0.002 if axis==0 else 4.,0.002 if axis==1 else 4.,0.001));cube.CreateDisplayColorAttr([Gf.Vec3f(0.6,0.6,0.6)])
  with imageio.get_writer(str(args.output_dir/'all_directions.mp4'),fps=25,codec='libx264',quality=7) as writer:
   for name,command in tests:
    base.reset(seed=734);rows,_=rollout(torch.tensor(command,device=base.device).reshape(1,3),3.,writer=writer,title=name)
  (args.output_dir/'video_provenance.json').write_text(json.dumps({'checkpoint':str(args.checkpoint.resolve()),'sha256':hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),'tests':tests},indent=2))
  print('VIDEO_SAVED',args.output_dir/'all_directions.mp4',flush=True)
 else:
  base.reset(seed=734);cmd=torch.tensor([c for _,c in tests for _ in range(args.replicates)],device=base.device)
  rows,distances=rollout(cmd,args.seconds)
  (args.output_dir/'trajectory.json').write_text(json.dumps(rows))
  summary=[]
  for index,(name,target) in enumerate(tests):
   velocities=[];yaw=[];tilt=[];errors=[];yerrors=[];slip=[];drag=[];jitter=[];processed_jitter=[];clip=[];joint_speed=[];torque=[];falls=0
   for row in rows:
    for n in range(index*args.replicates,(index+1)*args.replicates):
     falls+=int(row['fall'][n])
     if row['valid'][n] and row['time']>=1.:
      v=np.array(row['velocity'][n]);velocities.append(v);yaw.append(row['yaw_rate'][n]);tilt.append(row['tilt'][n]);errors.append(float(np.linalg.norm(v-np.array(target[:2]))));yerrors.append(abs(row['yaw_rate'][n]-target[2]));slip.append(row['foot_slip'][n]);drag.append(row['low_swing'][n]);jitter.append(row['action_delta'][n]);processed_jitter.append(row['processed_action_delta'][n]);clip.append(row['action_clip_fraction'][n]);joint_speed.append(row['joint_velocity_max'][n]);torque.append(row['torque_rms'][n])
   summary.append(dict(test=name,target=target,actual_mean_velocity=np.mean(velocities,axis=0).tolist() if velocities else None,actual_mean_yaw_rate=float(np.mean(yaw)) if yaw else None,
    linear_error=float(np.mean(errors)) if errors else None,yaw_error=float(np.mean(yerrors)) if yerrors else None,mean_travel_distance=float(np.mean(distances[index*args.replicates:(index+1)*args.replicates])),
    falls=falls,trials=args.replicates,fall_rate=falls/args.replicates,tilt_rms=float(np.sqrt(np.mean(np.array(tilt)**2))) if tilt else None,
    contact_slip_speed=float(np.mean(slip)) if slip else None,low_swing_proxy=float(np.mean(drag)) if drag else None,action_delta_mean_square=float(np.mean(jitter)) if jitter else None,valid_samples=len(velocities),processed_action_delta_mean_square=float(np.mean(processed_jitter)) if processed_jitter else None,action_clip_fraction=float(np.mean(clip)) if clip else None,mean_max_joint_speed=float(np.mean(joint_speed)) if joint_speed else None,mean_joint_torque_rms=float(np.mean(torque)) if torque else None))
  sequence=[(0.3,0.,0.),(-0.3,0.,0.),(0.,0.2,0.),(0.,0.,0.4),(0.2,0.1,0.2),(0.,0.,0.)]
  base.reset(seed=734);seq,dis=rollout(sequence,12.,sequence=True);(args.output_dir/'continuous_commands.json').write_text(json.dumps(seq))
  result=dict(checkpoint=str(args.checkpoint.resolve()),checkpoint_sha256=hashlib.sha256(args.checkpoint.read_bytes()).hexdigest(),seconds=args.seconds,settle_seconds=1.,seed=734,replicates=args.replicates,tests=summary,
   continuous_stop_linear_speed=float(np.mean([np.linalg.norm(v) for row in seq if row['time']>=10.5 for v,ok in zip(row['velocity'],row['valid']) if ok])) if any(any(r['valid']) for r in seq if r['time']>=10.5) else None,
   metric_notes='Knee-body force aggregates shin+foot contacts; drag is a low-swing proxy, not manual visual classification. Displacement integrates only pre-fall physical states; first 1s omitted from velocity metrics.')
  (args.output_dir/'summary.json').write_text(json.dumps(result,indent=2));print('EVALUATION',json.dumps(result),flush=True)
 env.close()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
