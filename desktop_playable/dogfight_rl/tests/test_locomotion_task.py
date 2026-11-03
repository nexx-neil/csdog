"""New-model identity and hard training budget regressions; no simulator or training launched."""
import json
from pathlib import Path
import pytest
from dogfight.common.paths import ROOT
from dogfight.locomotion.model_audit import inspect
from dogfight.locomotion.budget import Budget

def test_new_model_calibration_does_not_use_legacy_joint_semantics():
 data=inspect()
 assert data['actuated_joints']==12
 assert set(data['standing_pose'])=={f'joint_{leg}_{joint}' for leg in ['lf','rf','lr','rr'] for joint in [1,2,3]}
 assert all(abs(pos[2]+0.35)<0.002 for pos in data['standing_foot_positions'].values())
 assert abs(data['mass_kg']-7.6042608)<1e-6
 assert all(min(link['inertia_eigenvalues'])>0 for link in data['links'].values())

def test_cumulative_budget_rejects_update_301_without_starting_run(tmp_path):
 path=tmp_path/'training_budget.json'
 path.write_text(json.dumps({'max_updates':300,'max_seconds':2400,'official_validation_reservation':1,
  'runs':[{'status':'COMPLETE','completed_updates':299,'reserved_updates':299,'seconds':200.}]}))
 before=path.read_bytes()
 with pytest.raises(RuntimeError,match='budget exceeded'):
  Budget(tmp_path,'forbidden',1,60)
 assert path.read_bytes()==before

def test_cumulative_time_budget_blocks_new_training(tmp_path):
 path=tmp_path/'training_budget.json'
 path.write_text(json.dumps({'max_updates':300,'max_seconds':2400,'official_validation_reservation':1,
  'runs':[{'status':'COMPLETE','completed_updates':1,'reserved_updates':1,'seconds':2400.}]}))
 with pytest.raises(RuntimeError,match='budget exceeded'):
  Budget(tmp_path,'forbidden',1,60)

def test_gym_registration_points_to_new_external_task():
 import gymnasium as gym
 import dogfight.locomotion
 spec=gym.spec('Dogfight-CSDog-Velocity-Flat-v0')
 assert spec.entry_point=='isaaclab.envs:ManagerBasedRLEnv'
 assert spec.kwargs['env_cfg_entry_point']=='dogfight.locomotion.env_cfg:CSDogEnvCfg'
