"""Plot saved V4 real-physics validation; never starts simulation or training."""
from pathlib import Path
import json,numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
R=Path(__file__).resolve().parents[2]
E=R/'runs/locomotion/csdog_ppo_spot_v4';O=E/'reports/figures';O.mkdir(exist_ok=True)
legs=['LF','RF','LR','RR'];colors=['tab:blue','tab:orange','tab:green','tab:red']
d=np.load(E/'balance_actual_polygon/diagnostics.npz');t=d['t']
f,axs=plt.subplots(4,2,figsize=(13,11),sharex=True)
for i,leg in enumerate(legs):
 a=axs[i,0];a.plot(t,d['height'][:,i,i]*1000,label='actual entire-shin clearance');a.plot(t,d['lift_target'][:,i]*1000,'--',label='commanded lift');a.axhline(15,color='gray',ls=':');a.set_ylabel(leg+' height (mm)');a.legend(fontsize=7)
 a=axs[i,1];a.plot(t,d['margin'][:,i]*1000,label='actual COM/support margin (mm)');a.plot(t,d['tilt'][:,i]*100,label='tilt proxy x100');a.axhline(5,color='gray',ls=':');a.legend(fontsize=7)
f.suptitle('DIAGNOSTIC ONLY: free base, COM feedback + IK; 10 Nm / 3 rad/s unchanged');axs[-1,0].set_xlabel('time (s)');axs[-1,1].set_xlabel('time (s)');f.tight_layout();f.savefig(O/'loaded_leg_lift.png',dpi=160);plt.close(f)
f,axs=plt.subplots(3,1,figsize=(12,9),sharex=True)
for i,leg in enumerate(legs):
 axs[0].plot(t,np.sqrt(((d['target'][:,i]-d['q'][:,i])**2).mean(-1)),label=leg)
 axs[1].plot(t,(abs(d['torque'][:,i])>=9.9).mean(-1)*100,label=leg)
 axs[2].plot(t,d['root'][:,i,2],label=leg)
for a,title in zip(axs,['Joint tracking RMS (rad)','Torque saturation (% of joints)','Actual body height (m)']):a.set_ylabel(title);a.legend(ncol=4)
axs[-1].set_xlabel('time (s)');f.tight_layout();f.savefig(O/'loaded_joint_diagnostics.png',dpi=160);plt.close(f)
d=np.load(E/'evaluation_video/forward_trajectory.npz');t=d['t']
f,a=plt.subplots(figsize=(10,3))
for i,leg in enumerate(legs):a.step(t,3-i+d['contact'][:,0,i]*.7,where='post',label=leg)
a.set_yticks([0,1,2,3],labels=legs[::-1]);a.set_xlabel('time (s)');a.set_title('5-update SMOKE policy: forward contact timeline (no walking learned)');f.tight_layout();f.savefig(O/'foot_contact_timeline.png',dpi=160);plt.close(f)
f,a=plt.subplots(figsize=(10,4))
for i,leg in enumerate(legs):a.plot(t,d['foot_height'][:,0,i]*1000,label=leg)
a.axhline(15,ls=':',color='gray',label='effective swing threshold');a.set_ylabel('whole-shin ground clearance (mm)');a.set_xlabel('time (s)');a.legend();f.tight_layout();f.savefig(O/'foot_height_curves.png',dpi=160);plt.close(f)
f,axs=plt.subplots(2,1,figsize=(10,6),sharex=True)
axs[0].plot(t,(abs(d['raw_action'][:,0])>1).mean(-1),label='raw outside [-1,1] (NOT clipping)');axs[0].plot(t,(abs(d['raw_action'][:,0]-d['executed_action'][:,0])>1e-6).mean(-1),'--',label='actual action clipping');axs[0].legend()
axs[1].plot(t,(abs(d['torque'][:,0])>=9.9).mean(-1),label='torque saturation');axs[1].plot(t,(abs(d['qd'][:,0])>=2.97).mean(-1),'--',label='speed saturation');axs[1].legend();axs[1].set_xlabel('time (s)');f.tight_layout();f.savefig(O/'action_saturation.png',dpi=160);plt.close(f)
f,axs=plt.subplots(3,1,figsize=(10,7),sharex=True)
c=np.load(E/'evaluation_video/continuous_commands.npz');t=c['t']
for i,name in enumerate(['vx','vy','yaw']):
 axs[i].plot(t,c['command'][:,0,i],'--',label='command');axs[i].plot(t,c['velocity'][:,0,i] if i<2 else c['yaw'][:,0],label='actual');axs[i].set_ylabel(name);axs[i].legend()
axs[0].set_title('5-update SMOKE policy: continuous commands (nearly stationary, not successful tracking)');axs[-1].set_xlabel('time (s)');f.tight_layout();f.savefig(O/'velocity_tracking.png',dpi=160);plt.close(f)
rows=[]
for name in ['spot_v4_smoke_3','spot_v4_resume_boundary','spot_v4_resume_final_1']:
 rows += [json.loads(x) for x in (R/'runs/locomotion'/name/'metrics.jsonl').read_text().splitlines()]
f,axs=plt.subplots(2,2,figsize=(11,7));x=[r['total_updates'] for r in rows]
for a,ks in zip(axs.flat,[['reward_step'],['linear_error','yaw_error'],['contribution_gait','contribution_stand_motion'],['LF_swing_ratio','RF_swing_ratio','LR_swing_ratio','RR_swing_ratio']]):
 for k in ks:a.plot(x,[r[k] for r in rows],'o-',label=k)
 a.legend(fontsize=8);a.set_xlabel('total PPO updates');a.set_xticks(x)
f.suptitle('Smoke only: 3 + safe interruption at 1 + resume 1; fresh physics state on resume');f.tight_layout();f.savefig(O/'smoke_curves.png',dpi=160);plt.close(f)
print(O)
