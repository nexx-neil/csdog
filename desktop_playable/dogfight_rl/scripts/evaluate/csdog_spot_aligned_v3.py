"""Unified V3 comparison of native policies on a common 500Hz CSDog plant; no optimizer updates."""
from pathlib import Path
import argparse,sys,json,hashlib
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'))
p=argparse.ArgumentParser();p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output-dir',type=Path,required=True);p.add_argument('--video',action='store_true');p.add_argument('--video-seconds',type=float,default=4.);p.add_argument('--improved',action='store_true');p.add_argument('--kind',choices=['stage2','v2','v3'],default='v3');p.add_argument('--video-case',choices=['all','forward_stop'],default='all');p.add_argument('--seconds',type=float,default=6.);p.add_argument('--replicates',type=int,default=4);p.add_argument('--standing',action='store_true');p.add_argument('--debug-contact',action='store_true')
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.headless=True;a.enable_cameras=a.video
if a.output_dir.exists():p.error('output exists')
a.output_dir.mkdir(parents=True);app=AppLauncher(a).app
try:
 import torch,numpy as np,gymnasium as gym
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.robot_cfg import JOINTS,FEET,AUDIT
 from dogfight.locomotion.spot_v2.contacts import add_sensors,contact_state
 from dogfight.locomotion.ppo_cfg import CSDogPPORunnerCfg
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,AlignedPPOCfg,configure as configure_v3
 from isaaclab_rl.rsl_rl import RslRlVecEnvWrapper
 from rsl_rl.runners import OnPolicyRunner
 torch.set_num_threads(4)
 settings=json.loads((a.checkpoint.parent/'settings.json').read_text())
 if a.kind=='v3':
  cfg=configure_v3(AlignedEnvCfg(),{**settings,'no_reset_noise':True});agent=AlignedPPOCfg();task='Dogfight-CSDog-Spot-Aligned-Flat-v3';action_clip=None
 else:
  cfg=configure(CSDogEnvCfg(),{**settings,'no_reset_noise':True});agent=CSDogPPORunnerCfg();task='Dogfight-CSDog-Velocity-Flat-v0';action_clip=1.
  if a.kind=='v2':
   from dogfight.locomotion.spot_v2.config import improve
   cfg=improve(cfg,settings)
  # Common comparison plant: 500Hz, zero-delay explicit PD, same gains/limits/root/floor.
  common=AlignedEnvCfg();cfg.sim.dt=.002;cfg.decimation=10;cfg.sim.render_interval=10;cfg.scene.contact_forces.update_period=.002
  cfg.scene.robot.actuators=common.scene.robot.actuators;cfg.scene.robot.init_state.pos=(0.,0.,.36)
  add_sensors(cfg)
 cfg.scene.num_envs=1 if a.video else 8*a.replicates;cfg.seed=734;cfg.sim.device='cuda:0';cfg.episode_length_s=100.;cfg.viewer.resolution=(960,720)
 cfg.viewer.eye=(1.05,1.1,.65);cfg.viewer.lookat=(0.,0.,.16)
 env=gym.make(task,cfg=cfg,render_mode='rgb_array' if a.video else None);b=env.unwrapped;r=b.scene['robot'];j=r.find_joints(JOINTS,preserve_order=True)[0]
 w=RslRlVecEnvWrapper(env,clip_actions=action_clip);runner=OnPolicyRunner(w,agent.to_dict(),device='cuda:0',log_dir=None);runner.load(str(a.checkpoint));policy=runner.get_inference_policy(device='cuda:0')
 tests=[('stop',(0,0,0)),('forward',(.3,0,0)),('backward',(-.3,0,0)),('left',(0,.2,0)),('right',(0,-.2,0)),('left_turn',(0,0,.4)),('right_turn',(0,0,-.4)),('diagonal',(.2,.1,0))]
 all_rows=[]
 def rollout(commands,seconds,writer=None,label=''):
  b.reset(seed=734);alive=torch.ones(b.num_envs,device=b.device,dtype=torch.bool);rows=[]
  for step in range(round(seconds/b.step_dt)):
   cmd=commands[min(int(step*b.step_dt/2.),len(commands)-1)] if commands.ndim==3 else commands
   term=b.command_manager.get_term('base_velocity');term.vel_command_b[:]=cmd;term.is_standing_env[:]=False;term.time_left[:]=1000.
   obs=w.get_observations()
   with torch.inference_mode():act=torch.zeros(b.num_envs,12,device=b.device) if a.standing else policy(obs)
   obs,rew,done,extra=w.step(act);s=contact_state(b)
   first_fall=alive&done.bool();valid=alive&~done.bool();alive&=~done.bool()
   target=r.data.joint_pos_target[:,j]
   row=dict(t=(step+1)*b.step_dt,valid=valid,fall=first_fall,command=cmd.expand(b.num_envs,-1),velocity=r.data.root_lin_vel_b,yaw=r.data.root_ang_vel_b[:,2],position=r.data.root_pos_w,
    tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1),foot_height=s.clearance,tip_height=s.tip_position[:,:,2],contact=s.contact,force=s.force,raw_force=s.raw_force,contact_point=s.point,shin=s.shin,contact_count=s.count,
    foot_velocity=s.tip_velocity,patch_velocity=s.velocity,air_time=s.data.current_air_time,contact_time=s.data.current_contact_time,last_air_time=s.data.last_air_time,
    raw_action=act,clipped_action=b.action_manager.action,target=target,q=r.data.joint_pos[:,j],qd=r.data.joint_vel[:,j],torque=r.data.applied_torque[:,j],computed_torque=r.data.computed_torque[:,j],projected_joint_force=r.root_physx_view.get_dof_projected_joint_forces()[:,j])
   rows.append({k:v.detach().cpu().numpy().copy() if torch.is_tensor(v) else v for k,v in row.items()})
   if writer is not None and step%2==0:
    if a.debug_contact:
     from pxr import UsdGeom,Gf
     import omni.usd
     from scipy.spatial import ConvexHull
     from isaaclab.utils.math import quat_apply
     stage=omni.usd.get_context().get_stage()
     for k in range(4):
      verts=s.vertices[k];h=ConvexHull(verts.cpu().numpy());edges=sorted(set(tuple(sorted((int(face[x]),int(face[(x+1)%3])))) for face in h.simplices for x in range(3)))
      world=quat_apply(r.data.body_quat_w[0,b._csdog_feet_ids[k]].expand(len(verts),-1),verts)+r.data.body_pos_w[0,b._csdog_feet_ids[k]]
      q=world.cpu().numpy();curve=UsdGeom.BasisCurves.Define(stage,f'/World/DebugHull{k}');curve.CreateTypeAttr('linear');curve.CreateCurveVertexCountsAttr([2]*len(edges));curve.CreatePointsAttr([Gf.Vec3f(*[float(z) for z in q[x]]) for edge in edges for x in edge]);curve.CreateWidthsAttr([.0008]);curve.CreateDisplayColorAttr([Gf.Vec3f(1.,.6,.1)])
      cp=s.point[0,k].cpu().numpy();force=float(s.force[0,k]);normal=UsdGeom.BasisCurves.Define(stage,f'/World/DebugNormal{k}');normal.CreateTypeAttr('linear');normal.CreateCurveVertexCountsAttr([2]);normal.CreatePointsAttr([Gf.Vec3f(*[float(z) for z in cp]),Gf.Vec3f(float(cp[0]),float(cp[1]),float(cp[2])+min(force*.002,.15))]);normal.CreateWidthsAttr([.004]);normal.CreateDisplayColorAttr([Gf.Vec3f(.1,1.,.1)])
    from PIL import Image,ImageDraw
    im=Image.fromarray(env.render());d=ImageDraw.Draw(im);d.rectangle((0,0,960,70),fill=(15,15,15));d.text((10,8),label+'  target '+str(cmd[0].tolist()),fill='white');d.text((10,29),'actual '+str([round(x,3) for x in r.data.root_lin_vel_b[0,:2].tolist()])+f' yaw {float(r.data.root_ang_vel_b[0,2]):+.3f}',fill='white');d.text((10,49),'LF RF LR RR support: '+str(s.contact[0].int().tolist()),fill='white');writer.append_data(np.asarray(im))
  return rows
 if a.video:
  import imageio.v2 as imageio
  from pxr import UsdGeom,Gf
  import omni.usd
  stage=omni.usd.get_context().get_stage()
  for i in range(-12,13):
   for axis in [0,1]:
    cube=UsdGeom.Cube.Define(stage,f'/World/Ruler_{axis}_{i+12}');cube.CreateSizeAttr(1.)
    xf=UsdGeom.Xformable(cube);xf.AddTranslateOp().Set(Gf.Vec3d(i*.25 if axis==0 else 0.,i*.25 if axis==1 else 0.,.001));xf.AddScaleOp().Set(Gf.Vec3f(.002 if axis==0 else 6.,.002 if axis==1 else 6.,.001));cube.CreateDisplayColorAttr([Gf.Vec3f(.6,.6,.6)])
  with imageio.get_writer(str(a.output_dir/'all_directions.mp4'),fps=25,codec='libx264',quality=8) as writer:
   title=a.checkpoint.parent.name+'/'+a.checkpoint.stem
   if a.video_case=='forward_stop':
    rollout(torch.tensor([[[.3,0,0]],[[0,0,0]]],device=b.device,dtype=torch.float),4.,writer,title+' forward -> stop')
   else:
    for name,c in tests:rollout(torch.tensor([c],device=b.device,dtype=torch.float),a.video_seconds,writer,title+' '+name)
 else:
  commands=torch.tensor([c for _,c in tests for _ in range(a.replicates)],device=b.device,dtype=torch.float)
  if a.standing:commands.zero_()
  rows=rollout(commands,a.seconds)
  data={k:np.stack([x[k] for x in rows]) for k in rows[0]};np.savez_compressed(a.output_dir/'diagnostics.npz',**data)
  summary=[]
  for i,(name,c) in enumerate(tests):
   sl=slice(i*a.replicates,(i+1)*a.replicates);valid=data['valid'][:,sl]&(data['t'][:,None]>=1.);contact=data['contact'][:,sl];height=data['foot_height'][:,sl]
   def avg(x):return float(np.mean(x[valid])) if valid.any() else None
   delta=np.diff(data['clipped_action'][:,sl],axis=0,prepend=data['clipped_action'][:1,sl])
   slip=np.linalg.norm(data['patch_velocity'][:,sl,:,:2],axis=-1)
   ct=contact&valid[:,:,None]
   sync=((contact[:,:,0]==contact[:,:,3])&(contact[:,:,1]==contact[:,:,2])&(contact[:,:,0]!=contact[:,:,1]))
   summary.append(dict(test=name,target=c,velocity=np.mean(data['velocity'][:,sl][valid],axis=0).tolist() if valid.any() else None,yaw=avg(data['yaw'][:,sl]),linear_error=avg(np.linalg.norm(data['velocity'][:,sl,:2]-np.array(c[:2]),axis=-1)),yaw_error=avg(abs(data['yaw'][:,sl]-c[2])),
    slip=float(slip[ct].mean()) if ct.any() else None,air_fraction=avg(((~contact)&(height>.015)).mean(-1)),diagonal_support=avg(sync),clip=avg((abs(data['raw_action'][:,sl]-data['clipped_action'][:,sl])>1e-6).mean(-1)),raw_outside_unit_fraction=avg((abs(data['raw_action'][:,sl])>1).mean(-1)),action_delta=avg((delta**2).mean(-1)),
    torque_limit=avg((abs(data['torque'][:,sl])>=9.9).mean(-1)),speed_limit=avg((abs(data['qd'][:,sl])>=2.97).mean(-1)),target_limit=avg((abs(data['target'][:,sl])>=2.826).mean(-1)),tilt=avg(data['tilt'][:,sl]),falls=int(data['fall'][:,sl].any(axis=0).sum()),shin_fraction=avg(data['shin'][:,sl].mean(-1)),support_fraction=avg(contact.mean(-1)),
    raw_action_abs_max=float(abs(data['raw_action'][:,sl]).max()),height_max=height[valid].max(axis=0).tolist() if valid.any() else None))
  (a.output_dir/'summary.json').write_text(json.dumps(summary,indent=2))
  sequence=torch.tensor([[[x,y,z]]*b.num_envs for x,y,z in [( .3,0,0),(-.3,0,0),(0,.2,0),(0,0,-.4),(.2,.1,0),(0,0,0)]],device=b.device)
  seq=rollout(sequence,12.);sd={k:np.stack([x[k] for x in seq]) for k in seq[0]};np.savez_compressed(a.output_dir/'continuous_commands.npz',**sd)
  stop_mask=(sd['t'][:,None]>10.5)&sd['valid'];stop_speed=np.linalg.norm(sd['velocity'][:,:,:2],axis=-1)
  (a.output_dir/'continuous_stop.json').write_text(json.dumps(dict(linear_speed=float(stop_speed[stop_mask].mean()) if stop_mask.any() else None,yaw_speed=float(abs(sd['yaw'][stop_mask]).mean()) if stop_mask.any() else None,valid_samples=int(stop_mask.sum()),fallen_trials=int(sd['fall'].any(axis=0).sum())),indent=2))
  print('SUMMARY',json.dumps(summary),flush=True)
 # Dump actual imported collider metadata for auditing (no asset mutation).
 from pxr import UsdPhysics,UsdGeom,Usd
 import omni.usd
 stage=omni.usd.get_context().get_stage();colliders=[]
 for prim in Usd.PrimRange(stage.GetPseudoRoot(),Usd.TraverseInstanceProxies()):
  if prim.HasAPI(UsdPhysics.CollisionAPI) and ('env_0/' in str(prim.GetPath()) or 'ground_box' in str(prim.GetPath())):
   colliders.append(dict(path=str(prim.GetPath()),type=prim.GetTypeName(),approximation=UsdPhysics.MeshCollisionAPI(prim).GetApproximationAttr().Get() if prim.IsA(UsdGeom.Mesh) else None))
 (a.output_dir/'provenance.json').write_text(json.dumps(dict(checkpoint=str(a.checkpoint),sha256=hashlib.sha256(a.checkpoint.read_bytes()).hexdigest(),seed=734,joint_order=JOINTS,colliders=colliders,settings=settings,policy_std=runner.alg.policy.std.detach().cpu().tolist(),timing_resolution_s=b.step_dt,policy_kind=a.kind,physics_dt=b.physics_dt,actuator='explicit_pd_delay0',kp=25,kd=.8,effort_limit=10,velocity_limit=3,action_scale=cfg.actions.joint_pos.scale,wrapper_action_clip=action_clip,servo_bias_applied=False),indent=2))
 env.close()
except BaseException:
 import traceback
 traceback.print_exc()
 raise
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
