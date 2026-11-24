#!/usr/bin/env python3
"""Fixed48-case terrain holdout, including both signs of post-advance turn."""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint',type=Path,required=True)
p.add_argument('--output',type=Path,required=True)
p.add_argument('--profile',choices=('foundation','step225'),default='foundation')
p.add_argument('--seed',type=int,default=1091)
p.add_argument('--row',type=int,default=2)
p.add_argument('--num-envs',type=int,default=144)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.output.exists() or a.num_envs<=0 or a.num_envs%48 or not 0<=a.row<3:
 p.error('New output, positive multiple48 environments and row0..3 required')
app=AppLauncher(a)
import torch,numpy as np
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.terrain_library import build_library_cfg,WALKING_KINDS,scenario
from csdog_motion.terrain_library_matrix_evaluation import KINDS
from isaaclab.terrains import TerrainGenerator
import hashlib
from csdog_motion.terrain_library_matrix_dense import evaluate
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_liftoff_handover import MotionLiftOffEnvCfg as MotionScannedRoughEnvCfg,MotionLiftOffEnv as MotionScannedRoughEnv

class RecordedGenerator(TerrainGenerator):
 def __init__(self,*args,**kwargs):
  super().__init__(*args,**kwargs);m=self.terrain_mesh;type(self).mesh_arrays_sha256=hashlib.sha256(m.vertices.tobytes()+m.faces.tobytes()).hexdigest()
