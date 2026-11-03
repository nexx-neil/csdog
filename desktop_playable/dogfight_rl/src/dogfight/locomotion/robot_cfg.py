"""New URDF identity, calibrated stance and independent conservative simulation actuator."""
import json
from pathlib import Path
import isaaclab.sim as sim_utils
from isaaclab.assets import ArticulationCfg
from isaaclab.actuators import ImplicitActuatorCfg
ROOT=Path(__file__).resolve().parents[3]
AUDIT=json.loads((ROOT/'configs/locomotion/csdog_ppo/model_audit.json').read_text())
JOINTS=[f'joint_{leg}_{i}' for leg in ['lf','rf','lr','rr'] for i in [1,2,3]]
FEET=[f'link_{leg}_knee' for leg in ['lf','rf','lr','rr']]
ROBOT=ArticulationCfg(prim_path='{ENV_REGEX_NS}/Robot',
 spawn=sim_utils.UsdFileCfg(usd_path=str(ROOT/'assets/csdog_12dof/import_v1/csdog.usd'),activate_contact_sensors=True,
 rigid_props=sim_utils.RigidBodyPropertiesCfg(disable_gravity=False,max_depenetration_velocity=1.0),
 articulation_props=sim_utils.ArticulationRootPropertiesCfg(enabled_self_collisions=False,solver_position_iteration_count=8,solver_velocity_iteration_count=2)),
 init_state=ArticulationCfg.InitialStateCfg(pos=(0.,0.,AUDIT['root_height_m']),joint_pos=AUDIT['standing_pose'],joint_vel={'.*':0.}),
 actuators={'legs':ImplicitActuatorCfg(joint_names_expr=['joint_.*'],effort_limit_sim=10.,velocity_limit_sim=3.,stiffness=25.,damping=0.8)},
 soft_joint_pos_limit_factor=0.9)
