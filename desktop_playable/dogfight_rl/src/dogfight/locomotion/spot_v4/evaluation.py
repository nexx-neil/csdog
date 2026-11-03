"""Reusable V4 rollout and per-leg metrics using the unchanged V2/V3 contact implementation."""
import numpy as np
import torch
from ..spot_v2.contacts import contact_state
LEGS=('LF','RF','LR','RR')
TESTS=[('stop',(0.,0.,0.)),('forward',(.3,0.,0.)),('backward',(-.3,0.,0.)),('left',(0.,.2,0.)),('right',(0.,-.2,0.)),('left_turn',(0.,0.,.4)),('right_turn',(0.,0.,-.4)),('diagonal',(.2,.1,0.))]
def rollout(wrapped,policy,commands,seconds,seed,writer=None,title=''):
 b=wrapped.unwrapped;b.reset(seed=seed);r=b.scene['robot'];j=r.find_joints([f'joint_{leg}_{n}' for leg in ['lf','rf','lr','rr'] for n in [1,2,3]],preserve_order=True)[0]
 alive=torch.ones(b.num_envs,dtype=torch.bool,device=b.device);rows=[]
 for step in range(round(seconds/b.step_dt)):
  cmd=commands[min(int(step*b.step_dt/2.),len(commands)-1)] if commands.ndim==3 else commands
  term=b.command_manager.get_term('base_velocity');term.vel_command_b[:]=cmd;term.is_standing_env[:]=False;term.time_left[:]=1000.
  with torch.inference_mode():action=policy(wrapped.get_observations())
  obs,reward,done,info=wrapped.step(action);s=contact_state(b);fall=alive&done.bool();valid=alive&~done.bool();alive&=~done.bool()
  row=dict(t=(step+1)*b.step_dt,command=cmd.expand(b.num_envs,-1),velocity=r.data.root_lin_vel_b,yaw=r.data.root_ang_vel_b[:,2],position=r.data.root_pos_w,tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1),valid=valid,fall=fall,
   foot_height=s.clearance,contact=s.contact,force=s.force,raw_force=s.raw_force,shin=s.shin,patch_velocity=s.velocity,foot_velocity=s.tip_velocity,air_time=s.data.current_air_time,contact_time=s.data.current_contact_time,
   raw_action=action,executed_action=b.action_manager.action,q=r.data.joint_pos[:,j],target=r.data.joint_pos_target[:,j],qd=r.data.joint_vel[:,j],torque=r.data.applied_torque[:,j],projected_joint_force=r.root_physx_view.get_dof_projected_joint_forces()[:,j])
  rows.append({k:v.detach().cpu().numpy().copy() if torch.is_tensor(v) else v for k,v in row.items()})
  if writer is not None and step%2==0:
   from PIL import Image,ImageDraw
   image=Image.fromarray(b.render());draw=ImageDraw.Draw(image);draw.rectangle((0,0,image.width,70),fill=(12,12,12))
   draw.text((10,8),title+' | target '+str([round(x,2) for x in cmd[0].tolist()]),fill='white')
   draw.text((10,29),'actual '+str([round(x,3) for x in r.data.root_lin_vel_b[0,:2].tolist()])+f' yaw={float(r.data.root_ang_vel_b[0,2]):+.3f}',fill='white')
   draw.text((10,49),'LF RF LR RR support '+str(s.contact[0].int().tolist()),fill='white');writer.append_data(np.asarray(image))
 return {k:np.stack([r[k] for r in rows]) for k in rows[0]}

def durations(signal,dt=.02):
 changes=np.r_[0,np.flatnonzero(np.diff(signal.astype(int)))+1,len(signal)]
 return [float((changes[k+1]-changes[k])*dt) for k in range(len(changes)-1) if signal[changes[k]]]

def summarize(data,indices,name):
 valid=data['valid'][:,indices]&(data['t'][:,None]>=1.);c=data['contact'][:,indices];height=data['foot_height'][:,indices]
 def mean(x):return float(np.mean(x[valid])) if valid.any() else None
 cmd=data['command'][:,indices];velocity=data['velocity'][:,indices];yaw=data['yaw'][:,indices]
 row=dict(test=name,target=cmd[0,0].tolist(),valid_samples=int(valid.sum()),velocity=velocity[valid].mean(0).tolist() if valid.any() else None,yaw=mean(yaw),linear_error=mean(np.linalg.norm(velocity[:,:,:2]-cmd[:,:,:2],axis=-1)),yaw_error=mean(abs(yaw-cmd[:,:,2])),falls=int(data['fall'][:,indices].any(0).sum()),tilt=mean(data['tilt'][:,indices]),action_clip_fraction=mean((abs(data['raw_action'][:,indices]-data['executed_action'][:,indices])>1e-6).mean(-1)),raw_outside_unit_fraction=mean((abs(data['raw_action'][:,indices])>1).mean(-1)),torque_limit_fraction=mean((abs(data['torque'][:,indices])>=9.9).mean(-1)),speed_limit_fraction=mean((abs(data['qd'][:,indices])>=2.97).mean(-1)),target_limit_fraction=mean((abs(data['target'][:,indices])>=2.826).mean(-1)))
 v=np.linalg.norm(data['patch_velocity'][:,indices,:,:2],axis=-1);support=c&valid[:,:,None];row['support_slip_speed']=float(v[support].mean()) if support.any() else None
 row['diagonal_contact_proxy']=mean((c[:,:,0]==c[:,:,3])&(c[:,:,1]==c[:,:,2])&(c[:,:,0]!=c[:,:,1]))
 foot={}
 for i,leg in enumerate(LEGS):
  swing=(~c[:,:,i])&(height[:,:,i]>.015);stance_times=[];swing_times=[];switches=0
  for n in range(valid.shape[1]):
   contact=c[:,n,i][valid[:,n]];clear_swing=swing[:,n][valid[:,n]]
   if len(contact):
    stance_times+=durations(contact);swing_times+=durations(clear_swing);switches+=int((np.diff(contact.astype(int))!=0).sum())
  mask=support[:,:,i]
  foot[leg]=dict(swing_ratio=mean(swing.astype(float)),max_height=float(height[:,:,i][valid].max()) if valid.any() else None,mean_height=mean(height[:,:,i]),stance_seconds_per_trial=float((c[:,:,i]&valid).sum()*.02/valid.shape[1]),true_swing_seconds_per_trial=float((swing&valid).sum()*.02/valid.shape[1]),stance_durations_s=stance_times,true_swing_durations_s=swing_times,contact_switches=switches,support_slip_speed=float(v[:,:,i][mask].mean()) if mask.any() else None,contact_force_mean=mean(data['force'][:,indices,i]))
  row[leg+'_swing_ratio']=foot[leg]['swing_ratio']
 row['feet']=foot
 return row
