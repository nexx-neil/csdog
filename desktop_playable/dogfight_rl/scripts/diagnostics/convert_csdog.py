"""Convert only the new raw model; original URDF/Mesh remain unchanged."""
from pathlib import Path
from isaaclab.app import AppLauncher
app=AppLauncher(headless=True).app
try:
 from isaaclab.sim.converters import UrdfConverter,UrdfConverterCfg
 root=Path(__file__).resolve().parents[2]
 class PreserveInertiaConverter(UrdfConverter):
  def _get_urdf_import_config(self):
   cfg=super()._get_urdf_import_config();cfg.set_import_inertia_tensor(True);return cfg
 cfg=UrdfConverterCfg(asset_path=str(root.parent/'model/robot.urdf'),usd_dir=str(root/'assets/csdog_12dof/import_v1'),usd_file_name='csdog.usd',fix_base=False,merge_fixed_joints=False,make_instanceable=True,
  joint_drive=UrdfConverterCfg.JointDriveCfg(gains=UrdfConverterCfg.JointDriveCfg.PDGainsCfg(stiffness=0.,damping=0.)),self_collision=False)
 c=PreserveInertiaConverter(cfg)
 print('CONVERTED',c.usd_path,flush=True)
finally:app.close(wait_for_replicator=False,skip_cleanup=True)
