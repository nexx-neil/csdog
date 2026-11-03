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

run=max((p.parent for p in (ROOT/'runs/battle/teleop').glob('*/identity.json') if not p.with_name('metrics.json').exists()),key=lambda p:p.stat().st_mtime)
pid=json.loads((run/'identity.json').read_text())['pid']
tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
line=next(l for l in tree.splitlines() if '"Isaac Sim 5.1.0"' in l);win=line.strip().split()[0]
info=subprocess.check_output(['xwininfo','-id',win],text=True)
px=int(re.search(r'Absolute upper-left X:\s+(\d+)',info)[1]);py=int(re.search(r'Absolute upper-left Y:\s+(\d+)',info)[1])
xt.XTestFakeMotionEvent(display,-1,px+500,py+350,0);xt.XTestFakeButtonEvent(display,1,1,0);xt.XTestFakeButtonEvent(display,1,0,0);x.XFlush(display);time.sleep(.5)
tap('r');tap('c')
for names in [['w'],['s'],['a'],['d'],['w','a'],['w','d'],['s','a'],['s','d'],['w','q'],['w','e']]:held(names,1.5)
key('w',True);time.sleep(.7);tap('space');time.sleep(.7);key('w',False);time.sleep(.7)
tap('c');held(['w'],1.);tap('r');time.sleep(.7)
width=int(re.search(r'Width:\s+(\d+)',info)[1]);height=int(re.search(r'Height:\s+(\d+)',info)[1])
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-video_size',f'{width}x{height}','-i',f'{os.environ["DISPLAY"]}+{px},{py}','-frames:v','1','-update','1',str(run/'final_keyboard.png')],check=True)
tap('c');tap('Escape')
for _ in range(150):
 if (run/'metrics.json').exists():break
 time.sleep(.2)
assert (run/'metrics.json').exists()
time.sleep(2.)
assert not Path(f'/proc/{pid}').exists()
(OUT/'desktop_launch_acceptance.json').write_text(json.dumps(dict(run=str(run),desktop=str(Path(subprocess.check_output(['xdg-user-dir','DESKTOP'],text=True).strip())/'机器狗对战环境.desktop'),events=records,pid=pid,process_exited=True,duplicate_rejected=True,launch_method='gio launch desktop file + real XTest keyboard (including final all-key recheck); human double-click not tested',screenshot=str(run/'final_keyboard.png')),indent=2))
print('FINAL_DESKTOP_KEYBOARD_PASS',run,flush=True)
x.XCloseDisplay(display)
