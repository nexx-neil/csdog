"""Real floating-base gravity, contact, standing and joint-control gate, no PPO."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True,device='cuda:0').app
try:
 import torch,gymnasium as gym
 import dogfight.locomotion
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 from dogfight.locomotion.robot_cfg import AUDIT,JOINTS,FEET
 cfg=configure(CSDogEnvCfg(),{'no_reset_noise':True});cfg.scene.num_envs=4;cfg.scene.robot.init_state.pos=(0.,0.,0.435);cfg.episode_length_s=30.;cfg.sim.device='cuda:0'
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg).unwrapped
 obs,_=env.reset();robot=env.scene['robot'];sensor=env.scene['contact_forces'];ids=robot.find_joints(JOINTS,preserve_order=True)[0];feet=sensor.find_bodies(FEET,preserve_order=True)[0]
 action=torch.zeros(4,12,device=env.device);initial_z=float(robot.data.root_pos_w[0,2]);records=[];falls=0
 for i in range(400):
  cmd=env.command_manager.get_term('base_velocity');cmd.vel_command_b[:]=0.;cmd.is_standing_env[:]=True;cmd.time_left[:]=100.
  obs,reward,terminated,truncated,extra=env.step(action)
  falls+=int(terminated.sum());assert torch.isfinite(obs['policy']).all() and torch.isfinite(reward).all()
  records.append(dict(t=(i+1)*env.step_dt,z=float(robot.data.root_pos_w[0,2]),tilt=float(robot.data.projected_gravity_b[0,:2].norm()),contacts=sensor.data.net_forces_w[0,feet].norm(dim=-1).tolist()))
 settled=robot.data.joint_pos[:,ids].clone();response=[]
 for j in range(12):
  a=action.clone();a[:,j]=0.2
  for _ in range(12):env.step(a)
  response.append(float((robot.data.joint_pos[:,ids[j]]-settled[:,j]).abs().mean()))
  for _ in range(12):env.step(action)
 masses=robot.root_physx_view.get_masses()[0].cpu().tolist()
 result=dict(initial_z=initial_z,final_z=records[-1]['z'],minimum_z=min(x['z'] for x in records),maximum_settled_tilt=max(x['tilt'] for x in records[100:]),falls=falls,
  total_mass=sum(masses),expected_mass=AUDIT['mass_kg'],joint_names=robot.joint_names,controlled_order=JOINTS,body_names=robot.body_names,feet_names=FEET,
  final_contact_forces=records[-1]['contacts'],joint_pulse_response_rad=response,records=records,gravity=cfg.sim.gravity,fixed_base=robot.is_fixed_base,
  observation_shapes={key:list(value.shape) for key,value in obs.items()})
 failures=[]
 if robot.is_fixed_base:failures.append('fixed base')
 if initial_z-records[30]['z']<0.035:failures.append('no gravitational descent')
 if falls:failures.append('standing falls')
 if records[-1]['z']<0.25 or records[-1]['z']>0.40:failures.append('invalid standing height')
 if max(x['tilt'] for x in records[100:])>0.2:failures.append('unstable tilt')
 if min(records[-1]['contacts'])<3.:failures.append('not all four feet in contact')
 if min(response)<0.003:failures.append('joint control response missing')
 if abs(sum(masses)-AUDIT['mass_kg'])>0.02:failures.append('import mass mismatch')
 result.update(status='FAIL' if failures else 'PASS',failures=failures)
 out=ROOT/'runs/locomotion/csdog_ppo_20261026/reports/physics_gate.json';out.write_text(json.dumps(result,indent=2));print('PHYSICS_GATE',json.dumps({k:v for k,v in result.items() if k!='records'}),flush=True)
 env.close()
 if failures:raise RuntimeError(failures)
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
