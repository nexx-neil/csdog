#!/usr/bin/env python3
"""Known-course low-speed diagnostics. Oracle terrain is not a perception policy."""
import argparse,copy,json,math,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
p.add_argument('--extra-bar-clearance',type=float,default=0.)
p.add_argument('--tier',choices=('base','challenge'),default='base');p.add_argument('--yaw',action='store_true')
p.add_argument('--path-feedback',action='store_true');p.add_argument('--record',action='store_true')
AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.enable_cameras=a.record
if a.output.exists() or not 0<=a.extra_bar_clearance<=.02:p.error('New output and extra clearance in[0,.02]m required')
app=AppLauncher(a)
import numpy as np,torch,subprocess
from PIL import Image,ImageDraw,ImageFont
import isaaclab.sim as sim_utils
from isaaclab.utils.math import quat_apply,quat_apply_inverse
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_transfer import MotionBackwardEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_adaptive_speed import MotionAdaptiveSpeedEnvCfg,MotionAdaptiveSpeedEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg,YawMixin
from csdog_motion.terrain_course import BASE_COURSE,CHALLENGE_COURSE,course_height,extra_swing_clearance,START,RUN,PLATEAU,RISE,END,SLOPE_DEG,BAR_CENTERS,BAR_WIDTH
from csdog_motion.adaptive_speed import adaptive_reference,stance_fraction
from csdog_motion.training import validate_checkpoint,file_hash
COURSE=CHALLENGE_COURSE if a.tier=='challenge' else BASE_COURSE
SLOPE_DEG=COURSE.slope_deg;RISE=COURSE.rise_m
NAMES=['flat',f'three_{COURSE.low_bar_m*100:g}cm_bars',f'three_{COURSE.high_bar_m*100:g}cm_bars',f'{SLOPE_DEG:g}deg_up_down',f'{COURSE.high_bar_m*100:g}cm_bars_with_small_kick']
REPLICAS=3

