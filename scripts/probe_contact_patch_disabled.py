#!/usr/bin/env python3
"""Capability screening on an explicit external terrain scenario; never promote a model."""
import argparse,json,traceback,hashlib,time
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--migrate',action='store_true');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--kind',required=True);p.add_argument('--level',choices=('bridge','mixed','hard'),default='bridge');p.add_argument('--seed',type=int,default=12037);p.add_argument('--row',type=int,default=2);AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.row not in range(3):p.error('New output directory and row0..2 required')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from isaaclab.terrains import TerrainGenerator
from isaaclab.utils.math import quat_apply_inverse
from csdog_motion.terrain_library import build_library_cfg,scenario,WALKING_KINDS
from csdog_motion.training import validate_checkpoint,file_hash
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_contact_patch import MotionContactPatchEnvCfg as MotionTerrainTurnEnvCfg,MotionContactPatchEnv as MotionTerrainTurnEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_contact_tick_preview import MotionContactTickEnvCfg as MotionWorkspacePriorityEnvCfg
from csdog_motion.contact_patch import TAG
from csdog_motion.contracts import contract_hash

def write(d): (a.output/'assessment.json').write_text(json.dumps(d,indent=2)+'\n')

class RecordedGenerator(TerrainGenerator):
 records=[]
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);mesh=self.terrain_mesh
  type(self).mesh_arrays_sha256=hashlib.sha256(mesh.vertices.tobytes()+mesh.faces.tobytes()).hexdigest()
 def _get_terrain_mesh(self,difficulty,cfg):
  self._difficulty=float(difficulty);return super()._get_terrain_mesh(difficulty,cfg)
 def _add_sub_terrain(self,mesh,origin,row,col,cfg):
  type(self).records.append({'row':row,'column':col,'kind':list(self.cfg.sub_terrains)[col],'actual_difficulty':self._difficulty})
  return super()._add_sub_terrain(mesh,origin,row,col,cfg)

class SurveyEnv(MotionTerrainTurnEnv):
 def _setup_scene(self):
  super()._setup_scene();self.terrain_columns[:]=WALKING_KINDS.index(a.kind);self._terrain.env_origins[:]=self._terrain.terrain_origins[a.row,WALKING_KINDS.index(a.kind)]

