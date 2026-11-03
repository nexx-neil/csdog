"""Independent right-hand viewport; only the view camera follows the real agent."""
import math

DEFAULTS = dict(enabled=True, resolution=[640, 360], offset=[.22, 0., .16],
                horizontal_fov_deg=85., pitch_deg=-6., position_smoothing=.06,
                yaw_smoothing=.08, right_fraction=.34, hide_editors=True)

class FirstPersonPose:
    """Level horizon, yaw follows the robot; no physical state is ever changed."""
    def __init__(self, config):
        self.config=dict(DEFAULTS, **config);self.reset()
    def reset(self): self.eye=None;self.yaw=None
    def update(self, position, yaw, dt):
        cfg=self.config;x,y,z=position;ox,oy,oz=cfg['offset']
        target=(x+math.cos(yaw)*ox-math.sin(yaw)*oy,
                y+math.sin(yaw)*ox+math.cos(yaw)*oy,z+oz)
        if self.eye is None or math.dist(self.eye,target)>1.:
            self.eye=target;self.yaw=yaw
        else:
            alpha=1.-math.exp(-dt/max(.001,cfg['position_smoothing']))
            beta=1.-math.exp(-dt/max(.001,cfg['yaw_smoothing']))
            self.eye=tuple(a+alpha*(b-a) for a,b in zip(self.eye,target))
            error=math.atan2(math.sin(yaw-self.yaw),math.cos(yaw-self.yaw))
            self.yaw+=beta*error
        pitch=math.radians(cfg['pitch_deg'])
        direction=(math.cos(self.yaw)*math.cos(pitch),math.sin(self.yaw)*math.cos(pitch),math.sin(pitch))
        return self.eye,tuple(self.eye[i]+direction[i] for i in range(3))

class FirstPersonView:
    TITLE='DOG A | First Person'
    CAMERA_PATH='/World/TeleopFirstPersonCamera'
    def __init__(self, agent, config):
        import omni.ui as ui
        import omni.usd
        from omni.kit.widget.viewport import ViewportWidget
        from omni.kit.viewport.utility import get_active_viewport_window
        from pxr import Gf,UsdGeom
        self.agent=agent;self.config=dict(DEFAULTS,**config);self.pose=FirstPersonPose(self.config)
        self.Gf=Gf;self.hidden_editors=[];self.update_count=0;self.last={};self.docked=False
        self.main_viewport=get_active_viewport_window()
        self.main_title=self.main_viewport.title if self.main_viewport else "Viewport"
        self.main_camera=str(self.main_viewport.viewport_api.camera_path) if self.main_viewport else None
        stage=omni.usd.get_context().get_stage()
        self.camera=UsdGeom.Camera.Define(stage,self.CAMERA_PATH)
        aperture=20.955
        self.camera.CreateHorizontalApertureAttr(aperture)
        self.camera.CreateVerticalApertureAttr(aperture*self.config['resolution'][1]/self.config['resolution'][0])
        self.camera.CreateFocalLengthAttr(aperture/(2*math.tan(math.radians(self.config['horizontal_fov_deg']/2))))
        self.camera.CreateClippingRangeAttr((.025,50.))
        self.transform=UsdGeom.Xformable(self.camera).AddTransformOp()
        self.update(.02)
        self.window=ui.Window(self.TITLE,width=640,height=480)
        with self.window.frame:
            with ui.VStack(spacing=5):
                ui.Label('FIRST PERSON  |  dog_a  |  live',height=26,style={'font_size':18})
                self.widget=ViewportWidget(camera_path=self.CAMERA_PATH,resolution=tuple(self.config['resolution']))
                ui.Label('WASD / Q E: drive   Space: STOP   C: unlock   R: reset',height=24,style={'font_size':13})
        self.widget.viewport_api.fill_frame=False
        # Hide editor tabs so the right-hand region is available to the live feed.
        if self.config['hide_editors']:
            for name in ('Stage','Layer','Layers','Render Settings','Property','Semantics Schema Editor'):
                editor=ui.Workspace.get_window(name)
                if editor:
                    self.hidden_editors.append((editor,editor.visible));editor.visible=False
        # Kit must finish UI construction before docking by WindowHandle.
        self.apply_layout()
        print('FIRST_PERSON_READY '+self.CAMERA_PATH,flush=True)
    def apply_layout(self):
        import omni.ui as ui
        source=ui.Workspace.get_window(self.TITLE);target=ui.Workspace.get_window(self.main_title)
        if source and target:
            source.dock_in(target,ui.DockPosition.RIGHT,self.config['right_fraction'])
            self.docked=True
        else:self.window.position_x=900;self.window.position_y=70
    def reset_tracking(self):self.pose.reset()
    def update(self,dt):
        data=self.agent.articulation.data
        root=tuple(float(v) for v in data.root_pos_w[self.agent._environment_index])
        eye,target=self.pose.update(root,self.agent.get_pose().yaw,dt)
        Gf=self.Gf
        self.transform.Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*target),Gf.Vec3d(0,0,1)).GetInverse())
        self.update_count+=1
        self.last=dict(eye=eye,target=target,camera_path=self.CAMERA_PATH,updates=self.update_count,docked=self.docked,main_camera_unchanged=(str(self.main_viewport.viewport_api.camera_path)==self.main_camera if self.main_viewport else None))
        if self.update_count in (6,18) and hasattr(self,'window'):self.apply_layout()
        return self.last
    def close(self):
        self.widget.destroy();self.window.destroy()
        # This close path runs during application shutdown. Re-showing Kit editor
        # tabs here can run their callbacks before their lazy widgets exist.
        # They remain available from the Window menu; no third-party code is changed.
        self.hidden_editors.clear()

