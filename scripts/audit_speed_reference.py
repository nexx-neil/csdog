#!/usr/bin/env python3
"""Dense geometric screen of the explicit speed-command domain and stationary lowering."""
import argparse,itertools,json
from pathlib import Path
import torch
from csdog_motion.calibration import ASSET
from csdog_motion.residual_learning import learning_profile
from csdog_motion.speed_learning import valid_speed_request,SPEED_LIMITS
from csdog_motion.trajectory import LegKinematics,TrajectoryConfig,foot_reference
from csdog_motion.training import file_hash
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
if a.output.exists():p.error('New output required')
torch.set_num_threads(1);d=learning_profile();m=LegKinematics(ASSET/'robot_sim.urdf',d['nominal_joint_positions_rad'],offset_bound=.5,dtype=torch.float64)
nom=torch.tensor([d['nominal_sole_positions_body_m'][l] for l in ('lr','lf','rf','rr')],dtype=torch.float64)
commands=list(itertools.product((-.4,-.2,0.,.2,.4),(-.3,-.15,0.,.15,.3),(-.4,-.2,0.,.2,.4)))
for axis,limit in enumerate(SPEED_LIMITS):
 for sign in (-1,1):
  cmd=[0.,0.,0.];cmd[axis]=sign*limit;commands.append(tuple(cmd))
commands=torch.tensor(sorted(set(commands)),dtype=torch.float64);assert valid_speed_request(commands).all()
phase=torch.arange(400,dtype=torch.float64)/400
foot,_=foot_reference(phase.repeat(len(commands)),commands.repeat_interleave(400,0),nom,TrajectoryConfig(**d['trajectory']))
q,error=m.solve(foot,iterations=18);q=q.reshape(len(commands),400,4,3)
velocity=(q.roll(-1,1)-q.roll(1,1))/(d['trajectory']['period_s']/200)
margin=torch.minimum(q-m.lower,m.upper-q)
height=torch.linspace(d['nominal_height_m']-.04,d['nominal_height_m'],201,dtype=torch.float64)
foot,_=foot_reference(torch.zeros_like(height),torch.zeros(len(height),3,dtype=torch.float64),nom,TrajectoryConfig(**d['trajectory']),blend=torch.zeros_like(height),height_delta=height-d['nominal_height_m'])
hq,he=m.solve(foot,iterations=30)
result={'scope':'free-space geometry only; no contact, torque, collision, dynamics or hardware certification',
 'urdf_sha256':file_hash(ASSET/'robot_sim.urdf'),'phase_samples':400,'commands':commands.tolist(),
 'max_ik_error_m':float(error.max()),'max_periodic_joint_target_velocity_rad_s':float(velocity.abs().max()),'minimum_joint_reserve_rad':float(margin.min()),
 'stationary_posture':{'height_range_m':[float(height.min()),float(height.max())],'max_ik_error_m':float(he.max()),'minimum_joint_reserve_rad':float(torch.minimum(hq-m.lower,m.upper-hq).min()),'moving_lowered_gait_validated':False}}
result['gate']='PASS' if result['max_ik_error_m']<.001 and result['max_periodic_joint_target_velocity_rad_s']<8 and result['minimum_joint_reserve_rad']>.05 and he.max()<.001 else 'FAIL'
a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='commands'},indent=2))
