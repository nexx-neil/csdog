#!/usr/bin/env python3
"""Independent free-root tripod load-transfer and fold/recovery diagnostic.

No policy, optimization, root wrench, runtime root/joint teleport, or full lie/rise.
"""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--provenance',type=Path,required=True);p.add_argument('--plan',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--record',action='store_true');p.add_argument('--repeats',type=int,default=1)
AppLauncher.add_app_launcher_args(p);args=p.parse_args()
if args.output.exists():p.error('Refusing to overwrite evidence')
if not 1<=args.repeats<=3:p.error('repeats must be 1..3')
args.output.mkdir(parents=True);args.enable_cameras=args.record;launcher=AppLauncher(args)
import numpy as np,torch,subprocess
import isaaclab.sim as sim_utils
from isaaclab.sensors import ContactSensor,ContactSensorCfg
from isaaclab.utils import math as math_utils
from csdog_motion.training import file_hash
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics
from csdog_motion.support_feedback import support_forces
from csdog_motion.collision_cooking import normalize_mesh_colliders
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reference import MotionReferenceEnv,MotionReferenceEnvCfg,configure_reference

class TripodEnv(MotionReferenceEnv):
 def _setup_scene(self):
  super()._setup_scene()
  import omni.usd
  self.cooking_recipe=normalize_mesh_colliders(omni.usd.get_context().get_stage(),'/World/envs/env_0/Robot','fine')
  platform=sim_utils.CuboidCfg(size=(3.,3.,.10),rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True,disable_gravity=True),mass_props=sim_utils.MassPropertiesCfg(mass=100.),collision_props=sim_utils.CollisionPropertiesCfg(),visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.22,.25,.28)))
  platform.func('/World/TransferPlatform',platform,translation=(0.,0.,0.))
  self.ground_sensors={}
  for link in ['base']+[f'link_{leg}_{part}' for leg in ['lr','lf','rf','rr'] for part in ['hip_roll','hip_pitch','knee','sole']]:
   sensor=ContactSensor(ContactSensorCfg(prim_path=f'/World/envs/env_.*/Robot/{link}',filter_prim_paths_expr=['/World/TransferPlatform'],update_period=0.,history_length=1))
   self.scene.sensors['ground_'+link]=sensor;self.ground_sensors[link]=sensor
 def _reference(self):
  q=self.command_q if hasattr(self,'command_q') else self._robot.data.default_joint_pos[:,self._actuated_joint_ids]
  return q,torch.zeros(1,4,device=self.device),torch.ones(1,4,dtype=torch.bool,device=self.device)
 def _pre_physics_step(self,actions):
  self._raw_actions=actions.clone();self._actions.zero_();self._processed_actions=self.command_q.clone()
  d=self._robot.data;foot,_=self.full_model.fk(self.command_q.reshape(1,4,3))
  desired=self.desired_root.clone();desired[:,2]+=.05
  delta=math_utils.quat_apply_inverse(d.root_quat_w,desired-d.root_pos_w)
  request=torch.zeros(1,3,device=self.device);request[:,:2]=(4.*delta[:,:2]).clamp(-.2,.2)
  parameters=dict(self.cfg.reference_parameters['support_feedback'])
  forces=support_forces(foot,foot.new_tensor(parameters['com_body_m']),self.command_weights,d.projected_gravity_b*9.81,d.root_lin_vel_b,d.root_ang_vel_b,request,desired[:,2]-d.root_pos_w[:,2],parameters)
  self.feedforward=self.full_model.static_support_torque(self.command_q.reshape(1,4,3),forces,d.projected_gravity_b*9.81).reshape(1,12)
  if not torch.isfinite(self.feedforward).all() or self.feedforward.abs().max()>8.:raise RuntimeError('Feedforward torque outside diagnostic bound')
 def _apply_action(self):
  self._robot.set_joint_position_target(self.command_q,joint_ids=self._actuated_joint_ids)
  self._robot.set_joint_velocity_target(self.command_velocity,joint_ids=self._actuated_joint_ids)
  self._robot.set_joint_effort_target(self.feedforward,joint_ids=self._actuated_joint_ids)
 def _get_dones(self):
  # Preserve the measured failure frame. The outer loop stops immediately and
  # never takes another physics step after a guard; no automatic reset.
  return torch.zeros(1,dtype=torch.bool,device=self.device),torch.zeros(1,dtype=torch.bool,device=self.device)

