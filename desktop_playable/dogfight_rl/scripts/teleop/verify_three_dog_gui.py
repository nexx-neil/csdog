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
subprocess.run(['gio','launch',str(desktop)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,check=True)
run=None
for _ in range(120):
 found=set((ROOT/'runs/battle/teleop').glob('*/identity.json'))-existing
 if found:run=next(iter(found)).parent;break
 time.sleep(.5)
if run is None:raise TimeoutError('GUI startup >60 seconds')
time.sleep(3)
identity=json.loads((run/'identity.json').read_text());pid=identity['pid']
tree=subprocess.check_output(['xwininfo','-root','-tree'],text=True)
win=next(l.strip().split()[0] for l in tree.splitlines() if '"Isaac Sim 5.1.0"' in l)
info=subprocess.check_output(['xwininfo','-id',win],text=True)
px=int(re.search(r'Absolute upper-left X:\s+(\d+)',info)[1]);py=int(re.search(r'Absolute upper-left Y:\s+(\d+)',info)[1])
xt.XTestFakeMotionEvent(display,-1,px+350,py+380,0);xt.XTestFakeButtonEvent(display,1,1,0);xt.XTestFakeButtonEvent(display,1,0,0);x.XFlush(display);time.sleep(.5)
samples=[]
def sample(label):
 value=json.loads((run/'status.json').read_text());samples.append(dict(label=label,status=value));return value
def exercise(label,names,seconds=1.4):
 for name in names:key(name,True)
 time.sleep(seconds);sample(label)
 for name in names:key(name,False)
 time.sleep(.65)
try:
 tap('r');time.sleep(.8);tap('c');time.sleep(.8)
 exercise('both_forward',['w','KP_8'],2.5)
 for number in [8,2,4,6,7,9,1,3,5]:
  tap('c');exercise('keypad_'+str(number),['KP_'+str(number)])
 tap('c');exercise('A_force_left',['w','q']);tap('c');exercise('A_force_right',['w','e'])
 key('w',True);key('KP_8',True);time.sleep(.8);tap('space');time.sleep(1);sample('global_stop')
 key('w',False);key('KP_8',False);tap('c');time.sleep(.7);sample('unlocked')
 tap('r');time.sleep(1);sample('reset')
 width=int(re.search(r'Width:\s+(\d+)',info)[1]);height=int(re.search(r'Height:\s+(\d+)',info)[1])
 subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-f','x11grab','-video_size',f'{width}x{height}','-i',f'{os.environ["DISPLAY"]}+{px},{py}','-frames:v','1','-update','1',str(run/'three_dog_gui.png')],check=True)
finally:
 for n in ['w','s','a','d','q','e']+['KP_'+str(i) for i in range(1,10)]:key(n,False)
 tap('space');tap('Escape');x.XCloseDisplay(display)
for _ in range(150):
 if (run/'metrics.json').exists():break
 time.sleep(.2)
time.sleep(2)
report=dict(run=str(run),desktop=str(desktop),events=records,samples=samples,metrics=json.loads((run/'metrics.json').read_text()),process_exited=not Path(f'/proc/{pid}').exists(),screenshot=str(run/'three_dog_gui.png'))
(OUT/'three_dog_gui_acceptance.json').write_text(json.dumps(report,indent=2))
expected={8:(1,0),2:(-1,0),4:(0,1),6:(0,-1),7:(1,1),9:(1,-1),1:(-1,1),3:(-1,-1),5:(0,0)}
for s in samples:
 if s['label'].startswith('keypad_'):
  q=s['status']['agents']['dog_b']['command']
  assert ((q['vx']>0)-(q['vx']<0),(q['yaw_rate']>0)-(q['yaw_rate']<0))==expected[int(s['label'].split('_')[1])],s['label']
  assert not s['status']['estop'],s['status'].get('stop_reason')
assert report['metrics']['first_person_count']==3 and report['metrics']['first_person_docked'] and report['metrics']['main_camera_preserved']
assert report['process_exited']
print('THREE_DOG_GUI_REPORT',run,flush=True)
