#!/usr/bin/env python3
"""View a low-speed scanned-terrain candidate on one tile; see its selection record."""
import argparse,json,subprocess,tempfile,time,traceback
from pathlib import Path
from isaaclab.app import AppLauncher
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--full-range',action='store_true');p.add_argument('--checkpoint',type=Path,required=True);p.add_argument('--record',type=Path);p.add_argument('--column',type=int,default=5);p.add_argument('--row',type=int,default=3);p.add_argument('--seed',type=int,default=713);p.add_argument('--steps',type=int,default=900);p.add_argument('--demo',action='store_true');AppLauncher.add_app_launcher_args(p);a=p.parse_args();a.enable_cameras=bool(a.record)
if not 0<=a.column<8 or not 0<=a.row<4 or (a.headless and not a.demo) or (a.record and a.record.exists()):p.error('Valid row/column; headless requires demo; new recording directory')
app=AppLauncher(a)
import numpy as np,torch
from PIL import Image,ImageDraw,ImageFont
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_reachable_clearance import MotionReachableRoughEnvCfg as MotionScannedRoughEnvCfg,MotionReachableRoughEnv as MotionScannedRoughEnv
from csdog_motion.training import validate_checkpoint,file_hash

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
  k=self.keys;v=[(.25 if a.full_range else .2)*(('W'in k)-('S'in k)),(.2 if a.full_range else .18)*(('A'in k)-('D'in k)),.3*(('Q'in k)-('E'in k))]
  return v if sum(abs(x)>0 for x in v)<=1 else [0,0,0]
 def close(self):self.input.unsubscribe_to_keyboard_events(self.keyboard,self.sub)

def main():
 torch.set_num_threads(1);torch.manual_seed(a.seed);np.random.seed(a.seed);cfg=MotionScannedRoughEnvCfg();meta=validate_checkpoint(a.checkpoint,cfg,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
 cfg.scene.num_envs=1;cfg.sim.device=a.device;cfg.terrain_row=a.row;cfg.terrain.terrain_generator.seed=a.seed;cfg.seed=a.seed;cfg.periodic_commands=False;cfg.episode_length_s=120.;cfg.robot.spawn.usd_dir=tempfile.mkdtemp(prefix='csdog_scanned_rough_');cfg.viewer.resolution=(960,720)
 env=ViewEnv(cfg,render_mode='rgb_array' if a.record else None);keyboard=None;encoder=None
 try:
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
    if a.demo:cmd=[(.25 if a.full_range else .2),0,0] if 100<=step<550 else [0,0,.3] if 600<=step<750 else [0,0,0]
    else:
     for key in keyboard.pending:
      if key=='T':obs,_=env.reset()
     keyboard.pending.clear();cmd=keyboard.command()
    env.set_motion_request(cmd);obs,_,term,trunc,_=env.step(policy.act_inference(TensorDict(obs,batch_size=[1])));r=env._robot.data;terminations+=int(term[0]);finite &= bool(torch.isfinite(obs['policy']).all());h=float(env._support_height()[0]);v=torch.cat((r.root_lin_vel_b[0,:2],r.root_ang_vel_b[0,2:3])).cpu().tolist();root=r.root_pos_w[0].cpu().numpy()
    if step%2==0:
     env.sim.set_camera_view(tuple(root+np.array([1.05,-1.35,.60])),tuple(root+np.array([.05,0.,-.13])))
     if encoder:
      frame=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(frame);draw.rectangle((0,0,960,78),fill=(24,29,36));title='上台阶' if a.column==5 else '下台阶' if a.column==4 else '上缓坡' if a.column==3 else '地形运动'
      draw.text((12,5),f'地形稳定课程｜{title} → 停步 → 缓转｜{step*.02:.2f}s',font=font,fill='white');draw.text((12,38),f'实际 vx/vy/yaw {v[0]:+.2f}/{v[1]:+.2f}/{v[2]:+.2f}｜离地高度 {h:.3f}m',font=font,fill='white');encoder.stdin.write(np.asarray(frame).tobytes())
      if step in (350,550,700):frame.save(a.record/f'frame_{step:04d}.png')
    trace.append({'seconds':(step+1)*.02,'position':(r.root_pos_w[0]-env._terrain.env_origins[0]).cpu().tolist(),'support_height':h,'root_ground_w':float(env._surfaces()[0,0]),'actual_twist':v,'command':cmd,'scan_range_m':float((env.height_scanner.data.ray_hits_w[:,:,2].amax(1)-env.height_scanner.data.ray_hits_w[:,:,2].amin(1))[0]),'tilt_deg':float(torch.acos((-r.projected_gravity_b[0,2]).clamp(-1,1))*180/torch.pi),'terminated':bool(term[0])})
    if not a.demo:time.sleep(max(0.,.02-(time.monotonic()-start)))
  if encoder:encoder.stdin.close();error=encoder.stderr.read().decode();code=encoder.wait();assert code==0,error
  output=(a.record/'preview.json') if a.record else Path(f'outputs/motion_foundation/lesson22_play_{time.time_ns()}.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps({'complete':len(trace)==a.steps if a.demo else True,'seconds':len(trace)*.02,'unexpected_terminations':terminations,'finite':finite,'checkpoint_sha256':file_hash(a.checkpoint),'terrain_seed':a.seed,'row':a.row,'column':a.column,'motion_contract':cfg.motion_contract,'new_ppo_updates':0,'full_range':a.full_range,'trace':trace},indent=2)+'\n');print('Terrain preview saved',output,flush=True)
 finally:
  if keyboard:keyboard.close()
  if encoder and encoder.poll() is None:encoder.kill()
  env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
