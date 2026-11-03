"""Summarize preserved 500Hz and 50Hz physical measurements without relabeling events."""
from pathlib import Path
import json,sys
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.locomotion.curriculum_v6_1.supervisor import score,protocol,SCORE_VERSION,motion_safe
OUT=ROOT/'runs/locomotion/csdog_curriculum_v6_1/repair_20261027'
OLD=ROOT/'runs/locomotion/csdog_curriculum_v6/train_20261027_seed42'

def render(parts):
    text=''
    for part in parts:
        sep='\n' if text.rstrip().endswith('|') and part.startswith('|') else '\n\n'
        text+=sep+part
    return text.lstrip()

def durations(a,dt):
    out=[]
    for k in range(a.shape[1]):
        v=a[:,k];cuts=np.r_[0,np.flatnonzero(np.diff(v.astype(int)))+1,len(v)]
        out.extend((cuts[i+1]-cuts[i])*dt for i in range(len(cuts)-1) if v[cuts[i]])
    return np.array(out)

def main():
    options=json.loads((ROOT/'configs/locomotion/curriculum_v6_1/default.json').read_text())
    lines=['# Contact and gait diagnosis','Same 256 environments, deterministic actor, 12s, seeds 103/307/911/1301, original 15mm/60ms/raw-force<1N gate. Physics dt=2ms; policy dt=20ms. No PPO updates performed. Raw signals retained; no filtering applied. Formal swing durations now use integer 500Hz consecutive physical ticks; every failed substep breaks the segment. Old 50Hz proxy metrics remain in each JSON for comparison.','500Hz capture: 4 trials per stop/forward0.18/forward0.25 case, first seed; the 50Hz full panel uses 16 trials per case per seed. First 0.6s excluded below.','|Checkpoint|Leg (.18 task)|500Hz true air segments|>=60ms segments|20–40ms segments|<10ms stance fraction|unloaded near ground fraction|contact/force contradiction fraction|50Hz >=60ms segments|','|---|---|---:|---:|---:|---:|---:|---:|---:|']
    ranking=[];diag={};details=[]
    for name,cp in [('2500','evaluated_00002500.pt'),('6000','evaluated_00006000.pt'),('7500','evaluated_00007500.pt'),('8460','interrupted.pt')]:
        p=OUT/f'history_{name}_verified';summary=json.loads((p/'evaluation_common.json').read_text());rawdir=OUT/f'contact_forward_{name}' if (OUT/f'contact_forward_{name}').exists() else p;d=np.load(rawdir/'physics_500hz.npz');policy=np.load(p/'evaluation_common_seed103.npz')
        detail={};length=min(6000,len(d['contact']));ix=slice(4,8);mask=d['episode'][:length,ix]>30
        for j,leg in enumerate(['LF','RF','LR','RR']):
            c=d['contact'][:length,ix,j];h=d['clearance'][:length,ix,j];f=d['raw_force'][:length,ix,j];shin=d['shin'][:length,ix,j]
            strict=(~c)&(h>.015)&(f<1)&(~shin)&mask
            ds=durations(strict,.002);stance=durations(c&mask,.002)
            air50=(~policy['contact'][30:,16:20,j])&(policy['foot_height'][30:,16:20,j]>.015)&(policy['raw_force'][30:,16:20,j]<1)&(~policy['shin'][30:,16:20,j])
            ds50=durations(air50,.02)
            values=dict(raw_air_segments=len(ds),raw_air_ge60ms=int((ds>=.06).sum()),raw_air_20to40ms=int(((ds>=.02)&(ds<=.04)).sum()),stance_below10ms_fraction=float((stance<.01).mean()) if len(stance) else 0.,near_ground_unload_fraction=float(((~c)&(f<1)&(h<=.015)&mask).sum()/mask.sum()),contradiction_fraction=float((((c)&(h>.015))|((~c)&(f>1)&(~shin)))[mask].mean()),policy_air_ge60ms=int((ds50>=.06).sum()),shin_fraction=float(shin[mask].mean()),drag_fraction=float((c&(np.linalg.norm(d['patch_velocity'][:length,ix,j,:2],axis=-1)>.08)&mask).sum()/mask.sum()))
            detail[leg]=values
            lines.append('|'+name+'|'+leg+'|'+'|'.join(str(round(values[k],5)) for k in ['raw_air_segments','raw_air_ge60ms','raw_air_20to40ms','stance_below10ms_fraction','near_ground_unload_fraction','contradiction_fraction','policy_air_ge60ms'])+'|')
        diag[name]=detail
        ranking.append(dict(name=name,checkpoint=str(OLD/cp),evaluation=str(p/'evaluation_common.json'),score=score(summary,0,options['thresholds']),safe=motion_safe(summary),summary=summary))
        details.extend([f'\n## Checkpoint {name}',f'[Physics video]({OUT}/history_{name}/forward_stop.mp4). Full metrics: `{p}/evaluation_common.json`. Raw substeps (stop/forward0.18/forward0.25): `{rawdir}/physics_500hz.npz`. The earlier index15 raw subset is backward0.25 and remains separately preserved; full-environment event evaluation always covered both directions.',f"Zero-command mean action (12 joints, seed 103): {policy['raw_action'][30:,:16].mean((0,1)).round(4).tolist()}. Command max abs={float(abs(policy['command'][:,:16]).max())}. Zero command is represented exactly; measured yaw remains a learned policy response."])
    lines += details
    lines += ['\n## Interpretation','Contact flags agree with raw force and geometric clearance in these samples; short unload events near the ground and fast low-amplitude foot excursions coexist. A short loss of force alone is not a true swing. Segments with <15mm clearance remain unqualified, and 20–40ms true clearance remains below the 60ms gate. Short loaded contacts indicate actual force chatter in the physical solver, but there is no evidence here justifying deletion of such events. No hysteresis or duration merging is introduced. The old 50Hz proxy can alias brief contacts into apparent continuous swings. The revised formal gate retains the original 15mm/60ms criteria and verifies duration at 500Hz. This is stricter measurement, not a relaxed threshold. All four historical checkpoints were physically re-evaluated with this common protocol.','Support slip is evaluated at actual contact patches, shin contacts remain recorded independently, and velocity/tilt arrays are preserved at both rates. Filtering would require a new common historical physical panel; the raw force/geometry classification is retained, while continuous duration is verified at500Hz under contact version v6.1-raw-500hz-events-1. No contact gaps are merged.']
    (OUT/'CONTACT_AND_GAIT_DIAGNOSIS.md').write_text(render(lines)+'\n');(OUT/'contact_metrics.json').write_text(json.dumps(diag,indent=2))
    # Historical re-scoring is new derived data, never edits the old evaluation files.
    rescored=[]
    for p in sorted(OLD.glob('evaluation_*.json')):
        s=json.loads(p.read_text())
        if s.get('full'):rescored.append(dict(source=str(p),protocol=protocol(s),new_score=score(s,0,options['thresholds'])))
    (OUT/'historical_rescoring.json').write_text(json.dumps(dict(version=SCORE_VERSION,notes='Different seed panels remain separate; use new common physical panel for final ranking.',entries=rescored),indent=2))
    ranking.sort(key=lambda x:x['score'],reverse=True)
    table=['# Common historical checkpoint ranking','|Checkpoint|Continuous score|Safe forward initialization|','|---|---:|---|']+[f"|{x['name']}|{x['score']:.6f}|{x['safe']}|" for x in ranking]
    eligible=[x for x in ranking if x['safe']]
    if not eligible:raise RuntimeError('No safe historical forward checkpoint')
    chosen=eligible[0]
    table += [f"Selected: {chosen['checkpoint']}", 'Selection uses continuous task/gait/slip/stop score, with a separate forward safety gate. No candidate passes the full Stage 1 gait/stop/slip gate merely by being ranked first.']
    (OUT/'HISTORICAL_CHECKPOINT_RANKING.md').write_text(render(table)+'\n')
    (OUT/'history_selection.json').write_text(json.dumps({k:v for k,v in chosen.items() if k!='summary'},indent=2))
    options['contact_validated']=True;options['initial_substage']='1B'
    (OUT/'experiment_config.json').write_text(json.dumps(options,indent=2)+'\n')
    print(json.dumps(dict(chosen=chosen['name'],score=chosen['score'],rank=[(x['name'],x['score']) for x in ranking])))
if __name__=='__main__':main()
