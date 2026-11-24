"""Isolated geometric reference execution; deliberately not unlocked for PPO."""
import torch
from isaaclab.utils import configclass

from csdog_motion.calibration import ASSET
from csdog_motion.contracts import JOINT_NAMES
from csdog_motion.reference_control import REFERENCE_TAG, reference_data, reference_contract
from csdog_motion.trajectory import LegKinematics, TrajectoryConfig, foot_reference
from csdog_motion.support_feedback import support_forces,support_weights
from .motion_calibrated_cfg import MotionCalibratedEnvCfg, MotionCalibratedRunnerCfg
from .motion_env import MotionFoundationEnv


def configure_reference(cfg, data):
    """Apply an explicit diagnostic profile; never mutate the previous task."""
    cfg.motion_contract = reference_contract(data)
    pose = dict(zip(JOINT_NAMES, data["nominal_joint_positions_rad"]))
    cfg.robot.init_state.joint_pos = pose
    cfg.default_joint_angles = pose
    cfg.base_height_target = data["nominal_height_m"]
    cfg.motion_commands = dict(cfg.motion_commands,
        nominal_height_m=cfg.base_height_target, height_min_m=cfg.base_height_target,
        height_max_m=cfg.base_height_target, gait_period_s=data["trajectory"]["period_s"])
    cfg.action_scale = data["joint_target_offset_limit_rad"]
    cfg.reference_parameters = data
    gains = data.get("pd_gains", {"stiffness":40.,"damping":1.5})
    for actuator in cfg.robot.actuators.values():
        actuator.stiffness = gains["stiffness"]
        actuator.damping = gains["damping"]


@configclass
class MotionReferenceEnvCfg(MotionCalibratedEnvCfg):
    checkpoint_compatibility_tag = REFERENCE_TAG
    motion_contract = reference_contract()
    observation_space = 66
    training_enabled = False
    training_block_reason = "Reference-controller dynamics diagnostic; reward and residual-training acceptance are not yet validated"

    def __post_init__(self):
        super().__post_init__()
        configure_reference(self, reference_data())


@configclass
class MotionReferenceRunnerCfg(MotionCalibratedRunnerCfg):
    experiment_name = "csdog_motion_reference_diagnostic"


class MotionReferenceEnv(MotionFoundationEnv):
    def __init__(self, cfg, **kwargs):
        super().__init__(cfg, **kwargs)
        data = cfg.reference_parameters
        self.reference_model = LegKinematics(ASSET / "robot_sim.urdf", data["nominal_joint_positions_rad"],
            offset_bound=data["joint_target_offset_limit_rad"], device=self.device)
        self.reference_nominal = torch.tensor([data["nominal_sole_positions_body_m"][leg] for leg in ("lr","lf","rf","rr")],device=self.device)
        self.reference_config = TrajectoryConfig(**data["trajectory"])
        self.reference_q = self.reference_model.nominal_q.flatten().expand(self.num_envs,-1).clone()
        self.reference_error = torch.zeros(self.num_envs,4,device=self.device)
        self.reference_stance = torch.ones(self.num_envs,4,dtype=torch.bool,device=self.device)
        self.target_speed_limited = torch.zeros(self.num_envs,dtype=torch.bool,device=self.device)
        self._reference_tick = -1

    def _reference(self):
        if self._reference_tick == self.common_step_counter:
            return self._reference_cache
        target, stance = foot_reference(self.motion.phase, self.motion.applied[:,:3],
            self.reference_nominal, self.reference_config, blend=self.motion.blend)
        q, error = self.reference_model.solve(target, iterations=12)
        self._reference_cache = (q.flatten(1), error, stance)
        self._reference_tick = self.common_step_counter
        return self._reference_cache

    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        self._reference_tick = -1

    def _pre_physics_step(self, actions):
        self._raw_actions = actions.clone()
        self.reference_q, self.reference_error, self.reference_stance = self._reference()
        if not torch.isfinite(self.reference_q).all() or self.reference_error.max() > .001:
            raise RuntimeError("Reference IK failed; refusing to execute approximate gait")
        data = self.cfg.reference_parameters
        nominal = self.reference_model.nominal_q.flatten()
        self.previous_joint_targets = nominal + self.cfg.action_scale*self._actions
        self.last_residual_actions = actions.clamp(-1,1)*self.motion.blend[:,None]
        requested = self.reference_q + data["joint_residual_limit_rad"] * actions.clamp(-1,1) * self.motion.blend[:,None]
        feedback=self._support_parameters()
        if feedback:
            robot=self._robot.data
            foot,_=self.reference_model.fk(self.reference_q.reshape(-1,4,3))
            weights=self._support_weights()
            height=self._support_height()
            forces=support_forces(foot,foot.new_tensor(feedback["com_body_m"]),weights,
                robot.projected_gravity_b*9.81,robot.root_lin_vel_b,robot.root_ang_vel_b,
                self.motion.applied[:,:3],self.motion.applied[:,3]-height,feedback)
            torque=self.reference_model.static_support_torque(self.reference_q.reshape(-1,4,3),forces,robot.projected_gravity_b*9.81)
            gain=data.get("pd_gains",{"stiffness":40.})["stiffness"]
            correction=(torque/gain).clamp(-feedback["max_position_bias_rad"],feedback["max_position_bias_rad"]).flatten(1)
            requested=requested+correction
        limited = torch.maximum(torch.minimum(requested,self.reference_model.upper.flatten()),self.reference_model.lower.flatten())
        self.target_box_limited = (requested-limited).abs()>1e-6
        # Include initial motion from the actual reset pose; subsequent targets
        # are bounded relative to the last executed target, never stale pre-reset state.
        previous = nominal + self.cfg.action_scale * self._actions
        delta = limited-previous
        limit = data["joint_target_speed_limit_rad_s"] * self.step_dt
        self.target_speed_limited = (delta.abs()>limit+1e-6).any(dim=1)
        self._processed_actions = previous + delta.clamp(-limit,limit)
        self._processed_velocity_targets = (self._processed_actions-previous)/self.step_dt
        self._actions = (self._processed_actions-nominal)/self.cfg.action_scale
        self._pre_step_root_height = self._robot.data.root_pos_w[:,2]-self._terrain.env_origins[:,2]

    def _support_weights(self):
        return support_weights(self.motion.phase,self.motion.blend,
            self.reference_config.stance_fraction,
            self.cfg.reference_parameters.get("support_feedback",{}).get("transition"),
            twist=self.motion.applied[:,:3])

    def _support_height(self):
        return self._robot.data.root_pos_w[:,2]-self._terrain.env_origins[:,2]

    def _support_parameters(self):
        return self.cfg.reference_parameters.get("support_feedback")

    def _apply_action(self):
        super()._apply_action()
        velocity=self._processed_velocity_targets if self.cfg.reference_parameters.get("velocity_feedforward",False) else torch.zeros_like(self._processed_actions)
        self._robot.set_joint_velocity_target(velocity,joint_ids=self._actuated_joint_ids)

    def _get_observations(self):
        base = super()._get_observations()["policy"]
        if not hasattr(self,"reference_model"):
            reference = torch.zeros(self.num_envs,12,device=self.device)
        else:
            q, _, _ = self._reference()
            reference = (q-self.reference_model.nominal_q.flatten())/self.cfg.action_scale
        return {"policy":torch.cat((base,reference),dim=1)}

    def _get_rewards(self):
        # Do not accidentally optimize legacy action/contact penalties under a
        # different action meaning and stance schedule. The train entry blocks it.
        return torch.zeros(self.num_envs,device=self.device)
