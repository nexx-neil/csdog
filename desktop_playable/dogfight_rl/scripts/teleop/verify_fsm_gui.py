#!/usr/bin/env python3
"""Actual X11 GUI acceptance. Uses desktop launcher, real key events and screenshots."""
import argparse,ctypes as c,os,re,time,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser();p.add_argument('--attach',action='store_true');p.add_argument('--battle',action='store_true');p.add_argument('--leave-paused',action='store_true');args=p.parse_args()
os.environ.setdefault('DISPLAY',':1');os.environ.setdefault('XAUTHORITY',f'/run/user/{os.getuid()}/gdm/Xauthority')
x=c.CDLL('libX11.so.6');xt=c.CDLL('libXtst.so.6');x.XOpenDisplay.argtypes=[c.c_char_p];x.XOpenDisplay.restype=c.c_void_p;display=x.XOpenDisplay(None)
if not display:raise RuntimeError('No X11 display')
x.XStringToKeysym.argtypes=[c.c_char_p];x.XStringToKeysym.restype=c.c_ulong
x.XKeysymToKeycode.argtypes=[c.c_void_p,c.c_ulong];x.XKeysymToKeycode.restype=c.c_uint
x.XFlush.argtypes=[c.c_void_p];x.XCloseDisplay.argtypes=[c.c_void_p]
xt.XTestFakeKeyEvent.argtypes=[c.c_void_p,c.c_uint,c.c_int,c.c_ulong]
xt.XTestFakeMotionEvent.argtypes=[c.c_void_p,c.c_int,c.c_int,c.c_int,c.c_ulong]
xt.XTestFakeButtonEvent.argtypes=[c.c_void_p,c.c_uint,c.c_int,c.c_ulong]
def tap(name):
 code=x.XKeysymToKeycode(display,x.XStringToKeysym(name.encode()))
 xt.XTestFakeKeyEvent(display,code,1,0);x.XFlush(display);time.sleep(.08)
 xt.XTestFakeKeyEvent(display,code,0,0);x.XFlush(display);time.sleep(.3)
existing=set((ROOT/'runs/battle/teleop').glob('*/identity.json'))
if not args.attach:subprocess.run(['gio','launch','/home/zxq/桌面/三狗自主对战.desktop'],check=True)
run=None
for _ in range(160):
 found=(set((ROOT/'runs/battle/teleop').glob('*/identity.json'))-existing) if not args.attach else set((ROOT/'runs/battle/teleop').glob('*/identity.json'))
 if found:
  run=max(found,key=lambda f:f.stat().st_mtime).parent
  if (run/'status.json').exists():break
 time.sleep(.5)
if run is None or not (run/'status.json').exists():raise TimeoutError('No ready status')
print('RUN',run,flush=True)
time.sleep(2)
tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
win=next(l.strip().split()[0] for l in tree.splitlines() if '"Isaac Sim 5.1.0"' in l)
info=subprocess.check_output(['xwininfo','-id',win],text=True)
px=int(re.search(r'Absolute upper-left X:\s+(-?\d+)',info)[1]);py=int(re.search(r'Absolute upper-left Y:\s+(-?\d+)',info)[1])
width=int(re.search(r'Width:\s+(\d+)',info)[1]);height=int(re.search(r'Height:\s+(\d+)',info)[1])
xt.XTestFakeMotionEvent(display,-1,px+350,py+400,0);xt.XTestFakeButtonEvent(display,1,1,0);xt.XTestFakeButtonEvent(display,1,0,0);x.XFlush(display);time.sleep(.6)
def screenshot(label):
 path=run/(label+'.png')
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-video_size',f'{width}x{height}','-i',f'{os.environ["DISPLAY"]}+{px},{py}','-frames:v','1','-update','1',str(path)],check=True)
 return str(path)
def status():return json.loads((run/'status.json').read_text())
report={'run':str(run),'screenshots':[],'samples':{}}
try:
 if args.leave_paused:
  tap('space');time.sleep(.8);report['samples']['handoff']=status();report['screenshots'].append(screenshot('fsm_handoff_paused'))
 else:
  tap('c');time.sleep(2);report['screenshots'].append(screenshot('fsm_routes_on'));report['samples']['running']=status()
 if args.battle:
  tap('space');time.sleep(.8);a=status()['match']['time_s'];time.sleep(1.);b=status()['match']['time_s'];report['pause_frozen']=a==b
  tap('v');time.sleep(.8);report['screenshots'].append(screenshot('fsm_routes_off'))
  tap('v');time.sleep(.8);report['screenshots'].append(screenshot('fsm_routes_restored'))
  tap('r');time.sleep(1);report['samples']['reset']=status();report['screenshots'].append(screenshot('fsm_reset'))
  tap('c');start=time.monotonic();last=0
  while time.monotonic()-start<300:
   time.sleep(1);s=status();t=s['match']['time_s']
   if int(t)//20>last:
    last=int(t)//20;print('MATCH',round(t,2),'HP',{n:v['health'] for n,v in s['agents'].items()},'states',{n:v['state'] for n,v in s['match'].get('navigation',{}).items()},flush=True)
    report['screenshots'].append(screenshot('fsm_match_'+str(last*20)))
   if s['match']['round_over']:
    report['result']=s;report['screenshots'].append(screenshot('fsm_result'));break
  else:report['failure']='Match did not finish within 300 wall seconds'
finally:
 if not args.leave_paused:
  tap('space');tap('Escape')
  for _ in range(100):
   if (run/'metrics.json').exists():break
   time.sleep(.2)
 x.XCloseDisplay(display)
 if (run/'metrics.json').exists():report['metrics']=json.loads((run/'metrics.json').read_text())
 (run/'fsm_gui_acceptance.json').write_text(json.dumps(report,indent=2))
 print('REPORT',run/'fsm_gui_acceptance.json',flush=True)
