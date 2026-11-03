"""True upward knee-pulse comparison: no PPO, IK, root control, or asset edits."""
from pathlib import Path
import sys,argparse,fcntl,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
p=argparse.ArgumentParser();p.add_argument('--collision',choices=['original','sole'],required=True);a=p.parse_args()
base=ROOT/'runs/locomotion/csdog_phase_guided_ppo_v7';out=base/('lift_probe_'+a.collision);out.mkdir(exist_ok=False)
lock=(ROOT/'runs/locomotion/csdog_curriculum_v6/gpu.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,gymnasium as gym,numpy as np
 torch.set_num_threads(4)
 import dogfight.locomotion
 from dogfight.locomotion.phase_guided_v7.runtime import build,contacts
 cfg,_=build(dict(phase=False,collision=a.collision),4,42)
 cfg.events.reset_base.params['pose_range']={};cfg.events.reset_joints.params['position_range']=(0.,0.);cfg.episode_length_s=30.
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg).unwrapped;r=env.scene['robot'];rows=[];results={}
 for k,(leg,sign) in enumerate(zip(('lf','rf','lr','rr'),(-1,1,-1,1))):
  env.reset(seed=42)
  for t in range(210):
   action=torch.zeros(4,12,device=env.device)
   amp=min(1.,max(0.,(t-100)/15)) if t<135 else max(0.,1-(t-135)/15)
   action[:,3*k+2]=sign*amp
   cmd=env.command_manager.get_term('base_velocity');cmd.vel_command_b.zero_();cmd.is_standing_env[:]=True;cmd.time_left[:]=100.
   obs,reward,done,trunc,extra=env.step(action);s=contacts(env)
   row=dict(leg=leg,t=t*.02,amplitude=amp,clearance=s.clearance.tolist(),force=s.force.tolist(),raw_force=s.raw_force.tolist(),shin=s.shin.tolist(),slip=s.velocity[:,:,:2].norm(dim=-1).tolist(),root_z=r.data.root_pos_w[:,2].tolist(),tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).tolist(),joint_pos=r.data.joint_pos.tolist(),joint_target=r.data.joint_pos_target.tolist(),torque=r.data.applied_torque.tolist(),fallen=done.tolist())
   rows.append(row)
  active=[x for x in rows if x['leg']==leg and .99<=x['amplitude']<=1]
  all_leg=[x for x in rows if x['leg']==leg]
  results[leg]=dict(peak_clearance=float(max(np.array(x['clearance'])[:,k].max() for x in all_leg)),hold_clearance=float(np.mean([np.array(x['clearance'])[:,k] for x in active])),hold_force=float(np.mean([np.array(x['force'])[:,k] for x in active])),max_tilt=float(max(max(x['tilt']) for x in all_leg)),torque_saturation_fraction=float(np.mean(np.abs([x['torque'] for x in all_leg])>=9.99)),falls=int(np.sum([x['fallen'] for x in all_leg])))
 atomic=dict(collision=a.collision,summary=results,records=rows,joint_order=r.joint_names,signs=[-1,1,-1,1],action_scale=.2,source='upward signs established by finite-difference geometry; actual PhysX measurements below')
 (out/'results.json').write_text(json.dumps(atomic,indent=2));print('UPWARD_LIFT_RESULT',json.dumps(results),flush=True)
 env.close()
except BaseException:
 import traceback;traceback.print_exc();raise
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
