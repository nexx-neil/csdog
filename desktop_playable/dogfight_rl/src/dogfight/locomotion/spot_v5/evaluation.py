import json,random
import numpy as np
import torch
from ..spot_v4.evaluation import rollout,summarize,TESTS,durations
from ..spot_v2.contacts import contact_state

def evaluate(runner,out,updates,seconds=6):
 b=runner.env.unwrapped;cfg=b.cfg
 rng=(torch.get_rng_state(),torch.cuda.get_rng_state_all(),np.random.get_state(),random.getstate())
 pos=cfg.events.reset_joints.params['position_range'];pose=cfg.events.reset_base.params['pose_range'];episode=cfg.episode_length_s
 cfg.events.reset_joints.params['position_range']=(0.,0.);cfg.events.reset_base.params['pose_range']={};cfg.episode_length_s=100.
 reps=b.num_envs//8;commands=torch.tensor([c for _,c in TESTS for _ in range(reps)],device=b.device)
 runner.alg.policy.eval();policy=runner.get_inference_policy(device=b.device)
 rewards=[];compute=b.reward_manager.compute
 def measured(dt):
  value=compute(dt);rewards.append(b.reward_manager._step_reward.detach().cpu().numpy().copy());return value
 b.reward_manager.compute=measured
 try:
  with torch.inference_mode():d=rollout(runner.env,policy,commands,seconds,734)
 finally:b.reward_manager.compute=compute
 rows=[]
 for i,(name,_) in enumerate(TESTS):
  ix=list(range(i*reps,i*reps+min(4,reps)));row=summarize(d,ix,name);valid=d['valid'][:,ix]&(d['t'][:,None]>=1.)
  def mean(x):return float(x[valid].mean()) if valid.any() else None
  row['fall_rate']=row['falls']/len(ix)
  for leg_index,leg in enumerate(['LF','RF','LR','RR']):
   strict=(~d['contact'][:,ix,leg_index])&(d['foot_height'][:,ix,leg_index]>.015)&(d['raw_force'][:,ix,leg_index]<1.)&(~d['shin'][:,ix,leg_index])
   ratio=float(strict[valid].mean()) if valid.any() else None
   foot=row['feet'][leg];foot['swing_ratio']=ratio;row[leg+'_swing_ratio']=ratio
   foot['true_swing_durations_s']=[duration for j in range(len(ix)) for duration in durations(strict[:,j][valid[:,j]])]
   foot['true_swing_seconds_per_trial']=float((strict&valid).sum()*.02/len(ix))
  distances=[]
  for j,env_id in enumerate(ix):
   positions=d['position'][:,env_id,:2][d['valid'][:,env_id]]
   distances.append(float(np.linalg.norm(positions[-1]-positions[0])) if len(positions)>1 else 0.)
  row['distance_xy_m']=distances
  target=np.array(row['target'][:2]);target_norm=np.linalg.norm(target)
  if target_norm>0:
   unit=target/target_norm;velocity=d['velocity'][:,ix,:2]
   row['along_command_speed']=mean(velocity@unit)
   row['undesired_linear_speed']=mean(np.abs(velocity[:,:,0]*unit[1]-velocity[:,:,1]*unit[0]))
  else:
   row['along_command_speed']=0.;row['undesired_linear_speed']=mean(np.linalg.norm(d['velocity'][:,ix,:2],axis=-1))
  row['all_air_ratio']=mean(~d['contact'][:,ix].any(-1));row['shin_ratio']=mean(d['shin'][:,ix].any(-1))
  row['action_delta_rms']=float(np.sqrt(np.mean(np.diff(d['raw_action'][:,ix],axis=0)**2)))
  row['actual_joint_delta_rms']=float(np.sqrt(np.mean(np.diff(d['q'][:,ix],axis=0)**2)))
  row['target_delta_rms']=float(np.sqrt(np.mean(np.diff(d['target'][:,ix],axis=0)**2)))
  row['reward_contributions']={n:mean(np.stack(rewards)[:,ix,k]) for k,n in enumerate(b.reward_manager.active_terms)}
  row['periodic_swing_legs']=sum(sum(x>=.06 for x in f['true_swing_durations_s'])>=2*len(ix) and f['contact_switches']>=4*len(ix) for f in row['feet'].values())
  rows.append(row)
 summary=dict(updates=updates,seconds=seconds,seed=734,replicates=min(4,reps),rows=rows)
 # Keep all raw physical data, not only successful episodes.
 np.savez_compressed(out/f'evaluation_{updates:06d}.npz',**d)
 (out/f'evaluation_{updates:06d}.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
 runner.env.samples.clear();runner.env.previous=None
 cfg.events.reset_joints.params['position_range']=pos;cfg.events.reset_base.params['pose_range']=pose;cfg.episode_length_s=episode
 torch.set_rng_state(rng[0]);torch.cuda.set_rng_state_all(rng[1]);np.random.set_state(rng[2]);random.setstate(rng[3])
 with torch.inference_mode():b.reset()
 runner.alg.policy.train()
 return summary

def rank(summary):
 rows=summary['rows'];t=[r for r in rows if r['test'] in ['forward','backward','left','right','diagonal']]
 def progress(r):
  c=np.array(r['target'][:2]);v=np.array((r['velocity'] or [0,0])[:2]);return float(v@c/(np.linalg.norm(c)+1e-10))
 valid=[r for r in t if r['fall_rate']<=.125 and (r['support_slip_speed'] or 0)<=.08 and (r['shin_ratio'] or 0)<.05 and (r['all_air_ratio'] or 0)<.01]
 effective=sum(progress(r)>.03 and r['periodic_swing_legs']>=2 for r in valid)
 swing=np.mean([np.mean([r[l+'_swing_ratio'] or 0 for l in ['LF','RF','LR','RR']]) for r in valid]) if valid else 0.
 # Feasibility and genuine stepping precede speed. All scalar tie-breakers are reported.
 return (int(all(r['fall_rate']<.5 for r in rows)),effective,sum(progress(r)>.03 for r in valid),swing,-np.mean([r['fall_rate'] for r in rows]),-np.mean([r['linear_error'] if r['linear_error'] is not None else 10. for r in t]),-np.mean([r['yaw_error'] if r['yaw_error'] is not None else 10. for r in rows]))
