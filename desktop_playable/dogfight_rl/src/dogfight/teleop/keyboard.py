"""Hold-to-drive state machine; simulation, policy and map independent."""
import math
import time
from dogfight_v0.battle.types import VelocityCommand

class KeyboardTeleopController:
    MOTION=set('WSADQE')
    def __init__(self,config,clock=time.monotonic):
        self.cfg=config;self.clock=clock;self.pressed=set();self.estop=False
        self.quit_requested=False;self.reset_requested=False;self.last_input=clock()
        self.output=VelocityCommand();self.last_stop_reason=None
    def event(self,key,pressed=True):
        key=key.upper();self.last_input=self.clock()
        if not pressed:self.pressed.discard(key);return
        if key=='SPACE':self.emergency_stop()
        elif key=='C':self.last_stop_reason=None;self.estop=False;self.pressed.clear();self.output=VelocityCommand()
        elif key=='R':self.reset_requested=True;self.pressed.clear();self.output=VelocityCommand()
        elif key in ('ESC','ESCAPE'):self.quit_requested=True;self.emergency_stop()
        elif key in self.MOTION and not self.estop:self.pressed.add(key)
    def emergency_stop(self,reason='manual'):
        self.last_stop_reason=reason;self.estop=True;self.pressed.clear();self.output=VelocityCommand()
    def focus_lost(self):self.emergency_stop('focus_lost')
    def heartbeat(self):self.last_input=self.clock()
    def command(self,dt):
        if not math.isfinite(dt) or dt<=0: self.emergency_stop('invalid_dt')
        if self.clock()-self.last_input>self.cfg['input_timeout']:self.emergency_stop('input_timeout')
        if self.estop or self.quit_requested:return VelocityCommand()
        p=self.pressed
        if any(a in p and b in p for a,b in [('W','S'),('A','D'),('Q','E')]):
            self.output=VelocityCommand();return self.output
        vx=(self.cfg['forward_speed'] if 'W' in p else -self.cfg['backward_speed'] if 'S' in p else 0.)
        yaw=self.cfg['yaw_rate']*(int('A' in p)-int('D' in p))
        if 'Q' in p or 'E' in p:
            vx=0.;yaw=self.cfg['yaw_rate']*(int('Q' in p)-int('E' in p))
        alpha=1.-math.exp(-dt/self.cfg['smoothing_time']) if self.cfg['command_smoothing'] else 1.
        # Release and forced zero are immediate; smoothing never defeats stop/rotation priority.
        self.output=VelocityCommand(vx and self.output.vx+alpha*(vx-self.output.vx),0.,yaw and self.output.yaw_rate+alpha*(yaw-self.output.yaw_rate))
        return self.output

class X11Focus:
    """Fail-closed foreground PID check for the current Ubuntu X11 session."""
    def __init__(self):
        import ctypes as c,os
        self.c=c;self.pid=os.getpid();self.x=c.CDLL('libX11.so.6')
        self.x.XOpenDisplay.argtypes=[c.c_char_p];self.x.XOpenDisplay.restype=c.c_void_p
        self.display=self.x.XOpenDisplay(None)
        if not self.display:raise RuntimeError('Cannot open X11 display for keyboard focus protection')
        self.x.XDefaultRootWindow.argtypes=[c.c_void_p];self.x.XDefaultRootWindow.restype=c.c_ulong
        self.root=self.x.XDefaultRootWindow(self.display)
        self.x.XInternAtom.argtypes=[c.c_void_p,c.c_char_p,c.c_int];self.x.XInternAtom.restype=c.c_ulong
        self.x.XGetWindowProperty.argtypes=[c.c_void_p,c.c_ulong,c.c_ulong,c.c_long,c.c_long,c.c_int,c.c_ulong,c.POINTER(c.c_ulong),c.POINTER(c.c_int),c.POINTER(c.c_ulong),c.POINTER(c.c_ulong),c.POINTER(c.POINTER(c.c_ubyte))]
        self.x.XFree.argtypes=[c.c_void_p];self.x.XCloseDisplay.argtypes=[c.c_void_p]
    def prop(self,window,name):
        c=self.c;typ=c.c_ulong();fmt=c.c_int();n=c.c_ulong();after=c.c_ulong();ptr=c.POINTER(c.c_ubyte)()
        atom=self.x.XInternAtom(self.display,name.encode(),0)
        ok=self.x.XGetWindowProperty(self.display,window,atom,0,1,0,0,c.byref(typ),c.byref(fmt),c.byref(n),c.byref(after),c.byref(ptr))
        try:return c.cast(ptr,c.POINTER(c.c_ulong))[0] if ok==0 and n.value else None
        finally:
            if ptr:self.x.XFree(ptr)
    def focused(self):
        active=self.prop(self.root,'_NET_ACTIVE_WINDOW')
        return bool(active and self.prop(active,'_NET_WM_PID')==self.pid)
    def close(self):
        if self.display:self.x.XCloseDisplay(self.display);self.display=None

