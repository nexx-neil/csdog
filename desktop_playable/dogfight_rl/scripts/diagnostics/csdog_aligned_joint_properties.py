from pathlib import Path
import sys,json,traceback
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'src'));E=R/'runs/locomotion/csdog_ppo_spot_aligned_v3'
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 import gymnasium as gym,torch
 from dogfight.locomotion.spot_aligned_v3.config import AlignedEnvCfg
 from dogfight.locomotion.robot_cfg import JOINTS
 from pxr import Usd,UsdPhysics
 import omni.usd
 cfg=AlignedEnvCfg();cfg.scene.num_envs=1;cfg.seed=734
 e=gym.make('Dogfight-CSDog-Spot-Aligned-Flat-v3',cfg=cfg).unwrapped;r=e.scene['robot'];e.reset(seed=734)
 result={}
 for name in ['joint_stiffness','joint_damping','joint_armature','joint_friction_coeff','joint_dynamic_friction_coeff','joint_viscous_friction_coeff','joint_effort_limits','joint_vel_limits']:
  value=getattr(r.data,name,None);result[name]=value.cpu().tolist() if value is not None else None
 attrs=[]
 for prim in omni.usd.get_context().get_stage().Traverse():
  if prim.IsA(UsdPhysics.RevoluteJoint):attrs.append(dict(path=str(prim.GetPath()),attributes={x.GetName():str(x.Get()) for x in prim.GetAttributes() if any(k in x.GetName().lower() for k in ['friction','drive','armature','limit','axis','rot'])}))
 result['usd_joint_attributes']=attrs
 (E/'reports/runtime_joint_properties.json').write_text(json.dumps(result,indent=2));print('JOINT_PROPERTIES',json.dumps({k:v for k,v in result.items() if k!='usd_joint_attributes'}),flush=True);e.close()
except BaseException:traceback.print_exc();sys.stderr.flush()
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
