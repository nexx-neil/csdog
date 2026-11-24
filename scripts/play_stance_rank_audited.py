#!/usr/bin/env python3
"""View a low-speed scanned-terrain candidate on one tile; see its selection record."""
import argparse,json,subprocess,tempfile,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--profile',choices=('foundation','step225'),default='foundation');p.add_argument('--expected-mesh-sha256');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--record',type=Path);p.add_argument('--kind',choices=('pyramid_slope','inverted_slope','pyramid_stairs','inverted_stairs','blocks','waves','rails','compound'),default='compound');p.add_argument('--row',type=int,default=2);p.add_argument('--seed',type=int,default=12037);p.add_argument('--steps',type=int,default=900);p.add_argument('--demo',action='store_true');p.add_argument('--demo-direction',choices=('forward','backward','left','right','advance_then_turn','advance_then_turn_right'),default='forward');AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.full_range=False;a.enable_cameras=bool(a.record)
if not 0<=a.row<3 or (a.headless and not a.demo) or (a.record and a.record.exists()):p.error('Valid row/column; headless requires demo; new recording directory')
app=AppLauncher(a)
import numpy as np,torch
from PIL import Image,ImageDraw,ImageFont
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_stance_preview_rank import MotionStanceRankEnvCfg as MotionScannedRoughEnvCfg,MotionStanceRankEnv as MotionScannedRoughEnv
from isaaclab.terrains import TerrainGenerator
from isaaclab.utils.math import quat_apply_inverse
import hashlib
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.terrain_library import WALKING_KINDS,build_library_cfg
a.column=WALKING_KINDS.index(a.kind)

class RecordedGenerator(TerrainGenerator):
 def __init__(self,*args,**kwargs):
  type(self).torch_rng_before_sha256=hashlib.sha256(torch.get_rng_state().numpy().tobytes()).hexdigest()
  super().__init__(*args,**kwargs);mesh=self.terrain_mesh
  type(self).mesh_arrays_sha256=hashlib.sha256(mesh.vertices.tobytes()+mesh.faces.tobytes()).hexdigest()

class ViewEnv(MotionScannedRoughEnv):
 def _setup_scene(self):
  super()._setup_scene();self.terrain_columns[:]=a.column;self._terrain.env_origins[:]=self._terrain.terrain_origins[a.row,a.column]