class IsaacKeyboard:
    def __init__(self,controller):
        import carb.input,omni.appwindow
        self.carb=carb.input;self.controller=controller
        self.window=omni.appwindow.get_default_app_window();self.keyboard=self.window.get_keyboard()
        self.input=carb.input.acquire_input_interface();self.focus=X11Focus();self.had_focus=None;self.last_poll=controller.clock()
        self.debug_count=0
        self.subscription=self.input.subscribe_to_keyboard_events(self.keyboard,self.on_event)
    def on_event(self,event,*args):
        try:
            # Carb callbacks can carry either pybind enums or symbolic strings.
            key=str(getattr(event.input,'name',event.input)).rsplit('.',1)[-1].upper()
            kind=str(getattr(event.type,'name',event.type)).rsplit('.',1)[-1].upper()
            if self.debug_count<12:
                print('KEY_EVENT',repr(event.input),repr(event.type),key,kind,self.focus.focused(),flush=True);self.debug_count+=1
            if kind in ('KEY_PRESS','KEY_REPEAT'):
                if self.focus.focused():self.controller.event(key)
            elif kind=='KEY_RELEASE':self.controller.event(key,False)
            return key not in (self.controller.MOTION | {'SPACE','C','R','ESCAPE','V'})
        except Exception:
            self.controller.emergency_stop()
            return False
    def poll(self):
        try:
            now=self.controller.clock()
            if now-self.last_poll>self.controller.cfg["input_timeout"]:self.controller.emergency_stop('input_poll_stall')
            self.last_poll=now
            focused=self.focus.focused()
            if not focused:
                self.controller.focus_lost();self.had_focus=False;return
            self.had_focus=True
            # Poll physical key state in addition to events: handles held keys and missing releases.
            for key in self.controller.MOTION:
                value=self.input.get_keyboard_value(self.keyboard,getattr(self.carb.KeyboardInput,key))
                if value<=0:self.controller.event(key,False)
            self.controller.heartbeat()
        except Exception as exc:
            self.controller.emergency_stop()
            raise RuntimeError('Keyboard input/focus failed; commands stopped') from exc
    def close(self):
        self.controller.emergency_stop()
        self.input.unsubscribe_to_keyboard_events(self.keyboard,self.subscription);self.focus.close()

class KeypadTeleopController(KeyboardTeleopController):
    """Dedicated physical keypad; number-row keys never steer dog_b."""
    MOTION={f'NUMPAD_{i}' for i in range(1,10)}
    MAP={'NUMPAD_8':'W','NUMPAD_2':'S','NUMPAD_4':'A','NUMPAD_6':'D',
         'NUMPAD_7':'WA','NUMPAD_9':'WD','NUMPAD_1':'SA','NUMPAD_3':'SD'}
    def event(self,key,pressed=True):
        if key=='NUMPAD_5' and pressed:
            self.pressed.clear();self.output=VelocityCommand()
        super().event(key,pressed)
    def command(self,dt):
        raw=self.pressed
        if 'NUMPAD_5' in raw:
            self.output=VelocityCommand();return self.output
        try:
            self.pressed=set(''.join(self.MAP.get(k,'') for k in raw))
            return super().command(dt)
        finally:self.pressed=raw

class DualDogKeyboard:
    """One OS keyboard subscription, two isolated command histories and a global safety latch."""
    MOTION=KeyboardTeleopController.MOTION | KeypadTeleopController.MOTION
    def __init__(self,config,clock=time.monotonic):
        self.cfg=config;self.clock=clock;self.navigation_visible=True;self._v_down=False
        self.controllers={'dog_a':KeyboardTeleopController(config,clock),
                          'dog_b':KeypadTeleopController(config,clock)}
    def event(self,key,pressed=True):
        if key=='V':
            if pressed and not self._v_down:self.navigation_visible=not self.navigation_visible
            self._v_down=pressed
            return
        if key.startswith('NUMPAD_'):self.controllers['dog_b'].event(key,pressed)
        elif key in {'SPACE','C','R','ESC','ESCAPE'}:
            for controller in self.controllers.values():controller.event(key,pressed)
        else:self.controllers['dog_a'].event(key,pressed)
    @property
    def last_stop_reason(self):return next((c.last_stop_reason for c in self.controllers.values() if c.estop),None)
    def emergency_stop(self,reason='manual'):
        for controller in self.controllers.values():controller.emergency_stop(reason)
    def focus_lost(self):self.emergency_stop('focus_lost')
    def heartbeat(self):
        for controller in self.controllers.values():controller.heartbeat()
    def command_for(self,agent_id,dt):
        return self.controllers[agent_id].command(dt) if agent_id in self.controllers else VelocityCommand()
    @property
    def estop(self):return any(c.estop for c in self.controllers.values())
    @property
    def quit_requested(self):return any(c.quit_requested for c in self.controllers.values())
    @quit_requested.setter
    def quit_requested(self,value):
        for c in self.controllers.values():c.quit_requested=value
    @property
    def reset_requested(self):return any(c.reset_requested for c in self.controllers.values())
    @reset_requested.setter
    def reset_requested(self,value):
        for c in self.controllers.values():c.reset_requested=value
