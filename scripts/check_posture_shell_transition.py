#!/usr/bin/env python3
"""Guarded stand/lie/rise probe with user-confirmed hip bearing shells.

Independent fine-collision model, no policy or learned update, no root wrench.
"""
import argparse,json,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--provenance',type=Path,required=True);p.add_argument('--corridor',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--record',action='store_true');p.add_argument('--repeats',type=int,default=1)
AppLauncher.add_app_launcher_args(p);args=p.parse_args()
if args.output.exists():p.error('Refusing to overwrite evidence')
if not 1<=args.repeats<=3:p.error('repeats must be1..3')
args.output.mkdir(parents=True);args.enable_cameras=args.record;launcher=AppLauncher(args)
import numpy as np,torch,subprocess
import isaaclab.sim as sim_utils
from isaaclab.sensors import ContactSensor,ContactSensorCfg
from csdog_motion.training import file_hash
from csdog_motion.residual_learning import learning_profile
from csdog_motion.trajectory import LegKinematics
from csdog_motion.collision_cooking import normalize_mesh_colliders
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reference import MotionReferenceEnv,MotionReferenceEnvCfg,configure_reference

class ShellEnv(MotionReferenceEnv):
 def _setup_scene(self):
  super()._setup_scene()
  import omni.usd
  self.cooking_recipe=normalize_mesh_colliders(omni.usd.get_context().get_stage(),'/World/envs/env_0/Robot','fine')
  platform=sim_utils.CuboidCfg(size=(3.,3.,.10),rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True,disable_gravity=True),mass_props=sim_utils.MassPropertiesCfg(mass=100.),collision_props=sim_utils.CollisionPropertiesCfg(),visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.22,.25,.28)))
  platform.func('/World/ShellPlatform',platform,translation=(0.,0.,0.))
  self.ground_sensors={}
  for link in ['base']+[f'link_{leg}_{part}' for leg in ['lr','lf','rf','rr'] for part in ['hip_roll','hip_pitch','knee','sole']]:
   sensor=ContactSensor(ContactSensorCfg(prim_path=f'/World/envs/env_.*/Robot/{link}',filter_prim_paths_expr=['/World/ShellPlatform'],update_period=0.,history_length=1));self.scene.sensors['ground_'+link]=sensor;self.ground_sensors[link]=sensor
 def _reference(self):
  q=self.command_q if hasattr(self,'command_q') else self._robot.data.default_joint_pos[:,self._actuated_joint_ids]
  return q,torch.zeros(1,4,device=self.device),torch.ones(1,4,dtype=torch.bool,device=self.device)
 def _pre_physics_step(self,actions):
  self._raw_actions=actions.clone();self._actions.zero_();self._processed_actions=self.command_q.clone();d=self._robot.data
  q=self.command_q.reshape(1,4,3)
  self.feedforward=self.full_model.static_support_torque(q,torch.zeros(1,4,3,device=self.device),d.projected_gravity_b*9.81).reshape(1,12)
  self.pre_guard=None
  if not torch.isfinite(self.feedforward).all():
   self.pre_guard='nonfinite_feedforward';self.feedforward=torch.zeros_like(self.feedforward)
  elif self.feedforward.abs().max()>8.:
   self.pre_guard='feedforward_torque_guard';self.feedforward=self.feedforward.clamp(-8.,8.)
 def _apply_action(self):
  self._robot.set_joint_position_target(self.command_q,joint_ids=self._actuated_joint_ids);self._robot.set_joint_velocity_target(self.command_velocity,joint_ids=self._actuated_joint_ids);self._robot.set_joint_effort_target(self.feedforward,joint_ids=self._actuated_joint_ids)
 def _get_dones(self):return torch.zeros(1,dtype=torch.bool,device=self.device),torch.zeros(1,dtype=torch.bool,device=self.device)