def main():
 prov=json.loads(args.provenance.read_text());plan=json.loads(args.plan.read_text());profile=learning_profile()
 if not plan['preflight_pass'] or plan['urdf_sha256']!=prov['diagnostic_urdf_sha256']:raise ValueError('Preflight/asset mismatch')
 if file_hash(prov['urdf'])!=prov['diagnostic_urdf_sha256']:raise ValueError('URDF changed')
 for path,sha in prov['mesh_sha256'].items():
  if file_hash(path)!=sha:raise ValueError('Mesh changed')
 cfg=MotionReferenceEnvCfg();configure_reference(cfg,profile);cfg.scene.num_envs=1;cfg.seed=1911;cfg.sim.device=args.device;cfg.periodic_commands=False;cfg.episode_length_s=60.
 cfg.robot.spawn.asset_path=prov['urdf'];cfg.robot.spawn.usd_dir=str((args.output/'converted_asset').resolve());cfg.robot.spawn.force_usd_conversion=True
 for key,value in prov['required_import_settings'].items():
  if key=='enabled_self_collisions':cfg.robot.spawn.articulation_props.enabled_self_collisions=value
  else:setattr(cfg.robot.spawn,key,value)
 cfg.robot.init_state.pos=(0.,0.,plan['height_m']+.05+.003)
 cfg.checkpoint_compatibility_tag='csdog_independent_tripod_contact_transfer_v1';cfg.motion_contract=dict(cfg.motion_contract,compatibility_tag=cfg.checkpoint_compatibility_tag,training_enabled=False,root_teleport_after_reset=False,external_root_wrench=False)
 cfg.viewer.eye,cfg.viewer.lookat,cfg.viewer.resolution=(.9,1.1,.75),(-.06,0.,.23),(960,720)
 env=TripodEnv(cfg=cfg,render_mode='rgb_array' if args.record else None);encoder=None
 try:
  env.full_model=LegKinematics(prov['urdf'],profile['nominal_joint_positions_rad'],offset_bound=4.,device=env.device)
  env.command_q=torch.tensor(profile['nominal_joint_positions_rad'],device=env.device)[None];env.command_velocity=torch.zeros_like(env.command_q);env.command_weights=torch.ones(1,4,device=env.device);env.desired_root=torch.tensor([[0.,0.,plan['height_m']]],device=env.device)
  if args.record:encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','25','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output/'preview.mp4')],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  weight=profile['support_feedback']['mass_kg']*9.81;trials=[];raw=[]
  with torch.inference_mode():
   for trial in range(args.repeats):
    env.reset();events=[];fault=None;stable=0;missing=0;trialrows=[];previous=env.command_q.clone()
    for segment in plan['plan']:
     phase=segment['phase'];n=int(round(segment['duration_s']/.02));events.append({'phase':phase,'start_step':len(trialrows)})
     # Measured unload gate: time by itself never permits lifting.
     if phase=='roll_out' and stable<10:fault='unload_gate_not_ready';break
     if phase=='center' and stable<10:fault='reload_gate_not_ready';break
     for i in range(n):
      s=(i+1)/n;u=s**3*(10-15*s+6*s*s);q=np.array(segment['start_q'])+u*(np.array(segment['end_q'])-segment['start_q']);y=segment['start_y']+u*(segment['end_y']-segment['start_y']);rfw=segment['start_rf_weight']+u*(segment['end_rf_weight']-segment['start_rf_weight'])
      env.command_q=torch.tensor(q,dtype=torch.float32,device=env.device)[None];env.command_velocity=(env.command_q-previous)/.02;previous=env.command_q.clone();env.command_weights[:]=1.;env.command_weights[:,2]=rfw;env.desired_root[:]=torch.tensor([0.,y,plan['height_m']],device=env.device)
      obs,_,_,_,_=env.step(torch.zeros(1,12,device=env.device));d=env._robot.data
      tilt=float(torch.acos((-d.projected_gravity_b[0,2]).clamp(-1,1))*180/torch.pi)
      loads={link:float(sensor.data.force_matrix_w[0,0,:,2].sum()) for link,sensor in env.ground_sensors.items()};feet=[loads['link_'+leg+'_sole'] for leg in ['lr','lf','rf','rr']];other=sum(max(v,0.) for k,v in loads.items() if not k.endswith('_sole'))
      error=float((d.joint_pos[:,env._actuated_joint_ids]-env.command_q).abs().max());speed=float(d.root_lin_vel_w.norm());height=float(d.root_pos_w[0,2]-.05);torque=float(d.applied_torque[:,env._actuated_joint_ids].abs().max());qspeed=float(d.joint_vel[:,env._actuated_joint_ids].abs().max());rooterr=float((d.root_pos_w[0,:2]-env.desired_root[0,:2]).norm())
      tripod=min(feet[k] for k in [0,1,3])>.05*weight;ready=tripod and feet[2]<.15*weight and tilt<3. and speed<.05 and rooterr<.03
      four=min(feet)>1. and tilt<3. and speed<.05 and abs(height-plan['height_m'])<.02
      if phase in ['unload','unload_gate']:stable=stable+1 if ready else 0
      elif phase in ['reload','stand_final']:stable=stable+1 if four else 0
      elif phase in ['roll_out','fold_knee','tripod_hold','unfold_knee','roll_in']:
       missing=missing+1 if not tripod else 0
      else:stable=0
      limits=d.soft_joint_pos_limits[:,env._actuated_joint_ids];actualq=d.joint_pos[:,env._actuated_joint_ids];finite=bool(torch.isfinite(obs['policy']).all() and torch.isfinite(actualq).all() and torch.isfinite(d.root_lin_vel_w).all())
      row={'trial':trial,'phase':phase,'phase_time_s':(i+1)*.02,'q':actualq[0].cpu().tolist(),'q_target':q.tolist(),'root_xyz_m':d.root_pos_w[0].cpu().tolist(),'root_quat_wxyz':d.root_quat_w[0].cpu().tolist(),'height_m':height,'tilt_deg':tilt,'speed_m_s':speed,'root_xy_error_m':rooterr,'joint_error_rad':error,'peak_torque_nm':torque,'peak_qspeed_rad_s':qspeed,'feet_ground_force_n':feet,'other_ground_force_n':other,'all_ground_force_n':loads,'tripod_contact':tripod,'gate_ready':ready,'four_foot_stable':four}
      trialrows.append(row);raw.append(row)
      if not finite:fault='nonfinite'
      elif height<.25 or height>.43 or tilt>12. or speed>.8 or qspeed>10.05 or torque>12.05:fault='physical_guard'
      elif bool(((actualq<limits[...,0]-.005)|(actualq>limits[...,1]+.005)).any()):fault='soft_joint_limit'
      elif other>1.:fault='unexpected_body_ground_contact'
      elif missing>10:fault='tripod_contact_lost_over_0_2s'
      elif env.command_velocity.abs().max()>2.:fault='target_velocity'
      if encoder and len(trialrows)%2==0:
       from PIL import Image,ImageDraw,ImageFont
       frame=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(frame);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19);draw.rectangle((0,0,960,64),fill=(24,29,36));draw.text((12,4),f'三足承重与右前腿收放诊断 第{trial+1}/{args.repeats}次 | {phase}',font=font,fill='white');draw.text((12,32),f'足端载荷 {[round(v,1) for v in feet]} N | 倾斜 {tilt:.2f}° | 未执行趴卧',font=font,fill='white');encoder.stdin.write(np.asarray(frame).tobytes())
       if phase=='tripod_hold' and i==100:frame.save(args.output/'tripod_hold.png')
      if fault:break
     print('TRIPOD',trial,phase,'steps',len(trialrows),'forces',np.round(feet,2).tolist(),'tilt',round(tilt,3),'fault',fault,flush=True)
     if fault:break
    held=[r for r in trialrows if r['phase']=='tripod_hold' and r['phase_time_s']>1.];final=[r for r in trialrows if r['phase']=='stand_final' and r['phase_time_s']>1.]
    passed=fault is None and len(held)==100 and len(final)==100 and all(r['tripod_contact'] and r['feet_ground_force_n'][2]<1. for r in held) and all(r['four_foot_stable'] for r in final) and max(r['tilt_deg'] for r in held)<3. and max(r['joint_error_rad'] for r in held)<.08
    item={'trial':trial,'gate':'PASS' if passed else 'FAIL','fault':fault,'steps':len(trialrows),'events':events,'hold_frames':len(held),'final_stand_frames':len(final),'hold_tilt_max_deg':max([r['tilt_deg'] for r in held],default=None),'hold_foot_loads_mean_n':np.mean([r['feet_ground_force_n'] for r in held],axis=0).tolist() if held else None,'final_height_mean_m':float(np.mean([r['height_m'] for r in final])) if final else None,'final_tilt_max_deg':max([r['tilt_deg'] for r in final],default=None)};trials.append(item);print('TRIPOD TRIAL',item,flush=True)
    if not passed:break
  result={'scope':'Free-root body shift, measured tripod unloading, right-front roll/fold/restore, four-foot reload and recenter only. No descent/belly/rise or locomotion policy validation.','complete':len(trials)==args.repeats and all(t['steps']==1500 for t in trials),'gate':'PASS' if len(trials)==args.repeats and all(t['gate']=='PASS' for t in trials) else 'FAIL','trials':trials,'requested_repeats':args.repeats,'new_ppo_updates':0,'training_enabled':False,'external_root_wrench':False,'runtime_root_or_joint_teleports':False,'self_collision_enabled':True,'raw':raw,'seed':1911,'urdf_sha256':file_hash(prov['urdf']),'plan_sha256':file_hash(args.plan),'script_sha256':file_hash(__file__),'cooking_recipe':env.cooking_recipe,'cooking_module_sha256':file_hash(Path(__file__).resolve().parents[1]/'source/stackforce_simready_generated_robot_lab/csdog_motion/collision_cooking.py'),'full_lie_rise_executed':False,'locomotion_release_changed':False,'gate_thresholds':{'unload_stable_frames':10,'unload_three_feet_min_fraction_weight_each':.05,'unload_rf_max_fraction_weight':.15,'unload_tilt_deg':3.,'unload_speed_m_s':.05,'unload_root_xy_error_m':.03,'tripod_lost_max_frames':10,'unexpected_body_ground_max_n':1.,'hold_rf_ground_max_n':1.,'hold_joint_error_rad':.08,'hold_tilt_deg':3.,'final_all_four_contact_min_n':1.,'final_height_error_m':.02}}
  (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print('TRIPOD RESULT',result['gate'],'complete',result['complete'],flush=True)
 finally:
  if encoder:
   encoder.stdin.close();err=encoder.stderr.read().decode();rc=encoder.wait()
   if rc:raise RuntimeError('video encoding failed: '+err)
  env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:launcher.app.close()
