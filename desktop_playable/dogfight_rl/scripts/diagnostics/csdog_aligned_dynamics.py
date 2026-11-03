"""No PPO: 500Hz step/lift/swing/squat/coordination and real external-force tests."""
from pathlib import Path
import argparse,sys,json,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3'
p=argparse.ArgumentParser();p.add_argument('--implicit',action='store_true');a=p.parse_args()
out=E/('dynamics_implicit' if a.implicit else 'dynamics_explicit')
if out.exists():p.error('No overwrite')
out.mkdir()
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,numpy as np,gymnasium as gym
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,configure,AlignedPPOCfg
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 cfg=configure(AlignedEnvCfg(),{'implicit_actuator':a.implicit,'no_reset_noise':True});cfg.scene.num_envs=4;cfg.seed=734;cfg.episode_length_s=100.
 # Diagnostic tasks must not reset on intentionally lifted/perturbed states.
 e=gym.make('Dogfight-CSDog-Spot-Aligned-Flat-v3',cfg=cfg).unwrapped
 r=e.scene['robot'];ids=r.find_joints(JOINTS,preserve_order=True)[0];baseid=r.find_bodies('base')[0]
 target=json.loads((E/'reports/ik_dynamic_targets.json').read_text());records=[]
 def command():
  term=e.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.is_standing_env[:]=True;term.time_left[:]=1000.
 def run(name,seconds,target_function):
  e.reset(seed=734)
  for k in range(round(seconds/e.step_dt)):
   t=k*e.step_dt;command();delta=target_function(t)
   action=torch.tensor(delta,dtype=torch.float,device=e.device).expand(4,-1)/.2
   force=torch.zeros(4,1,3,device=e.device)
   if name=='push' and 2.<=t<2.1:force[:,:,1]=8.
   # Real 0.8 N*s lateral impulse, not root velocity injection.
   if name=='push':r.set_external_force_and_torque(force,torch.zeros_like(force),body_ids=baseid,is_global=True)
   obs,rew,term,trunc,extra=e.step(action);s=contact_state(e)
   assert obs['policy'].shape==(4,48) and obs['critic'].shape==(4,48)
   assert torch.isfinite(obs['policy']).all() and torch.isfinite(rew).all()
   # Official observation order and frames.
   assert torch.allclose(obs['policy'][:,:3],r.data.root_lin_vel_b,atol=1e-5)
   assert torch.allclose(obs['policy'][:,6:9],r.data.projected_gravity_b,atol=1e-5)
   row=dict(test=name,t=t,q=r.data.joint_pos[:,ids],target=r.data.joint_pos_target[:,ids],qd=r.data.joint_vel[:,ids],torque=r.data.applied_torque[:,ids],projected=r.root_physx_view.get_dof_projected_joint_forces()[:,ids],height=s.clearance,contact=s.contact,force=s.force,raw_force=s.raw_force,shin=s.shin,
    root_height=r.data.root_pos_w[:,2],velocity=r.data.root_lin_vel_b,tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1),fall=term,air_time=s.data.current_air_time,contact_time=s.data.current_contact_time)
   records.append({k:v.detach().cpu().numpy().copy() if torch.is_tensor(v) else v for k,v in row.items()})
  return s
 zero=lambda t:np.zeros(12)
 run('stand',6.,zero)
 for j in range(12):
  run('step_'+JOINTS[j],3.,lambda t,j=j:np.eye(12)[j]*.15*(1.<=t<2.))
 # Same geometrically calibrated cap lift for all legs, independent unilateral trials.
 for i,leg in enumerate(['lf','rf','lr','rr']):
  delta=np.zeros(12);delta[i*3:i*3+3]=target[leg]['0.8']['delta']
  run('lift_'+leg,4.,lambda t,d=delta:d*np.clip((t-1.)/.7,0,1)*np.clip((3.5-t)/.7,0,1))
  run('swing_'+leg,4.,lambda t,d=delta,i=i:d*np.clip((t-1.)/.7,0,1)*np.clip((3.5-t)/.7,0,1)+np.eye(12)[i*3+1]*.10*np.sin(2*np.pi*(t-1.)/1.5)*(1.7<t<2.8))
 all_lift=np.concatenate([np.array(target[leg]['0.8']['delta'])*.3 for leg in ['lf','rf','lr','rr']])
 run('height_all',4.,lambda t:all_lift*np.sin(np.pi*np.clip((t-1)/2,0,1))**2)
 run('coordination',4.,lambda t:np.array([0,.05,-.08,0,-.05,.08,0,.05,-.08,0,-.05,.08])*np.sin(2*np.pi*t/1.2))
 run('push',4.,zero)
 data={k:np.stack([x[k] for x in records]) for k in records[0]};np.savez_compressed(out/'dynamics.npz',**data)
 summary=[]
 for name in dict.fromkeys(data['test']):
  mask=(data['test']==name)&(data['t']>=1.)
  q=data['q'][mask];qtarget=data['target'][mask];tau=data['torque'][mask];qd=data['qd'][mask]
  summary.append(dict(test=name,tracking_rmse=float(np.sqrt(np.mean((q-qtarget)**2))),joint_tracking_rmse=np.sqrt(np.mean((q-qtarget)**2,axis=(0,1))).tolist(),max_torque=float(abs(tau).max()),torque_limit_fraction=float((abs(tau)>=9.9).mean()),speed_peak=float(abs(qd).max()),speed_limit_fraction=float((abs(qd)>=2.97).mean()),position_limit_fraction=float((abs(qtarget)>=2.826).mean()),height_max=data['height'][mask].max(axis=(0,1)).tolist(),falls=int(data['fall'][mask].any(axis=0).sum()),tilt_max=float(data['tilt'][mask].max()),shin_fraction=float(data['shin'][mask].mean())))
 stand=next(x for x in summary if x['test']=='stand')
 failures=[]
 if stand['falls']:failures.append('standing falls')
 if stand['tilt_max']>.1:failures.append('standing unstable')
 last=(data['test']=='stand')&(data['t']>5.)
 if not np.all(data['contact'][last]):failures.append('standing contacts missing')
 total_force=float(data['force'][last].sum(-1).mean())
 if abs(total_force-AUDIT['mass_kg']*9.81)>10:failures.append('force balance')
 lifted=[next(x for x in summary if x['test']=='lift_'+leg)['height_max'][i] for i,leg in enumerate(['lf','rf','lr','rr'])]
 if min(lifted)<.015:failures.append('one or more legs cannot actually lift 15mm')
 result=dict(status='FAIL' if failures else 'PASS',failures=failures,actuator='implicit' if a.implicit else 'DelayedPD_zero_delay',physics_dt=e.physics_dt,step_dt=e.step_dt,observation_dimension=48,all_states_finite=True,total_stand_force=total_force,leg_lift_heights=lifted,summary=summary,mass=float(r.root_physx_view.get_masses()[0].sum()),settings=dict(kp=25,kd=.8,effort_limit=10,velocity_limit=3),notes='Explicit applied torque is commanded physical torque; implicit torque remains PD estimate. Projected joint force stored separately.')
 (out/'summary.json').write_text(json.dumps(result,indent=2));print('DYNAMIC_GATE',json.dumps({k:v for k,v in result.items() if k!='summary'}),flush=True)
 e.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
