"""Fixed-base calibration fixture: motor/URDF FK test only, never locomotion evidence."""
from pathlib import Path
import sys,json,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';out=E/'fixture';out.mkdir(exist_ok=False)
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,numpy as np,gymnasium as gym
 from scipy.spatial.transform import Rotation
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg,configure
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.robot_cfg import JOINTS,AUDIT
 torch.set_num_threads(4);cfg=configure(AlignedEnvCfg(),{'no_reset_noise':True});cfg.scene.num_envs=4;cfg.seed=734;cfg.episode_length_s=100.
 cfg.scene.robot.spawn.articulation_props.fix_root_link=True;cfg.scene.robot.init_state.pos=(0.,0.,.5)
 # In the unloaded fixture static support compensation is inapplicable.
 cfg.actions.joint_pos.use_default_offset=True
 e=gym.make('Dogfight-CSDog-Spot-Aligned-Flat-v3',cfg=cfg).unwrapped;r=e.scene['robot'];j=r.find_joints(JOINTS,preserve_order=True)[0];e.reset(seed=734)
 target=json.loads((E/'reports/ik_dynamic_targets.json').read_text());legs=['lf','rf','lr','rr'];lift=np.zeros((4,12));rows=[]
 for i,leg in enumerate(legs):lift[i,i*3:i*3+3]=target[leg]['0.8']['delta']
 for k in range(150):
  t=k*.02;term=e.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.time_left[:]=1000.;term.is_standing_env[:]=True
  ratio=np.clip((t-1.)/.7,0,1)
  obs,rew,done,trunc,info=e.step(torch.tensor(lift*ratio/.2,dtype=torch.float,device=e.device));s=contact_state(e)
  rows.append(dict(t=t,q=r.data.joint_pos[:,j].cpu().numpy().copy(),target=r.data.joint_pos_target[:,j].cpu().numpy().copy(),height=s.clearance.cpu().numpy().copy(),tip=s.tip_position.cpu().numpy().copy(),torque=r.data.applied_torque[:,j].cpu().numpy().copy()))
 data={k:np.stack([x[k] for x in rows]) for k in rows[0]};np.savez_compressed(out/'diagnostics.npz',**data)
 fk_errors=[]
 for i,leg in enumerate(legs):
  pos=r.data.root_pos_w[i].cpu().numpy().copy();rot=np.eye(3);q=data['q'][-1,i,i*3:i*3+3]
  for n,angle in enumerate(q,1):
   joint=next(x for x in AUDIT['joints'] if x['name']==f'joint_{leg}_{n}');pos+=rot@joint['origin'];axis=np.array(joint['axis']);axis/=np.linalg.norm(axis);rot=rot@Rotation.from_rotvec(axis*angle).as_matrix()
  point=pos+rot@AUDIT['feet_local'][f'link_{leg}_knee'];fk_errors.append(float(np.linalg.norm(point-data['tip'][-1,i,i])))
 base=data['height'][(data['t']>.6)&(data['t']<.9)].mean(0);last=data['height'][-1];rise=[float(last[i,i]-base[i,i]) for i in range(4)]
 result=dict(fixed_base=bool(r.is_fixed_base),driven_dofs=r.num_joints,unloaded_foot_rise=rise,fk_errors_m=fk_errors,target_tracking_rmse=float(np.sqrt(np.mean((data['q'][-1]-data['target'][-1])**2))),torque_peak=float(abs(data['torque']).max()),NOT_locomotion_evidence=True)
 (out/'summary.json').write_text(json.dumps(result,indent=2));print('FIXTURE',json.dumps(result),flush=True);e.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
