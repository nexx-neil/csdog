#!/usr/bin/env python3
"""Explicit bounded migration and paired fixed-controller quality verification."""
import argparse,copy,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--migrate',action='store_true');p.add_argument('--holdout',action='store_true');p.add_argument('--seed',type=int,default=42)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists():p.error('New output required')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_return import MotionTrotReturnEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_bounded import MotionTrotBoundedEnvCfg,MotionTrotBoundedEnv
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.contracts import contract_hash
from csdog_motion.trot_bounded import TAG,CAP,cases
from csdog_motion.trot_course import cases as previous_cases
from csdog_motion.adaptive_speed import fast_cases,fast_holdout_cases
from csdog_motion.trot_flight_policy import compose,record
from csdog_motion.diagnostic_evaluation import evaluate
from csdog_motion.evaluation import regression_gate
ROOT=Path.cwd();PREVIOUS=ROOT/'outputs/motion_foundation/lesson20_candidate/candidate.pt'

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 tag=json.loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag']
 parent=MotionTrotBoundedEnvCfg() if tag==TAG else MotionTrotReturnEnvCfg();meta=validate_checkpoint(a.checkpoint,parent,policy_only=True)
 if tag!=TAG and not a.migrate:raise ValueError('Source controller differs; explicit --migrate required')
 cfg=MotionTrotBoundedEnvCfg();cfg.scene.num_envs=256;cfg.sim.device=a.device;cfg.seed=a.seed;cfg.episode_length_s=30.
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve());env=MotionTrotBoundedEnv(cfg)
 cp=a.checkpoint
 try:
  state=torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']
  if a.migrate:
   cp=a.output/'candidate.pt';torch.save({'model_state_dict':state,'iter':0},cp)
   mapped=copy.deepcopy(meta);mapped.update(checkpoint_sha256=file_hash(cp),checkpoint_compatibility_tag=TAG,motion_contract=cfg.motion_contract,motion_contract_sha256=contract_hash(cfg.motion_contract),motion_commands=cfg.motion_commands,updates_in_this_run=0,initialization_only=True,parent_checkpoint=str(a.checkpoint.resolve()),parent_sha256=file_hash(a.checkpoint),source_learning_updates_in_trial=meta['updates_in_this_run'],resume_semantics='Explicit policy-only v45 to bounded v47; neural tensors equal, optimizer discarded; selected source learning recorded separately')
   mapped['runtime_source_files_sha256']={str(f.relative_to(ROOT)):file_hash(f)for folder in ['source','scripts']for f in (ROOT/folder).rglob('*.py')}
   Path(str(cp)+'.metadata.json').write_text(json.dumps(mapped,indent=2)+'\n')
  with torch.inference_mode():obs,_=env.reset()
  def actor(weights):
   model=ActorCritic(TensorDict(obs,batch_size=[256]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device);model.load_state_dict(weights);model.eval();return model
  policy=actor(state);assert all(torch.equal(v,state[k])for k,v in policy.state_dict().items());selected=compose(policy,PREVIOUS)
  old_state=torch.load(PREVIOUS,map_location=a.device,weights_only=True)['model_state_dict'];baseline=compose(actor(old_state),PREVIOUS)
  suite=fast_holdout_cases() if a.holdout else fast_cases()
  for c in previous_cases(a.holdout):
   if c['name']!='stand':suite.append(dict(c,name='previous_'+c['name']))
  suite+=cases(a.holdout)
  base=evaluate(env,baseline,PREVIOUS,a.output/'baseline.json',cases=suite,seed=a.seed,protocol_name='bounded_flat_trot',task='Bounded-v47')
  result=evaluate(env,selected,cp,a.output/'evaluation.json',cases=suite,seed=a.seed,protocol_name='bounded_flat_trot',task='Bounded-v47')
  comparison=regression_gate(result,base);rule=json.loads((ROOT/'analysis/motion_foundation_20261112/lesson27/return_selection_rule.json').read_text())['required'];bmap={c['name']:c for c in base['cases']};quality=[];reasons=[];old_delta=0.
  for c in result['cases']:
   b=bmap[c['name']]
   if c['name'].startswith('bounded_forward_') and c['profile'][0][1][0]>.8+1e-6:
    foot=sum(c['foot_reference_tracking_rms_m'])/4;oldfoot=sum(b['foot_reference_tracking_rms_m'])/4
    checks=dict(foot_ratio=foot<=oldfoot*rule['max_foot_rms_ratio_vs_initial'],foot_absolute=foot<=rule['mean_foot_reference_rms_max_m'],slide_increment=c['contact_slide_speed_proxy_mps']<=b['contact_slide_speed_proxy_mps']+rule['max_contact_slide_increase_vs_initial_mps'],slide_absolute=c['contact_slide_speed_proxy_mps']<=rule['contact_slide_proxy_max_mps'],tilt=c['body_tilt_rms_deg']<=b['body_tilt_rms_deg']+rule['max_tilt_rms_increase_vs_initial_deg'],yaw=abs(c['mean_actual_twist'][2])<=rule['max_abs_mean_yaw_rad_s'],lateral=abs(c['mean_actual_twist'][1])<=rule['max_abs_mean_lateral_mps'],timing=c['contact_schedule_agreement']>=rule['contact_schedule_agreement_min'],swing=sum(c['planned_swing_contact_fraction'])/4<=rule['mean_planned_swing_contact_max'])
    why=[k for k,v in checks.items()if not v];reasons += [c['name']+':'+w for w in why];quality.append(dict(name=c['name'],vx=c['mean_actual_twist'][0],foot_rms_m=foot,slide_mps=c['contact_slide_speed_proxy_mps'],contact_schedule=c['contact_schedule_agreement'],reasons=why))
   elif not c['name'].startswith('bounded_'):
    for metric in ['mean_actual_twist','steady_rmse','foot_reference_tracking_rms_m','contact_slide_speed_proxy_mps','body_tilt_rms_deg']:
     v,z=c[metric],b[metric];old_delta=max(old_delta,max(abs(x-y) for x,y in zip(v if isinstance(v,list)else[v],z if isinstance(z,list)else[z])))
  endpoint=next(c for c in result['cases']if c['name']=='bounded_forward_0.9500');origin=bmap[endpoint['name']]
  if endpoint['mean_actual_twist'][0]<.88:reasons.append('endpoint_speed_floor')
  if endpoint['mean_actual_twist'][0]<origin['mean_actual_twist'][0]+.01:reasons.append('endpoint_learned_gain')
  if old_delta>1e-6:reasons.append('frozen_old_domain_metrics_changed')
  if comparison['status']!='PASS':reasons.append('original_regression')
  if result['development_safety_gate']['status']!='PASS' or base['development_safety_gate']['status']!='PASS':reasons.append('safety')
  summary=dict(complete=True,gate='FAIL'if reasons else'PASS',reasons=reasons,paired_regression=comparison,static_quality=quality,old_domain_max_metric_delta=old_delta,endpoint=endpoint,seed=a.seed,holdout=a.holdout,cap_mps=CAP,checkpoint=str(cp.resolve()),checkpoint_sha256=file_hash(cp),motion_contract=cfg.motion_contract,source=str(a.checkpoint.resolve()),source_sha256=file_hash(a.checkpoint),policy_tensors_equal_to_source=True,selected_new_optimizer_updates=0,source_learning_updates_in_trial=meta.get('source_learning_updates_in_trial',meta['updates_in_this_run']),routing=record(PREVIOUS),script_sha256=file_hash(__file__),scope='nominal flat simulation; paired identical controller baseline; no rough/terrain or jump claim')
  (a.output/'assessment.json').write_text(json.dumps(summary,indent=2)+'\n');print('BOUNDED',summary['gate'],reasons,flush=True)
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
