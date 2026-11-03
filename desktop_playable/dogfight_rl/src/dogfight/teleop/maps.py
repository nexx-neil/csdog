"""Map registry consumes the existing V0 MapInterface; no robot/rule dependency."""
from dogfight_v0.arena.test_map import TestMap, WallSpec
from dogfight_v0.arena.map_interface import MapInterface

class BoundedTestMap(TestMap):
    def __init__(self, boundary_walls=True):
        super().__init__()
        if boundary_walls:
            lo,hi,bottom,top=self.get_bounds();t=.2;h=1.2
            self.walls += [WallSpec('/World/TestMap/Boundary/'+n,c,s) for n,c,s in [
                ('west',(lo-t/2,0,h/2),(t,top-bottom+2*t,h)),
                ('east',(hi+t/2,0,h/2),(t,top-bottom+2*t,h)),
                ('south',(0,bottom-t/2,h/2),(hi-lo,t,h)),
                ('north',(0,top+t/2,h/2),(hi-lo,t,h))]]

class MapRegistry:
    def __init__(self): self.factories={}
    def register(self,name,factory):
        if name in self.factories: raise ValueError(f'Map already registered: {name}')
        self.factories[name]=factory
    def create(self,name,**options):
        if name not in self.factories: raise ValueError(f'Unknown map {name}; registered: {list(self.factories)}')
        arena=self.factories[name](**options)
        if not isinstance(arena,MapInterface): raise TypeError('Map does not implement V0 MapInterface')
        arena.load();arena.reset()
        if not arena.get_spawn_points(): raise ValueError('Map has no spawn')
        return arena

MAPS=MapRegistry()
MAPS.register('test_map',BoundedTestMap)

def create_selected_map(settings):
    return MAPS.create(settings["map"]["name"],boundary_walls=settings["map"].get("boundary_walls",True))

def build_map(arena):
    """Materialize map-provided geometry only; shared with no particular robot."""
    import isaaclab.sim as sim
    data=arena.get_navigation_data()
    lo,hi,bottom,top=arena.get_bounds()
    ground=sim.GroundPlaneCfg(size=(hi-lo+2,top-bottom+2),physics_material=sim.RigidBodyMaterialCfg(
        static_friction=1.,dynamic_friction=1.,restitution=0.,friction_combine_mode='multiply',restitution_combine_mode='multiply'))
    ground.func('/World/TestMap/Ground',ground)
    for wall in data['walls']:
        cfg=sim.CuboidCfg(size=wall.size,collision_props=sim.CollisionPropertiesCfg(),
            visual_material=sim.PreviewSurfaceCfg(diffuse_color=(.35,.35,.38)))
        cfg.func(wall.path,cfg,translation=wall.center)
    light=sim.DomeLightCfg(intensity=1800.,color=(.85,.9,1.))
    light.func('/World/Light',light)
