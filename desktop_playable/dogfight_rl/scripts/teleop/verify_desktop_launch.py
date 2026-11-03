#!/usr/bin/env python3
"""X11/XTest acceptance: real OS keyboard events into the Isaac window, never policy injection."""
import ctypes as c,os,re,time,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'runs/validation';records=[]
x=c.CDLL('libX11.so.6');xt=c.CDLL('libXtst.so.6')
x.XOpenDisplay.argtypes=[c.c_char_p];x.XOpenDisplay.restype=c.c_void_p
display=x.XOpenDisplay(None)
if not display:raise RuntimeError('X11 unavailable')
x.XStringToKeysym.argtypes=[c.c_char_p];x.XStringToKeysym.restype=c.c_ulong
x.XKeysymToKeycode.argtypes=[c.c_void_p,c.c_ulong];x.XKeysymToKeycode.restype=c.c_uint
x.XFlush.argtypes=[c.c_void_p];x.XCloseDisplay.argtypes=[c.c_void_p]
xt.XTestFakeKeyEvent.argtypes=[c.c_void_p,c.c_uint,c.c_int,c.c_ulong]
xt.XTestFakeMotionEvent.argtypes=[c.c_void_p,c.c_int,c.c_int,c.c_int,c.c_ulong]
xt.XTestFakeButtonEvent.argtypes=[c.c_void_p,c.c_uint,c.c_int,c.c_ulong]
def key(name,down):
 code=x.XKeysymToKeycode(display,x.XStringToKeysym(name.encode()))
 xt.XTestFakeKeyEvent(display,code,int(down),0);x.XFlush(display)
 records.append(dict(wall=time.time(),event=name,pressed=down));print(name,down,flush=True)
def tap(name):key(name,True);time.sleep(.08);key(name,False)
def held(names,seconds=2.):
 for n in names:key(n,True)
 time.sleep(seconds)
 for n in names:key(n,False)
 time.sleep(.8)
existing=set((ROOT/'runs/battle/teleop').glob('*/identity.json'))
desktop=Path(subprocess.check_output(['xdg-user-dir','DESKTOP'],text=True).strip())/'机器狗对战环境.desktop'
launched=subprocess.run(['gio','launch',str(desktop)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
proc=None
try:
 run=None
 for _ in range(110):
  found=set((ROOT/'runs/battle/teleop').glob('*/identity.json'))-existing
  if found:run=next(iter(found)).parent;break

  time.sleep(.5)
 if run is None:raise TimeoutError('GUI startup >55 seconds')
 tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
 line=next(l for l in tree.splitlines() if '"Isaac Sim 5.1.0"' in l)
 win=line.strip().split()[0]
 info=subprocess.check_output(['xwininfo','-id',win],text=True)
 px=int(re.search(r'Absolute upper-left X:\s+(\d+)',info)[1]);py=int(re.search(r'Absolute upper-left Y:\s+(\d+)',info)[1])
 xt.XTestFakeMotionEvent(display,-1,px+500,py+350,0)
 xt.XTestFakeButtonEvent(display,1,1,0);xt.XTestFakeButtonEvent(display,1,0,0);x.XFlush(display);time.sleep(.7)
 pid=json.loads((run/'identity.json').read_text())['pid']
 duplicate=subprocess.run([str(ROOT/'scripts/launch_dogfight_teleop.sh'),'--duration','1'],env=dict(os.environ,DOGFIGHT_NO_DIALOG='1'),capture_output=True,text=True,timeout=5)
 assert duplicate.returncode==1 and '已经运行' in duplicate.stderr
 tap('c');held(['w'],2.);held(['s'],2.);held(['w','q'],2.);held(['w','e'],2.)
 key('w',True);time.sleep(1.);tap('space');time.sleep(1.);key('w',False);time.sleep(1.)
 tap('c');held(['w'],1.);tap('r');time.sleep(1.)
 # Capture only this application's rectangle, never unrelated desktop windows.
 width=int(re.search(r'Width:\s+(\d+)',info)[1]);height=int(re.search(r'Height:\s+(\d+)',info)[1])
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-video_size',f'{width}x{height}','-i',f'{os.environ["DISPLAY"]}+{px},{py}','-frames:v','1','-update','1',str(run/'desktop_verified.png')],check=True)
 tap('c');tap('Escape')
 for _ in range(100):
  if (run/'metrics.json').exists():break
  time.sleep(.2)
 assert (run/'metrics.json').exists(),'Esc failed to exit'
 time.sleep(2.)
 alive=Path(f'/proc/{pid}').exists()
 (OUT/'desktop_launch_acceptance.json').write_text(json.dumps(dict(run=str(run),desktop=str(desktop),events=records,pid=pid,process_exited=not alive,duplicate_rejected=True,launch_method='gio launch actual desktop file; XTest real keyboard; human double-click not tested'),indent=2))
 print('DESKTOP_LAUNCH_RESULT',run,'process_exited',not alive,flush=True)

finally:
 for n in ['w','s','a','d','q','e','space']:key(n,False)
 if proc is not None and proc.poll() is None:proc.terminate();proc.wait(timeout=30)
 x.XCloseDisplay(display)