class TerrainDiagnostic(MotionAdaptiveSpeedEnv):
 def _setup_scene(self):
  super()._setup_scene()
  material=sim_utils.RigidBodyMaterialCfg(static_friction=COURSE.material_friction,dynamic_friction=COURSE.material_friction,restitution=0.)
  def box(path,size,position,orientation=(1.,0.,0.,0.)):
   cfg=sim_utils.CuboidCfg(size=size,collision_props=sim_utils.CollisionPropertiesCfg(),physics_material=material,visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.75,.35,.15)))
   cfg.func(path,cfg,translation=position,orientation=orientation)
  theta=math.radians(SLOPE_DEG);length=RUN/math.cos(theta);thickness=.04
  for i,origin in enumerate(self._terrain.env_origins.cpu().tolist()):
   case=i//REPLICAS;ox,oy,oz=origin
   if case in (1,2,4):
    height=COURSE.low_bar_m if case==1 else COURSE.high_bar_m
    for j,x in enumerate(BAR_CENTERS):box(f'/World/Course_{i}_bar_{j}',(BAR_WIDTH,1.2,height),(ox+x,oy,oz+height/2))
   if case==3:
    q=(math.cos(theta/2),0.,-math.sin(theta/2),0.)
    box(f'/World/Course_{i}_up',(length,1.2,thickness),(ox+START+RUN/2+thickness/2*math.sin(theta),oy,oz+RISE/2-thickness/2*math.cos(theta)),q)
    box(f'/World/Course_{i}_top',(PLATEAU,1.2,RISE),(ox+START+RUN+PLATEAU/2,oy,oz+RISE/2))
    q=(math.cos(theta/2),0.,math.sin(theta/2),0.)
    box(f'/World/Course_{i}_down',(length,1.2,thickness),(ox+START+RUN+PLATEAU+RUN/2-thickness/2*math.sin(theta),oy,oz+RISE/2-thickness/2*math.cos(theta)),q)
 def _case(self):return torch.arange(self.num_envs,device=self.device)//REPLICAS
 def _surface(self,positions):
  local=positions-self._terrain.env_origins[:,None,:] if positions.ndim==3 else positions-self._terrain.env_origins
  case=self._case()[:,None] if positions.ndim==3 else self._case()
  return course_height(local[...,0],case,local[...,1],COURSE)
 def _support_height(self):
  robot=self._robot.data;ground=self._surface(robot.root_pos_w)
  ground=torch.where(self._case()==3,ground,0.)
  return robot.root_pos_w[:,2]-self._terrain.env_origins[:,2]-ground
 def _foot_clearance(self):
  feet=self._robot.data.body_pos_w[:,self._robot_foot_ids]
  return feet[:,:,2]-self._terrain.env_origins[:,2:3]-.018-self._surface(feet)
 def _reference(self):
  if self._reference_tick==self.common_step_counter:return self._reference_cache
  robot=self._robot.data
  target,stance=adaptive_reference(self.motion.phase,self.motion.applied[:,:3],self.reference_nominal,self.reference_config,blend=self.motion.blend)
  extra=(((self._case()==2)|(self._case()==4)).float()*a.extra_bar_clearance)
  target=extra_swing_clearance(target,self.motion.phase,stance_fraction(self.motion.applied[:,:3]),extra,self.motion.blend)
  quat=robot.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4)
  predicted=quat_apply(quat,target.reshape(-1,3)).reshape(-1,4,3)+robot.root_pos_w[:,None,:]
  root_ground=self._surface(robot.root_pos_w)
  diff=self._surface(predicted)-root_ground[:,None]
  diff=torch.where((self._case()==3)[:,None],diff,0.)
  delta=torch.zeros_like(target);delta[:,:,2]=diff
  target+=quat_apply_inverse(quat,delta.reshape(-1,3)).reshape(-1,4,3)
  q,error=self.reference_model.solve(target,iterations=18)
  self._reference_cache=(q.flatten(1),error,stance);self._reference_tick=self.common_step_counter
  return self._reference_cache
 def _get_rewards(self):return torch.zeros(self.num_envs,device=self.device)
 def _get_dones(self):
  term,trunc=super()._get_dones();term|=(self._support_height()<self.cfg.min_base_height)&(self.episode_length_buf>self._termination_grace_steps)
  return term,trunc

class TerrainYawDiagnostic(YawMixin,TerrainDiagnostic):pass