def main():
 assert a.kind in WALKING_KINDS
 a.output.mkdir(parents=True);torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 cfg=MotionTerrainTurnEnvCfg()
 tag=json.loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag']
 parent=cfg if tag==TAG else MotionWorkspacePriorityEnvCfg()
 meta=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 if tag!=TAG and not a.migrate:raise ValueError('Explicit controller transfer requires --migrate')
 if a.migrate:
  source=a.checkpoint;state=torch.load(source,map_location=a.device,weights_only=True)['model_state_dict'];cp=a.output/'candidate.pt';torch.save({'model_state_dict':state,'iter':0},cp)
  mapped=dict(meta);mapped.update(checkpoint_sha256=file_hash(cp),checkpoint_compatibility_tag=TAG,motion_contract=cfg.motion_contract,motion_contract_sha256=contract_hash(cfg.motion_contract),motion_commands=cfg.motion_commands,initialization_only=True,updates_in_this_run=0,optimizer_lrs=[],algorithm_learning_rate=None,actual_lr_audit=None,optimizer_state_present=False,parent_checkpoint=str(source.resolve()),parent_sha256=file_hash(source),new_selected_ppo_updates=0,parent_learning_ancestry_updates=170,resume_semantics='Explicit same175 policy-only transfer to contact support datum; no optimizer or new learning')
  Path(str(cp)+'.metadata.json').write_text(json.dumps(mapped,indent=2)+'\n');a.checkpoint=cp
 external=scenario(a.level,'walking',a.seed,a.row)
 # Validate the frozen controller first, then record a separate, explicit scenario override.
 cfg.terrain.terrain_generator=build_library_cfg(a.level,'walking',a.seed);cfg.terrain.terrain_generator.class_type=RecordedGenerator;cfg.terrain_row=a.row;cfg.scene.num_envs=18;cfg.seed=a.seed;cfg.sim.device=a.device;cfg.periodic_commands=False;cfg.episode_length_s=18.;cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 result={'complete':False,'status':'RUNNING','scope':'DIAGNOSTIC ABLATION ONLY;v56 patch activation disabled, four point sensors retained; not a promotion candidate','scenario':external,'kind':a.kind,'checkpoint_sha256':file_hash(a.checkpoint),'controller_contract':cfg.motion_contract,'source_sha256':{'probe':file_hash(__file__),'terrain_library':file_hash(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab/csdog_motion/terrain_library.py')},'new_ppo_updates':0,'command_targets':[.2,.18,.3]};write(result)
 env=None;step=-1;trace=[]
 try:
  env=SurveyEnv(cfg)
  original_patch_update=env.patch.update
  def disabled_patch_update(tick,stance,points,forces,actual_rays,foot_positions,unsafe_ray,active_env):
   return original_patch_update(tick,stance,points,forces,actual_rays,foot_positions,torch.zeros_like(unsafe_ray),active_env)
  env.patch.update=disabled_patch_update
  result['diagnostic_controller_override']={'activation_disabled':True,'scope':'causal ablation only; same4 point sensors and v56 code; not compatible deployment behavior or promotion candidate'}
  result['generated_cells']=RecordedGenerator.records;result['terrain_mesh_prim_paths']=env._terrain.terrain_prim_paths;result['terrain_mesh_arrays_sha256']=RecordedGenerator.mesh_arrays_sha256
  from csdog_motion.workspace_diagnosis import install,save
  from csdog_motion.terrain_query_diagnosis import install as install_queries,save as save_queries
  install(env);install_queries(env)
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[18]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device);policy.load_state_dict(torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']);policy.eval()
  dirs=torch.arange(18,device=env.device)%6;fail=torch.zeros(18,device=env.device);finite=torch.ones(18,dtype=torch.bool,device=env.device);box=torch.zeros_like(fail);rate=box.clone();qpeak=box.clone();ik=box.clone();maxI=0.;maxTorque=0.;clockok=True;dense=[]
  with torch.inference_mode():
   for step in range(750):
    t=step*.02;cmd=torch.zeros(18,3,device=env.device)
    if 2<=t<12:cmd[dirs==0,0]=.2;cmd[dirs==1,0]=-.2;cmd[dirs==2,1]=.18;cmd[dirs==3,1]=-.18
    if 2<=t<10:cmd[dirs>=4,0]=.2
    if 10<=t<13:cmd[dirs==4,2]=.3;cmd[dirs==5,2]=-.3
    env.set_motion_request(cmd);obs,rew,term,trunc,_=env.step(policy.act_inference(TensorDict(obs,batch_size=[18])));r=env._robot.data
    fail+=term;finite &= torch.isfinite(obs['policy']).all(1)&torch.isfinite(rew);box+=env.target_box_limited.float().mean(1);rate+=env.target_speed_limited.float();qpeak=torch.maximum(qpeak,env._processed_velocity_targets.abs().amax(1));ik=torch.maximum(ik,env.reference_error.amax(1));maxI=max(maxI,float(env.yaw_control.moment.abs().max()));maxTorque=max(maxTorque,float(r.applied_torque[:,env._actuated_joint_ids].abs().max()))
    if maxI>.600001 or maxTorque>12.001:raise RuntimeError('Existing actuator/yaw cap exceeded')
    if env.datum_peak_velocity>.080001 or env.datum_peak_acceleration>.40001:raise RuntimeError('Contact datum cap exceeded')
    if env.height_peak_offset>.030001 or env.height_peak_velocity>.120001 or env.height_peak_acceleration>.80001:raise RuntimeError('Automatic height rate/acceleration cap exceeded')
    contact=torch.linalg.vector_norm(env._contact_sensor.data.net_forces_w[:,env._foot_ids],dim=-1)>1.;slide=(torch.linalg.vector_norm(r.body_lin_vel_w[:,env._robot_foot_ids,:2],dim=-1)*contact).sum(1)/contact.sum(1).clamp_min(1);dense.append(slide.cpu().tolist())
    if step%250==0:
     before=[env.patch.active.clone(),env.patch.height.clone(),env.patch.xy.clone(),env.contact_datum.value.clone(),env.contact_datum.velocity.clone(),env.motion.phase.clone(),env.motion.command_age.clone(),env.yaw_control.integral.clone(),env.height_coordinator.value.clone(),env.height_coordinator.velocity.clone(),env.height_coordinator.goal.clone()]
     for _ in range(3):env._get_observations()
     clockok &= all(torch.equal(x,y)for x,y in zip(before,[env.patch.active,env.patch.height,env.patch.xy,env.contact_datum.value,env.contact_datum.velocity,env.motion.phase,env.motion.command_age,env.yaw_control.integral,env.height_coordinator.value,env.height_coordinator.velocity,env.height_coordinator.goal]))
    if step%5==0:
     w,x,y,z=r.root_quat_w.unbind(-1);yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z));quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4);body=quat_apply_inverse(quat,(r.body_pos_w[:,env._robot_foot_ids]-r.root_pos_w[:,None]).reshape(-1,3)).reshape(-1,4,3);ref,_=env.reference_model.fk(env.reference_q.reshape(-1,4,3))
     trace.append({'seconds':(step+1)*.02,'datum':env.contact_datum.value.cpu().tolist(),'datum_velocity':env.contact_datum.velocity.cpu().tolist(),'root_ground':env._surfaces()[:,0].cpu().tolist(),'position':(r.root_pos_w-env._terrain.env_origins).cpu().tolist(),'height':env._support_height().cpu().tolist(),'tilt':(torch.acos((-r.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi).cpu().tolist(),'yaw':yaw.cpu().tolist(),'twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1).cpu().tolist(),'command':cmd.cpu().tolist(),'foot_error_sq':(body-ref).square().sum(2).mean(1).cpu().tolist()})
  ts=np.array([x['seconds']for x in trace]);pos=np.array([x['position']for x in trace]);height=np.array([x['height']for x in trace]);tilt=np.array([x['tilt']for x in trace]);yaw=np.unwrap(np.array([x['yaw']for x in trace]),axis=0);twist=np.array([x['twist']for x in trace]);cmds=np.array([x['command']for x in trace]);foot=np.array([x['foot_error_sq']for x in trace]);cases=[]
  for i,name in enumerate(['forward','backward','left','right','advance_then_turn','advance_then_turn_right']):
   ids=np.arange(i,18,6);axis=1 if i in (2,3)else 0;sgn=-1 if i in (1,3)else 1;progress=sgn*(pos[-1,ids,axis]-pos[0,ids,axis]);cross=float(abs(pos[:,ids,1-axis]-pos[0,ids,1-axis]).max());angle=float((yaw[ts>=12.9][0,ids]-yaw[ts>=10][0,ids]).mean());mask=(ts>=3)&(ts<(9 if i>=4 else 12));dt=(np.arange(750)+1)*.02;dm=(dt>=3)&(dt<(9 if i>=4 else 12))
   row={'direction':name,'progress_m':progress.tolist(),'cross_track_m':cross,'height_mean_m':float(height[:,ids].mean()),'height_min_m':float(height[:,ids].min()),'tilt_rms_deg':float(np.sqrt((tilt[:,ids]**2).mean())),'peak_tilt_deg':float(tilt[:,ids].max()),'turn_rad':angle,'steady_rmse':np.sqrt(((twist[mask][:,ids]-cmds[mask][:,ids])**2).mean((0,1))).tolist(),'foot_reference_rms_m':float(np.sqrt(foot[mask][:,ids].mean())),'contact_center_velocity_proxy_50hz_mps':float(np.array(dense)[dm][:,ids].mean()),'failures':int(fail[ids].sum()),'finite':bool(finite[ids].all()),'peak_target_qspeed_rad_s':float(qpeak[ids].max()),'max_ik_error_m':float(ik[ids].max()),'box_clip_fraction':float(box[ids].mean()/750),'rate_clip_fraction':float(rate[ids].mean()/750)}
   checks={'progress':bool((progress>[1.3,1.3,1.17,1.17,1.04,1.04][i]).all()),'cross_track':cross<.4,'height_mean':abs(row['height_mean_m']-cfg.base_height_target)<.04,'height_min':row['height_min_m']>.25,'tilt_rms':row['tilt_rms_deg']<10,'tilt_peak':row['peak_tilt_deg']<20,'q_speed':row['peak_target_qspeed_rad_s']<=8.0001,'ik':row['max_ik_error_m']<.001,'box_clip':row['box_clip_fraction']<.1,'rate_clip':row['rate_clip_fraction']<.2,'turn':i<4 or (angle if i==4 else -angle)>.6,'finite':row['finite'],'no_termination':not row['failures']};row['reasons']=[k for k,v in checks.items()if not v];row['functional_gate']='PASS'if not row['reasons']else'FAIL';cases.append(row)
  result.update(complete=True,status='SCREEN_COMPLETE',functional_gate='PASS'if clockok and all(x['functional_gate']=='PASS'for x in cases)else'FAIL',cases=cases,trace=trace,observation_clock_guard=clockok,controller_audit={'max_extra_yaw_nm':maxI,'peak_actual_torque_nm':maxTorque,'adjusted_surplus_plans':getattr(env,'clearance_adjusted_foot_steps',0)},physical_limits={'joint_target_offset_rad':.5,'joint_target_speed_rad_s':8.,'actuator_torque_nm':12.,'actuator_speed_rad_s':10.,'ik_error_m':.001});result['controller_audit']['workspace_height']={'max_offset_m':env.height_peak_offset,'max_velocity_mps':env.height_peak_velocity,'max_acceleration_mps2':env.height_peak_acceleration,'no_common_preview_env_plans':env.height_preview_no_common_plan,'height_adjustment_env_steps':env.height_adjustment_env_steps,'patch_env_leg_steps':env.patch_env_leg_steps,'patch_peak_count':env.patch_peak_count,'patch_force_disagreement_n':env.patch_force_disagreement_n};result['controller_audit']['contact_datum']={'max_world_speed_mps':env.datum_peak_velocity,'max_world_acceleration_mps2':env.datum_peak_acceleration,'max_root_datum_difference_m':env.datum_peak_root_difference};write(result)
 except BaseException as exc:
  if env is not None:save(env,a.output/'workspace_failure.json',exc);save_queries(env,a.output/'terrain_queries.json')
  if env is not None:result['contact_datum_at_failure']={'value':env.contact_datum.value.cpu().tolist(),'goal':env.contact_datum.goal.cpu().tolist(),'velocity':env.contact_datum.velocity.cpu().tolist(),'root_ground':env._surfaces()[:,0].cpu().tolist()}
  if env is not None:result['patch_at_failure']={'active':env.patch.active.cpu().tolist(),'height':env.patch.height.cpu().tolist(),'xy':env.patch.xy.cpu().tolist()}
  if env is not None:result['height_state_at_failure']={'value':env.height_coordinator.value.cpu().tolist(),'goal':env.height_coordinator.goal.cpu().tolist(),'velocity':env.height_coordinator.velocity.cpu().tolist(),'no_common_preview_env_plans':env.height_preview_no_common_plan}
  rejected=isinstance(exc,RuntimeError)and any(s in str(exc)for s in ['Reference IK failed','Base foot reference is infeasible','Terrain query missed','cap exceeded'])
  result.update(status='REFERENCE_OR_SIMULATION_REJECTED'if rejected else'HARNESS_ERROR',complete=False,functional_gate='FAIL',last_step=step,exception=repr(exc),completed_sample_frames=len(trace));write(result);raise
 finally:
  if env is not None:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
