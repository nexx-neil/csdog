#!/usr/bin/env python3
"""Inference-only keyboard/demo player for guarded v11 locomotion and crouch/rise."""
import argparse,json,subprocess,time,traceback,tempfile
from pathlib import Path
from isaaclab.app import AppLauncher
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--checkpoint',type=Path,default=ROOT/'outputs/motion_foundation/lesson12_candidate/candidate.pt')
p.add_argument('--profile',choices=('trot',),default='trot')
p.add_argument('--speed',choices=('agile',),default='agile')
p.add_argument('--demo-tour',action='store_true')
p.add_argument('--demo',action='store_true');p.add_argument('--steps',type=int,default=3000)
p.add_argument('--record',type=Path);p.add_argument('--metrics-output',type=Path)
AppLauncher.add_app_launcher_args(p);a=p.parse_args()
if a.demo_tour and (not a.demo or a.profile not in ('agile','yaw','trot')):p.error('Demo tour requires --demo --profile agile')
if a.speed=='agile' and a.profile not in ('agile','yaw','trot'):p.error('Agile keyboard speeds require the agile controller profile')
if a.steps<=0 or (a.headless and not a.demo):p.error('Positive steps required; headless playback requires --demo')
if a.record and a.record.exists():p.error('New recording directory required')
if a.metrics_output and a.metrics_output.exists():p.error('New metrics path required')
a.enable_cameras=bool(a.record);app=AppLauncher(a)
import numpy as np,torch
import gymnasium as gym
from tensordict import TensorDict
from rsl_rl.modules import ActorCritic
import stackforce_simready_generated_robot_lab.tasks
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_clean import MotionCleanEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_skills import MotionSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_transfer import MotionBackwardEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_skills import MotionBackwardSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_responsive_skills import MotionResponsiveSkillsEnvCfg
from csdog_motion.teleop import keyboard_twist
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_agile_skills import MotionAgileSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_yaw import MotionYawEnvCfg,MotionYawSkillsEnvCfg
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_skills import MotionTrotSkillsEnvCfg,MotionTrotSkillsEnv
from stackforce_simready_generated_robot_lab.tasks.direct.motion_foundation.motion_trot_course import MotionTrotEnvCfg
from csdog_motion.skill_supervisor import SkillMode,SkillFault
from csdog_motion.training import validate_checkpoint,file_hash
from csdog_motion.trot_policy_routing import routing_record,with_saved_routing


class Keyboard:
    def __init__(self):
        import carb,omni.appwindow
        self.carb=carb;self.pressed=set();self.blocked=set();self.pending=[];self.quit=False
        window=omni.appwindow.get_default_app_window()
        if window is None:raise RuntimeError('Keyboard requires an Isaac Sim app window')
        self.input=carb.input.acquire_input_interface();self.keyboard=window.get_keyboard()
        self.subscription=self.input.subscribe_to_keyboard_events(self.keyboard,self.event)
    def event(self,event,*args):
        key=event.input.name;types=self.carb.input.KeyboardEventType
        if event.type==types.KEY_RELEASE:
            self.pressed.discard(key);self.blocked.discard(key)
        elif event.type in (types.KEY_PRESS,types.KEY_REPEAT):
            if key in ('C','R','SPACE','T') and event.type==types.KEY_PRESS:
                self.blocked.update(self.pressed);self.pressed.clear();self.pending.append(key)
            elif key=='ESCAPE':self.quit=True
            elif key in ('W','S','A','D','Q','E') and key not in self.blocked:self.pressed.add(key)
        return True
    def command(self):
        return [.8,0.,0.] if self.pressed=={'W'} else keyboard_twist(self.pressed,a.speed)
    def close(self):self.input.unsubscribe_to_keyboard_events(self.keyboard,self.subscription)