def main():
 torch.set_num_threads(1);parent=MotionYawEnvCfg() if a.yaw else MotionBackwardEnvCfg();meta=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 cfg=MotionYawEnvCfg() if a.yaw else MotionAdaptiveSpeedEnvCfg();cfg.scene.num_envs=len(NAMES)*REPLICAS;cfg.scene.env_spacing=8.;cfg.sim.device=a.device;cfg.seed=713;cfg.episode_length_s=30.
 cfg.motion_contract=copy.deepcopy(cfg.motion_contract);cfg.motion_contract.update(schema_version=21 if a.path_feedback else 20,compatibility_tag='csdog_known_terrain_path_diagnostic_obs74_v21' if a.path_feedback else 'csdog_known_terrain_diagnostic_obs74_v20',terrain_diagnostic={'known_geometry_oracle':True,'controller_body_height':'relative hill surface; small bars retain floor support plane','clearance_observation':'relative to local foot surface','reference':'hill-only oracle footZ adjustment; low bars retain original swing','reward':'zero; training blocked','scope':'3x1cm/2cm bars and 5deg up/down at .2m/s only; no generic terrain claim'})
 cfg.motion_contract['terrain_diagnostic']['path_feedback']={'enabled':a.path_feedback,'world_path':'local y=0, yaw=0','lateral_gain_s_inv':.6,'yaw_gain_s_inv':1.5,'yaw_lateral_gain_rad_m_s':.4,'vy_limit_mps':.08,'yaw_limit_radps':.12}
 cfg.motion_contract['terrain_diagnostic']['scope']=f'three {COURSE.low_bar_m:g}/{COURSE.high_bar_m:g}m bars; {SLOPE_DEG:g}deg up/down at {COURSE.speed_mps:g}m/s; known geometry only'
 cfg.motion_contract['terrain_diagnostic']['course_parameters']={**vars(COURSE),'tier':a.tier,'observed_yaw_integral':a.yaw,'extra_bar_swing_clearance_m':a.extra_bar_clearance}
 if a.yaw:cfg.motion_contract.update(schema_version=26,compatibility_tag=f'csdog_known_terrain_{a.tier}_yaw_diagnostic_obs76_v26')
 cfg.checkpoint_compatibility_tag=cfg.motion_contract['compatibility_tag'];cfg.training_enabled=False;cfg.residual_training_enabled=False
 a.output.mkdir(parents=True);cfg.robot.spawn.usd_dir=str((a.output/'converted_asset').resolve());cfg.terrain.physics_material=sim_utils.RigidBodyMaterialCfg(static_friction=COURSE.material_friction,dynamic_friction=COURSE.material_friction,restitution=0.)
 cfg.viewer.resolution=(960,720);env=(TerrainYawDiagnostic if a.yaw else TerrainDiagnostic)(cfg,render_mode='rgb_array' if a.record else None);n=env.num_envs;encoder=None
 try:
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[n]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(env.device)
  if a.record:
   font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
   encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','25','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(a.output/'preview.mp4')],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  state=torch.load(a.checkpoint,map_location=env.device,weights_only=True)['model_state_dict'];policy.load_state_dict(state);policy.eval()
  trace=[];fail=torch.zeros(n,device=env.device);peakq=torch.zeros_like(fail);peake=torch.zeros_like(fail);boxclip=torch.zeros_like(fail);finite=torch.ones(n,device=env.device,dtype=torch.bool);began=time.monotonic()
  with torch.inference_mode():
   for step in range(1100):
    command=torch.zeros(n,3,device=env.device)
    if 100<=step<1050:
     command[:,0]=COURSE.speed_mps
     if a.path_feedback:
      r=env._robot.data;local_y=r.root_pos_w[:,1]-env._terrain.env_origins[:,1];w,x,y,z=r.root_quat_w.unbind(-1);yaw=torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z))
      command[:,1]=(-.6*local_y).clamp(-.08,.08);command[:,2]=(-1.5*yaw-.4*local_y).clamp(-.12,.12)
    env.set_motion_request(command)
    if step==500:
     ids=torch.arange(12,15,device=env.device);v=env._robot.data.root_vel_w[ids].clone();sign=torch.tensor([1.,-1.,1.],device=env.device);v[:,0]+=.05*sign;v[:,1]-=.04*sign;v[:,5]+=.08*sign;env._robot.write_root_velocity_to_sim(v,env_ids=ids);obs=env._get_observations()
    action=policy.act_inference(TensorDict(obs,batch_size=[n]));obs,_,term,_,_=env.step(action);fail+=term
    r=env._robot.data;peakq=torch.maximum(peakq,env._processed_velocity_targets.abs().amax(1));peake=torch.maximum(peake,env.reference_error.amax(1));boxclip+=env.target_box_limited.float().mean(1);finite&=torch.isfinite(obs['policy']).all(1)
    if step%2==0:trace.append({'seconds':step*.02,'local_position':(r.root_pos_w-env._terrain.env_origins).cpu().tolist(),'height_above_support_surface':env._support_height().cpu().tolist(),'tilt_deg':(torch.acos((-r.projected_gravity_b[:,2]).clamp(-1,1))*180/torch.pi).cpu().tolist(),'requested_twist':command.cpu().tolist(),'actual_twist':torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1).cpu().tolist(),'foot_clearance_m':env._foot_clearance().cpu().tolist(),'terminated':term.cpu().tolist()})
    if encoder and step%2==0:
     root=r.root_pos_w[9].cpu().numpy();env.sim.set_camera_view(tuple(root+np.array([1.0,-1.4,.55])),tuple(root+np.array([.1,0.,-.12])))
     canvas=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(canvas);draw.rectangle((0,0,960,92),fill=(24,29,36))
     draw.text((15,8),f'已知地形诊断｜{SLOPE_DEG:g}°上坡—平台—下坡｜{step*.02:.2f}s',font=font,fill='white')
     draw.text((15,39),f'速度命令{COURSE.speed_mps:.2f}m/s｜地形相对机身高度 {float(env._support_height()[9]):.3f}m｜解析地面+路线外环',font=font,fill=(190,215,235))
     encoder.stdin.write(np.asarray(canvas).tobytes())
     if step in (300,600,900):canvas.save(a.output/f'frame_{step:04d}.png')
    if step%300==0:print('terrain',step,'failures',int(fail.sum()),flush=True)
  if encoder:
   encoder.stdin.close();error=encoder.stderr.read().decode();code=encoder.wait()
   if code:raise RuntimeError(error)
  pos=np.array([t['local_position'] for t in trace]);height=np.array([t['height_above_support_surface'] for t in trace]);tilt=np.array([t['tilt_deg'] for t in trace]);twist=np.array([t['actual_twist'] for t in trace]);rows=[]
  for i,name in enumerate(NAMES):
   ids=slice(i*3,(i+1)*3);finish=END+.3 if i==3 else (2.75 if i else 2.75)
   row={'name':name,'command_mps':COURSE.speed_mps,'failures':int(fail[ids].sum()),'finite':bool(finite[ids].all()),'final_x_m':pos[-1,ids,0].tolist(),'max_abs_y_m':float(np.abs(pos[:,ids,1]).max()),'full_body_crossed_all_features':bool((pos[-1,ids,0]>finish).all()),'height_mean_m':float(height[:,ids].mean()),'minimum_height_m':float(height[:,ids].min()),'body_tilt_rms_deg':float(np.sqrt(np.square(tilt[:,ids]).mean())),'peak_tilt_deg':float(tilt[:,ids].max()),'peak_target_velocity_rad_s':float(peakq[ids].max()),'max_ik_error_m':float(peake[ids].max()),'target_box_clip_fraction':float(boxclip[ids].mean()/1100),'mean_twist':twist[:,ids].mean((0,1)).tolist()}
   ok=row['finite'] and not row['failures'] and row['full_body_crossed_all_features'] and row['max_abs_y_m']<.25 and abs(row['height_mean_m']-cfg.base_height_target)<.04 and row['minimum_height_m']>.25 and row['body_tilt_rms_deg']<10 and row['peak_target_velocity_rad_s']<=8.0001 and row['max_ik_error_m']<=.001 and row['target_box_clip_fraction']<.1
   row['gate']='PASS' if ok else 'FAIL';rows.append(row)
  report={'complete':True,'new_ppo_updates':0,'all_network_tensors_bitwise_supplied_checkpoint':all(torch.equal(v,state[k]) for k,v in policy.state_dict().items()),'checkpoint_sha256':file_hash(a.checkpoint),'motion_contract':cfg.motion_contract,'scope':'known geometry oracle, deterministic cloned resets, low-speed course diagnostics only','gate':'PASS' if all(r['gate']=='PASS' for r in rows) else 'FAIL','wall_seconds':time.monotonic()-began,'cases':rows,'trace':trace}
  (a.output/'evaluation.json').write_text(json.dumps(report,indent=2)+'\n');print('terrain gate',report['gate'],flush=True)
  for row in rows:print(row['name'],row['gate'],row['final_x_m'],row['failures'],flush=True)
 finally:
  if encoder and encoder.poll() is None:encoder.kill()
  env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
