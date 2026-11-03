"""Measured plots, gait proxies and checkpoint provenance for all aligned comparisons."""
from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[2];E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3';O=E/'reports'
names=['stop','forward','backward','left','right','left_turn','right_turn','diagonal'];legs=['LF','RF','LR','RR']
def finish(fig,path):fig.tight_layout();fig.savefig(path,dpi=145);plt.close(fig)
for folder in ['evaluation_first','evaluation_second','comparison_stage2','comparison_v2_b','comparison_v2_c']:
 out=E/folder;p=out/'diagnostics.npz'
 if not p.exists():continue
 d=np.load(p);t=d['t'];valid=d['valid'];rep=valid.shape[1]//8
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  n=i*rep;value=np.where(valid[:,n,None],d['contact'][:,n].astype(float),np.nan).T
  ax.imshow(value,origin='lower',aspect='auto',extent=(t[0],t[-1],-.5,3.5),interpolation='nearest',vmin=0,vmax=1,cmap='Blues');ax.set_yticks(range(4),legs);ax.set_title(names[i])
 fig.supxlabel('Time (s), blue = distal force-bearing contact; post-fall samples excluded');finish(fig,out/'foot_contact_timeline.png')
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  for j,leg in enumerate(legs):ax.plot(t,np.where(valid[:,i*rep],d['foot_height'][:,i*rep,j],np.nan),label=leg)
  ax.axhline(.03,color='gray',ls='--');ax.set_title(names[i]);ax.set_ylabel('Whole shin convex hull min z (m)')
 axs.flat[0].legend(ncol=4);finish(fig,out/'foot_height_curves.png')
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  n=i*rep;v=valid[:,n]
  ax.plot(t,np.where(v,(abs(d['raw_action'][:,n])>1).mean(-1),np.nan),label='raw outside +/-1 (not actual clip)')
  ax.plot(t,np.where(v,(abs(d['raw_action'][:,n]-d['clipped_action'][:,n])>1e-6).mean(-1),np.nan),label='actual wrapper clip')
  ax.plot(t,np.where(v,(abs(d['torque'][:,n])>=9.9).mean(-1),np.nan),label='motor torque limit')
  ax.plot(t,np.where(v,(abs(d['qd'][:,n])>=2.97).mean(-1),np.nan),label='joint speed threshold')
  ax.set_title(names[i]);ax.set_ylabel('Fraction')
 axs.flat[0].legend(fontsize=7);finish(fig,out/'action_saturation.png')
 fig,axs=plt.subplots(4,2,figsize=(14,10),sharex=True)
 for i,ax in enumerate(axs.flat):
  n=i*rep
  for j,label in enumerate(['vx','vy','wz']):
   y=d['velocity'][:,n,j] if j<2 else d['yaw'][:,n]
   ax.plot(t,np.where(valid[:,n],y,np.nan),label=label);ax.axhline(d['command'][0,n,j],color=['C0','C1','C2'][j],ls='--',alpha=.5)
  ax.set_title(names[i])
 axs.flat[0].legend();finish(fig,out/'velocity_tracking.png')
 gait=[]
 for i,name in enumerate(names):
  n=i*rep;entry=dict(test=name,feet={})
  for j,leg in enumerate(legs):
   keep=valid[:,n];c=d['contact'][keep,n,j];h=d['foot_height'][keep,n,j];tt=t[keep];cut=tt>=1.
   trans=np.flatnonzero(np.diff(c.astype(int)))+1;bounds=np.r_[0,trans,len(c)]
   durations=[float((bounds[k+1]-bounds[k])*.02) for k in range(len(bounds)-1) if c[bounds[k]]]
   swing=((~c)&(h>.015))[cut].astype(float)
   lag=None;autocorr=None
   if len(swing)>50 and np.var(swing)>1e-8:
    z=swing-swing.mean();ac=np.correlate(z,z,mode='full')[len(z)-1:];ac=ac/ac[0];lag=10+np.argmax(ac[10:51]);autocorr=float(ac[lag])
   entry['feet'][leg]=dict(contact_durations_s=durations,landings=int((np.diff(c.astype(int))==1).sum()),true_clearance_swing_fraction=float(swing.mean()) if len(swing) else None,period_proxy_s=float(lag*.02) if lag is not None else None,autocorrelation_proxy=autocorr)
  gait.append(entry)
 (out/'gait_metrics.json').write_text(json.dumps(gait,indent=2,allow_nan=False))
# Training rates are not cross-version reward-performance scores.
fig,axs=plt.subplots(4,2,figsize=(14,13))
for stage in ['first','second']:
 p=E/stage/'metrics.jsonl'
 if not p.exists():continue
 rows=[json.loads(x) for x in p.read_text().splitlines()]
 for ax,key in zip(axs.flat,['mean_episode_reward','linear_error','yaw_error','contribution_gait','slip','air_fraction','exploration_std','torque_saturation']):
  ax.plot(np.arange(len(rows))+1,[np.nan if r[key] is None else r[key] for r in rows],label=stage);ax.set_title(key);ax.legend();ax.grid(alpha=.2)
finish(fig,O/'training_curves.png')
# Dynamics review plots do not treat fixture or intentional motion as learned locomotion.
d=np.load(E/'dynamics_explicit/dynamics.npz');fig,axs=plt.subplots(3,2,figsize=(14,10))
for leg in range(4):
 mask=d['test']=='lift_'+legs[leg].lower();tt=d['t'][mask]
 axs[0,0].plot(tt,d['height'][mask,0,leg],label=legs[leg])
 axs[0,1].plot(tt,d['root_height'][mask,0],label=legs[leg])
 for n in range(3):
  if leg==0:
   axs[1,0].plot(tt,d['q'][mask,0,n],label=f'q{n+1}');axs[1,0].plot(tt,d['target'][mask,0,n],ls='--',label=f'target{n+1}')
 axs[1,1].plot(tt,np.sqrt(np.mean((d['q'][mask,0]-d['target'][mask,0])**2,axis=-1)),label=legs[leg])
 axs[2,0].plot(tt,(abs(d['torque'][mask,0])>=9.9).mean(-1),label=legs[leg]);axs[2,1].plot(tt,abs(d['qd'][mask,0]).max(-1),label=legs[leg])
for ax,title in zip(axs.flat,['Floating open-loop lift: actual min surface z','Body height drops instead of lifting','LF commanded versus measured joint positions','All-joint tracking RMSE rad','Commanded torque saturation fraction','Max joint speed rad/s']):ax.set_title(title);ax.legend(fontsize=7);ax.grid(alpha=.2)
finish(fig,O/'dynamic_controller_diagnostics.png')
