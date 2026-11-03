"""Physics-substep PD sensitivity at fixed 10Nm/3rad/s; no PPO."""
from pathlib import Path
import sys,json,traceback,argparse
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';p=argparse.ArgumentParser();p.add_argument('--stiffness',action='store_true');a=p.parse_args();out=E/('kp_probe' if a.stiffness else 'pd_probe');out.mkdir(exist_ok=False)
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,numpy as np,gymnasium as gym
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,configure
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.robot_cfg import JOINTS
 torch.set_num_threads(4);cfg=configure(AlignedEnvCfg(),{'no_reset_noise':True});cfg.scene.num_envs=12;cfg.episode_length_s=100.;cfg.seed=734
 e=gym.make('Dogfight-CSDog-Spot-Aligned-Flat-v3',cfg=cfg).unwrapped;r=e.scene['robot'];j=r.find_joints(JOINTS,preserve_order=True)[0];e.reset(seed=734)
 actuator=r.actuators['legs']
 if a.stiffness:
  actuator.stiffness[:4]=25.;actuator.stiffness[4:8]=50.;actuator.stiffness[8:]=75.
 else:
  actuator.damping[:4]=.2;actuator.damping[4:8]=.4;actuator.damping[8:]=.8
 target=json.loads((E/'reports/ik_dynamic_targets.json').read_text());lift=np.zeros((12,12))
 for n in range(12):
  leg=n%4;lift[n,leg*3:leg*3+3]=target[['lf','rf','lr','rr'][leg]]['0.8']['delta']
 sub=[];original=e.scene.write_data_to_sim
 def write():
  original()
  sub.append(dict(q=r.data.joint_pos[:,j].cpu().numpy().copy(),qd=r.data.joint_vel[:,j].cpu().numpy().copy(),torque=r.data.applied_torque[:,j].cpu().numpy().copy()))
 e.scene.write_data_to_sim=write;rows=[]
 for k in range(250):
  t=k*.02;term=e.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.time_left[:]=1000.;term.is_standing_env[:]=True
  ratio=np.clip((t-1.5)/.8,0,1)*np.clip((4.5-t)/.8,0,1)
  obs,rew,done,trunc,info=e.step(torch.tensor(lift*ratio/.2,dtype=torch.float,device=e.device));s=contact_state(e)
  rows.append(dict(t=t,height=s.clearance.cpu().numpy().copy(),tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).cpu().numpy().copy(),z=r.data.root_pos_w[:,2].cpu().numpy().copy(),fall=done.cpu().numpy().copy(),force=s.force.cpu().numpy().copy()))
 data={k:np.stack([x[k] for x in rows]) for k in rows[0]};np.savez_compressed(out/'policy_steps.npz',**data);np.savez_compressed(out/'physics_substeps.npz',**{k:np.stack([x[k] for x in sub]) for k in sub[0]})
 result=[]
 for group,value in enumerate([25.,50.,75.] if a.stiffness else [.2,.4,.8]):
  heights=[]
  for leg in range(4):
   n=group*4+leg;mask=(data['t']>1.5)&(data['tilt'][:,n]<.3)&(data['z'][:,n]>.28)&~data['fall'][:,n]
   heights.append(float(data['height'][mask,n,leg].max()) if mask.any() else None)
  result.append(dict(kp=value if a.stiffness else 25,kd=.8 if a.stiffness else value,stable_lift_maxima=heights,falls=int(data['fall'][:,group*4:(group+1)*4].any(0).sum())))
 (out/'summary.json').write_text(json.dumps(result,indent=2));print('PD_PROBE',json.dumps(result),flush=True);e.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
