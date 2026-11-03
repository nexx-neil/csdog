"""Plots and repeatable gait metrics from measured NPZ, never fabricated trajectories."""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_v2';O=E/'reports'
legs=['LF','RF','LR','RR'];names=['stop','forward','backward','left','right','left_turn','right_turn','diagonal']
for stage in ['baseline_final','evaluation_b','evaluation_c']:
 path=E/stage/'diagnostics.npz'
 if not path.exists():continue
 d=np.load(path);t=d['t'];out=E/stage
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  n=i*4;ax.imshow(np.where(d['valid'][:,n,None],d['contact'][:,n,:].astype(float),np.nan).T,origin='lower',aspect='auto',extent=(t[0],t[-1],-.5,3.5),interpolation='nearest',vmin=0,vmax=1,cmap='Blues');ax.set_yticks(range(4),legs);ax.set_title(names[i])
 fig.supxlabel('Time (s); blue = force-bearing distal contact, 50Hz');fig.tight_layout();fig.savefig(out/'foot_contact_timeline.png',dpi=150);plt.close(fig)
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  for k,leg in enumerate(legs):ax.plot(t,np.where(d['valid'][:,i*4],d['foot_height'][:,i*4,k],np.nan),label=leg)
  ax.axhline(.03,color='gray',ls='--');ax.set_title(names[i]);ax.set_ylabel('Whole knee hull minimum z (m)')
 axs.flat[0].legend(ncol=4);fig.tight_layout();fig.savefig(out/'foot_height_curves.png',dpi=150);plt.close(fig)
 fig,axs=plt.subplots(6,2,figsize=(16,15),sharex=True)
 for j,ax in enumerate(axs.flat):
  n=4
  ax.plot(t,d['raw_action'][:,n,j],label='raw action',alpha=.65);ax.plot(t,d['clipped_action'][:,n,j],label='clipped action',lw=.8);ax.plot(t,d['q'][:,n,j],label='q rad');ax.plot(t,d['target'][:,n,j],label='target rad',lw=.7);ax.plot(t,d['qd'][:,n,j],label='qd rad/s',alpha=.4);ax.plot(t,d['torque'][:,n,j],label='PD torque estimate Nm',alpha=.4);ax.set_title(f'{legs[j//3]} joint {j%3+1} | forward')
 axs.flat[0].legend(fontsize=7,ncol=2);fig.tight_layout();fig.savefig(out/'joint_action_diagnostics.png',dpi=140);plt.close(fig)
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  for k,leg in enumerate(legs):
   v=np.linalg.norm(d['patch_velocity'][:,i*4,k,:2],axis=-1);ax.plot(t,np.where(d['contact'][:,i*4,k]&d['valid'][:,i*4],v,np.nan),label=leg)
  ax.set_title(names[i]);ax.set_ylabel('Contact patch speed (m/s)')
 axs.flat[0].legend();fig.tight_layout();fig.savefig(out/'foot_slip_diagnostics.png',dpi=150);plt.close(fig)
 # Contact run durations and swing autocorrelation; stance agreement alone is not a gait.
 gait=[]
 for i,name in enumerate(names):
  entry=dict(test=name,feet={})
  for k,leg in enumerate(legs):
   keep=d['valid'][:,i*4];c=d['contact'][keep,i*4,k];trans=np.flatnonzero(np.diff(c.astype(int)))+1;bounds=np.r_[0,trans,len(c)];dur=[(bounds[x+1]-bounds[x])*.02 for x in range(len(bounds)-1) if c[bounds[x]]]
   swing=((~c)&(d['foot_height'][keep,i*4,k]>.015)).astype(float)[50:];z=swing-swing.mean();ac=np.correlate(z,z,mode='full')[len(z)-1:];ac=ac/max(ac[0],1e-9);lag=10+np.argmax(ac[10:51]) if len(ac)>50 and np.var(swing)>1e-8 else None;period=float(lag*.02) if lag is not None else None
   entry['feet'][leg]=dict(contact_durations_s=dur,stance_mean_s=float(np.mean(dur)) if dur else None,swing_fraction=float(swing.mean()),period_proxy_s=period,autocorrelation_proxy=float(ac[lag]) if lag is not None else None,landings=int(np.sum(np.diff(c.astype(int))==1)))
  gait.append(entry)
 (out/'gait_metrics.json').write_text(json.dumps(gait,indent=2))
# Training curves include actual per-term weighted contributions.
fig,axs=plt.subplots(3,2,figsize=(13,11))
for stage in ['stage_b','stage_c']:
 p=E/stage/'metrics.jsonl'
 if not p.exists():continue
 rows=[json.loads(x) for x in p.read_text().splitlines()]
 for ax,key in zip(axs.flat,['mean_episode_reward','linear_error','yaw_error','slip','action_clip','gait_coordination']):
  ax.plot(np.arange(len(rows))+1,[x[key] for x in rows],label=stage);ax.set_title(key);ax.legend();ax.grid(alpha=.2)
fig.tight_layout();fig.savefig(O/'training_curves.png',dpi=150);plt.close(fig)
