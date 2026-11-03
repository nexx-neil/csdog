#!/usr/bin/env python3
"""DOGFIGHT V0.2 real CSDog inference in the existing TestMap; never trains."""
import os,sys,json,argparse,datetime,uuid
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
sys.dont_write_bytecode=True
from dogfight.teleop.config import load_settings
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--config',default='configs/teleop/default.yaml');p.add_argument('--map',default=None);p.add_argument('--robot',default=None)
p.add_argument('--duration',type=float,default=0.,help='Simulated seconds, 0 means interactive until Esc/close')
p.add_argument('--scenario',choices=['interactive','motion','wall','laser','dual-motion','combat','occlusion','range-check','fsm-recovery','navigation-check'],default='interactive')
p.add_argument('--autostart',action='store_true',help='Start autonomous match after GUI initialization (validation only)')
p.add_argument('--exit-on-result',action='store_true',help='Exit after a completed autonomous round')
p.add_argument('--preflight',action='store_true')
p.add_argument('--width',type=int,default=1600);p.add_argument('--height',type=int,default=900)
from isaaclab.app import AppLauncher
AppLauncher.add_app_launcher_args(p);args=p.parse_args()
args.window_width=1440;args.window_height=900
if args.rendering_mode is None:args.rendering_mode="balanced"
settings,robot=load_settings(args.config,args.map,args.robot)
# PhysX CPU scene queries must see current articulation transforms. GPU renders
# remain enabled; three 12-DOF dogs run faster than real time on this host's CPU.
if settings.get('mode') in ('three_dog_battle','fsm_battle'):
 if '--device' not in sys.argv and not any(a.startswith('--device=') for a in sys.argv):
  args.device=settings.get('simulation',{}).get('device','cpu')
 if args.scenario in ('motion','laser'):
  p.error('For single-dog motion/laser validation use --config configs/teleop/single_dog.yaml; three-dog modes: dual-motion, combat, occlusion, wall.')
 if args.device!='cpu':
  p.error('Three-dog combat currently requires --device cpu for accurate moving-body PhysX raycasts; RTX rendering still uses the GPU.')
if args.duration<0:p.error('duration must be nonnegative')
if args.preflight:
 from dogfight.teleop.policy import PolicyLoader
 _,meta=PolicyLoader.load(robot['checkpoint'],robot['contract'])
 print(json.dumps(dict(settings=settings,robot=robot,actor=meta),indent=2));raise SystemExit(0)
out=ROOT/'runs/battle/teleop'/ (datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'_'+uuid.uuid4().hex[:8]);out.mkdir(parents=True)
(out/'launch.json').write_text(json.dumps(dict(argv=sys.argv,python=sys.executable,started=datetime.datetime.now().isoformat(),settings=settings,robot=robot),indent=2))
import fcntl
lock=(ROOT/"runs/battle/teleop/runtime.lock").open("a+")
try:
 fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
except BlockingIOError:
 raise SystemExit("已有机器狗遥控仿真正在运行，请先关闭原窗口。")
lock.seek(0);lock.truncate();lock.write(str(os.getpid()));lock.flush()
app=None
try:
 screenshots=out/'screenshots';screenshots.mkdir()
 args.kit_args=(args.kit_args or '')+f' --/app/captureFrame/path={screenshots}/ --/persistent/app/captureFrame/path={screenshots}/'
 app=AppLauncher(args).app
 if args.rendering_mode == "balanced":
  import carb.settings
  carb.settings.get_settings().set_int("/rtx/post/dlss/execMode",2)  # DLSS Quality; balanced preset enables denoising
 if settings.get("mode") in ("three_dog_battle","fsm_battle"):
  from dogfight.teleop.multi_runtime import run
 else:
  from dogfight.teleop.runtime import run
 raise SystemExit(run(app,args,settings,robot,out))
except Exception:
 import traceback
 (out/'ERROR.txt').write_text(traceback.format_exc());raise
finally:
 if app is not None:app.close(wait_for_replicator=False,skip_cleanup=True)
