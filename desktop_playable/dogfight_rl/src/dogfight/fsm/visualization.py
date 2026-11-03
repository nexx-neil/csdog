"""Native debug draw buffers: explicit clear/redraw, no USD/Fabric geometry cache."""
class RouteVisuals:
    def __init__(self,ids,config):
        import omni.kit.app
        manager=omni.kit.app.get_app().get_extension_manager()
        manager.set_extension_enabled_immediate('isaacsim.util.debug_draw',True)
        from isaacsim.util.debug_draw import _debug_draw
        self.draw=_debug_draw.acquire_debug_draw_interface()
        self.colors=dict(zip(ids,((1.,.04,.03,1.),(.04,.22,1.,1.),(.04,1.,.08,1.))))
        self.z=config['route_height_m'];self.width=config['route_line_width_px'];self.enabled=True;self.rows={}
        self.clear()
    def clear(self):
        self.draw.clear_lines();self.draw.clear_points();self.rows={}
    def update(self,agents,controllers,enabled=True):
        self.clear();self.enabled=enabled
        starts=[];ends=[];line_colors=[];points=[];point_colors=[];sizes=[]
        for name,color in self.colors.items():
            agent=agents[name];s=controllers[name].status() if name in controllers else None
            active=enabled and agent.is_alive() and s and s['planning'] not in ('dead','round_over')
            self.rows[name]=dict(route='invisible',vertices=0,markers={k:'invisible' for k in ('position','goal','waypoint')})
            if not active:continue
            pose=agent.get_pose();path=[(pose.x,pose.y)]+s['path']
            if len(path)>1:
                lifted=[(x,y,self.z) for x,y in path]
                starts.extend(lifted[:-1]);ends.extend(lifted[1:]);line_colors.extend([color]*(len(lifted)-1))
                self.rows[name].update(route='visible',vertices=len(lifted))
            for key,xy,size in (('position',(pose.x,pose.y),8.),('goal',s['navigation_goal'],12.),('waypoint',s['waypoint'],6.)):
                if xy is not None:
                    points.append((xy[0],xy[1],self.z+.025));point_colors.append(color);sizes.append(size)
                    self.rows[name]['markers'][key]='visible'
        if starts:self.draw.draw_lines(starts,ends,line_colors,[self.width]*len(starts))
        if points:self.draw.draw_points(points,point_colors,sizes)
    def diagnostics(self):
        return dict(backend='isaacsim.util.debug_draw',prim_count=0,physics_schemas=0,enabled=self.enabled,
                    line_count=self.draw.get_num_lines(),point_count=self.draw.get_num_points(),visible=self.rows)
