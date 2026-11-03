"""Conservative distal-contact classification from actual PhysX ground manifolds.

No synthetic contact sensor: timing below is a 50Hz proxy based on measured
points, explicitly excluding shin contact. Raw knee force remains separately available.
"""
import torch
from types import SimpleNamespace
from isaaclab.sensors import ContactSensorCfg
from isaaclab.utils.math import quat_apply
from ..robot_cfg import FEET, AUDIT
from ..mdp import feet_kinematics

def add_sensors(cfg):
 import isaaclab.sim as sim_utils
 from isaaclab.assets import AssetBaseCfg
 material=cfg.scene.terrain.physics_material if cfg.scene.terrain is not None else cfg.sim.physics_material
 cfg.scene.terrain=None
 cfg.scene.floor=AssetBaseCfg(prim_path='/World/ground_box',init_state=AssetBaseCfg.InitialStateCfg(pos=(0.,0.,-.05)),spawn=sim_utils.CuboidCfg(size=(100.,100.,.1),rigid_props=sim_utils.RigidBodyPropertiesCfg(kinematic_enabled=True,disable_gravity=True),mass_props=sim_utils.MassPropertiesCfg(mass=1.),collision_props=sim_utils.CollisionPropertiesCfg(),physics_material=material,visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(.38,.40,.43))))
 for leg,body in zip(('lf','rf','lr','rr'),FEET):
  setattr(cfg.scene,'ground_'+leg,ContactSensorCfg(prim_path='{ENV_REGEX_NS}/Robot/'+body,
   filter_prim_paths_expr=['/World/ground_box'],track_pose=True,track_contact_points=True,
   max_contact_data_count_per_prim=32,update_period=cfg.sim.dt))
 return cfg

class ContactState:
 def __init__(self,env):
  self.env=env;self.key=None
  import numpy as np
  from scipy.spatial import ConvexHull
  from ..model_audit import mesh_vertices,MODEL
  self.vertices=[]
  for body in FEET:
   v=mesh_vertices(MODEL/'meshes'/(body+'_collision.stl'))
   self.vertices.append(torch.tensor(v[ConvexHull(v).vertices],device=env.device,dtype=torch.float))
  self.data=SimpleNamespace(**{k:torch.zeros(env.num_envs,4,device=env.device) for k in
   ['current_air_time','current_contact_time','last_air_time','last_contact_time']})
 def update(self):
  e=self.env;key=e.common_step_counter
  if self.key==key:return self
  self.key=key;p,v=feet_kinematics(e);forces=[];points=[];bad=[];counts=[];raw=[]
  for i,leg in enumerate(('lf','rf','lr','rr')):
   s=e.scene['ground_'+leg];d=s.data
   f,cp,n,sep,count,start=s.contact_physx_view.get_contact_data(dt=e.physics_dt)
   count=count.reshape(e.num_envs,-1).sum(-1).long();start=start.reshape(e.num_envs,-1)[:,0].long()
   slots=torch.arange(32,device=e.device)[None,:];ix=(start[:,None]+slots).clamp(0,len(cp)-1)
   exists=slots<count[:,None];q=cp[ix]
   distal=(q-p[:,i,None]).norm(dim=-1)<0.035
   usable=exists & distal & (q[:,:,2].abs()<0.02)
   nf=f.reshape(-1)[ix].abs();weight=torch.where(usable,nf,0.)
   force=weight.sum(-1)
   point=(torch.where(usable[:,:,None],q,0.)*weight[:,:,None]).sum(1)/force[:,None].clamp_min(1e-8)
   point=torch.where((force>1.)[:,None],point,p[:,i])
   forces.append(force);points.append(point);bad.append((exists&~distal).any(-1)|(count>32));counts.append(count)
   raw.append(d.net_forces_w[:,0].norm(dim=-1))
  self.force=torch.stack(forces,1);self.point=torch.stack(points,1);self.shin=torch.stack(bad,1)
  self.count=torch.stack(counts,1);self.raw_force=torch.stack(raw,1)
  self.contact=(self.force>1.)&~self.shin
  # velocity at actual contact patch, using COM reference, all in world coordinates.
  r=e.scene['robot'];ids=e._csdog_feet_ids
  self.velocity=r.data.body_com_lin_vel_w[:,ids]+torch.cross(r.data.body_com_ang_vel_w[:,ids],self.point-r.data.body_com_pos_w[:,ids],dim=-1)
  self.tip_position=p;self.tip_velocity=v
  minimum=[]
  for i,vertices in enumerate(self.vertices):
   rotation=r.data.body_quat_w[:,ids[i],None,:].expand(-1,len(vertices),-1)
   world=quat_apply(rotation,vertices[None].expand(e.num_envs,-1,-1))+r.data.body_pos_w[:,ids[i],None,:]
   minimum.append(world[:,:,2].min(-1).values)
  self.clearance=torch.stack(minimum,1)
  reset=e.episode_length_buf<=1
  for value in vars(self.data).values():value[reset]=0.
  air=self.data.current_air_time;stance=self.data.current_contact_time
  self.first=self.contact&(air>0.)
  self.data.last_air_time=torch.where(self.first,air,self.data.last_air_time)
  self.data.last_contact_time=torch.where(~self.contact&(stance>0.),stance,self.data.last_contact_time)
  self.data.current_air_time=torch.where(~self.contact,air+e.step_dt,0.)
  self.data.current_contact_time=torch.where(self.contact,stance+e.step_dt,0.)
  return self

def contact_state(env):
 if not hasattr(env,'_spot_contact'):env._spot_contact=ContactState(env)
 return env._spot_contact.update()