def main():
 prov=json.loads(args.provenance.read_text());corr=json.loads(args.corridor.read_text());profile=learning_profile()
 if not corr['self_screen_pass']:raise ValueError('Sampled self screen required')
 if file_hash(prov['urdf'])!=prov['diagnostic_urdf_sha256']:raise ValueError('URDF changed')
 for path,sha in prov['mesh_sha256'].items():
  if file_hash(path)!=sha:raise ValueError('Mesh changed')
 # User confirmed on2026-11-11 that hip actuators have dedicated bearing shells.
 # Ground contact attribution to existing hip links is a simulation proxy; no
 # new mesh/collider is invented and the source asset stays untouched.
 wp=[np.array(v) for v in corr['waypoints_q_rad']]
 if len(wp)==8:
  nom,splay,lift,tuck,medial,shell,fold,belly=wp
  segments=[('stand',3.,nom,nom),('splay',4.,nom,splay),('lift_rf',4.,splay,lift),('tuck_rf',4.,lift,tuck),('lower_medial',6.,tuck,medial),('lower_on_shells',6.,medial,shell),('fold_rf_hip',4.,shell,fold),('belly_align',4.,fold,belly),('belly_hold',5.,belly,belly),('deploy',4.,belly,fold),('open_rf_hip',4.,fold,shell),('rise_on_shells',6.,shell,medial),('rise_medial',6.,medial,tuck),('untuck_rf',4.,tuck,lift),('land_rf',4.,lift,splay),('center',4.,splay,nom),('stand_final',5.,nom,nom)]
 elif len(wp)==6:
  nom,splay,lift,tuck,fold,belly=wp
  segments=[('stand',3.,nom,nom),('splay',4.,nom,splay),('lift_rf',4.,splay,lift),('tuck_rf',4.,lift,tuck),('lower_on_shells',8.,tuck,fold),('belly_align',4.,fold,belly),('belly_hold',5.,belly,belly),('deploy',4.,belly,fold),('rise_on_shells',8.,fold,tuck),('untuck_rf',4.,tuck,lift),('land_rf',4.,lift,splay),('center',4.,splay,nom),('stand_final',5.,nom,nom)]
 else:raise ValueError('Expected6 or8 preflighted waypoints')

 cfg=MotionReferenceEnvCfg();configure_reference(cfg,profile);
 for actuator in cfg.robot.actuators.values():actuator.stiffness=400.;actuator.damping=6.
 cfg.scene.num_envs=1;cfg.seed=1911;cfg.sim.device=args.device;cfg.periodic_commands=False;cfg.episode_length_s=90.;cfg.robot.spawn.asset_path=prov['urdf'];cfg.robot.spawn.usd_dir=str((args.output/'converted_asset').resolve());cfg.robot.spawn.force_usd_conversion=True
 for key,value in prov['required_import_settings'].items():
  if key=='enabled_self_collisions':cfg.robot.spawn.articulation_props.enabled_self_collisions=value
  else:setattr(cfg.robot.spawn,key,value)
 cfg.robot.init_state.pos=(0.,0.,profile['nominal_height_m']+.05+.006);cfg.checkpoint_compatibility_tag='csdog_hip_shell_contact_transition_diagnostic_v1';cfg.motion_contract=dict(cfg.motion_contract,compatibility_tag=cfg.checkpoint_compatibility_tag,training_enabled=False,hip_bearing_shells_user_confirmed='2026-11-11')
 cfg.viewer.eye,cfg.viewer.lookat,cfg.viewer.resolution=(.9,1.1,.75),(-.08,0.,.20),(960,720)
 env=ShellEnv(cfg=cfg,render_mode='rgb_array' if args.record else None);encoder=None;raw=[];trials=[]
 try:
  env.full_model=LegKinematics(prov['urdf'],profile['nominal_joint_positions_rad'],offset_bound=4.,device=env.device);env.command_q=torch.tensor(nom,dtype=torch.float32,device=env.device)[None];env.command_velocity=torch.zeros_like(env.command_q);env.filtered_foot_force=torch.zeros(1,4,3,device=env.device);env.standing_support=1.;env.rf_support=1.
  if args.record:encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','25','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(args.output/'preview.mp4')],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  weight=profile['support_feedback']['mass_kg']*9.81
  with torch.inference_mode():
   for trial in range(args.repeats):
    env.reset();env.filtered_foot_force.zero_();previous=env.command_q.clone();rows=[];fault=None;events=[];belly_ok=False;unload_stable=0;reload_stable=0;shell_stable=0;airborne_frames=0
    for phase,duration,a,b in segments:
     if phase=='fold_rf_hip' and shell_stable<10:fault='shell_support_gate_not_ready';break
     if phase=='tuck_rf' and unload_stable<10:fault='rf_unload_gate_not_ready';break
     if phase=='center' and reload_stable<10:fault='four_foot_reload_gate_not_ready';break
     if phase=='deploy' and not belly_ok:fault='belly_gate_not_ready';break
     events.append({'phase':phase,'start_step':len(rows)});n=int(round(duration/.02))
     for i in range(n):
      s=(i+1)/n;u=s**3*(10-15*s+6*s*s);q=a+u*(b-a);env.rf_support=1. if phase in ['stand','splay','center','stand_final'] else (1-u if phase=='tuck_rf' else (u if phase=='untuck_rf' else 0.));env.command_q=torch.tensor(q,dtype=torch.float32,device=env.device)[None];env.command_velocity=(env.command_q-previous)/.02;previous=env.command_q.clone()
      obs,_,_,_,_=env.step(torch.zeros(1,12,device=env.device));d=env._robot.data;loads={link:float(sensor.data.force_matrix_w[0,0,:,2].sum()) for link,sensor in env.ground_sensors.items()};feet=[loads['link_'+leg+'_sole'] for leg in ['lr','lf','rf','rr']];hips=sum(max(v,0.) for k,v in loads.items() if '_hip_' in k);knees=sum(max(v,0.) for k,v in loads.items() if k.endswith('_knee'));base=loads['base'];height=float(d.root_pos_w[0,2]-.05);tilt=float(torch.acos((-d.projected_gravity_b[0,2]).clamp(-1,1))*180/torch.pi);speed=float(d.root_lin_vel_w.norm());qspeed=float(d.joint_vel[:,env._actuated_joint_ids].abs().max());torque=float(d.applied_torque[:,env._actuated_joint_ids].abs().max());error=float((d.joint_pos[:,env._actuated_joint_ids]-env.command_q).abs().max());limits=d.soft_joint_pos_limits[:,env._actuated_joint_ids];actualq=d.joint_pos[:,env._actuated_joint_ids];finite=bool(torch.isfinite(obs['policy']).all() and torch.isfinite(actualq).all() and torch.isfinite(d.root_lin_vel_w).all())
      row={'trial':trial,'phase':phase,'phase_time_s':(i+1)*.02,'q':actualq[0].cpu().tolist(),'q_target':q.tolist(),'root_xyz_m':d.root_pos_w[0].cpu().tolist(),'root_quat_wxyz':d.root_quat_w[0].cpu().tolist(),'height_m':height,'tilt_deg':tilt,'speed_m_s':speed,'joint_error_rad':error,'peak_torque_nm':torque,'peak_qspeed_rad_s':qspeed,'feet_ground_force_n':feet,'hip_ground_force_n':hips,'knee_ground_force_n':knees,'base_ground_force_n':base,'all_ground_force_n':loads};rows.append(row);raw.append(row)
      if phase=='lift_rf':unload_stable=unload_stable+1 if min(feet[j] for j in [0,1,3])>.05*weight and feet[2]<1. and tilt<3. and speed<.05 else 0
      if phase=='land_rf':reload_stable=reload_stable+1 if min(feet)>1. and tilt<3. and speed<.05 else 0
      if phase=='lower_on_shells':shell_stable=shell_stable+1 if hips+base>.2*weight and tilt<15. and speed<.08 else 0
      airborne_frames=airborne_frames+1 if len(rows)>50 and sum(max(v,0.) for v in loads.values())<.2*weight else 0
      if airborne_frames>3:fault='ground_support_lost_over_60ms'
      elif env.pre_guard:fault=env.pre_guard
      elif not finite:fault='nonfinite'
      elif height<.07 or height>.43 or tilt>20. or speed>1.0 or qspeed>10.05 or torque>12.05:fault='physical_guard'
      elif bool(((actualq<limits[...,0]-.005)|(actualq>limits[...,1]+.005)).any()):fault='soft_joint_limit'
      elif knees>1.:fault='unexpected_knee_ground_contact'
      elif sum(max(v,0.) for v in loads.values())>4.*weight:fault='ground_impact_over_4mg'
      elif env.command_velocity.abs().max()>2.:fault='target_velocity'
      if encoder and len(rows)%2==0:
       from PIL import Image,ImageDraw,ImageFont
       frame=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(frame);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',19);draw.rectangle((0,0,960,64),fill=(24,29,36));draw.text((12,4),f'独立趴卧/起身诊断 第{trial+1}/{args.repeats}次 | {phase}',font=font,fill='white');draw.text((12,32),f'机腹 {base:.1f} N | 髋护壳 {hips:.1f} N | 倾斜 {tilt:.2f}°',font=font,fill='white');encoder.stdin.write(np.asarray(frame).tobytes())
      if fault:break
     print('SHELL',trial,phase,'steps',len(rows),'height',round(height,3),'tilt',round(tilt,2),'base/hip/knee',np.round([base,hips,knees],2).tolist(),'fault',fault,flush=True)
     if phase=='belly_hold':
      hold=[r for r in rows if r['phase']=='belly_hold' and r['phase_time_s']>2.]
      belly_ok=len(hold)==150 and sum(r['base_ground_force_n']>.6*weight for r in hold)/len(hold)>=.99 and max(r['tilt_deg'] for r in hold)<=3. and abs(np.mean([r['height_m'] for r in hold])-.1)<=.01 and max(r['joint_error_rad'] for r in hold)<=.08 and np.mean([r['hip_ground_force_n'] for r in hold])<1.
     if fault:break
    final=[r for r in rows if r['phase']=='stand_final' and r['phase_time_s']>2.];stand_ok=len(final)==150 and all(min(r['feet_ground_force_n'])>1. and r['tilt_deg']<3. and abs(r['height_m']-profile['nominal_height_m'])<.02 for r in final)
    item={'trial':trial,'gate':'PASS' if fault is None and belly_ok and stand_ok else 'FAIL','fault':fault,'steps':len(rows),'events':events,'belly_hold_gate':belly_ok,'standing_recovery_gate':stand_ok,'max_tilt_deg':max(r['tilt_deg'] for r in rows),'max_root_speed_m_s':max(r['speed_m_s'] for r in rows),'max_knee_ground_force_n':max(r['knee_ground_force_n'] for r in rows)};trials.append(item);print('SHELL TRIAL',item,flush=True)
    if item['gate']!='PASS':break
  expected=int(round(sum(v[1] for v in segments)/.02));result={'scope':'Independent fine-collision free-root shell-assisted stand/lie/rise probe. Existing hip-link geometry is a proxy for user-confirmed load-bearing shells; no hardware release or locomotion migration.','complete':len(trials)==args.repeats and all(t['steps']==expected for t in trials),'gate':'PASS' if len(trials)==args.repeats and all(t['gate']=='PASS' for t in trials) else 'FAIL','trials':trials,'requested_repeats':args.repeats,'raw':raw,'hip_bearing_shells_user_confirmed':'2026-11-11','new_ppo_updates':0,'training_enabled':False,'external_root_wrench':False,'runtime_root_or_joint_teleports':False,'self_collision_enabled':True,'script_sha256':file_hash(__file__),'urdf_sha256':file_hash(prov['urdf']),'corridor_sha256':file_hash(args.corridor),'cooking_recipe':env.cooking_recipe,'selected_locomotion_changed':False,'diagnostic_pd_gains':{'stiffness':400.,'damping':6.},'foot_mg_feedforward':False,'guard_thresholds':{'tilt_deg':20.,'height_min_m':.07,'height_max_m':.43,'root_speed_m_s':1.,'joint_speed_rad_s':10.05,'torque_nm':12.05,'knee_ground_max_n':1.,'ground_impact_max_weight_fraction':4.,'joint_target_speed_rad_s':2.,'ground_support_lost_max_frames':3,'hip_support_min_weight_fraction_before_fold_rf':.2,'hip_support_stable_frames':10}}
  (args.output/'summary.json').write_text(json.dumps(result,indent=2)+'\n');print('SHELL RESULT',result['gate'],'complete',result['complete'],flush=True)
 finally:
  if encoder:
   encoder.stdin.close();err=encoder.stderr.read().decode();rc=encoder.wait()
   if rc:raise RuntimeError('video encoding failed: '+err)
  env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:launcher.app.close()
