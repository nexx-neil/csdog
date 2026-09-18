from __future__ import annotations

import gymnasium as gym
import torch

import isaaclab.sim as sim_utils
from isaaclab.assets import Articulation
from isaaclab.envs import DirectRLEnv
from isaaclab.sensors import ContactSensor

from .custom_rewards import compute_custom_reward_terms
from .generated_robot_env_cfg import GeneratedRobotEnvCfg


class GeneratedRobotEnv(DirectRLEnv):
    cfg: GeneratedRobotEnvCfg

    def __init__(self, cfg: GeneratedRobotEnvCfg, render_mode: str | None = None, **kwargs):
        super().__init__(cfg, render_mode, **kwargs)

        self._actions = torch.zeros(self.num_envs, gym.spaces.flatdim(self.single_action_space), device=self.device)
        self._raw_actions = torch.zeros_like(self._actions)
        self._previous_actions = torch.zeros_like(self._actions)
        self._commands = torch.zeros(self.num_envs, 3, device=self.device)

        self._episode_sums = {
            key: torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
            for key in self.cfg.reward_scales.keys()
        }

        self._actuated_joint_ids, _ = self._robot.find_joints(self.cfg.actuated_joint_names, preserve_order=True)
        self._foot_ids, _ = self._contact_sensor.find_bodies(self.cfg.foot_link_names, preserve_order=True)
        self._robot_foot_ids, _ = self._robot.find_bodies(self.cfg.foot_link_names, preserve_order=True)
        self._termination_body_ids, _ = self._contact_sensor.find_bodies([self.cfg.base_link_name], preserve_order=True)
        self._undesired_contact_body_ids, _ = self._contact_sensor.find_bodies(
            self.cfg.undesired_contact_body_names, preserve_order=True
        )
        self._termination_grace_steps = max(0, int(self.cfg.termination_grace_time_s / self.step_dt))
        self._fallen_termination_steps = max(1, int(self.cfg.fallen_termination_time_s / self.step_dt))
        self._fallen_fail_buf = torch.zeros(self.num_envs, dtype=torch.float, device=self.device)
        self._pre_step_root_height = torch.full(
            (self.num_envs,), self.cfg.base_height_target, dtype=torch.float, device=self.device
        )

    def _setup_scene(self):
        self._robot = Articulation(self.cfg.robot)
        self.scene.articulations["robot"] = self._robot
        self._contact_sensor = ContactSensor(self.cfg.contact_sensor)
        self.scene.sensors["contact_sensor"] = self._contact_sensor
        self.cfg.terrain.num_envs = self.scene.cfg.num_envs
        self.cfg.terrain.env_spacing = self.scene.cfg.env_spacing
        self._terrain = self.cfg.terrain.class_type(self.cfg.terrain)
        self.scene.clone_environments(copy_from_source=False)
        if self.device == "cpu":
            self.scene.filter_collisions(global_prim_paths=[self.cfg.terrain.prim_path])
        light_cfg = sim_utils.DomeLightCfg(intensity=2000.0, color=(0.75, 0.75, 0.75))
        light_cfg.func("/World/Light", light_cfg)

    def _pre_physics_step(self, actions: torch.Tensor):
        self._raw_actions = actions.clone()
        self._actions = torch.clamp(actions.clone(), -self.cfg.action_clip, self.cfg.action_clip)
        self._pre_step_root_height = self._robot.data.root_pos_w[:, 2] - self._terrain.env_origins[:, 2]
        default_pos = self._robot.data.default_joint_pos[:, self._actuated_joint_ids]
        self._processed_actions = self.cfg.action_scale * self._actions + default_pos

    def _apply_action(self):
        self._robot.set_joint_position_target(self._processed_actions, joint_ids=self._actuated_joint_ids)

    def _get_observations(self) -> dict:
        obs = torch.cat(
            [
                self._robot.data.root_lin_vel_b,
                self._robot.data.root_ang_vel_b,
                self._robot.data.projected_gravity_b,
                self._commands,
                self._robot.data.joint_pos[:, self._actuated_joint_ids]
                - self._robot.data.default_joint_pos[:, self._actuated_joint_ids],
                self._robot.data.joint_vel[:, self._actuated_joint_ids],
                self._actions,
            ],
            dim=-1,
        )
        self._previous_actions = self._actions.clone()
        return {"policy": obs}

    def _get_rewards(self) -> torch.Tensor:
        reward_scales = self.cfg.reward_scales
        joint_pos_error = self._robot.data.joint_pos[:, self._actuated_joint_ids] - self._robot.data.default_joint_pos[:, self._actuated_joint_ids]
        lin_vel_error = torch.sum(torch.square(self._commands[:, :2] - self._robot.data.root_lin_vel_b[:, :2]), dim=1)
        lin_vel_x_error = torch.square(self._commands[:, 0] - self._robot.data.root_lin_vel_b[:, 0])
        lin_vel_y_error = torch.square(self._commands[:, 1] - self._robot.data.root_lin_vel_b[:, 1])
        ang_vel_error = torch.square(self._commands[:, 2] - self._robot.data.root_ang_vel_b[:, 2])
        # Normalize zero-command tracking across all three axes so standing and
        # any single active command have the same maximum positive reward.
        stand_command = torch.linalg.vector_norm(self._commands, dim=1) < 1.0e-6
        command_masks = [
            (torch.abs(self._commands[:, axis]) > 1.0e-6).float() + stand_command.float() / 3.0
            for axis in range(3)
        ]
        z_vel_error = torch.square(self._robot.data.root_lin_vel_b[:, 2])
        ang_vel_xy_error = torch.sum(torch.square(self._robot.data.root_ang_vel_b[:, :2]), dim=1)
        orientation_error = torch.sum(torch.square(self._robot.data.projected_gravity_b[:, :2]), dim=1)
        joint_torques = torch.sum(torch.square(self._robot.data.applied_torque[:, self._actuated_joint_ids]), dim=1)
        joint_vel = torch.sum(torch.square(self._robot.data.joint_vel[:, self._actuated_joint_ids]), dim=1)
        joint_accel = torch.sum(torch.square(self._robot.data.joint_acc[:, self._actuated_joint_ids]), dim=1)
        action_rate = torch.sum(torch.square(self._actions - self._previous_actions), dim=1)
        root_height = self._robot.data.root_pos_w[:, 2] - self._terrain.env_origins[:, 2]
        base_height_error = torch.square(root_height - self.cfg.base_height_target)

        first_contact = self._contact_sensor.compute_first_contact(self.step_dt)[:, self._foot_ids]
        last_air_time = self._contact_sensor.data.last_air_time[:, self._foot_ids]
        feet_air_time = torch.sum((last_air_time - self.cfg.feet_air_time_threshold) * first_contact, dim=1) * (
            torch.norm(self._commands[:, :2], dim=1) > 0.1
        )

        if self._undesired_contact_body_ids:
            net_contact_forces = self._contact_sensor.data.net_forces_w_history
            is_contact = (
                torch.max(torch.norm(net_contact_forces[:, :, self._undesired_contact_body_ids], dim=-1), dim=1)[0] > 1.0
            )
            collision = torch.sum(is_contact, dim=1)
        else:
            collision = torch.zeros(self.num_envs, device=self.device)

        foot_forces = torch.linalg.vector_norm(
            self._contact_sensor.data.net_forces_w[:, self._foot_ids], dim=-1
        )
        foot_contacts = foot_forces > 1.0
        foot_planar_speed = torch.linalg.vector_norm(
            self._robot.data.body_lin_vel_w[:, self._robot_foot_ids, :2], dim=-1
        )
        feet_slide = torch.sum(foot_planar_speed * foot_contacts, dim=1)

        stand_still = torch.sum(torch.abs(joint_pos_error), dim=1) * (torch.norm(self._commands, dim=1) < 0.1)
        termination = self.reset_terminated.float()

        rewards = {
            "termination": termination * reward_scales.get("termination", 0.0),
            "tracking_lin_vel": torch.exp(-lin_vel_error / self.cfg.tracking_lin_vel_std**2)
            * reward_scales.get("tracking_lin_vel", 0.0),
            "tracking_lin_vel_x": torch.exp(-lin_vel_x_error / self.cfg.tracking_lin_vel_std**2)
            * command_masks[0]
            * reward_scales.get("tracking_lin_vel_x", 0.0),
            "tracking_lin_vel_y": torch.exp(-lin_vel_y_error / self.cfg.tracking_lin_vel_std**2)
            * command_masks[1]
            * reward_scales.get("tracking_lin_vel_y", 0.0),
            "tracking_ang_vel": torch.exp(-ang_vel_error / self.cfg.tracking_ang_vel_std**2)
            * command_masks[2]
            * reward_scales.get("tracking_ang_vel", 0.0),
            "tracking_lin_vel_l2": lin_vel_error * reward_scales.get("tracking_lin_vel_l2", 0.0),
            "tracking_lin_vel_x_l2": lin_vel_x_error * reward_scales.get("tracking_lin_vel_x_l2", 0.0),
            "tracking_lin_vel_y_l2": lin_vel_y_error * reward_scales.get("tracking_lin_vel_y_l2", 0.0),
            "tracking_ang_vel_l2": ang_vel_error * reward_scales.get("tracking_ang_vel_l2", 0.0),
            "lin_vel_z": z_vel_error * reward_scales.get("lin_vel_z", 0.0),
            "ang_vel_xy": ang_vel_xy_error * reward_scales.get("ang_vel_xy", 0.0),
            "orientation": orientation_error * reward_scales.get("orientation", 0.0),
            "torques": joint_torques * reward_scales.get("torques", 0.0),
            "dof_vel": joint_vel * reward_scales.get("dof_vel", 0.0),
            "dof_acc": joint_accel * reward_scales.get("dof_acc", 0.0),
            "base_height": base_height_error * reward_scales.get("base_height", 0.0),
            "feet_air_time": feet_air_time * reward_scales.get("feet_air_time", 0.0),
            "collision": collision * reward_scales.get("collision", 0.0),
            "feet_stumble": torch.zeros_like(collision),
            "action_rate": action_rate * reward_scales.get("action_rate", 0.0),
            "action_magnitude": torch.sum(torch.square(self._actions), dim=1)
            * reward_scales.get("action_magnitude", 0.0),
            "action_overflow": torch.sum(
                torch.square(torch.relu(torch.abs(self._raw_actions) - self.cfg.action_clip)), dim=1
            )
            * reward_scales.get("action_overflow", 0.0),
            "joint_deviation": torch.sum(torch.square(joint_pos_error), dim=1)
            * reward_scales.get("joint_deviation", 0.0),
            "feet_slide": feet_slide * reward_scales.get("feet_slide", 0.0),
            "stand_still": stand_still * reward_scales.get("stand_still", 0.0),
        }
        custom_rewards = compute_custom_reward_terms(self)
        for key, value in custom_rewards.items():
            rewards[key] = rewards.get(key, torch.zeros_like(value)) + value * reward_scales.get(key, 0.0)
        reward = torch.sum(torch.stack(list(rewards.values())), dim=0) * self.step_dt
        for key, value in rewards.items():
            self._episode_sums[key] += value * self.step_dt
        return reward

    def _get_dones(self) -> tuple[torch.Tensor, torch.Tensor]:
        time_out = self.episode_length_buf >= self.max_episode_length - 1
        if getattr(self.cfg, "visual_disable_resets", False):
            no_reset = torch.zeros_like(time_out)
            return no_reset, no_reset
        after_grace = self.episode_length_buf > self._termination_grace_steps
        if self._termination_body_ids:
            net_contact_forces = self._contact_sensor.data.net_forces_w_history
            termination_contacts = torch.max(torch.norm(net_contact_forces[:, :, self._termination_body_ids], dim=-1), dim=1)[0]
            contact_died = torch.any(termination_contacts > self.cfg.termination_contact_force_threshold, dim=1)
        else:
            contact_died = torch.zeros_like(time_out)
        root_height = torch.minimum(
            self._robot.data.root_pos_w[:, 2] - self._terrain.env_origins[:, 2],
            self._pre_step_root_height,
        )
        height_died = root_height < self.cfg.min_base_height
        fallen = self._robot.data.projected_gravity_b[:, 2] > self.cfg.fallen_projected_gravity_z
        fallen &= after_grace
        self._fallen_fail_buf *= fallen.float()
        self._fallen_fail_buf += fallen.float()
        fallen_died = self._fallen_fail_buf > self._fallen_termination_steps
        died = ((contact_died | height_died) & after_grace) | fallen_died
        return died, time_out

    def _sample_commands(self, env_ids: torch.Tensor) -> None:
        num_resets = len(env_ids)
        ranges = (
            self.cfg.command_ranges["lin_vel_x"],
            self.cfg.command_ranges["lin_vel_y"],
            self.cfg.command_ranges["ang_vel_yaw"],
        )
        if all(lower == upper for lower, upper in ranges):
            self._commands[env_ids] = torch.tensor(
                [axis_range[0] for axis_range in ranges], device=self.device
            )
            return

        if self.cfg.command_sampling != "single_axis":
            for axis, axis_range in enumerate(ranges):
                self._commands[env_ids, axis] = torch.empty(num_resets, device=self.device).uniform_(*axis_range)
            return

        self._commands[env_ids] = 0.0
        active = torch.rand(num_resets, device=self.device) >= self.cfg.stand_command_probability
        enabled_axes = torch.tensor(
            [axis for axis, (lower, upper) in enumerate(ranges) if lower != 0.0 or upper != 0.0],
            dtype=torch.long,
            device=self.device,
        )
        if len(enabled_axes) == 0:
            return
        axes = enabled_axes[torch.randint(0, len(enabled_axes), (num_resets,), device=self.device)]
        magnitudes = torch.empty(num_resets, device=self.device).uniform_(
            self.cfg.command_min_magnitude, 1.0
        )
        signs = torch.where(
            torch.rand(num_resets, device=self.device) < 0.5,
            -torch.ones(num_resets, device=self.device),
            torch.ones(num_resets, device=self.device),
        )
        for axis, (lower, upper) in enumerate(ranges):
            axis_mask = active & (axes == axis)
            negative_limit = abs(lower)
            positive_limit = abs(upper)
            limits = torch.where(signs < 0.0, negative_limit, positive_limit)
            values = signs * magnitudes * limits
            self._commands[env_ids[axis_mask], axis] = values[axis_mask]

    def _reset_idx(self, env_ids: torch.Tensor | None):
        if env_ids is None or len(env_ids) == self.num_envs:
            env_ids = self._robot._ALL_INDICES
        self._robot.reset(env_ids)
        super()._reset_idx(env_ids)
        if len(env_ids) == self.num_envs and getattr(self.cfg, "randomize_initial_episode_length", False):
            self.episode_length_buf[:] = torch.randint_like(self.episode_length_buf, high=int(self.max_episode_length))

        self._actions[env_ids] = 0.0
        self._raw_actions[env_ids] = 0.0
        self._previous_actions[env_ids] = 0.0
        self._fallen_fail_buf[env_ids] = 0.0
        self._pre_step_root_height[env_ids] = self.cfg.base_height_target
        self._sample_commands(env_ids)

        joint_pos = self._robot.data.default_joint_pos[env_ids]
        joint_vel = self._robot.data.default_joint_vel[env_ids]
        default_root_state = self._robot.data.default_root_state[env_ids]
        default_root_state[:, :3] += self._terrain.env_origins[env_ids]
        self._robot.write_root_pose_to_sim(default_root_state[:, :7], env_ids)
        self._robot.write_root_velocity_to_sim(default_root_state[:, 7:], env_ids)
        self._robot.write_joint_state_to_sim(joint_pos, joint_vel, None, env_ids)

        extras = {}
        for key in self._episode_sums.keys():
            extras["Episode_Reward/" + key] = torch.mean(self._episode_sums[key][env_ids]) / self.max_episode_length_s
            self._episode_sums[key][env_ids] = 0.0
        self.extras["log"] = extras
