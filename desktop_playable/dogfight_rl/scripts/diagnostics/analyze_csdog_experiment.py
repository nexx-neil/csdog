"""Generate figures and comparison tables solely from saved measurements."""
from pathlib import Path
import json,csv,hashlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[2];EXP=ROOT/'runs/locomotion/csdog_ppo_20261026';OUT=EXP/'reports'
def load_metrics(stage):return [json.loads(line) for line in (EXP/stage/'metrics.jsonl').read_text().splitlines()]
a,b=load_metrics('stage1'),load_metrics('stage2')
evals=[json.loads((EXP/f'evaluation_stage{s}_final/summary.json').read_text()) for s in [1,2]]
fig,axes=plt.subplots(3,2,figsize=(13,11));plots=[('mean_episode_reward','Mean episodic reward (weights change at150)'),('mean_episode_length','Episode length (steps;400=8s)'),('linear_error','Training planar tracking error (m/s)'),('yaw_error','Training yaw tracking error (rad/s)'),('action_delta_sq','Raw action change mean square'),('gpu_memory_mib','GPU used memory (MiB)')]
for ax,(key,title) in zip(axes.flat,plots):
 for rows,label,color in [(a,'Stage1','#1677a8'),(b,'Stage2','#d16b20')]:
  ax.plot([r['iteration']+1 for r in rows],[r[key] if r[key] is not None else np.nan for r in rows],label=label,color=color,lw=1.2)
 ax.axvline(150,c='gray',ls='--');ax.set_title(title);ax.set_xlabel('Policy PPO updates (smoke excluded)');ax.grid(alpha=.25);ax.legend()
fig.tight_layout();fig.savefig(OUT/'training_curves.png',dpi=160);plt.close(fig)
fig,axes=plt.subplots(2,2,figsize=(13,8));labels=[r['test'] for r in evals[0]['tests']];x=np.arange(8)
for ax,(key,title) in zip(axes.flat,[('linear_error','Fixed-command planar error (m/s)'),('yaw_error','Fixed-command yaw error (rad/s)'),('contact_slip_speed','Contact foot slip proxy (m/s)'),('processed_action_delta_mean_square','Clipped action change mean square')]):
 for j,d in enumerate(evals):ax.bar(x+(j-.5)*.36,[r[key] for r in d['tests']],.36,label=f'Stage{j+1}')
 ax.set_xticks(x,labels,rotation=30,ha='right');ax.set_title(title);ax.legend();ax.grid(axis='y',alpha=.2)
fig.tight_layout();fig.savefig(OUT/'evaluation_comparison.png',dpi=160);plt.close(fig)

fig,axes=plt.subplots(2,2,figsize=(12,8))
for ax,(key,title) in zip(axes.flat,[('value_function','Value loss'),('surrogate','PPO surrogate loss'),('policy_entropy','Policy entropy'),('learning_rate','Adaptive learning rate')]):
 for rows,label in [(a,'Stage1'),(b,'Stage2')]:ax.plot([r['iteration']+1 for r in rows],[r[key] for r in rows],label=label)
 ax.axvline(150,c='gray',ls='--');ax.set_title(title);ax.grid(alpha=.2);ax.legend()
fig.tight_layout();fig.savefig(OUT/'ppo_diagnostics.png',dpi=160);plt.close(fig)

rows=[]
for i,name in enumerate(labels):
 row={'test':name}
 for s,d in enumerate(evals,1):
  value=d['tests'][i]
  for key in ['target','actual_mean_velocity','actual_mean_yaw_rate','linear_error','yaw_error','mean_travel_distance','falls','fall_rate','tilt_rms','contact_slip_speed','low_swing_proxy','action_delta_mean_square','processed_action_delta_mean_square','action_clip_fraction']:
   row[f'stage{s}_{key}']=value[key]
 rows.append(row)
with (OUT/'comparison.csv').open('w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
summary={}
for stage,metrics,ev in [('stage1',a,evals[0]),('stage2',b,evals[1])]:
 summary[stage]={'updates':len(metrics),'last_mean_reward':metrics[-1]['mean_episode_reward'],'last10_mean_reward':float(np.mean([r['mean_episode_reward'] for r in metrics[-10:]])),
  'first10_mean_reward':float(np.mean([r['mean_episode_reward'] for r in metrics[:10] if r['mean_episode_reward'] is not None])),
  'last10_episode_seconds':float(np.mean([r['mean_episode_length'] for r in metrics[-10:]]))*.02,
  'training_fall_fraction_of_completed_episodes':sum(r['falls'] for r in metrics)/max(1.,sum(r['done'] for r in metrics)),
  'max_gpu_memory_mib':max(r['gpu_memory_mib'] for r in metrics),'eval_falls':sum(r['falls'] for r in ev['tests']),
  'eval_mean_linear_error':float(np.mean([r['linear_error'] for r in ev['tests']])),
  'eval_mean_yaw_error':float(np.mean([r['yaw_error'] for r in ev['tests']])),
  'stop_error':ev['tests'][0]['linear_error'],'continuous_stop_error':ev['continuous_stop_linear_speed'],
  'mean_processed_action_delta':float(np.mean([r['processed_action_delta_mean_square'] for r in ev['tests']]))}
summary['budget']=json.loads((EXP/'training_budget.json').read_text());summary['new_task_updates']=sum(r['completed_updates'] for r in summary['budget']['runs']);summary['official_validation_updates']=1;summary['total_updates']=summary['new_task_updates']+1
summary['new_task_wall_seconds']=sum(r['seconds'] for r in summary['budget']['runs'])
summary['recommended_for_further_development']='stage2/final.pt';summary['deployment_ready']=False
(OUT/'comparison.json').write_text(json.dumps(summary,indent=2))
print(json.dumps(summary,indent=2))