class StackedFirstPersonViews:
    """Three cameras in one right-hand dock, with per-agent health headings."""
    TITLE='DOGFIGHT | Three First Person Views'
    def __init__(self,agents,config):
        import omni.ui as ui,omni.usd
        from omni.kit.widget.viewport import ViewportWidget
        from omni.kit.viewport.utility import get_active_viewport_window
        from pxr import UsdGeom,Gf
        self.Gf=Gf;self.agents=agents;self.config=dict(DEFAULTS,**config)
        self.main=get_active_viewport_window();self.main_title=self.main.title if self.main else 'Viewport'
        self.main_camera=str(self.main.viewport_api.camera_path) if self.main else None
        self.views={};self.labels={};self.widgets=[];self.updates=0;self.docked=False;self.last={}
        stage=omni.usd.get_context().get_stage()
        for name,agent in agents.items():
            path='/World/FirstPerson/'+name;camera=UsdGeom.Camera.Define(stage,path);aperture=20.955
            camera.CreateHorizontalApertureAttr(aperture)
            camera.CreateVerticalApertureAttr(aperture*self.config['resolution'][1]/self.config['resolution'][0])
            camera.CreateFocalLengthAttr(aperture/(2*math.tan(math.radians(self.config['horizontal_fov_deg']/2))))
            camera.CreateClippingRangeAttr((.025,50.))
            self.views[name]=(FirstPersonPose(self.config),UsdGeom.Xformable(camera).AddTransformOp(),path)
        self.window=ui.Window(self.TITLE,width=640,height=850)
        colors={'dog_a':0xFF7777FF,'dog_b':0xFFFFBB77,'dog_c':0xFF88EE88}
        with self.window.frame:
            with ui.VStack(spacing=3):
                for name in agents:
                    with ui.Frame(height=ui.Fraction(1)):
                        with ui.VStack(spacing=1):
                            self.labels[name]=ui.Label(name.upper(),height=22,style={'font_size':17,'color':colors[name]})
                            widget=ViewportWidget(camera_path=self.views[name][2],resolution=tuple(self.config['resolution']))
                            widget.viewport_api.fill_frame=False;self.widgets.append(widget)
                ui.Label('Space: pause | C: resume | R: reset | V: navigation routes',height=18,style={'font_size':11})
        if self.config['hide_editors']:
            for name in ('Stage','Layer','Layers','Render Settings','Property','Semantics Schema Editor'):
                win=ui.Workspace.get_window(name)
                if win:win.visible=False
        self.apply_layout();self.update(.02)
    def apply_layout(self):
        import omni.ui as ui
        source=ui.Workspace.get_window(self.TITLE);target=ui.Workspace.get_window(self.main_title)
        if source and target:source.dock_in(target,ui.DockPosition.RIGHT,self.config['right_fraction']);self.docked=True
    def reset_tracking(self):
        for pose,_,_ in self.views.values():pose.reset()
    def update(self,dt,state=None):
        for name,agent in self.agents.items():
            pose,transform,path=self.views[name];root=tuple(float(x) for x in agent.articulation.data.root_pos_w[0])
            eye,target=pose.update(root,agent.get_pose().yaw,dt);Gf=self.Gf
            transform.Set(Gf.Matrix4d().SetLookAt(Gf.Vec3d(*eye),Gf.Vec3d(*target),Gf.Vec3d(0,0,1)).GetInverse())
            self.last[name]=dict(eye=eye,target=target,camera_path=path)
            if state:
                health=state['agents'][name];mode=state.get('navigation',{}).get(name,{}).get('state') or ('WASD/QE' if name=='dog_a' else 'KEYPAD 1-9' if name=='dog_b' else 'STAND')
                self.labels[name].text=f"{name.upper()} | {mode} | HP {health['health']:.0f}/{state['max_health']:.0f} | {'ALIVE' if health['alive'] else 'DEAD'}"
        self.updates+=1
        if self.updates in (6,18):self.apply_layout()
        return self.last
    def close(self):
        for widget in self.widgets:widget.destroy()
        self.window.destroy()
