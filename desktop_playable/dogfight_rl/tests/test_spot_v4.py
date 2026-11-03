from pathlib import Path
from types import SimpleNamespace
import json
import numpy as np
import torch
import pytest
from dogfight.locomotion.spot_v4.rewards import stop_weight,command_stop_weight,joint_position_penalty,stand_motion_penalty
from dogfight.locomotion.spot_v4.contracts import IDENTITY,completed_updates,validate_identity,output_path
from dogfight.locomotion.spot_v4.diagnostic_ik import LegKinematics,support_margin

def env(command=(0.,0.,0.),speed=0.,jitter=0.):
 e=SimpleNamespace(command=torch.tensor([command]),common_step_counter=0,step_dt=.02,episode_length_buf=torch.tensor([10]))
 d=SimpleNamespace(joint_pos=torch.full((1,12),.1),default_joint_pos=torch.zeros(1,12),root_lin_vel_b=torch.tensor([[speed,0.,0.]]),root_ang_vel_b=torch.zeros(1,3),joint_vel=torch.full((1,12),jitter))
 e.scene={'robot':SimpleNamespace(data=d)};e.command_manager=SimpleNamespace(get_command=lambda _:e.command)
 e.action_manager=SimpleNamespace(action=torch.full((1,12),jitter),prev_action=torch.zeros(1,12))
 return e

def test_zero_command_cannot_escape_posture_penalty_by_drifting():
 rest=env();drift=env(speed=.2)
 assert torch.equal(joint_position_penalty(rest),joint_position_penalty(drift))
 assert stand_motion_penalty(drift)>stand_motion_penalty(rest)
 assert command_stop_weight(rest)==1. and command_stop_weight(drift)==1.

def test_moving_command_is_not_suppressed_by_stop_control():
 e=env((.3,0.,0.),speed=.3)
 assert stand_motion_penalty(e)==0.
 assert torch.allclose(joint_position_penalty(e),torch.tensor([.1*np.sqrt(12)],dtype=torch.float))

def test_command_step_ramps_and_is_speed_independent():
 slow=env((.3,0.,0.));fast=env((.3,0.,0.),speed=.2)
 command_stop_weight(slow);command_stop_weight(fast)
 seq=[]
 for k in range(1,101):
  for e in [slow,fast]:e.command[:]=0.;e.common_step_counter=k
  w=command_stop_weight(slow);assert torch.equal(w,command_stop_weight(fast));seq.append(float(w))
  # Multiple reward reads during one simulation step must not advance the filter.
  assert float(command_stop_weight(slow))==seq[-1]
 assert 0.<seq[0]<.1 and seq[-1]>.999
 assert np.all(np.diff(seq)>0)
 slow.command[:]=torch.tensor([[.3,0.,0.]]);slow.common_step_counter+=1
 assert command_stop_weight(slow)==0.

def test_static_joint_jitter_is_penalized():
 assert stand_motion_penalty(env(jitter=2.))>stand_motion_penalty(env(jitter=0.))

def test_command_weight_smooth_transition_and_reset():
 cmd=torch.zeros(1001,3);cmd[:,0]=torch.linspace(0,.1,1001);w=stop_weight(cmd)
 assert bool((w[1:]<=w[:-1]).all()) and float(abs(w[1:]-w[:-1]).max())<.003
 e=env((.3,0,0));command_stop_weight(e);e.command[:]=0;e.common_step_counter=1;e.episode_length_buf[:]=0
 assert command_stop_weight(e)==1.

def test_counter_is_new_updates_and_legacy_zero_based():
 assert completed_updates({'iter':219,'infos':None})==220
 assert completed_updates({'iter':4,'infos':{'spot_v4':{'completed_updates':5}}})==5

def test_checkpoint_contract_rejects_wrong_observation_before_loading(tmp_path):
 p=tmp_path/'bad.pt';p.write_bytes(b'not loaded')
 (tmp_path/'identity.json').write_text(json.dumps({**IDENTITY,'actor_obs':45}))
 with pytest.raises(ValueError,match='actor_obs'):validate_identity(p)

def test_output_name_rejects_traversal_and_existing_run():
 with pytest.raises(ValueError):output_path('../bad')
 with pytest.raises(FileExistsError):output_path('csdog_ppo_spot_aligned_v3')

def test_analytic_leg_jacobian_matches_finite_difference():
 root=Path(__file__).resolve().parents[1];kin=LegKinematics(json.loads((root/'configs/locomotion/csdog_ppo/model_audit.json').read_text()))
 q=kin.default[None]+.05;tip,jac=kin.forward(q,True)
 for j in range(3):
  plus=q.copy();minus=q.copy();plus[...,j]+=1e-6;minus[...,j]-=1e-6
  numerical=(kin.forward(plus)-kin.forward(minus))/2e-6
  np.testing.assert_allclose(jac[...,j],numerical,atol=1e-7)

def test_support_polygon_margin_uses_actual_triangle_winding():
 tri=np.array([[[0.,0.],[1.,0.],[0.,1.]]])
 assert support_margin(np.array([[.2,.2]]),tri)>0.
 assert support_margin(np.array([[1.,1.]]),tri)<0.
 np.testing.assert_allclose(support_margin(np.array([[.2,.2]]),tri),support_margin(np.array([[.2,.2]]),tri[:,::-1]))

def test_gait_no_bonus_for_all_air_or_all_stance():
 from dogfight.locomotion.spot_v4.rewards import gait_phase_eligible
 c=torch.tensor([[False]*4,[True]*4,[True,False,False,True]])
 h=torch.tensor([[.04]*4,[0.]*4,[0.,.03,.03,0.]])
 f=torch.tensor([[0.]*4,[20.]*4,[20.,0.,0.,20.]])
 assert gait_phase_eligible(c,h,f).tolist()==[False,False,True]
