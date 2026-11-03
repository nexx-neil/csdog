"""Real physics / contact / kinematic / reward gate for Spot v2; no training."""
from pathlib import Path
import sys,json,argparse
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_v2'
p=argparse.ArgumentParser();p.add_argument('--experiment-dir',type=Path,default=E);args=p.parse_args();E=args.experiment_dir.resolve()
if not E.is_relative_to(R/'runs/locomotion') or E.name=='csdog_ppo_20261026':p.error('Use an independent experiment under runs/locomotion')
if (E/'reports/physics_gate.json').exists():p.error('Refusing to overwrite physics gate; use an independent experiment directory')
(E/'reports').mkdir(parents=True,exist_ok=True)
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import torch,gymnasium as gym
 from types import SimpleNamespace
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.spot_v2.contacts import add_sensors,contact_state
 from dogfight.locomotion.spot_v2.config import improve
 from dogfight.locomotion.spot_v2 import rewards
 from dogfight.locomotion.robot_cfg import AUDIT,JOINTS
 from isaaclab_tasks.manager_based.locomotion.velocity.config.spot.mdp import GaitReward
 cfg=add_sensors(improve(configure(CSDogEnvCfg(),{'no_reset_noise':True}),{'enable_gait_reward':True}));cfg.scene.num_envs=4;cfg.episode_length_s=100.;cfg.seed=734
 e=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg).unwrapped;r=e.scene['robot'];e.reset();records=[]
 def command(c):
  term=e.command_manager.get_term('base_velocity');term.vel_command_b[:]=torch.tensor(c,device=e.device);term.time_left[:]=1000.;term.is_standing_env[:]=False
 for k in range(400):
  command([0,0,0]);obs,reward,terminated,truncated,info=e.step(torch.zeros(4,12,device=e.device));s=contact_state(e)
  assert torch.isfinite(reward).all() and torch.isfinite(obs['policy']).all()
  ids=e._csdog_feet_ids
  other=r.data.body_link_lin_vel_w[:,ids]+torch.cross(r.data.body_com_ang_vel_w[:,ids],s.tip_position-r.data.body_link_pos_w[:,ids],dim=-1)
  records.append(dict(t=k*.02,height=r.data.root_pos_w[:,2].tolist(),tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).tolist(),falls=int(terminated.sum()),force=s.force.tolist(),raw=s.raw_force.tolist(),clearance=s.clearance.tolist(),support=s.contact.tolist(),count=s.count.tolist(),velocity_error=float((s.tip_velocity-other).abs().max())))
 assert sum(x['falls'] for x in records)==0
 assert min(records[-1]['force'][0])>3.
 assert abs(sum(records[-1]['force'][0])-AUDIT['mass_kg']*9.81)<10.
 assert max(x['velocity_error'] for x in records)<1e-4
 assert max(records[-1]['tilt'])<.1
 assert float(s.data.current_contact_time.min())>6.
 assert float(rewards.air_time(e).max())==0. and float(rewards.clearance(e).max())==0.
 # Exercise twelve real joints independently and check finite values and slip direction.
 responses=[];j=r.find_joints(JOINTS,preserve_order=True)[0]
 for n in range(12):
  start=r.data.joint_pos[:,j[n]].clone();act=torch.zeros(4,12,device=e.device);act[:,n]=.2
  for k in range(12):
   command([.3,0,0]);obs,rew,term,trunc,info=e.step(act)
   assert torch.isfinite(rew).all();assert (rewards.slip(e)>=0).all()
  responses.append(float((r.data.joint_pos[:,j[n]]-start).abs().mean()))
  for _ in range(12):e.step(torch.zeros_like(act))
 assert min(responses)>.003
 # Official kernels tested on known timing, independently of simulator reset.
 g=object.__new__(GaitReward);g.std=.025;g.max_err=.2
 g.contact_sensor=SimpleNamespace(data=SimpleNamespace(current_air_time=torch.tensor([[0.,.12,.12,0.]]),current_contact_time=torch.tensor([[.12,0.,0.,.12]])))
 assert g._sync_reward_func(0,3)>g._sync_reward_func(0,1)
 assert g._async_reward_func(0,1)>g._async_reward_func(0,3)
 result=dict(status='PASS',contact_method='Actual GPU PhysX per-point manifold, distal radius 35mm; kinematic stationary box floor',timing_resolution_s=.02,mass=float(r.root_physx_view.get_masses()[0].sum()),driven_joints=r.num_joints,standing=records[-1],joint_response=responses,records=records,limitations='50Hz timing proxy; force-bearing distal points only, mixed shin contacts veto gait. Exact geometric source is unchanged convex-hull mesh.')
 (E/'reports/physics_gate.json').write_text(json.dumps(result,indent=2));print('SPOT_GATE PASS',flush=True);e.close()
except BaseException:
 import traceback
 traceback.print_exc()
 raise
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
