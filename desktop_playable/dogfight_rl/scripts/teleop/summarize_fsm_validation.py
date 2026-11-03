#!/usr/bin/env python3
"""Read saved evidence; never replaces human inspection of the actual screenshots."""
import argparse,json,math,hashlib,sys
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from dogfight.teleop.config import load_settings
from dogfight.teleop.maps import create_selected_map
from dogfight.fsm.navigation import GridPlanner
p=argparse.ArgumentParser();p.add_argument('run');args=p.parse_args();run=Path(args.run)
metrics=json.loads((run/'metrics.json').read_text());acceptance=json.loads((run/'fsm_gui_acceptance.json').read_text())
events=[json.loads(x) for x in (run/'combat_events/events.jsonl').read_text().splitlines()]
trace=json.loads((run/'trace.json').read_text());cfg,_=load_settings('configs/teleop/fsm_battle.yaml');arena=create_selected_map(cfg)
planner=GridPlanner(arena,cfg['autonomy']['grid_resolution_m'],cfg['autonomy']['body_radius_m'])
plans=[e for e in events if e['event_type']=='PATH_PLAN'];bad_paths=[]
for e in plans:
 points=e['data']['points']
 if e['data']['valid'] and not all(planner.clear(a,b) for a,b in zip(points,points[1:])):bad_paths.append(e)
shots=[e for e in events if e['event_type']=='SHOT_FIRED'];bad_shots=[e for e in shots if e['data'].get('distance_m') is not None and not 0<=e['data']['distance_m']<=cfg['battle']['weapon_range_m']]
visuals=[r['route_visuals'] for r in trace if 'route_visuals' in r]
off=[v for v in visuals if not v['enabled']];over=[r['route_visuals'] for r in trace if r['match']['round_over'] and 'route_visuals' in r]
max_deltas={n:0. for n in cfg['participants']}
for a,b in zip(trace,trace[1:]):
 if b['match']['time_s']<a['match']['time_s'] or b['match']['time_s']<.3:continue
 for n in max_deltas:
  ap,bp=a['agents'][n]['pose'],b['agents'][n]['pose'];max_deltas[n]=max(max_deltas[n],math.hypot(ap['x']-bp['x'],ap['y']-bp['y']))
protected=json.loads((ROOT/'runs/validation/fsm_v1_20261103/protected_assets_after.json').read_text())
changed=[f for f,h in protected.items() if hashlib.sha256((ROOT/f).read_bytes()).hexdigest()!=h]
result=dict(run=str(run.resolve()),metrics=metrics,pause_frozen=acceptance.get('pause_frozen'),event_counts=Counter(e['event_type'] for e in events),
  intel_times=[e['timestamp_s'] for e in events if e['event_type']=='INTEL_UPDATE'],successful_plans=sum(e['data']['valid'] for e in plans),failed_plans=sum(not e['data']['valid'] for e in plans),
  invalid_body_clearance_paths=bad_paths,out_of_range_shots=bad_shots,
  all_three_ppo=all(v>0 for v in metrics['policy_steps'].values()),max_trace_step_displacement_m=max_deltas,
  visual_backend=visuals[0].get('backend') if visuals else None,maximum_debug_lines=max((v.get('line_count',0) for v in visuals),default=0),
  maximum_debug_points=max((v.get('point_count',0) for v in visuals),default=0),route_prim_counts=sorted(set(v['prim_count'] for v in visuals)),
  route_physics_schema_counts=sorted(set(v['physics_schemas'] for v in visuals)),off_clears_buffers=bool(off) and all(v.get('line_count')==v.get('point_count')==0 for v in off),
  over_clears_buffers=bool(over) and all(v.get('line_count')==v.get('point_count')==0 for v in over),
  reset_policy_zero=all(all(n==0 for n in e['data']['policy_steps'].values()) for e in events if e['event_type']=='AUTONOMY_RESET'),
  protected_assets_changed=changed,screenshots=acceptance['screenshots'])
(run/'validation_summary.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
assert metrics['match']['round_over'] and result['all_three_ppo'] and not bad_paths and not bad_shots and not changed
assert result['off_clears_buffers'] and result['over_clears_buffers'] and result['reset_policy_zero'] and result['pause_frozen']
