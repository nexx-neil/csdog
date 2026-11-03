"""Always-on visual ray. No weapon, cooldown, health, or physics-body mutation."""
import math
from dataclasses import dataclass

@dataclass
class LaserHit:
    distance: float
    object_path: str | None
    endpoint: tuple

class LaserEmitter:
    def __init__(self,agent,config,query,visual=None):
        self.agent=agent;self.config=config;self.query=query;self.visual=visual
        if config.get('damage_enabled'):raise ValueError('LaserEmitter never applies damage')
        self.last=None
    def update(self):
        origin=self.agent.get_muzzle_origin_world();direction=self.agent.get_forward_vector_world()
        norm=math.sqrt(sum(v*v for v in direction));direction=tuple(v/norm for v in direction)
        distance=float(self.config['max_range']);path=None
        if self.config['raycast_enabled']:
            hits=self.query(origin,direction,distance)
            valid=[h for h in hits if 0 <= h['distance'] <= distance and h['path'] and not (h['path']==self.agent.prim_path or h['path'].startswith(self.agent.prim_path+'/'))]
            if valid:
                hit=min(valid,key=lambda h:h['distance']);distance=hit['distance'];path=hit['path']
        end=tuple(origin[i]+direction[i]*distance for i in range(3))
        self.last=LaserHit(distance,path,end)
        if self.visual:self.visual(origin,end,self.config['enabled'])
        return self.last

class PhysXAllHits:
    def __init__(self):
        import omni.physx
        self.query=omni.physx.get_physx_scene_query_interface()
    def __call__(self,origin,direction,distance):
        hits=[]
        def report(hit):
            path=str(hit.collision or hit.rigid_body or '')
            hits.append(dict(path=path,distance=float(hit.distance)))
            return True
        self.query.raycast_all(origin,direction,distance,report)
        return hits

class CylinderLaserVisual:
    """Tiny emissive USD cylinder, no collision/rigid-body schema."""
    def __init__(self,radius=.006,prim_path='/World/TeleopLaser'):
        import omni.usd
        from pxr import UsdGeom,UsdShade,Sdf,Gf
        self.Gf=Gf;self.geom=UsdGeom.Cylinder.Define(omni.usd.get_context().get_stage(),prim_path)
        self.geom.CreateRadiusAttr(radius);self.geom.CreateAxisAttr('Z');self.geom.CreateHeightAttr(1.)
        self.xform=UsdGeom.Xformable(self.geom);self.translate=self.xform.AddTranslateOp();self.orient=self.xform.AddOrientOp();self.scale=self.xform.AddScaleOp()
        stage=omni.usd.get_context().get_stage();mat=UsdShade.Material.Define(stage,prim_path+'Material')
        shader=UsdShade.Shader.Define(stage,prim_path+'Material/Shader');shader.CreateIdAttr('UsdPreviewSurface')
        shader.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set((1.,0.,0.))
        shader.CreateInput('emissiveColor',Sdf.ValueTypeNames.Color3f).Set((2.,0.,0.))
        mat.CreateSurfaceOutput().ConnectToSource(shader.ConnectableAPI(),'surface')
        UsdShade.MaterialBindingAPI.Apply(self.geom.GetPrim()).Bind(mat)
    def __call__(self,origin,end,enabled):
        if not enabled:self.scale.Set((0.,0.,0.));self.geom.MakeInvisible();return
        self.geom.MakeVisible();Gf=self.Gf
        start=Gf.Vec3d(*origin);finish=Gf.Vec3d(*end);delta=finish-start;length=delta.GetLength()
        self.scale.Set((1.,1.,max(length,.00001)));self.translate.Set((start+finish)*.5)
        self.orient.Set(Gf.Quatf(Gf.Rotation(Gf.Vec3d(0,0,1),delta.GetNormalized()).GetQuat()))
