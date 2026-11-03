"""Floating-base, COM-feedback support transfer and leg-lift validation; zero PPO updates."""
from pathlib import Path
import sys,argparse,json,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_v4'
p=argparse.ArgumentParser();p.add_argument('--name',default='balance_feedback');p.add_argument('--body-height',type=float,default=.32);p.add_argument('--integral-gain',type=float,default=1.0);p.add_argument('--actual-polygon',action='store_true');p.add_argument('--video',action='store_true');a=p.parse_args();out=E/a.name
if out.exists():p.error('Refusing overwrite')
out.mkdir()
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True,enable_cameras=a.video).app
try:
 import torch,numpy as np,gymnasium as gym
 from dogfight.locomotion.spot_v4.config import V4EnvCfg
 from dogfight.locomotion.spot_v4.diagnostic_ik import LegKinematics,support_margin,LEGS
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 torch.set_num_threads(4);cfg=V4EnvCfg();cfg.scene.num_envs=4;cfg.seed=734;cfg.episode_length_s=100.
 cfg.events.reset_joints.params['position_range']=(0.,0.);cfg.events.reset_base.params['pose_range']={}
 if a.video:cfg.viewer.origin_type='world';cfg.viewer.resolution=(960,720)
 env=gym.make('Dogfight-CSDog-Spot-Flat-v4',cfg=cfg,render_mode='rgb_array' if a.video else None).unwrapped;r=env.scene['robot'];ids=r.find_joints(JOINTS,preserve_order=True)[0];env.reset(seed=734)
 assert not r.is_fixed_base
 mass=r.root_physx_view.get_masses().to(env.device);totalmass=mass.sum(-1)
 kin=LegKinematics(AUDIT);qik=np.broadcast_to(kin.default,(4,4,3)).copy();integral=np.zeros_like(qik);last_target=qik.reshape(4,12).copy();anchors=None;rows=[];alive=np.ones(4,dtype=bool);armed=np.zeros(4,dtype=bool);armed_at=np.full(4,np.nan);steady=np.zeros(4,dtype=int);force_ema=np.zeros((4,4))
 writer=None
 if a.video:
  import imageio.v2 as imageio
  from PIL import Image,ImageDraw
  writer=imageio.get_writer(str(out/'diagnostic_balance.mp4'),fps=25,codec='libx264',quality=8)
 for k in range(1000 if a.actual_polygon else 800):
  t=k*.02;s=contact_state(env)
  root=r.data.root_pos_w.cpu().numpy().copy();com=(r.data.body_com_pos_w*mass[:,:,None]).sum(1)/totalmass[:,None];com=com.cpu().numpy()
  qactual=r.data.joint_pos[:,ids].cpu().numpy().reshape(4,4,3).copy()
  points=s.tip_position.cpu().numpy().copy();tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).cpu().numpy()
  if k==100:
   anchors=points.copy();initial_com=com.copy();initial_root=root.copy();last_target=qactual.reshape(4,12).copy();qik=qactual.copy()
  margins=np.zeros(4);lift=np.zeros(4);desired_com=com.copy();targets=qik.copy()
  if anchors is not None:
   triangle=np.stack([(points if a.actual_polygon else anchors)[n,[j for j in range(4) if j!=n],:2] for n in range(4)])
   margins=support_margin(com[:,:2],triangle)
   progress=np.clip((t-2.)/3.,0,1)
   desired_com[:,:2]=(1.-progress)*initial_com[:,:2]+progress*triangle.mean(1)
   root_goal=initial_root.copy();root_goal[:,:2]=desired_com[:,:2]-(com-root)[:,:2]+np.clip(.5*(desired_com[:,:2]-com[:,:2]),-.025,.025)
   root_goal[:,2]=(1.-progress)*initial_root[:,2]+progress*a.body_height
   root_goal[:,2]+=np.clip(.5*(root_goal[:,2]-root[:,2]),-.02,.02)
   contact=s.contact.cpu().numpy();stable=np.array([contact[n,[j for j in range(4) if j!=n]].all() for n in range(4)])
   if a.actual_polygon:
    force_ema=.8*force_ema+.2*s.force.cpu().numpy()
    geometry=s.clearance.cpu().numpy()
    stable=np.array([((force_ema[n,[j for j in range(4) if j!=n]]>3.)&(geometry[n,[j for j in range(4) if j!=n]]<.008)).all() for n in range(4)])
   acceptable=(margins>.008)&(tilt<(.25 if a.actual_polygon else .18))&stable&alive
   steady=np.where(acceptable,steady+1,0)
   newly=(steady>=15)&~armed&(t>=5.)
   armed_at[newly]=t;armed|=newly
   elapsed=np.where(armed,t-armed_at,0.)
   lift=np.where(armed,.04*np.clip(elapsed/1.,0,1),0.)
   # Once aloft, add only a small bounded test oscillation; not a walking CPG.
   lift+=np.where(armed&(elapsed>2.),.005*np.sin(2*np.pi*(elapsed-2.)/1.5),0.)
   foot_goal=anchors.copy()
   for n in range(4):foot_goal[n,n,2]+=lift[n]
   qik=kin.inverse(foot_goal-root_goal[:,None,:],qik)
   error=qik-qactual;tau=r.data.applied_torque[:,ids].cpu().numpy().reshape(4,4,3)
   can_integrate=(abs(tau)<9.5)|(tau*error<0)
   integral=np.clip(integral+a.integral_gain*.02*error*can_integrate,-.25,.25)
   targets=(qik+integral).reshape(4,12)
   targets=last_target+np.clip(targets-last_target,-.04,.04);last_target=targets.copy()
  else:targets=np.broadcast_to(kin.default,(4,4,3)).reshape(4,12)
  term=env.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.is_standing_env[:]=True;term.time_left[:]=1000.
  action=(targets-np.broadcast_to(kin.default,(4,4,3)).reshape(4,12))/.2
  obs,rew,done,trunc,extra=env.step(torch.tensor(action,dtype=torch.float,device=env.device));s=contact_state(env);alive&=~done.cpu().numpy()
  if a.actual_polygon:
   com_after=((r.data.body_com_pos_w*mass[:,:,None]).sum(1)/totalmass[:,None]).cpu().numpy()
   support_now=np.stack([s.point.cpu().numpy()[n,[j for j in range(4) if j!=n],:2] for n in range(4)])
   margins=support_margin(com_after[:,:2],support_now);com=com_after
  row=dict(t=t+.02,com=com,foot_position=s.tip_position,contact_point=s.point,desired_com=desired_com,margin=margins,armed=armed.copy(),lift_target=lift,q=r.data.joint_pos[:,ids],target=r.data.joint_pos_target[:,ids],qd=r.data.joint_vel[:,ids],torque=r.data.applied_torque[:,ids],height=s.clearance,contact=s.contact,force=s.force,raw_force=s.raw_force,shin=s.shin,tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1),root=r.data.root_pos_w,valid=alive.copy(),fall=done,integral=integral.copy())
  rows.append({key:value.detach().cpu().numpy().copy() if torch.is_tensor(value) else value for key,value in row.items()})
  if writer is not None and t>=8. and k%2==0:
   which=min(int((t-8.)/3.),3);center=r.data.root_pos_w[which].cpu().numpy()
   env.sim.set_camera_view(eye=center+np.array([.9,.9,.55]),target=center+np.array([0,0,-.10]))
   image=Image.fromarray(env.render());draw=ImageDraw.Draw(image);draw.rectangle((0,0,960,75),fill=(12,12,12))
   draw.text((10,8),'DIAGNOSTIC ONLY - COM feedback + IK, NOT PPO | '+LEGS[which].upper(),fill='white')
   draw.text((10,30),f'actual clearance {float(s.clearance[which,which]):+.3f}m | COM margin {margins[which]:+.3f}m',fill='white')
   draw.text((10,51),'10Nm / 3rad/s unchanged | support '+str(s.contact[which].int().tolist()),fill='white')
   writer.append_data(np.asarray(image))
  assert torch.isfinite(obs['policy']).all() and torch.isfinite(rew).all()
 if writer is not None:writer.close()
 data={key:np.stack([row[key] for row in rows]) for key in rows[0]};np.savez_compressed(out/'diagnostics.npz',**data)
 summary=[]
 for n,leg in enumerate(LEGS):
  support=data['contact'][:,n].sum(-1)>=3;valid=data['valid'][:,n]&(data['t']>5.)&(data['tilt'][:,n]<.25)&support
  lifted=valid&data['armed'][:,n]&(data['lift_target'][:,n]>.025)&(data['height'][:,n,n]>.015)&(~data['contact'][:,n,n])&(data['margin'][:,n]>.005)
  longest=0;current=0
  for flag in lifted:
   current=current+1 if flag else 0;longest=max(longest,current)
  summary.append(dict(leg=leg,longest_commanded_lift_seconds=longest*.02,armed=bool(armed[n]),armed_at_s=float(armed_at[n]) if armed[n] else None,max_stable_clearance=float(data['height'][valid,n,n].max()) if valid.any() else None,stable_lift_seconds=float(lifted.sum()*.02),max_support_margin=float(data['margin'][:,n].max()),falls=int(data['fall'][:,n].any()),torque_saturation=float((abs(data['torque'][:,n])>=9.9).mean()),speed_saturation=float((abs(data['qd'][:,n])>=2.97).mean()),tracking_rmse=float(np.sqrt(np.mean((data['q'][:,n]-data['target'][:,n])**2)))))
 result=dict(status='PASS' if all(x['stable_lift_seconds']>=1. and x['longest_commanded_lift_seconds']>=.5 and not x['falls'] for x in summary) else 'INCOMPLETE',legs=summary,actual_polygon=a.actual_polygon,controller='diagnostic COM/body feedback + world foot-anchor IK + bounded integral, never in PPO',body_height_target=a.body_height,integral_gain=a.integral_gain,root_writes=False,fixed_base=False,kp=25,kd=.8,effort_limit=10,velocity_limit=3,all_states_finite=all(np.isfinite(data[k]).all() for k in ['q','target','torque','height','com']))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print('BALANCE_DIAGNOSTIC',json.dumps(result),flush=True);env.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
