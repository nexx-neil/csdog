"""Generate traceable A/B tables and curves from actual local experiments."""
from pathlib import Path
import json,sys,csv
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.locomotion.curriculum_v6_1.supervisor import score,motion_safe,protocol,assess,SCORE_VERSION
OUT=ROOT/'runs/locomotion/csdog_curriculum_v6_1/repair_20261027';RUNS=OUT.parent

def render(parts):
    text=''
    for part in parts:
        sep='\n' if text.rstrip().endswith('|') and part.startswith('|') else '\n\n'
        text+=sep+part
    return text.lstrip()

def metrics(s):
    f=[r for r in s['rows'] if r['test']=='forward'];z=[r for r in s['rows'] if r['test']=='stop']
    return dict(vx=np.mean([r['velocity'][0] for r in f]).item(),slip=np.mean([r['support_slip_speed'] for r in f]).item(),periodic_legs=min(r['periodic_legs'] for r in f),gait_fraction=np.mean([r['gait_trial_fraction'] for r in f]).item(),stop_speed=np.mean([r['speed_xy'] for r in z]).item(),stop_yaw=np.mean([r.get('yaw_abs',abs(r['yaw'])) for r in z]).item(),fall_rate=max(r['fall_rate'] for r in f+z))

def main():
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import torch
    chosen=json.loads((OUT/'history_selection.json').read_text());config=json.loads((OUT/'experiment_config.json').read_text());t=config['thresholds']
    data={};endpoints={};baseline=None;lines=['# V6.1 A/B comparison','Both arms: identical complete source learner (actor/critic/optimizer/std/RNG), 256 environments, seed 42, 24 steps/update, 500 PPO updates = 3,072,000 environment samples per arm. No automatic repairs or rollbacks inside either fixed-budget arm. Fixed 12s full panel: seeds 103/307/911/1301; lightweight 6s seed103 at update250 is kept separate. Formal capability thresholds remain unchanged.',f"Source checkpoint: `{chosen['checkpoint']}`.",'|Arm|Forward vx m/s|Support slip m/s|Minimum periodic legs|Gait trial fraction|Stop norm m/s|Stop abs yaw rad/s|Worst fall rate|Continuous score|Safe relative to initialization|','|---|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    summaries={};safe={};details=[]
    for arm,name in [('A','ab_A_verified_20261027'),('B','ab_B_verified_20261027')]:
        p=RUNS/name;state=json.loads((p/'TRAINING_STATUS.json').read_text())
        if state['training_status']!='EXPERIMENT_COMPLETE':raise RuntimeError('A/B incomplete')
        d=[json.loads(x) for x in (p/'metrics.jsonl').read_text().splitlines()];data[arm]=d
        init=json.loads(next(p.glob('evaluation_baseline_*.json')).read_text())
        full=json.loads(next(p.glob('evaluation_*_full.json')).read_text());summaries[arm]=full
        if protocol(init)!=protocol(full):raise RuntimeError('Initialization/end panel mismatch')
        if baseline is None:baseline=init
        for key in ['vx','slip','stop_speed','stop_yaw']:
            if abs(metrics(init)[key]-metrics(baseline)[key])>.02:raise RuntimeError('A/B baseline physical discrepancy exceeds tolerance: '+key)
        hashes=json.loads((p/'initialization.json').read_text())
        a=torch.load(p/'initial.pt',map_location='cpu',weights_only=False)
        b=torch.load(chosen['checkpoint'],map_location='cpu',weights_only=False)
        def equal(x,y):
            if torch.is_tensor(x):return torch.equal(x,y)
            if isinstance(x,dict):return x.keys()==y.keys() and all(equal(x[k],y[k]) for k in x)
            if isinstance(x,(list,tuple)):return len(x)==len(y) and all(equal(v,w) for v,w in zip(x,y))
            return x==y
        if not equal(a['model_state_dict'],b['model_state_dict']) or not equal(a['optimizer_state_dict'],b['optimizer_state_dict']):raise RuntimeError('A/B initial learner mismatch')
        if len(d)!=500:raise RuntimeError('Unequal PPO budget')
        m=metrics(full);endpoints[arm]=m;safe[arm]=motion_safe(full,baseline)
        lines.append('|'+arm+'|'+'|'.join(str(round(m[k],6)) for k in m)+f"|{score(full,0,t):.6f}|{safe[arm]}|")
        details += [f"\n{arm} active training configuration: `{p}/ACTIVE_TRAINING_CONFIG.json`. Final summary: `{next(p.glob('evaluation_*_full.json'))}`. Initialization SHA256: `{hashes['initial_network_sha256']}`."]
    lines += details
    a_sources=json.loads((RUNS/'ab_A_verified_20261027/source_sha256.json').read_text());b_sources=json.loads((RUNS/'ab_B_verified_20261027/source_sha256.json').read_text())
    source_differences=[key for key in a_sources if a_sources[key]!=b_sources.get(key)]
    if any(not key.endswith('/curriculum_v6_1/rewards.py') for key in source_differences):raise RuntimeError('Unexpected shared implementation change between arms: '+str(source_differences))
    lines += ['B-only source revision: completed landing reward additionally requires >2cm placement in the commanded translation/tangential direction, rejecting vertical-only lifting. A always uses the unchanged V6 reward module. Revision source and hashes are preserved in B_only_reward_revision.json and rewards_before_excursion_gate.py; no shared policy, physics, evaluation or PPO logic changed between arms.']
    for arm in ['A','B']:
        gate_path=RUNS/('ab_'+arm+'_verified_20261027')/'CONTINUATION_GATE.json'
        gate_path.write_text(json.dumps(dict(allowed=safe[arm],reason='full 500Hz panel compared with initialization',reference_checkpoint=chosen['checkpoint']),indent=2))
    baseline_metrics=metrics(baseline)
    lines += ['\nInitial full-panel metrics: `'+json.dumps(baseline_metrics)+'`.','A retains V6 rewards and command sampling. B uses translation-conditioned continuous swing guidance (0.30), V6.1 internal courses, and only after the baseline full panel confirms four-leg periodic gait at 500Hz (otherwise Stage1B retains original slip/smoothness/stop sampling): slip weight -0.225, smoothness -0.00375, stop sampling 25% versus A 15%. Original directional progress 4.0, tracking 2.0, completed swing 0.15, stop reward 2.0, PPO and physical properties remain unchanged. Final active configuration reflects any declared internal course transition after endpoint evaluation.','Scoring changes affect both arms equally at evaluation; the B reward and sampling differences change training behavior. Both arms use the same new 500Hz verified evaluation. A retains original 50Hz reward events; B uses verified 500Hz landing rewards and continuous swing guidance. The 15mm/60ms thresholds are unchanged.']
    a_score=score(summaries['A'],0,t);b_score=score(summaries['B'],0,t)
    selected='B' if safe['B'] and (not safe['A'] or b_score>a_score+.02) else 'A' if safe['A'] else None
    decision=dict(selected_arm=selected,safe=safe,scores=dict(A=a_score,B=b_score),initial_metrics=baseline_metrics,final_metrics=endpoints,source_checkpoint=chosen['checkpoint'])
    if selected:
        p=RUNS/('ab_'+selected+'_verified_20261027');state=json.loads((p/'TRAINING_STATUS.json').read_text())
        # Retain a verified better initialization when the endpoint is slightly worse.
        checkpoint=p/'final.pt'
        if score(baseline,0,t)>score(summaries[selected],0,t):checkpoint=p/'initial.pt'
        decision.update(checkpoint=str(checkpoint),variant='improved' if selected=='B' else 'control',status='ELIGIBLE_FOR_LONG_TRAINING')
    else:decision.update(status='BLOCKED_BOTH_ARMS_REGRESSED',checkpoint=chosen['checkpoint'])
    lines += [f'\nDecision: `{json.dumps(decision)}`.','Passing the continuation safety gate does not imply Stage 1 formal acceptance. Forward/slip/gait/stop must still pass the unchanged full gate three times before Stage 2.','\n![Training curves](AB_TRAINING_CURVES.png)','\n![Common full-panel comparison](AB_CAPABILITY_COMPARISON.png)']
    (OUT/'ab_selection.json').write_text(json.dumps(decision,indent=2));(OUT/'V6_1_AB_COMPARISON.md').write_text(render(lines)+'\n')
    fig,axes=plt.subplots(2,2,figsize=(12,7))
    for ax,key,label in zip(axes.flat,['reward_step','linear_error','physics_slip','physics_air_fraction'],['Training reward / control step','Training linear error (m/s)','Training support slip at 500Hz (m/s)','Training raw air duty at 500Hz']):
        for arm,d in data.items():
            values=np.array([r[key] for r in d]);smooth=np.convolve(values,np.ones(25)/25,mode='valid');ax.plot(np.arange(25,501),smooth,label=arm)
        ax.set(xlabel='PPO updates in arm',ylabel=label);ax.grid(alpha=.2);ax.legend()
    fig.tight_layout();fig.savefig(OUT/'AB_TRAINING_CURVES.png',dpi=150);plt.close(fig)
    keys=['vx','slip','periodic_legs','gait_fraction','stop_speed','stop_yaw','fall_rate'];fig,axes=plt.subplots(2,4,figsize=(15,7))
    for ax,key in zip(axes.flat,keys):
        ax.bar(['Initial','A500','B500'],[baseline_metrics[key],endpoints['A'][key],endpoints['B'][key]],color=['gray','steelblue','orange']);ax.set_title({'vx':'Forward speed (m/s)','slip':'Support slip (m/s)','periodic_legs':'Minimum periodic legs','gait_fraction':'Four-leg trial pass fraction','stop_speed':'Stop translation norm (m/s)','stop_yaw':'Stop absolute yaw (rad/s)','fall_rate':'Worst fall fraction'}[key]);ax.grid(axis='y',alpha=.2)
        limits={'periodic_legs':(0,4.3),'gait_fraction':(0,1.),'fall_rate':(0,.06)}
        if key in limits:ax.set_ylim(*limits[key])
        goals={'slip':.08,'periodic_legs':4,'gait_fraction':.8,'stop_speed':.03,'stop_yaw':.08,'fall_rate':.05}
        if key in goals:ax.axhline(goals[key],color='firebrick',linestyle='--',linewidth=1,label='Gate');ax.legend(fontsize=8)
    axes.flat[-1].axis('off');fig.tight_layout();fig.savefig(OUT/'AB_CAPABILITY_COMPARISON.png',dpi=150);plt.close(fig)
    with (OUT/'AB_CAPABILITY_COMPARISON.csv').open('w') as f:
        writer=csv.DictWriter(f,fieldnames=['arm',*keys]);writer.writeheader()
        for name,m in [('Initial',baseline_metrics),*endpoints.items()]:writer.writerow(dict(arm=name,**m))
    print(json.dumps(decision))
if __name__=='__main__':main()
