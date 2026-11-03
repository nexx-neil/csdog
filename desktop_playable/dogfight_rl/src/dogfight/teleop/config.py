"""Resource selection and immutable policy/robot ABI validation (no simulation)."""
import hashlib
import json
import math
from pathlib import Path
from dogfight.common.paths import ROOT, load_project_yaml, project_path

OBSERVATION_ORDER = ['root_lin_vel_b:3', 'root_ang_vel_b:3', 'projected_gravity_b:3',
                     'command_vx_vy_yaw:3', 'joint_pos_minus_default:12', 'joint_vel:12',
                     'previous_clipped_action:12', 'phase_sin_cos:2']
JOINT_ORDER = [f'joint_{leg}_{i}' for leg in ('lr', 'lf', 'rf', 'rr') for i in (1, 2, 3)]
CONTRACT = dict(observation_dim=50, observation_order=OBSERVATION_ORDER, action_dim=12,
                joint_order=JOINT_ORDER, hidden_dims=[256, 256, 128], activation='elu',
                observation_normalization=False, action_scale=.35, action_clip=1.,
                physics_dt=.005, policy_dt=.02, gait_cycle_time=.5,
                stiffness=40., damping=1.5, effort_limit=12., velocity_limit=10.,
                default_joint_angles=[0.] * 12, articulation_yaw_from_agent_yaw=0.)

def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def load_settings(path=None, map_name=None, robot_id=None):
    path = project_path(path or 'configs/teleop/default.yaml')
    with path.open() as stream:
        settings = load_project_yaml(stream)
    if map_name: settings['map']['name'] = map_name
    if robot_id: settings['robot'] = robot_id
    from .maps import MAPS
    if settings['map']['name'] not in MAPS.factories:
        raise ValueError('Unknown map: '+settings['map']['name'])
    if settings.get('mode') in ('three_dog_battle','fsm_battle'):
        battle=settings['battle'];weapon_range=battle.get('weapon_range_m',battle.get('range_m'))
        if weapon_range is None or not math.isfinite(weapon_range) or weapon_range<=0:raise ValueError('Positive weapon_range_m required')
        # Canonical range controls both query and display. range_m is a legacy alias.
        battle['weapon_range_m']=weapon_range;settings['laser']['max_range']=weapon_range
        if settings.get('mode')=='fsm_battle':
            nav=settings['autonomy'];nav['weapon_range_m']=weapon_range
            for key in ('intel_period_s','vision_max_range_m','decision_period_s','visual_period_s','grid_resolution_m','body_radius_m','min_plan_interval_s','waypoint_tolerance_m','corner_waypoint_tolerance_m','route_height_m','route_line_width_px','stuck_timeout_s','max_speed','max_yaw_rate'):
                if not math.isfinite(nav[key]) or nav[key]<=0:raise ValueError('Positive autonomy parameter required: '+key)
            if not math.isfinite(nav['tracking_margin_m']) or nav['tracking_margin_m']<0:raise ValueError('Negative/nonfinite tracking reserve')
            if not (0<nav['vision_fov_deg']<=360):raise ValueError('Invalid FOV')
            if nav['max_speed']>.25 or nav['max_yaw_rate']>.3:raise ValueError('FSM exceeds validated PPO command range')
            if not (0<nav['attack_enter_m']<nav['attack_exit_m']<weapon_range):raise ValueError('Attack hysteresis must fit inside weapon range')
    teleop=settings['teleop']
    if not (0 < teleop['forward_speed'] <= .25 and 0 < teleop['backward_speed'] <= .25 and 0 < teleop['yaw_rate'] <= .3):
        raise ValueError('Teleop speeds exceed the locally validated range (.25 m/s, .3 rad/s)')
    if teleop['input_timeout'] <= 0 or teleop['smoothing_time'] <= 0:
        raise ValueError('Input timeout/smoothing time must be positive')
    registry = settings['robots']
    if settings['robot'] not in registry:
        raise ValueError(f"Robot not registered: {settings['robot']}; configure robots.<id>")
    with project_path(registry[settings['robot']]).open() as stream:
        robot = load_project_yaml(stream)
    for k, v in CONTRACT.items():
        if robot['contract'].get(k) != v:
            raise ValueError(f'Incompatible policy contract: {k}: expected {v!r}')
    if settings['laser'].get('damage_enabled'):
        raise ValueError('TELEOP is visual-only: laser.damage_enabled must be false')
    asset_manifest = json.loads(project_path(robot['asset_manifest']).read_text())
    base = project_path(robot['asset_manifest']).parent
    for rel, digest in asset_manifest['files'].items():
        # Models are imported immutable; alternative policy is checked by its own manifest.
        if rel.startswith('model/') and sha256(base / rel) != digest:
            raise ValueError(f'Model resource identity mismatch: {rel}')
    for key in ('urdf', 'checkpoint', 'policy_manifest'):
        robot[key] = str(project_path(robot[key]))
    identity = json.loads(Path(robot['policy_manifest']).read_text())
    if identity['contract'] != robot['contract']:
        raise ValueError('Policy manifest and robot observation/action/control ABI mismatch')
    if sha256(robot['checkpoint']) != identity['checkpoint_sha256']:
        raise ValueError('Checkpoint SHA256 mismatch; select a matching policy manifest')
    return settings, robot
