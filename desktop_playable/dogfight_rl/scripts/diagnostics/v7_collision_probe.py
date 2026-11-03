"""Independent collision layer and equal-target physical comparison; never trains PPO."""
from pathlib import Path
import sys,json,hashlib,os
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
OUT=ROOT/'runs/locomotion/csdog_phase_guided_ppo_v7';OUT.mkdir(exist_ok=True)
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
import faulthandler
faulthandler.dump_traceback_later(60,repeat=True)
try:
 import numpy as np,torch,gymnasium as gym
 torch.set_num_threads(4)
 from pxr import Usd,UsdGeom,UsdPhysics,Gf,Sdf
 from scipy.spatial.transform import Rotation
 import dogfight.locomotion
 from dogfight.locomotion.robot_cfg import AUDIT,FEET,JOINTS
 from dogfight.locomotion.curriculum_v6.config import EnvCfg
 from dogfight.locomotion.spot_v2.contacts import contact_state
 from dogfight.locomotion.model_audit import MODEL,mesh_vertices
 protected=[MODEL/'robot.urdf',*MODEL.rglob('*.stl'),*MODEL.rglob('*.STL'),* (ROOT/'assets/csdog_12dof/import_v1').rglob('*')]
 hashes={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in protected if p.is_file()}
 (OUT/'protected_assets_sha256.json').write_text(json.dumps(hashes,indent=2))
 original=ROOT/'assets/csdog_12dof/import_v1/csdog.usd'
 dest=ROOT/'assets/csdog_12dof/collision_sole_candidate';dest.mkdir(exist_ok=True)
 stage=Usd.Stage.Open(str(original));colliders=[]
 for prim in Usd.PrimRange.Stage(stage,Usd.TraverseInstanceProxies()):
  if prim.HasAPI(UsdPhysics.CollisionAPI):
   colliders.append(dict(path=str(prim.GetPath()),type=prim.GetTypeName(),approximation=prim.GetAttribute('physics:approximation').Get()))
 # Flatten into a new artifact: visual meshes, bodies, masses and joints preserved.
 stage.Flatten().Export(str(dest/'csdog.usda'))
 candidate=Usd.Stage.Open(str(dest/'csdog.usda'))
 for p in list(candidate.Traverse()):
  if p.IsInstance():p.SetInstanceable(False)
 # Fit sole to original minimum plane at the calibrated standing joint targets.
 # Geometry is per-body local, no added body, joint, drive, mass, or inertia.
 from dogfight.locomotion.model_audit import inspect
 model=inspect();legs={};radius=.012
 for leg,body in zip(('lf','rf','lr','rr'),FEET):
  rot=np.eye(3)
  for j in [next(j for j in model['joints'] if j['name']==f'joint_{leg}_{i}') for i in (1,2,3)]:
   rot=rot@Rotation.from_rotvec(np.array(j['axis'])*AUDIT['standing_pose'][j['name']]).as_matrix()
  v=mesh_vertices(MODEL/'meshes'/(body+'_collision.stl')); tip=np.array(AUDIT['feet_local'][body])
  world=v@rot.T;old_min=world[:,2].min()
  # Keep distal x/y; sole lowest point lies on calibrated common plane (-.36m).
  # Original feet-local points are at -.35 relative root by calibration.
  delta=-.010  # shift representative cap point 10mm down, not absolute local z
  center=tip+rot.T@np.array([0.,0.,delta+radius])
  bodies=[p for p in candidate.Traverse() if p.GetName()==body and p.HasAPI(UsdPhysics.RigidBodyAPI)]
  assert len(bodies)==1,(body,[str(p.GetPath()) for p in bodies]);bp=bodies[0].GetPath()
  disabled=[]
  for p in list(candidate.Traverse()):
   if p.GetPath().HasPrefix(bp) and p.HasAPI(UsdPhysics.CollisionAPI):
    UsdPhysics.CollisionAPI(p).CreateCollisionEnabledAttr(False);disabled.append(str(p.GetPath()))
  # Preserve the original distal contact contour, trim away the shaft.
  from scipy.spatial import ConvexHull
  height=(v@rot.T)[:,2];cap=np.unique(v[height<height.min()+.014],axis=0)
  hull=ConvexHull(cap)
  sole=UsdGeom.Mesh.Define(candidate,str(bp)+'/v7_sole')
  sole.CreatePointsAttr([Gf.Vec3f(*x) for x in cap]);sole.CreateFaceVertexCountsAttr([3]*len(hull.simplices));sole.CreateFaceVertexIndicesAttr(hull.simplices.flatten().tolist())
  sole.CreateSubdivisionSchemeAttr('none');UsdPhysics.CollisionAPI.Apply(sole.GetPrim());UsdPhysics.MeshCollisionAPI.Apply(sole.GetPrim()).CreateApproximationAttr('convexHull')
  sole.CreateVisibilityAttr('invisible')
  # Shaft finishes well above sole; no overlapping collision volume.
  axis=tip/np.linalg.norm(tip);start=axis*.018;end=tip-axis*.055
  shaft=UsdGeom.Capsule.Define(candidate,str(bp)+'/v7_shaft');shaft.CreateRadiusAttr(.008);shaft.CreateHeightAttr(float(np.linalg.norm(end-start)));shaft.CreateAxisAttr('Z')
  xf=UsdGeom.Xformable(shaft);xf.AddTranslateOp().Set(Gf.Vec3d(*((start+end)/2)))
  direction=(end-start)/np.linalg.norm(end-start);q=Gf.Rotation(Gf.Vec3d(0,0,1),Gf.Vec3d(*direction)).GetQuat();xf.AddOrientOp().Set(Gf.Quatf(q))
  UsdPhysics.CollisionAPI.Apply(shaft.GetPrim());shaft.CreateVisibilityAttr('invisible')
  legs[leg]=dict(body=body,sole_center=center.tolist(),sole_radius=radius,shaft_start=start.tolist(),shaft_end=end.tolist(),shaft_radius=.008,original_local_bounds=[v.min(0).tolist(),v.max(0).tolist()],disabled=disabled,original_stance_min_relative_body=float(old_min),sole_vertices=cap.tolist(),sole_type='convex_cap')
 candidate.GetRootLayer().Save()
 manifest=dict(original=str(original),candidate=str(dest/'csdog.usda'),colliders=colliders,legs=legs,note='collision_original references immutable import_v1; candidate same 13 bodies/12 joints/inertias; shortened narrowed capsule and original distal convex cap per existing knee body')
 (OUT/'collision_geometry.json').write_text(json.dumps(manifest,indent=2))
 results={}
 for name,asset in [('collision_original',original),('collision_sole_candidate',dest/'csdog.usda')]:
  if os.environ.get('V7_COLLISION_ONLY') and name!=os.environ['V7_COLLISION_ONLY']:continue
  cfg=EnvCfg();cfg.scene.num_envs=4;cfg.seed=42;cfg.sim.device='cuda:0';cfg.episode_length_s=30.
  cfg.scene.robot.spawn.usd_path=str(asset);cfg.events.reset_base.params['pose_range']={};cfg.events.reset_joints.params['position_range']=(0.,0.)
  env=gym.make('Dogfight-CSDog-Velocity-Flat-v0',cfg=cfg).unwrapped;env.reset(seed=42);r=env.scene['robot'];records=[]
  for t in range(500):
   if t%100==0:print('PROBE_PROGRESS',name,t,flush=True)
   cmd=env.command_manager.get_term('base_velocity');cmd.vel_command_b.zero_();cmd.is_standing_env[:]=True;cmd.time_left[:]=100.
   action=torch.zeros(4,12,device=env.device)
   # Identical joint targets: single LF knee lift for 1s, then return.
   if 250<=t<300:action[:,2]=1.
   obs,rew,done,trunc,extra=env.step(action);s=contact_state(env)
   # Sphere exact clearance for candidate, full original convex hull otherwise.
   clear=s.clearance.clone()
   if name=='collision_sole_candidate':
    from isaaclab.utils.math import quat_apply
    ids=env._csdog_feet_ids;minimum=[]
    for i,leg in enumerate(('lf','rf','lr','rr')):
     cv=torch.tensor(legs[leg]['sole_vertices'],device=env.device,dtype=torch.float)
     w=quat_apply(r.data.body_quat_w[:,ids[i],None,:].expand(-1,len(cv),-1),cv[None].expand(4,-1,-1))+r.data.body_pos_w[:,ids[i],None,:]
     minimum.append(w[:,:,2].min(-1).values)
    clear=torch.stack(minimum,1)
   records.append(dict(t=(t+1)*env.step_dt,root_z=r.data.root_pos_w[:,2].tolist(),tilt=r.data.projected_gravity_b[:,:2].norm(dim=-1).tolist(),force=s.force.tolist(),point=s.point.tolist(),raw_force=s.raw_force.tolist(),shin=s.shin.tolist(),clearance=clear.tolist(),slip=s.velocity[:,:,:2].norm(dim=-1).tolist(),torque=r.data.applied_torque.tolist(),falls=done.tolist()))
  steady=records[100:240]
  results[name]=dict(bodies=r.body_names,joints=r.joint_names,mass=float(r.root_physx_view.get_masses()[0].sum()),records=records,
    summary=dict(height=float(np.mean([x['root_z'] for x in steady])),tilt=float(np.mean([x['tilt'] for x in steady])),force=np.mean([x['force'] for x in steady],axis=(0,1)).tolist(),clearance=np.mean([x['clearance'] for x in steady],axis=(0,1)).tolist(),shin_rate=float(np.mean([x['shin'] for x in steady])),slip=float(np.mean([x['slip'] for x in steady])),torque_rms=float(np.sqrt(np.mean(np.square([x['torque'] for x in steady])))),falls=int(np.sum([x['falls'] for x in records]))))
  (OUT/(name+'_physics.json')).write_text(json.dumps(results[name],indent=2))
  print('ARM_DONE',name,results[name]['summary'],flush=True)
  env.close()
 for name in ('collision_original','collision_sole_candidate'):
  p=OUT/(name+'_physics.json')
  if p.exists():results[name]=json.loads(p.read_text())
 (OUT/'collision_physics.json').write_text(json.dumps(results,indent=2))
 assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest()==h for p,h in hashes.items())
 print('V7_COLLISION_RESULTS',json.dumps({k:v['summary'] for k,v in results.items()}),flush=True)
except BaseException:
 import traceback;traceback.print_exc()
 raise
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
