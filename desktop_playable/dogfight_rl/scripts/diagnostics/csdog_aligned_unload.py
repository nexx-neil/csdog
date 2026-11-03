"""Four independent leg tests: shift support through joint IK, then lift/swing.
No root writes; no PPO; reference is diagnostic only, not a training gait."""
from pathlib import Path
import argparse,sys,json,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3'
p=argparse.ArgumentParser();p.add_argument('--implicit',action='store_true');p.add_argument('--calibrated',action='store_true');p.add_argument('--retract',action='store_true');a=p.parse_args();out=E/(('unload_implicit' if a.implicit else 'unload_explicit')+('_calibrated' if a.calibrated else '')+('_retract' if a.retract else ''))
if out.exists():p.error('output exists')
out.mkdir()
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,numpy as np,gymnasium as gym
 from scipy.optimize import least_squares
 from scipy.spatial.transform import Rotation
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,configure
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 torch.set_num_threads(4)
 cfg=configure(AlignedEnvCfg(),{'implicit_actuator':a.implicit,'no_reset_noise':True});cfg.scene.num_envs=4;cfg.seed=734;cfg.episode_length_s=100.
 if a.calibrated:
  from dogfight.locomotion.spot_aligned_v3.calibration import SERVO_BIAS_RAD
  cfg.actions.joint_pos.use_default_offset=False
  cfg.actions.joint_pos.offset={name:AUDIT['standing_pose'][name]+bias for name,bias in zip(JOINTS,SERVO_BIAS_RAD)}
 e=gym.make('Dogfight-CSDog-Spot-Aligned-Flat-v3',cfg=cfg).unwrapped;r=e.scene['robot'];j=r.find_joints(JOINTS,preserve_order=True)[0];e.reset(seed=734)
 legs=['lf','rf','lr','rr'];q0=np.array([AUDIT['standing_pose'][x] for x in JOINTS]);delta=np.zeros((4,12));lift=np.zeros((4,12))
 for env_id,active in enumerate(legs):
  shift=np.array([.035 if active[1]=='f' else -.035,.035 if active[0]=='l' else -.035,0.])
  for i,leg in enumerate(legs):
   chain=[next(x for x in AUDIT['joints'] if x['name']==f'joint_{leg}_{k}') for k in [1,2,3]];tip=np.array(AUDIT['feet_local'][f'link_{leg}_knee'])
   def fk(q):
    pos=np.zeros(3);rot=np.eye(3)
    for angle,x in zip(q,chain):
     pos+=rot@x['origin'];axis=np.array(x['axis']);axis/=np.linalg.norm(axis);rot=rot@Rotation.from_rotvec(angle*axis).as_matrix()
    return pos+rot@tip
   default=q0[i*3:i*3+3];p0=fk(default)
   fit=least_squares(lambda x:fk(default+x)-(p0+shift),np.zeros(3),bounds=(-.8,.8))
   delta[env_id,i*3:i*3+3]=fit.x
   if i==env_id:
    raised=least_squares(lambda x:fk(default+x)-(p0+shift+[0,0,.05]),fit.x,bounds=(-.8,.8))
    lift[env_id,i*3:i*3+3]=raised.x-fit.x
 if a.retract:
  delta[:]=0.;lift[:]=0.
  for n in range(4):
   for i in range(4):
    sign=1. if i in [0,2] else -1.
    if i!=n:delta[n,i*3+2]=sign*.15
   sign=1. if n in [0,2] else -1.
   lift[n,n*3+1]=sign*.35;lift[n,n*3+2]=-sign*.65
 rows=[];alive=torch.ones(4,dtype=torch.bool,device=e.device)
 for k in range(450):
  t=k*.02;shift_ratio=np.clip((t-1.)/1.5,0,1)*np.clip((8.5-t)/1.,0,1);lift_ratio=np.clip((t-3.)/1.,0,1)*np.clip((7.-t)/1.,0,1)
  action=(delta*shift_ratio+lift*lift_ratio)/.2
  # Small fore-aft hip excitation during the lifted interval.
  for i in range(4):action[i,i*3+1]+=.25*np.sin(2*np.pi*(t-4.)/1.5)*(4.<t<6.)
  term=e.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.is_standing_env[:]=True;term.time_left[:]=1000.
  obs,rew,done,trunc,info=e.step(torch.tensor(action,dtype=torch.float,device=e.device));s=contact_state(e)
  valid=alive&~done;alive&=~done
  rows.append(dict(t=t,q=r.data.joint_pos[:,j].cpu().numpy().copy(),target=r.data.joint_pos_target[:,j].cpu().numpy().copy(),qd=r.data.joint_vel[:,j].cpu().numpy().copy(),torque=r.data.applied_torque[:,j].cpu().numpy().copy(),height=s.clearance.cpu().numpy().copy(),force=s.force.cpu().numpy().copy(),contact=s.contact.cpu().numpy().copy(),tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).cpu().numpy().copy(),root_height=r.data.root_pos_w[:,2].cpu().numpy().copy(),valid=valid.cpu().numpy().copy(),fall=done.cpu().numpy().copy()))
 data={k:np.stack([x[k] for x in rows]) for k in rows[0]};np.savez_compressed(out/'diagnostics.npz',**data)
 result=[]
 for i,leg in enumerate(legs):
  mask=(data['t']>=3)&(data['t']<7)&data['valid'][:,i]&(data['tilt'][:,i]<.3)&(data['root_height'][:,i]>.28)&(data['contact'][:,i].sum(-1)>=2)
  result.append(dict(leg=leg,max_clearance_stable=float(data['height'][mask,i,i].max()) if mask.any() else None,valid_lift_samples=int(mask.sum()),fall=bool(data['fall'][:,i].any()),torque_limit_fraction=float((abs(data['torque'][:,i])>=9.9).mean()),speed_peak=float(abs(data['qd'][:,i]).max()),tracking_rmse=float(np.sqrt(np.mean((data['target'][:,i]-data['q'][:,i])**2)))))
 passed=all(x['max_clearance_stable'] is not None and x['max_clearance_stable']>.015 and not x['fall'] for x in result)
 report=dict(status='PASS' if passed else 'FAIL',legs=result,actuator='implicit' if a.implicit else 'explicit_delay0',shift_m=.035,lift_cap_target_m=.05,root_writes=False,all_states_finite=all(np.isfinite(data[k]).all() for k in ['q','qd','torque','height']))
 (out/'summary.json').write_text(json.dumps(report,indent=2));print('UNLOADED_TEST',json.dumps(report),flush=True);e.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
