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
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_contact_lift_priority import MotionContactPriorityEnvCfg as MotionScannedRoughEnvCfg,MotionContactPriorityEnv as MotionScannedRoughEnv

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
  audit['workspace_height']={'max_offset_m':env.height_peak_offset,'max_velocity_mps':env.height_peak_velocity,'max_acceleration_mps2':env.height_peak_acceleration,'no_common_preview_env_plans':env.height_preview_no_common_plan,'height_adjustment_env_steps':env.height_adjustment_env_steps,'optional_preview_env_plans':getattr(env,'optional_preview_env_plans',0),'peak_full_preview_goal_m':getattr(env,'peak_full_preview_goal_m',0.),'basic_preview_no_common_plans':getattr(env,'basic_preview_no_common_plans',0)}
  assert env.height_peak_offset<=.030001 and env.height_peak_velocity<=.120001 and env.height_peak_acceleration<=.80001
  audit['contact_datum']={'max_world_speed_mps':env.datum_peak_velocity,'max_world_acceleration_mps2':env.datum_peak_acceleration,'max_root_datum_difference_m':env.datum_peak_root_difference}
  result['scenario']=scenario('bridge','walking',a.seed,a.row);result['terrain_mesh_arrays_sha256']=RecordedGenerator.mesh_arrays_sha256;result['protocol']='library_8kinds_x6directions_x3_nominal_clones';result['script_sha256']=file_hash(__file__)
  result['controller_audit']=audit
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n')
 except BaseException as exc:
  rejected=isinstance(exc,RuntimeError)and any(x in str(exc)for x in ['Reference IK failed','Base foot reference is infeasible','Terrain query missed','cap exceeded'])
  result={'complete':False,'gate':'FAIL','status':'REFERENCE_OR_SIMULATION_REJECTED'if rejected else'HARNESS_ERROR','exception':repr(exc),'last_control_counter':env.common_step_counter,'checkpoint_sha256':file_hash(a.checkpoint),'script_sha256':file_hash(__file__)}
  (a.output/'evaluation.json').write_text(json.dumps(result,indent=2)+'\n');raise
 finally:env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