def main():
    torch.set_num_threads(1)
    tag=__import__('json').loads(Path(str(a.checkpoint)+'.metadata.json').read_text())['checkpoint_compatibility_tag']
    parent=MotionTrotEnvCfg() if tag==MotionTrotEnvCfg().checkpoint_compatibility_tag else MotionYawEnvCfg()
    meta=validate_checkpoint(a.checkpoint,parent,policy_only=True);assert meta['checkpoint_sha256']==file_hash(a.checkpoint)
    cfg=MotionTrotSkillsEnvCfg();route=routing_record(a.checkpoint)
    if route is not None:cfg.motion_contract=dict(cfg.motion_contract,policy_routing=route)
    assert not cfg.training_enabled and not cfg.residual_training_enabled
    cfg.scene.num_envs=1;cfg.sim.device=a.device;cfg.seed=713;cfg.episode_length_s=max(90.,a.steps*.02+10)
    cfg.robot.spawn.usd_dir=tempfile.mkdtemp(prefix='csdog_trot_skills_')
    cfg.viewer.resolution=(960,720);cfg.viewer.eye=(.95,-1.3,.75);cfg.viewer.lookat=(.12,0.,.19)
    env=MotionTrotSkillsEnv(cfg,render_mode='rgb_array' if a.record else None);raw=env.unwrapped
    keyboard=None;encoder=None;status=None;trace=[];failures=0;faulted=False
    try:
        with torch.inference_mode():obs,_=env.reset()
        policy=ActorCritic(TensorDict(obs,batch_size=[1]),{'policy':['policy'],'critic':['policy']},12,actor_hidden_dims=[256,256,128],critic_hidden_dims=[256,256,128],activation='elu')
        policy.to(raw.device);policy.load_state_dict(torch.load(a.checkpoint,map_location=raw.device,weights_only=True)['model_state_dict']);policy.eval();policy=with_saved_routing(policy,a.checkpoint)
        if not a.demo:
            keyboard=Keyboard()
            import omni.ui as ui
            window=ui.Window('CSDog guarded skills',width=420,height=150)
            with window.frame:
                with ui.VStack():
                    ui.Label(f'W/S move | A/D strafe | Q/E turn | {a.speed}')
                    ui.Label('C crouch | R stand | SPACE stop | T reset')
                    status=ui.Label('Click the viewport for keyboard input')
            print('Click viewport. C brakes then crouches. A move key while crouched first raises the body. R stands. SPACE stops; T explicitly resets; ESC exits.',flush=True)
        if a.record:
            from PIL import Image,ImageDraw,ImageFont
            a.record.mkdir(parents=True)
            font=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',22)
            encoder=subprocess.Popen(['ffmpeg','-hide_banner','-loglevel','error','-f','rawvideo','-pix_fmt','rgb24','-s','960x720','-r','25','-i','-','-an','-c:v','libx264','-crf','20','-pix_fmt','yuv420p','-movflags','+faststart',str(a.record/'preview.mp4')],stdin=subprocess.PIPE,stderr=subprocess.PIPE)
        mode_names={SkillMode.LOCOMOTION:'行走/站立',SkillMode.BRAKE:'减速并等待四足站稳',SkillMode.LOWER:'降身',SkillMode.HOLD:'保持蹲伏',SkillMode.RISE:'起身',SkillMode.SETTLE:'站稳后放行移动',SkillMode.FAULT:'故障保持'}
        with torch.inference_mode():
            for step in range(a.steps):
                started=time.monotonic()
                if not app.app.is_running() or (keyboard and keyboard.quit):break
                if a.demo_tour:
                    tour={0:[0,0,0],100:[.8,0,0],350:[0,0,0],600:[0,.4,0],700:[0,0,.8],800:[0,0,0]}
                    if step in tour:raw.set_motion_request(tour[step])
                    if step in (400,850):raw.request_crouch()
                    if step in (500,900):raw.request_stand()
                elif a.demo:
                    if step==0:raw.set_motion_request([-(.5 if a.speed in ('fast','agile') else .3),0,0] if a.profile!="clean" else [.2,0,0])
                    if step==150:raw.request_crouch()
                    if step==500:raw.set_motion_request([-.3,0,0] if a.profile!="clean" else [.2,0,.15])
                    if step==900:raw.set_motion_request([0,0,0])
                    if step==1000:raw.request_crouch()
                    if step==1250:raw.request_stand()
                else:
                    actions=keyboard.pending;keyboard.pending=[]
                    for key in actions:
                        if key=='C':raw.request_crouch()
                        elif key=='R':raw.request_stand()
                        elif key=='SPACE':raw.set_motion_request([0,0,0])
                        elif key=='T':obs,_=env.reset()
                    raw.set_motion_request(keyboard.command())
                action=policy.act_inference(TensorDict(obs,batch_size=[1]));obs,_,term,_,_=env.step(action);failures+=int(term.sum())
                if not torch.isfinite(obs['policy']).all():raise RuntimeError('Nonfinite skill observation')
                r=raw._robot.data;root=r.root_pos_w[0].cpu().numpy();h=float(root[2]-raw._terrain.env_origins[0,2]);mode=SkillMode(int(raw.skills.mode[0]));fault=SkillFault(int(raw.skills.fault[0]));faulted|=mode==SkillMode.FAULT
                velocity=torch.cat((r.root_lin_vel_b[:,:2],r.root_ang_vel_b[:,2:3]),1)[0].cpu().tolist()
                if status is not None:status.text=f'{mode.name}  height {h:.3f}m  vx/vy/yaw {velocity[0]:+.2f}/{velocity[1]:+.2f}/{velocity[2]:+.2f}  fault {fault.name}'
                if step%2==0:
                    raw.sim.set_camera_view(tuple(root+np.array([.95,-1.3,.5])),tuple(root+np.array([0.,0.,-.15])))
                    if encoder:
                        canvas=Image.fromarray(env.render().copy());draw=ImageDraw.Draw(canvas);draw.rectangle((0,0,960,92),fill=(24,29,36))
                        draw.text((15,8),f'小跑与快速四足浅蹲｜{mode_names[mode]}｜{step*.02:.2f}s',font=font,fill='white')
                        draw.text((15,39),f'高度 {h:.3f}m   实际vx/vy/yaw {velocity[0]:+.2f}/{velocity[1]:+.2f}/{velocity[2]:+.2f}   C降身 R起身',font=font,fill=(190,215,235))
                        encoder.stdin.write(np.asarray(canvas).tobytes())
                        if step in (300,650,1100):canvas.save(a.record/f'frame_{step:04d}.png')
                trace.append({'seconds':step*.02,'mode':mode.name,'height':h,'height_command':float(raw.motion.applied[0,3]),'command':raw.motion.applied[0,:3].cpu().tolist(),'actual_twist':velocity,'fault':fault.name,'terminated':bool(term[0]),'contacts':(torch.linalg.vector_norm(raw._contact_sensor.data.net_forces_w[0,raw._foot_ids],dim=-1)>1.).cpu().tolist(),'phase':float(raw.motion.phase[0]),'q':raw._robot.data.joint_pos[0,raw._actuated_joint_ids].cpu().tolist(),'root_quat_wxyz':raw._robot.data.root_quat_w[0].cpu().tolist(),'tilt_deg':float(torch.acos((-raw._robot.data.projected_gravity_b[0,2]).clamp(-1,1))*180/torch.pi)})
                if a.demo and mode==SkillMode.FAULT:break
                if not a.demo:time.sleep(max(0.,raw.step_dt-(time.monotonic()-started)))
        if encoder:
            encoder.stdin.close();error=encoder.stderr.read().decode();code=encoder.wait()
            if code:raise RuntimeError(error)
        summary={'complete':len(trace)==a.steps if a.demo else True,'script_sha256':file_hash(__file__),'demo':a.demo,'keyboard_speed':a.speed,'demo_tour':a.demo_tour,'seconds':len(trace)*.02,'fps':25,'checkpoint':str(a.checkpoint.resolve()),'checkpoint_sha256':file_hash(a.checkpoint),
            'motion_contract':cfg.motion_contract,'training_updates':0,'unexpected_terminations':failures,'faulted':faulted,
            'visited_modes':sorted(set(x['mode'] for x in trace)),'scope':'guarded flat-ground inference only; no jump/belly-contact or hardware control','trace':trace}
        output=a.metrics_output or (a.record/'preview.json' if a.record else ROOT/'outputs/motion_foundation'/f'guarded_play_{time.time_ns()}.json')
        output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(summary,indent=2)+'\n');print('Guarded playback complete:',output,flush=True)
    finally:
        if keyboard:keyboard.close()
        if encoder and encoder.poll() is None:encoder.kill()
        env.close()
try:main()
except BaseException:traceback.print_exc();raise
finally:app.app.close()