class LibraryMatrixEnv(MotionScannedRoughEnv):
 def _setup_scene(self):
  super()._setup_scene();columns=torch.tensor([WALKING_KINDS.index(KINDS[i%8])for i in range(self.num_envs)],device=self.device);self.terrain_columns[:]=columns;self._terrain.env_origins[:]=self._terrain.terrain_origins[self.cfg.terrain_row,columns]

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed)
 cfg=MotionScannedRoughEnvCfg();meta=validate_checkpoint(a.checkpoint,cfg,policy_only=True)
 assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 a.output.mkdir(parents=True);cfg.scene.num_envs=a.num_envs;cfg.sim.device=a.device
 cfg.seed=a.seed;cfg.terrain.terrain_generator=build_library_cfg('bridge','walking',a.seed);cfg.terrain.terrain_generator.class_type=RecordedGenerator;cfg.terrain_row=a.row
 cfg.periodic_commands=False;cfg.episode_length_s=18.;cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve())
 env=LibraryMatrixEnv(cfg)
 from csdog_motion.workspace_diagnosis import install,save as save_workspace
 from csdog_motion.terrain_query_diagnosis import install as install_queries,save as save_queries
 install(env);install_queries(env)
 try:
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[a.num_envs]),{'policy':['policy'],'critic':['policy']},12,
      actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(a.device)
  policy.load_state_dict(torch.load(a.checkpoint,map_location=a.device,weights_only=True)['model_state_dict']);policy.eval()
  original_step=env.step;audit={'max_extra_yaw_moment_nm':0.,'peak_actual_torque_nm':0.}
  def audited_step(actions):
   result=original_step(actions)
   audit['max_extra_yaw_moment_nm']=max(audit['max_extra_yaw_moment_nm'],float(env.yaw_control.moment.abs().max()))
   audit['peak_actual_torque_nm']=max(audit['peak_actual_torque_nm'],float(env._robot.data.applied_torque[:,env._actuated_joint_ids].abs().max()))
   if audit['max_extra_yaw_moment_nm']>.600001:raise RuntimeError('Yaw integral cap violated')
   return result
  env.step=audited_step
  result=evaluate(env,policy,a.checkpoint,a.output/'evaluation.json',profile=a.profile)
  audit['adjusted_surplus_foot_reference_plans']=getattr(env,'clearance_adjusted_foot_steps',0)
  audit['workspace_height']={'max_offset_m':env.height_peak_offset,'max_velocity_mps':env.height_peak_velocity,'max_acceleration_mps2':env.height_peak_acceleration,'no_common_preview_env_plans':env.height_preview_no_common_plan,'height_adjustment_env_steps':env.height_adjustment_env_steps,'liftoff_handover_events':env.handover.events,'liftoff_peak_offset_m':env.handover.peak_offset_m,'stance_endpoint_preview_plans':getattr(env,'stance_endpoint_preview_plans',0),'stance_projection_leg_steps':getattr(env,'stance_projection_leg_steps',0),'stance_projection_peak_shift_m':getattr(env,'stance_projection_peak_shift_m',0.),'stance_projection_peak_fraction':getattr(env,'stance_projection_peak_fraction',0.),'patch_env_leg_steps':env.patch_env_leg_steps,'patch_peak_count':env.patch_peak_count,'patch_force_disagreement_n':env.patch_force_disagreement_n,'swing_workspace_leg_steps':env.swing_workspace_leg_steps,'swing_min_clearance_surplus_m':env.swing_min_clearance_surplus_m if env.swing_workspace_leg_steps else None}
  assert env.height_peak_offset<=.030001 and env.height_peak_velocity<=.120001 and env.height_peak_acceleration<=.80001
  audit['contact_datum']={'max_world_speed_mps':env.datum_peak_velocity,'max_world_acceleration_mps2':env.datum_peak_acceleration,'max_root_datum_difference_m':env.datum_peak_root_difference}
  result['scenario']=scenario('bridge','walking',a.seed,a.row);result['terrain_mesh_arrays_sha256']=RecordedGenerator.mesh_arrays_sha256;result['protocol']='library_8kinds_x6directions_x3_nominal_clones';result['script_sha256']=file_hash(__file__)
  result['controller_audit']=audit
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
 except BaseException as exc:
  save_workspace(env,a.output/'workspace_failure.json',exc);save_queries(env,a.output/'terrain_queries.json')
  diagnosis=json.loads((a.output/'workspace_failure.json').read_text());diagnosis['environment_direction_index']='kind=KINDS[environment%8];direction=DIRECTIONS[(environment//8)%6];clone=environment//48';diagnosis['terrain_mesh_arrays_sha256']=RecordedGenerator.mesh_arrays_sha256;diagnosis['actual_reference_error_m']=env.reference_error.cpu().tolist();diagnosis['actual_reference_stance']=env.reference_stance.cpu().tolist();diagnosis['contact_datum_at_failure']={'value':env.contact_datum.value.cpu().tolist(),'goal':env.contact_datum.goal.cpu().tolist(),'velocity':env.contact_datum.velocity.cpu().tolist(),'root_ground':env._surfaces()[:,0].cpu().tolist()};diagnosis['patch_at_failure']={'active':env.patch.active.cpu().tolist(),'height':env.patch.height.cpu().tolist(),'xy':env.patch.xy.cpu().tolist(),'xyz':env.patch.xyz.cpu().tolist()};diagnosis['height_state_at_failure']={'value':env.height_coordinator.value.cpu().tolist(),'goal':env.height_coordinator.goal.cpu().tolist(),'velocity':env.height_coordinator.velocity.cpu().tolist()};(a.output/'workspace_failure.json').write_text(json.dumps(diagnosis,indent=2)+'\n')
  rejected=isinstance(exc,RuntimeError)and any(x in str(exc)for x in ['Reference IK failed','Base foot reference is infeasible','Terrain query missed','cap exceeded'])
  result={'complete':False,'gate':'FAIL','status':'REFERENCE_OR_SIMULATION_REJECTED'if rejected else'HARNESS_ERROR','exception':repr(exc),'last_control_counter':env.common_step_counter,'terrain_mesh_arrays_sha256':RecordedGenerator.mesh_arrays_sha256,'checkpoint_sha256':file_hash(a.checkpoint),'script_sha256':file_hash(__file__)}
  from csdog_motion.adaptive_speed import adaptive_reference
  from isaaclab.utils.math import quat_apply,quat_apply_inverse
  base,planned=adaptive_reference(env.motion.phase,env.motion.applied[:,:3],env.reference_nominal,env.reference_config,env.motion.blend)
  r=env._robot.data;n=env.num_envs;quat=r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
  world=quat_apply(quat,base.reshape(-1,3)).reshape(n,4,3)+r.root_pos_w[:,None];ground=env._rays(world)
  points=torch.stack([x.data.contact_pos_w[:,0,0]for x in env._patch_sensors],1);forces=torch.stack([x.data.force_matrix_w[:,0,0]for x in env._patch_sensors],1)
  finite=torch.isfinite(points).all(2)&torch.isfinite(forces).all(2)
  from csdog_motion.contact_patch import measured_patch
  equivalent,edge=measured_patch(points,forces,env._surfaces()[:,1:],env.patch.cfg)
  audit={'purpose':'passive failure replay;no controller change;old datum/height inferred by subtracting actual integrated velocity*dt at this non-reset tick','counter':env.common_step_counter,'phase':env.motion.phase.cpu().tolist(),'planned_stance':planned.cpu().tolist(),'patch_active':env.patch.active.cpu().tolist(),'point_finite':finite.cpu().tolist(),'point_nan_encoded_zero':torch.nan_to_num(points).cpu().tolist(),'normal_force_world':forces.cpu().tolist(),'sensor_agreement_peak_n':float((forces-env._contact_sensor.data.net_forces_w[:,env._foot_ids]).norm(dim=-1).max()),'equivalent_height':equivalent.cpu().tolist(),'edge_gate':edge.cpu().tolist(),'current_offset':env.height_coordinator.value.cpu().tolist(),'current_datum':env.contact_datum.value.cpu().tolist(),'recomputed_predicates':{}}
  for name,datum,height in [('before_filter_updates',env.contact_datum.value-env.step_dt*env.contact_datum.velocity,env.height_coordinator.value-env.step_dt*env.height_coordinator.velocity),('after_filter_updates',env.contact_datum.value,env.height_coordinator.value)]:
   delta=torch.zeros_like(base);delta[:,:,2]=ground-datum[:,None]-height[:,None]
   q,e=env.reference_model.solve(base+quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(n,4,3),iterations=18)
   margin=torch.minimum(q-env.reference_model.lower,env.reference_model.upper-q).amin(2)
   unsafe=(e>.00005)|(margin<env.patch.cfg.minimum_ray_joint_margin_rad)
   loaded=finite&(forces[:,:,2]>env.patch.cfg.minimum_vertical_force_n)
   enter=planned&loaded&((edge&unsafe)|(e>.00005))
   audit['recomputed_predicates'][name]={'error':e.cpu().tolist(),'margin':margin.cpu().tolist(),'loaded':loaded.cpu().tolist(),'would_enter':enter.cpu().tolist()}
  (a.output/'contact_activation_at_failure.json').write_text(json.dumps(audit,indent=2)+'\n')
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');raise
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