class Keyboard:
 def __init__(self):
  import carb,omni.appwindow
  self.carb=carb;self.keys=set();self.pending=[];self.quit=False;window=omni.appwindow.get_default_app_window();self.input=carb.input.acquire_input_interface();self.keyboard=window.get_keyboard();self.sub=self.input.subscribe_to_keyboard_events(self.keyboard,self.event)
 def event(self,event,*args):
  key=event.input.name
  if event.type==self.carb.input.KeyboardEventType.KEY_RELEASE:self.keys.discard(key)
  elif event.type==self.carb.input.KeyboardEventType.KEY_PRESS:
   if key=='ESCAPE':self.quit=True
   elif key in ('T','SPACE'):self.keys.clear();self.pending.append(key)
   elif key in 'WSADQE':self.keys.add(key)
  return True
 def command(self):
  k=self.keys;v=[(.225 if a.profile=='step225' else .2)*(('W'in k)-('S'in k)),(.19 if a.profile=='step225' else .18)*(('A'in k)-('D'in k)),.3*(('Q'in k)-('E'in k))]
  return v if sum(abs(x)>0 for x in v)<=1 else [0,0,0]
 def close(self):self.input.unsubscribe_to_keyboard_events(self.keyboard,self.sub)

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed);cfg=MotionScannedRoughEnvCfg();meta=validate_checkpoint(a.checkpoint,cfg,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 cfg.terrain.terrain_generator=build_library_cfg('bridge','walking',a.seed);cfg.terrain.terrain_generator.class_type=RecordedGenerator;cfg.scene.num_envs=1;cfg.sim.device=a.device;cfg.terrain_row=a.row;cfg.terrain.terrain_generator.seed=a.seed;cfg.seed=a.seed;cfg.periodic_commands=False;cfg.episode_length_s=120.;cfg.robot.spawn.usd_dir=tempfile.mkdtemp(prefix='csdog_scanned_rough_');cfg.viewer.resolution=(960,720)
 env=ViewEnv(cfg,render_mode='rgb_array' if a.record else None);keyboard=None;encoder=None
 try:
  if a.expected_mesh_sha256 and RecordedGenerator.mesh_arrays_sha256!=a.expected_mesh_sha256:raise RuntimeError('Single/batch terrain mesh mismatch; do not count as matched replay')
  with torch.inference_mode():obs,_=env.reset()
  policy=ActorCritic(TensorDict(obs,batch_size=[1]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu').to(env.device);policy.load_state_dict(torch.load(a.checkpoint,map_location=env.device,weights_only=True)['model_state_dict']);policy.eval()
  if not a.demo:keyboard=Keyboard()
  if a.record:
   a.record.mkdir(parents=True);font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',20)
   encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','25','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(a.record/'preview.mp4')],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
  trace=[];terminations=0;finite=True
  with torch.inference_mode():
   for step in range(a.steps):
    start=time.monotonic()
    if not app.app.is_running() or (keyboard and keyboard.quit):break
    if a.demo:
     t=step*.02;forward,lateral=(.225,.19)if a.profile=='step225'else(.2,.18);cmd=[0,0,0]
     if a.demo_direction.startswith('advance'):
      if 2<=t<10:cmd=[forward,0,0]
      if 10<=t<13:cmd=[0,0,-.3 if a.demo_direction.endswith('right')else .3]
     elif 2<=t<12:cmd={'forward':[forward,0,0],'backward':[-forward,0,0],'left':[0,lateral,0],'right':[0,-lateral,0]}[a.demo_direction]
    else:
     for key in keyboard.pending:
      if key=='T':obs,_=env.reset()
     keyboard.pending.clear();cmd=keyboard.command()
    env.set_motion_request(cmd);obs,_,term,trunc,_=env.step(policy.act_inference(TensorDict(obs,batch_size=[1])));r=env._robot.data;terminations+=int(term[0]);finite &= bool(torch.isfinite(obs['policy']).all());h=float(env._support_height()[0]);v=torch.cat((r.root_lin_vel_b[0,:2],r.root_ang_vel_b[0,2:3])).cpu().tolist();root=r.root_pos_w[0].cpu().numpy()
    if step%2==0:
     env.sim.set_camera_view(tuple(root+np.array([1.05,-1.35,.60])),tuple(root+np.array([.05,0.,-.13])))
     if encoder:
      frame=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(frame);draw.rectangle((0,0,960,100),fill=(24,29,36));title={'pyramid_slope':'金字塔坡','inverted_slope':'凹形坡','pyramid_stairs':'金字塔台阶','inverted_stairs':'凹形台阶','blocks':'随机方块','waves':'连续波浪','rails':'连续横栏','compound':'坡→台阶→碎块'}[a.kind]
      draw.text((12,5),f'复杂地形支撑验证｜{title}｜{step*.02:.2f}s',font=font,fill='white');draw.text((12,38),f'实际 vx/vy/yaw {v[0]:+.2f}/{v[1]:+.2f}/{v[2]:+.2f}｜离地高度 {h:.3f}m',font=font,fill='white');draw.text((12,66),f'指令 vx/vy/yaw {cmd[0]:+.3f}/{cmd[1]:+.3f}/{cmd[2]:+.2f}｜W/S前后 A/D横移 Q/E转向',font=font,fill='white');encoder.stdin.write(np.asarray(frame).tobytes())
      if step in (350,550,700):frame.save(a.record/f'frame_{step:04d}.png')
    body=quat_apply_inverse(r.root_quat_w[:,None].expand(-1,4,-1).reshape(-1,4),(r.body_pos_w[:,env._robot_foot_ids]-r.root_pos_w[:,None]).reshape(-1,3)).reshape(1,4,3);reference,_=env.reference_model.fk(env.reference_q.reshape(-1,4,3));contacts=torch.linalg.vector_norm(env._contact_sensor.data.net_forces_w[:,env._foot_ids],dim=-1)>1.;contact_speed=(torch.linalg.vector_norm(r.body_lin_vel_w[:,env._robot_foot_ids,:2],dim=-1)*contacts).sum(1)/contacts.sum(1).clamp_min(1)
    w,x,y,z=r.root_quat_w[0];yaw=float(torch.atan2(2*(w*z+x*y),1-2*(y*y+z*z)))
    trace.append({'swing_workspace_leg_steps':env.swing_workspace_leg_steps,'min_swing_clearance_surplus_m':env.swing_min_clearance_surplus_m if env.swing_workspace_leg_steps else None,'stance_endpoint_preview_plans':getattr(env,'stance_endpoint_preview_plans',0),'stance_projection_leg_steps':getattr(env,'stance_projection_leg_steps',0),'stance_projection_peak_shift_m':getattr(env,'stance_projection_peak_shift_m',0.),'patch_force_disagreement_n':env.patch_force_disagreement_n,'foot_contact':contacts[0].cpu().tolist(),'foot_vertical_force_n':env._contact_sensor.data.net_forces_w[0,env._foot_ids,2].cpu().tolist(),'gait_phase':float(env.motion.phase[0]),'patch_active':env.patch.active[0].cpu().tolist(),'patch_anchor_xyz_w':env.patch.xyz[0].cpu().tolist(),'patch_support_height_w':env.patch.height[0].cpu().tolist(),'patch_anchor_xy_w':env.patch.xy[0].cpu().tolist(),'actual_foot_world_xyz':r.body_pos_w[0,env._robot_foot_ids].cpu().tolist(),'peak_target_qspeed_rad_s':float(env._processed_velocity_targets.abs().max()),'max_ik_error_m':float(env.reference_error.max()),'peak_torque_nm':float(r.applied_torque[:,env._actuated_joint_ids].abs().max()),'box_clip_fraction':float(env.target_box_limited.float().mean()),'rate_clip':bool(env.target_speed_limited[0]),'foot_error_sq':float((body-reference).square().sum(2).mean()),'contact_slide_50hz_mps':float(contact_speed[0]),'yaw_rad':yaw,'datum_world_m':float(env.contact_datum.value[0]),'datum_velocity_mps':float(env.contact_datum.velocity[0]),'seconds':(step+1)*.02,'position':(r.root_pos_w[0]-env._terrain.env_origins[0]).cpu().tolist(),'support_height':h,'height_target':float(env.motion.applied[0,3]),'automatic_height_offset_m':float(env.height_coordinator.value[0]),'automatic_height_rate_mps':float(env.height_coordinator.velocity[0]),'root_ground_w':float(env._surfaces()[0,0]),'actual_twist':v,'command':cmd,'scan_range_m':float((env.height_scanner.data.ray_hits_w[:,:,2].amax(1)-env.height_scanner.data.ray_hits_w[:,:,2].amin(1))[0]),'tilt_deg':float(torch.acos((-r.projected_gravity_b[0,2]).clamp(-1,1))*180/torch.pi),'terminated':bool(term[0])})
    if not a.demo:time.sleep(max(0.,.02-(time.monotonic()-start)))
  if encoder:encoder.stdin.close();error=encoder.stderr.read().decode();code=encoder.wait();assert code==0,error
  output=(a.record/'preview.json') if a.record else Path(f'outputs/motion_foundation/lesson28_play_{time.time_ns()}.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps({'complete':len(trace)==a.steps if a.demo else True,'seconds':len(trace)*.02,'unexpected_terminations':terminations,'finite':finite,'checkpoint_sha256':file_hash(a.checkpoint),'terrain_seed':a.seed,'profile':a.profile,'terrain_mesh_arrays_sha256':RecordedGenerator.mesh_arrays_sha256,'terrain_torch_rng_before_sha256':RecordedGenerator.torch_rng_before_sha256,'level':'bridge','kind':a.kind,'demo_direction':a.demo_direction if a.demo else None,'viewer_source_sha256':file_hash(__file__),'row':a.row,'column':a.column,'motion_contract':cfg.motion_contract,'new_ppo_updates':0,'full_range':a.full_range,'trace':trace},indent=2)+'\n');print('Terrain preview saved',output,flush=True)
 finally:
  if keyboard:keyboard.close()
  if encoder and encoder.poll() is None:encoder.kill()
  env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
