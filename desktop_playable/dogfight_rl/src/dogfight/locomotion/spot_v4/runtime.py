"""Actual simulation preflight and compatible RSL learner restoration."""
import json,hashlib,random
from pathlib import Path
import numpy as np
import torch
from .contracts import IDENTITY,TASK,JOINTS,completed_updates,finite_tree
def preflight(env):
 from ..spot_v2.contacts import contact_state
 b=env.unwrapped;r=b.scene['robot'];obs,_=b.reset(seed=b.cfg.seed)
 if r.num_joints!=12:raise ValueError('Expected exactly 12 driven joints')
 action=b.action_manager.get_term('joint_pos')
 if list(action._joint_names)!=JOINTS:raise ValueError('Action joint order mismatch')
 if list(r.find_joints(JOINTS,preserve_order=True)[1])!=JOINTS:raise ValueError('Robot joint mapping mismatch')
 for _ in range(8):
  term=b.command_manager.get_term('base_velocity');term.vel_command_b[:]=0.;term.is_standing_env[:]=True;term.time_left[:]=100.
  obs,reward,done,trunc,extra=b.step(torch.zeros(b.num_envs,12,device=b.device))
  if done.any():raise RuntimeError('Robot terminated during zero-action preflight')
  for group in ['policy','critic']:
   if obs[group].shape!=(b.num_envs,48) or not torch.isfinite(obs[group]).all():raise ValueError(f'Invalid {group} observation')
  if not torch.isfinite(reward).all() or not torch.isfinite(b.reward_manager._step_reward).all():raise ValueError('Non-finite rewards')
 if not torch.allclose(obs['policy'][:,:3],r.data.root_lin_vel_b,atol=1e-5):raise ValueError('Linear velocity observation frame/order mismatch')
 if not torch.allclose(obs['policy'][:,9:12],b.command_manager.get_command('base_velocity')):raise ValueError('Velocity command observation mismatch')
 if not torch.allclose(r.data.joint_effort_limits,torch.full_like(r.data.joint_effort_limits,10.)):raise ValueError('Unexpected effort limits')
 if not torch.allclose(r.data.joint_vel_limits,torch.full_like(r.data.joint_vel_limits,3.)):raise ValueError('Unexpected velocity limits')
 s=contact_state(b)
 if not torch.isfinite(s.velocity).all() or not torch.isfinite(s.clearance).all():raise ValueError('Non-finite foot diagnostics')
 b.reset(seed=b.cfg.seed)
 return dict(status='PASS',num_envs=b.num_envs,actor_obs=48,critic_obs=48,action_dim=12,joint_order=JOINTS,physics_dt=b.physics_dt,policy_dt=b.step_dt,mass_kg=float(r.root_physx_view.get_masses()[0].sum()),rewards=b.reward_manager.active_terms,hardware_limits=dict(effort_nm=10,velocity_rad_s=3),foot_timing_proxy_s=.02,dynamics_limitation='All four legs lift with diagnostic COM feedback at body target .30m; front-leg torque/tracking margins remain limited. No diagnostic controller in PPO.')
def load_learner(runner,path,weights_only=False,restore_rng=True):
 state=torch.load(path,map_location=runner.device,weights_only=False)
 if not finite_tree(state):raise ValueError('Checkpoint contains NaN/Inf tensors')
 expected=runner.alg.policy.state_dict()
 actual=state.get('model_state_dict',{})
 if set(expected)!=set(actual) or any(expected[k].shape!=actual[k].shape for k in expected):raise ValueError('Checkpoint network tensors incompatible with 48D Spot V4 architecture')
 source=completed_updates(state)
 if not weights_only and 'optimizer_state_dict' not in state:raise ValueError('Full resume requires optimizer state; use --weights-only for explicit network initialization')
 runner.load(str(path),load_optimizer=not weights_only,map_location=runner.device)
 if weights_only:runner.current_learning_iteration=0
 else:
  runner.current_learning_iteration=source
  # RSL 3.1.2 loads optimizer but does not restore PPO.learning_rate scalar.
  v4=(state.get('infos') or {}).get('spot_v4',{})
  lr=float(v4.get('learning_rate',state['optimizer_state_dict']['param_groups'][0]['lr']))
  runner.alg.learning_rate=lr
  for group in runner.alg.optimizer.param_groups:group['lr']=lr
  if restore_rng and 'rng' in v4:
   rng=v4['rng'];torch.set_rng_state(rng['torch_cpu'].cpu());np.random.set_state(rng['numpy']);random.setstate(rng['python'])
   if torch.cuda.is_available() and rng.get('torch_cuda'):torch.cuda.set_rng_state_all([x.cpu() for x in rng['torch_cuda']])
 return dict(mode='weights_only' if weights_only else 'full_learner_resume',source_checkpoint_updates=source,base_updates=0 if weights_only else source,optimizer_restored=not weights_only,learning_rate=float(runner.alg.learning_rate),simulation_state_restored=False,rng_restored=bool(not weights_only and (state.get('infos') or {}).get('spot_v4',{}).get('rng')),checkpoint=str(Path(path).resolve()),sha256=hashlib.sha256(Path(path).read_bytes()).hexdigest())
