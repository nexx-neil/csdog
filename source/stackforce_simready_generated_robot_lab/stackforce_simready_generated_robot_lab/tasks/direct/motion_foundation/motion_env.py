"""Command, gait and observation foundation, isolated from the legacy policy task."""

import torch

from isaaclab.utils import math as math_utils

from csdog_motion.commands import MotionCommandConfig, MotionCommandState, foot_velocity_body
from csdog_motion.curriculum import sample_lateral_balanced
from csdog_motion.action_bounds import action_bounds, executed_actions
from ..generated_robot.generated_robot_env import GeneratedRobotEnv


class MotionFoundationEnv(GeneratedRobotEnv):
    def __init__(self, cfg, **kwargs):
        if cfg.command_curriculum not in ("legacy", "balanced_lateral_v1"):
            raise ValueError("Unknown command curriculum")
        if cfg.command_curriculum == "balanced_lateral_v1":
            expected = {"lin_vel_x": (-.4, .4), "lin_vel_y": (-.3, .3), "ang_vel_yaw": (-.4, .4)}
            if any(tuple(cfg.command_ranges[key]) != value for key, value in expected.items()):
                raise ValueError("Balanced lateral curriculum requires its validated command ranges")
        self.motion = None
        super().__init__(cfg, **kwargs)
        self.motion = MotionCommandState(self.num_envs, self.device, MotionCommandConfig(**cfg.motion_commands))
        self._command_remaining = torch.zeros(self.num_envs, device=self.device)
        self._just_reset = torch.zeros(self.num_envs, dtype=torch.bool, device=self.device)
        self._motion_tick = self.common_step_counter
        self._external_commands = False
        self._action_bounds = action_bounds(cfg, self.device)

    def _pre_physics_step(self, actions):
        if self.cfg.action_clip_per_joint is None and not self.cfg.posture_blend_actions:
            return super()._pre_physics_step(actions)
        self._raw_actions = actions.clone()
        blend = self.motion.blend[:, None] if self.cfg.posture_blend_actions else None
        self._actions = executed_actions(actions, self._action_bounds, blend)
        self._pre_step_root_height = self._robot.data.root_pos_w[:, 2] - self._terrain.env_origins[:, 2]
        self._processed_actions = self.cfg.action_scale * self._actions + self._robot.data.default_joint_pos[:, self._actuated_joint_ids]

    def _sample_commands(self, env_ids):
        if self.motion is None:
            return super()._sample_commands(env_ids)
        previous = self.motion.applied[env_ids, :3].clone()
        if self.cfg.command_curriculum == "balanced_lateral_v1":
            self._commands[env_ids], _ = sample_lateral_balanced(len(env_ids), self.device)
        else:
            super()._sample_commands(env_ids)
        self.motion.set_request(self._commands[env_ids].clone(), env_ids)
        self._commands[env_ids] = previous
        lo, hi = self.cfg.command_resampling_interval_s
        self._command_remaining[env_ids] = torch.empty(len(env_ids), device=self.device).uniform_(lo, hi)

    def _reset_idx(self, env_ids):
        if env_ids is None:
            env_ids = self._robot._ALL_INDICES
        if self.motion is not None:
            self.motion.reset(env_ids)
            self._just_reset[env_ids] = True
        super()._reset_idx(env_ids)
        if self.motion is not None and self._external_commands:
            self.motion.set_request([0.0, 0.0, 0.0], env_ids)

    def set_motion_request(self, request, env_ids=None):
        """External callers own the command stream until reset by their controller."""
        self._external_commands = True
        self.motion.set_request(request, env_ids)

    def _before_observations(self):
        if self.motion is None:
            return
        if self._motion_tick != self.common_step_counter:
            ids = torch.where(~self._just_reset)[0]
            if len(ids):
                self._command_remaining[ids] -= self.step_dt
                if self.cfg.periodic_commands and not self._external_commands:
                    due = ids[self._command_remaining[ids] <= 0]
                    if len(due):
                        self._sample_commands(due)
                contacts = torch.linalg.vector_norm(
                    self._contact_sensor.data.net_forces_w[:, self._foot_ids], dim=-1
                ) > 1.0
                self.motion.tick(self.step_dt, ids, contacts)
            self._motion_tick = self.common_step_counter
        self._just_reset.zero_()
        self._commands.copy_(self.motion.applied[:, :3])

    def _get_gait_phase(self):
        return super()._get_gait_phase() if self.motion is None else self.motion.phase

    def _get_observations(self):
        legacy = super()._get_observations()["policy"]
        return {"policy": torch.cat((legacy, self.motion.extras()), dim=-1)}

    def _get_rewards(self):
        robot = self._robot.data
        twist = torch.cat((robot.root_lin_vel_b[:, :2], robot.root_ang_vel_b[:, 2:3]), dim=1)
        error = twist - self._commands
        std = error.new_tensor([self.cfg.tracking_lin_vel_std] * 2 + [self.cfg.tracking_ang_vel_std])
        contact_target, clearance = self.motion.gait_targets()
        forces = self._contact_sensor.data.net_forces_w[:, self._foot_ids]
        contacts = torch.linalg.vector_norm(forces, dim=-1) > 1.0
        foot_position = robot.body_pos_w[:, self._robot_foot_ids]
        foot_velocity = robot.body_lin_vel_w[:, self._robot_foot_ids]
        offset = foot_position - robot.root_pos_w[:, None]
        quaternion = robot.root_quat_w[:, None].expand(-1, 4, -1).reshape(-1, 4)
        relative_velocity = foot_velocity - robot.root_lin_vel_w[:, None] - torch.cross(
            robot.root_ang_vel_w[:, None].expand_as(offset), offset, dim=-1
        )
        velocity_body = math_utils.quat_apply_inverse(quaternion, relative_velocity.reshape(-1, 3)).reshape(-1, 4, 3)
        # Combined SE(2) stance reference; no yaw-only fixed foot-position target.
        nominal_xy = error.new_tensor(self.cfg.nominal_foot_positions_body_m)[:, :2]
        stance_reference = foot_velocity_body(self._commands, nominal_xy)
        foot_height = foot_position[:, :, 2] - self._terrain.env_origins[:, 2:3] - 0.018
        joint_deviation = robot.joint_pos[:, self._actuated_joint_ids] - robot.default_joint_pos[:, self._actuated_joint_ids]
        if self._undesired_contact_body_ids:
            collision = torch.sum(torch.max(torch.linalg.vector_norm(
                self._contact_sensor.data.net_forces_w_history[:, :, self._undesired_contact_body_ids], dim=-1
            ), dim=1)[0] > 1.0, dim=1).float()
        else:
            collision = torch.zeros(self.num_envs, device=self.device)
        terms = {
            "tracking_twist": torch.exp(-torch.sum((error / std).square(), dim=1)),
            "twist_error": torch.sum(error.square(), dim=1),
            "base_height": (robot.root_pos_w[:, 2] - self._terrain.env_origins[:, 2] - self.motion.applied[:, 3]).square(),
            "orientation": torch.sum(robot.projected_gravity_b[:, :2].square(), dim=1),
            "ang_vel_xy": torch.sum(robot.root_ang_vel_b[:, :2].square(), dim=1),
            "normal_velocity": (robot.root_lin_vel_w[:, 2] - self.motion.height_rate).square(),
            "contact_schedule": 1 - torch.mean(torch.abs(contacts.float() - contact_target), dim=1),
            "swing_clearance": torch.mean(((foot_height - clearance) / 0.02).square() * (1 - contact_target), dim=1),
            "stance_velocity": torch.mean(torch.sum((velocity_body[:, :, :2] - stance_reference).square(), dim=2) * contact_target * contacts, dim=1),
            "feet_slide_proxy": torch.sum(torch.linalg.vector_norm(foot_velocity[:, :, :2], dim=-1) * contacts, dim=1),
            "collision": collision,
            "torques": torch.sum(robot.applied_torque[:, self._actuated_joint_ids].square(), dim=1),
            "dof_acc": torch.sum(robot.joint_acc[:, self._actuated_joint_ids].square(), dim=1),
            "action_rate": torch.sum((self._actions - self._previous_actions).square(), dim=1),
            "action_magnitude": torch.sum(self._actions.square(), dim=1),
            "action_overflow": torch.sum(torch.relu(self._raw_actions.abs() - self._action_bounds).square(), dim=1),
            "joint_deviation": torch.sum(joint_deviation.square(), dim=1),
            "termination": self.reset_terminated.float(),
        }
        reward = torch.zeros(self.num_envs, device=self.device)
        if self.cfg.record_reward_terms:
            self.last_reward_terms = {}
        for name, value in terms.items():
            scaled = value * self.cfg.reward_scales[name] * self.step_dt
            if self.cfg.record_reward_terms:
                self.last_reward_terms[name] = scaled.detach()
            reward += scaled
            self._episode_sums[name] += scaled
        return reward
