"""Execute every optional reward once in real physics without any PPO updates."""
from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True,device='cuda:0').app
try:
 import torch,gymnasium as gym
 import dogfight.locomotion
 from dogfight.locomotion.env_cfg import CSDogEnvCfg,configure
 cfg=configure(CSDogEnvCfg(),{k:True for k in ['enable_gait_reward','enable_foot_air_time_reward','enable_foot_clearance_reward','enable_foot_slip_penalty']})
 cfg.scene.num_envs=4;cfg.sim.device='cuda:0'
 env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg).unwrapped;env.reset()
 for _ in range(30):
  obs,reward,terminated,truncated,extras=env.step(torch.zeros(4,12,device=env.device))
  assert torch.isfinite(reward).all() and torch.isfinite(obs['policy']).all()
 assert all(name in env.reward_manager.active_terms for name in ['gait','foot_air_time','foot_clearance','foot_slip'])
 result=dict(status='PASS',active_terms=env.reward_manager.active_terms,physics_steps=30,ppo_updates=0)
 (ROOT/'runs/locomotion/csdog_ppo_20261026/reports/optional_rewards_gate_final.json').write_text(json.dumps(result,indent=2));print('OPTIONAL_REWARDS',json.dumps(result),flush=True);env.close()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
