"""Script to play a trained RSL-RL policy."""

import argparse
import json
import math
import os
import sys
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description="Play a trained RSL-RL policy.")
parser.add_argument("--num_envs", type=int, default=1, help="Number of environments to simulate.")
parser.add_argument("--task", type=str, default=None, help="Name of the task.")
parser.add_argument("--agent", type=str, default="rsl_rl_cfg_entry_point", help="Agent configuration entry point.")
parser.add_argument("--seed", type=int, default=None, help="Seed used for the environment.")
parser.add_argument("--load_run", type=str, default=".*", help="Run folder name or regex to load from.")
parser.add_argument(
    "--checkpoint",
    type=str,
    default="model_.*.pt",
    help="Checkpoint filename regex under logs, or a direct path to a .pt file.",
)
parser.add_argument("--num_steps", type=int, default=500, help="Number of inference steps to simulate.")
parser.add_argument(
    "--disable_resets",
    action="store_true",
    default=False,
    help="Disable environment reset during visual play so short or unstable policies do not instantly jump back to the start pose.",
)
parser.add_argument("--export_io_descriptors", action="store_true", default=False, help="Export IO descriptors.")
parser.add_argument("--export_onnx", action="store_true", default=False, help="Export policy.onnx from the loaded checkpoint.")
parser.add_argument("--camera-eye", type=float, nargs=3, metavar=("X", "Y", "Z"), default=None)
parser.add_argument("--camera-lookat", type=float, nargs=3, metavar=("X", "Y", "Z"), default=None)
parser.add_argument("--follow-robot", action="store_true", default=False, help="Track the robot root in the GUI.")
parser.add_argument(
    "--command",
    type=float,
    nargs=3,
    metavar=("VX", "VY", "YAW_RATE"),
    default=None,
    help="Use one fixed velocity command for all environments.",
)
parser.add_argument("--keyboard", action="store_true", default=False, help="Drive interactively with Q/W/E/A/S/D.")
parser.add_argument("--keyboard-forward-speed", type=float, default=0.35, help="W/S speed in m/s.")
parser.add_argument("--keyboard-lateral-speed", type=float, default=0.22, help="A/D speed in m/s.")
parser.add_argument("--keyboard-yaw-rate", type=float, default=0.35, help="Q/E yaw rate in rad/s.")
parser.add_argument(
    "--keyboard-smoothing-time",
    type=float,
    default=0.20,
    help="First-order command ramp time in seconds; zero disables smoothing.",
)
parser.add_argument("--metrics-output", type=Path, default=None, help="Write bounded inference metrics to JSON.")
AppLauncher.add_app_launcher_args(parser)
args_cli, hydra_args = parser.parse_known_args()

if args_cli.keyboard and args_cli.command is not None:
    parser.error("--keyboard and --command are mutually exclusive")
if args_cli.keyboard and args_cli.headless:
    parser.error("--keyboard requires a visible Isaac Sim window; remove --headless")

sys.argv = [sys.argv[0]] + hydra_args

app_launcher = AppLauncher(args_cli)
simulation_app = app_launcher.app

import gymnasium as gym
import inspect
import os
import torch
import carb
import omni
from rsl_rl.runners import OnPolicyRunner
try:
    from rsl_rl.algorithms import PPO
except ImportError:
    PPO = None
try:
    from tensordict import TensorDict
except ImportError:
    TensorDict = None

from isaaclab.envs import DirectMARLEnv, DirectMARLEnvCfg, DirectRLEnvCfg, ManagerBasedRLEnvCfg, multi_agent_to_single_agent
from isaaclab.utils import math as math_utils
from isaaclab_rl.rsl_rl import RslRlBaseRunnerCfg

from isaaclab_tasks.utils import get_checkpoint_path
from isaaclab_tasks.utils.hydra import hydra_task_config

import stackforce_simready_generated_robot_lab.tasks  # noqa: F401

import os
import torch


class QweasdKeyboard:
    """Hold-to-drive SE(2) command source for the visible Isaac Sim window."""

    def __init__(self, forward_speed: float, lateral_speed: float, yaw_rate: float, device: str):
        self._device = device
        self._pressed = set()
        self._forward_speed = float(forward_speed)
        self._lateral_speed = float(lateral_speed)
        self._yaw_rate = float(yaw_rate)
        self._app_window = omni.appwindow.get_default_app_window()
        if self._app_window is None:
            raise RuntimeError("QWEASD keyboard control requires an Isaac Sim app window")
        self._input = carb.input.acquire_input_interface()
        self._keyboard = self._app_window.get_keyboard()
        self._subscription = self._input.subscribe_to_keyboard_events(self._keyboard, self._on_event)

    def _on_event(self, event, *args):
        key = event.input.name
        if event.type in (carb.input.KeyboardEventType.KEY_PRESS, carb.input.KeyboardEventType.KEY_REPEAT):
            if key == "SPACE":
                self._pressed.clear()
            elif key in {"Q", "W", "E", "A", "S", "D"}:
                self._pressed.add(key)
        elif event.type == carb.input.KeyboardEventType.KEY_RELEASE:
            self._pressed.discard(key)
        return True

    def target(self) -> torch.Tensor:
        command = torch.zeros(3, dtype=torch.float32, device=self._device)
        command[0] = self._forward_speed * (float("W" in self._pressed) - float("S" in self._pressed))
        command[1] = self._lateral_speed * (float("A" in self._pressed) - float("D" in self._pressed))
        command[2] = self._yaw_rate * (float("Q" in self._pressed) - float("E" in self._pressed))
        return command

    def close(self):
        if self._subscription is not None:
            self._input.unsubscribe_to_keyboard_events(self._keyboard, self._subscription)
            self._subscription = None


def _write_command_to_policy_observation(obs, commands: torch.Tensor) -> None:
    """Keep the command slice in an already-built observation synchronized."""
    policy_obs = obs
    if isinstance(obs, dict):
        policy_obs = obs.get("policy", next(iter(obs.values())))
    elif not isinstance(obs, torch.Tensor) and hasattr(obs, "get"):
        candidate = obs.get("policy")
        if candidate is not None:
            policy_obs = candidate
    if isinstance(policy_obs, torch.Tensor):
        policy_obs[..., 9:12] = commands


class _StackForceOnnxPolicy(torch.nn.Module):
    def __init__(self, policy):
        super().__init__()
        self.policy = policy

    def forward(self, obs):
        actions = self.policy(obs)
        if isinstance(actions, (tuple, list)):
            return actions[0]
        if isinstance(actions, dict):
            if "actions" in actions:
                return actions["actions"]
            if "action" in actions:
                return actions["action"]
            return next(iter(actions.values()))
        return actions


def _stackforce_policy_obs_tensor(obs):
    if isinstance(obs, dict):
        obs = obs["policy"] if "policy" in obs else next(iter(obs.values()))
    elif not isinstance(obs, torch.Tensor) and hasattr(obs, "get"):
        try:
            candidate = obs.get("policy")
        except Exception:
            candidate = None
        if candidate is not None:
            obs = candidate
    if not isinstance(obs, torch.Tensor):
        raise TypeError(f"ONNX export requires a tensor policy observation, got {type(obs)!r}")
    if hasattr(obs, "detach"):
        obs = obs.detach()
    if obs.dim() == 1:
        obs = obs.unsqueeze(0)
    elif obs.shape[0] > 1:
        obs = obs[:1]
    return obs.contiguous()


def stackforce_export_policy_as_onnx(policy, obs, output_dir, file_name="policy.onnx", opset=17):
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, file_name)
    sample_obs = _stackforce_policy_obs_tensor(obs)
    module = _StackForceOnnxPolicy(policy).to(sample_obs.device).eval()
    with torch.no_grad():
        torch.onnx.export(
            module,
            sample_obs,
            output_path,
            input_names=["obs"],
            output_names=["actions"],
            dynamic_axes={"obs": {0: "batch"}, "actions": {0: "batch"}},
            opset_version=opset,
        )
    print(f"Exported ONNX policy to: {output_path}")
    return output_path



def _runner_uses_obs_groups():
    try:
        source = inspect.getsource(OnPolicyRunner)
        if PPO is not None and hasattr(PPO, "construct_algorithm"):
            source += "\n" + inspect.getsource(PPO.construct_algorithm)
    except OSError:
        return False
    return "resolve_obs_groups" in source or '"obs_groups"' in source or "'obs_groups'" in source


def _runner_uses_split_actor_critic():
    try:
        source = inspect.getsource(OnPolicyRunner)
        if PPO is not None and hasattr(PPO, "construct_algorithm"):
            source += "\n" + inspect.getsource(PPO.construct_algorithm)
    except OSError:
        return False
    return 'cfg["actor"]' in source or "cfg['actor']" in source or 'cfg["critic"]' in source or "cfg['critic']" in source


def _runner_expects_privileged_step():
    try:
        source = inspect.getsource(OnPolicyRunner.learn)
    except OSError:
        return True
    return "privileged_obs" in source or "critic_obs" in source


def _format_rsl_rl_obs(obs_dict, use_obs_groups):
    if not use_obs_groups:
        return obs_dict["policy"]
    if TensorDict is not None and not isinstance(obs_dict, TensorDict):
        first_obs = next(iter(obs_dict.values()))
        return TensorDict(dict(obs_dict), batch_size=[first_obs.shape[0]], device=first_obs.device)
    return obs_dict


class LegacyRslRlVecEnvWrapper:
    def __init__(self, env, clip_actions=None):
        self.env = env
        self.clip_actions = clip_actions
        self.use_obs_groups = _runner_uses_obs_groups()
        self.return_privileged_obs = _runner_expects_privileged_step()
        self.num_envs = env.unwrapped.num_envs
        self.device = env.unwrapped.device
        self.max_episode_length = env.unwrapped.max_episode_length
        self.cfg = env.unwrapped.cfg
        self.num_actions = gym.spaces.flatdim(env.unwrapped.single_action_space)
        obs_dict, extras = self.env.reset()
        self.obs_buf = _format_rsl_rl_obs(obs_dict, self.use_obs_groups)
        self.privileged_obs_buf = obs_dict.get("critic")
        self.num_obs = obs_dict["policy"].shape[-1]
        self.num_privileged_obs = self.privileged_obs_buf.shape[-1] if self.privileged_obs_buf is not None else None
        self.rew_buf = torch.zeros(self.num_envs, device=self.device)
        self.reset_buf = torch.zeros(self.num_envs, dtype=torch.long, device=self.device)
        self.episode_length_buf = env.unwrapped.episode_length_buf
        self.extras = extras

    def get_observations(self):
        return self.obs_buf

    def get_privileged_observations(self):
        return self.privileged_obs_buf

    def reset(self, env_ids=None):
        del env_ids
        obs_dict, extras = self.env.reset()
        self.obs_buf = _format_rsl_rl_obs(obs_dict, self.use_obs_groups)
        self.privileged_obs_buf = obs_dict.get("critic")
        self.extras = extras
        if not self.return_privileged_obs:
            return self.obs_buf
        return self.obs_buf, self.privileged_obs_buf

    def step(self, actions):
        if self.clip_actions is not None:
            actions = torch.clamp(actions, -self.clip_actions, self.clip_actions)
        obs_dict, rewards, terminated, truncated, extras = self.env.step(actions)
        dones = (terminated | truncated).to(dtype=torch.long)
        if not self.env.unwrapped.cfg.is_finite_horizon:
            extras["time_outs"] = truncated
        episode_log = dict(extras.get("episode", {}))
        if torch.any(dones.bool()) and "log" in extras:
            episode_log.update(extras["log"])
        episode_log["Step_Reward/mean"] = torch.mean(rewards.detach())
        episode_log["Step_Reward/abs_mean"] = torch.mean(torch.abs(rewards.detach()))
        extras["episode"] = episode_log
        self.obs_buf = _format_rsl_rl_obs(obs_dict, self.use_obs_groups)
        self.privileged_obs_buf = obs_dict.get("critic")
        self.rew_buf = rewards
        self.reset_buf = dones
        self.extras = extras
        if not self.return_privileged_obs:
            return self.obs_buf, rewards, dones, extras
        return self.obs_buf, self.privileged_obs_buf, rewards, dones, extras

    def close(self):
        return self.env.close()


def _runner_expects_nested_runner():
    try:
        source = inspect.getsource(OnPolicyRunner)
    except OSError:
        return True
    return 'train_cfg["runner"]' in source or "train_cfg['runner']" in source


def _runner_uses_nested_class_name():
    try:
        source = inspect.getsource(OnPolicyRunner)
    except OSError:
        return False
    return (
        'algorithm"]["class_name' in source
        or "algorithm']['class_name" in source
        or 'policy_cfg.pop("class_name")' in source
        or "policy_cfg.pop('class_name')" in source
        or 'self.policy_cfg.pop("class_name")' in source
        or "self.policy_cfg.pop('class_name')" in source
        or "resolve_callable" in source
    )


def _runner_uses_split_actor_critic():
    try:
        source = inspect.getsource(OnPolicyRunner)
        if PPO is not None and hasattr(PPO, "construct_algorithm"):
            source += "\n" + inspect.getsource(PPO.construct_algorithm)
    except OSError:
        return False
    return 'cfg["actor"]' in source or "cfg['actor']" in source or 'cfg["critic"]' in source or "cfg['critic']" in source


def to_compatible_rsl_rl_cfg(agent_cfg):
    data = agent_cfg.to_dict() if hasattr(agent_cfg, "to_dict") else dict(agent_cfg)
    allowed_policy_keys = {
        "actor_hidden_dims",
        "critic_hidden_dims",
        "activation",
        "init_noise_std",
        "clip_actions",
        "actor_obs_normalization",
        "critic_obs_normalization",
    }
    allowed_algorithm_keys = {
        "num_learning_epochs",
        "num_mini_batches",
        "clip_param",
        "gamma",
        "lam",
        "value_loss_coef",
        "entropy_coef",
        "learning_rate",
        "max_grad_norm",
        "use_clipped_value_loss",
        "schedule",
        "desired_kl",
        "use_spo",
    }
    if "runner" in data and "policy" in data and "algorithm" in data:
        runner_cfg = dict(data["runner"])
        policy_cfg = {key: value for key, value in dict(data["policy"]).items() if key in allowed_policy_keys or key == "class_name"}
        algorithm_cfg = {key: value for key, value in dict(data["algorithm"]).items() if key in allowed_algorithm_keys or key == "class_name"}
    else:
        policy_cfg = {key: value for key, value in dict(data["policy"]).items() if key in allowed_policy_keys}
        algorithm_cfg = {key: value for key, value in dict(data["algorithm"]).items() if key in allowed_algorithm_keys}
        runner_cfg = {key: value for key, value in data.items() if key not in {"policy", "algorithm", "class_name"}}

    runner_cfg.setdefault("num_steps_per_env", getattr(agent_cfg, "num_steps_per_env", 24))
    runner_cfg.setdefault("max_iterations", getattr(agent_cfg, "max_iterations", 1500))
    runner_cfg.setdefault("save_interval", getattr(agent_cfg, "save_interval", 50))
    runner_cfg.setdefault("obs_groups", {"policy": ["policy"], "critic": ["policy"]})
    runner_cfg.setdefault("experiment_name", getattr(agent_cfg, "experiment_name", "stackforce"))
    runner_cfg.setdefault("run_name", getattr(agent_cfg, "run_name", ""))
    runner_cfg.setdefault("resume", getattr(agent_cfg, "resume", False))
    runner_cfg.setdefault("load_run", getattr(agent_cfg, "load_run", ".*"))
    runner_cfg.setdefault("checkpoint", getattr(agent_cfg, "load_checkpoint", "model_.*.pt"))

    if _runner_uses_nested_class_name():
        policy_cfg.setdefault("class_name", "ActorCritic")
        algorithm_cfg.setdefault("class_name", "PPO")
    else:
        runner_cfg.setdefault("policy_class_name", "ActorCritic")
        runner_cfg.setdefault("algorithm_class_name", "PPO")

    if _runner_expects_nested_runner():
        return {"runner": runner_cfg, "policy": policy_cfg, "algorithm": algorithm_cfg}
    if _runner_uses_split_actor_critic():
        algorithm_cfg.setdefault("class_name", "PPO")
        algorithm_cfg.pop("use_spo", None)
        actor_cfg = {
            "class_name": "MLPModel",
            "hidden_dims": policy_cfg.get("actor_hidden_dims", [256, 256, 128]),
            "activation": policy_cfg.get("activation", "elu"),
            "obs_normalization": policy_cfg.get("actor_obs_normalization", False),
            "distribution_cfg": {
                "class_name": "GaussianDistribution",
                "init_std": policy_cfg.get("init_noise_std", 1.0),
            },
        }
        critic_cfg = {
            "class_name": "MLPModel",
            "hidden_dims": policy_cfg.get("critic_hidden_dims", [256, 256, 128]),
            "activation": policy_cfg.get("activation", "elu"),
            "obs_normalization": policy_cfg.get("critic_obs_normalization", False),
        }
        runner_cfg.pop("policy_class_name", None)
        runner_cfg.pop("algorithm_class_name", None)
        runner_cfg["obs_groups"] = {"actor": ["policy"], "critic": ["policy"], "policy": ["policy"]}
        runner_cfg.setdefault("multi_gpu", None)
        return {**runner_cfg, "actor": actor_cfg, "critic": critic_cfg, "algorithm": algorithm_cfg}
    return {**runner_cfg, "policy": policy_cfg, "algorithm": algorithm_cfg}


@hydra_task_config(args_cli.task, args_cli.agent)
def main(env_cfg: ManagerBasedRLEnvCfg | DirectRLEnvCfg | DirectMARLEnvCfg, agent_cfg: RslRlBaseRunnerCfg):
    env_cfg.scene.num_envs = args_cli.num_envs if args_cli.num_envs is not None else env_cfg.scene.num_envs
    env_cfg.seed = args_cli.seed if args_cli.seed is not None else agent_cfg.seed
    env_cfg.sim.device = args_cli.device if args_cli.device is not None else env_cfg.sim.device
    if args_cli.camera_eye is not None:
        env_cfg.viewer.eye = tuple(args_cli.camera_eye)
    if args_cli.camera_lookat is not None:
        env_cfg.viewer.lookat = tuple(args_cli.camera_lookat)
    if args_cli.follow_robot:
        env_cfg.viewer.origin_type = "asset_root"
        env_cfg.viewer.asset_name = "robot"
        env_cfg.viewer.env_index = 0
    if args_cli.command is not None:
        env_cfg.command_ranges = {
            "lin_vel_x": (args_cli.command[0], args_cli.command[0]),
            "lin_vel_y": (args_cli.command[1], args_cli.command[1]),
            "ang_vel_yaw": (args_cli.command[2], args_cli.command[2]),
        }
    elif args_cli.keyboard:
        # Resets must not inject random training commands while the operator is
        # holding or releasing keys.  The live loop overwrites this zero command.
        env_cfg.command_ranges = {
            "lin_vel_x": (0.0, 0.0),
            "lin_vel_y": (0.0, 0.0),
            "ang_vel_yaw": (0.0, 0.0),
        }
    if isinstance(env_cfg, ManagerBasedRLEnvCfg):
        env_cfg.export_io_descriptors = args_cli.export_io_descriptors
    elif args_cli.disable_resets and hasattr(env_cfg, "visual_disable_resets"):
        env_cfg.visual_disable_resets = True

    log_root_path = os.path.abspath(os.path.join("logs", "rsl_rl", agent_cfg.experiment_name))
    checkpoint_arg = args_cli.checkpoint
    if os.path.isfile(checkpoint_arg):
        resume_path = os.path.abspath(checkpoint_arg)
    else:
        resume_path = get_checkpoint_path(log_root_path, args_cli.load_run, checkpoint_arg)
    print(f"[INFO]: Loading model checkpoint from: {resume_path}")

    expected_compatibility_tag = getattr(env_cfg, "checkpoint_compatibility_tag", None)
    if expected_compatibility_tag is not None:
        metadata_path = Path(resume_path + ".metadata.json")
        if not metadata_path.is_file():
            # Periodic checkpoints are written by RSL-RL before our final
            # sidecar hook runs.  They share the same task, joints and code as
            # model_final.pt in that run, so use that run-level metadata when
            # it exists instead of making intermediate model selection opaque.
            run_metadata_path = Path(resume_path).parent / "model_final.pt.metadata.json"
            if run_metadata_path.is_file():
                metadata_path = run_metadata_path
            else:
                raise RuntimeError(
                    f"Refusing checkpoint without compatibility metadata for {args_cli.task}: {metadata_path}"
                )
        checkpoint_metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        actual_tag = checkpoint_metadata.get("checkpoint_compatibility_tag")
        if actual_tag != expected_compatibility_tag:
            raise RuntimeError(
                f"Checkpoint compatibility mismatch: expected {expected_compatibility_tag!r}, got {actual_tag!r}"
            )
        if checkpoint_metadata.get("actuated_joint_names") != list(env_cfg.actuated_joint_names):
            raise RuntimeError("Checkpoint joint names/order do not match the task configuration")

    env = gym.make(args_cli.task, cfg=env_cfg)
    if isinstance(env.unwrapped, DirectMARLEnv):
        env = multi_agent_to_single_agent(env)

    legacy_agent_cfg = to_compatible_rsl_rl_cfg(agent_cfg)
    wrapped_env = LegacyRslRlVecEnvWrapper(env, clip_actions=getattr(agent_cfg, "clip_actions", None))
    runner = OnPolicyRunner(wrapped_env, legacy_agent_cfg, log_dir=None, device=env.unwrapped.device)
    runner.load(resume_path, load_optimizer=False)
    policy = runner.get_inference_policy(device=env.unwrapped.device)

    obs = wrapped_env.get_observations()
    keyboard_controller = None
    keyboard_command = torch.zeros(3, dtype=torch.float32, device=env.unwrapped.device)
    keyboard_alpha = 1.0
    if args_cli.keyboard:
        keyboard_controller = QweasdKeyboard(
            args_cli.keyboard_forward_speed,
            args_cli.keyboard_lateral_speed,
            args_cli.keyboard_yaw_rate,
            env.unwrapped.device,
        )
        if args_cli.keyboard_smoothing_time > 0.0:
            keyboard_alpha = 1.0 - math.exp(-env.unwrapped.step_dt / args_cli.keyboard_smoothing_time)
        print("[QWEASD] Hold W/S: forward/back, A/D: left/right, Q/E: turn left/right")
        print("[QWEASD] Release keys to ramp to stop; SPACE clears all held commands")
        print(
            "[QWEASD] Limits: "
            f"x={args_cli.keyboard_forward_speed:.2f} m/s, "
            f"y={args_cli.keyboard_lateral_speed:.2f} m/s, "
            f"yaw={args_cli.keyboard_yaw_rate:.2f} rad/s"
        )
    if args_cli.export_onnx:
        stackforce_export_policy_as_onnx(
            policy,
            obs,
            os.path.join(os.path.dirname(resume_path), "exported", "policies"),
        )
    steps = 0
    total_resets = 0
    total_terminations = 0
    total_timeouts = 0
    reward_sum = 0.0
    lin_vel_error_sq_sum = 0.0
    lin_vel_error_sq_by_axis = torch.zeros(2, device=env.unwrapped.device)
    yaw_rate_error_sq_sum = 0.0
    min_base_height = float("inf")
    max_base_height = float("-inf")
    base_height_sum = 0.0
    command_linear_speed_sq_sum = 0.0
    command_nonzero_axis_counts = torch.zeros(3, device=env.unwrapped.device)
    multi_axis_command_samples = 0
    stand_command_samples = 0
    actual_linear_speed_sq_sum = 0.0
    actual_linear_velocity_sum = torch.zeros(3, device=env.unwrapped.device)
    command_yaw_rate_sq_sum = 0.0
    actual_yaw_rate_sq_sum = 0.0
    actual_yaw_rate_sum = 0.0
    action_sq_sum = 0.0
    clipped_action_sq_sum = 0.0
    action_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    clipped_action_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    joint_position_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    joint_abs_deviation_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    joint_deviation_sq_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    joint_abs_deviation_max = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    joint_velocity_sq_sum = 0.0
    joint_target_limit_violations = 0
    joint_position_near_limit_samples = 0
    torque_saturation_samples = 0
    joint_samples = 0
    saturated_action_samples = 0
    action_samples = 0
    foot_contact_samples = 0
    foot_contact_possible = 0
    contacting_foot_planar_speed_sum = 0.0
    robot = env.unwrapped._robot
    contact_sensor = env.unwrapped._contact_sensor
    robot_foot_ids, _ = robot.find_bodies(env.unwrapped.cfg.foot_link_names, preserve_order=True)
    contact_foot_ids = env.unwrapped._foot_ids
    num_feet = len(contact_foot_ids)
    yaw_command_samples = 0
    yaw_joint_abs_deviation_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    yaw_joint_deviation_sq_sum = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    yaw_joint_abs_deviation_max = torch.zeros(wrapped_env.num_actions, device=env.unwrapped.device)
    yaw_foot_position_body_sum = torch.zeros(num_feet, 3, device=env.unwrapped.device)
    yaw_foot_lateral_sq_sum = torch.zeros(num_feet, device=env.unwrapped.device)
    yaw_foot_abs_lateral_max = torch.zeros(num_feet, device=env.unwrapped.device)
    yaw_projected_gravity_abs_sum = torch.zeros(2, device=env.unwrapped.device)
    yaw_body_tilt_max = torch.tensor(0.0, device=env.unwrapped.device)
    contact_on_force = float(getattr(env.unwrapped.cfg, "foot_contact_on_force_threshold", 5.0))
    contact_off_force = float(getattr(env.unwrapped.cfg, "foot_contact_off_force_threshold", 2.0))
    foot_contact_state = torch.zeros(
        wrapped_env.num_envs, num_feet, dtype=torch.bool, device=env.unwrapped.device
    )
    previous_foot_contact_state = foot_contact_state.clone()
    per_foot_contact_samples = torch.zeros(num_feet, device=env.unwrapped.device)
    per_foot_touchdowns = torch.zeros(num_feet, device=env.unwrapped.device)
    per_foot_liftoffs = torch.zeros(num_feet, device=env.unwrapped.device)
    per_foot_stance_origin_speed_sum = torch.zeros(num_feet, device=env.unwrapped.device)
    per_foot_stance_samples = torch.zeros(num_feet, device=env.unwrapped.device)
    swing_origin_height_max = torch.full(
        (wrapped_env.num_envs, num_feet), float("-inf"), device=env.unwrapped.device
    )
    per_foot_completed_swing_height_sum = torch.zeros(num_feet, device=env.unwrapped.device)
    per_foot_completed_swings = torch.zeros(num_feet, device=env.unwrapped.device)
    support_count_histogram = torch.zeros(num_feet + 1, device=env.unwrapped.device)
    diagonal_same_state_samples = torch.zeros(2, device=env.unwrapped.device)
    diagonal_cross_opposite_samples = torch.tensor(0.0, device=env.unwrapped.device)
    contact_sequence_env0 = []
    finite = True
    with torch.inference_mode():
        while simulation_app.is_running():
            if keyboard_controller is not None:
                keyboard_target = keyboard_controller.target()
                keyboard_command += keyboard_alpha * (keyboard_target - keyboard_command)
                command_batch = keyboard_command.unsqueeze(0).expand(wrapped_env.num_envs, -1)
                env.unwrapped._commands[:] = command_batch
                _write_command_to_policy_observation(obs, command_batch)
            actions = policy(obs)
            step_result = wrapped_env.step(actions)
            obs = step_result[0]
            steps += 1
            total_resets += int(torch.count_nonzero(wrapped_env.reset_buf).item())
            total_terminations += int(torch.count_nonzero(env.unwrapped.reset_terminated).item())
            total_timeouts += int(torch.count_nonzero(env.unwrapped.reset_time_outs).item())
            reward_sum += float(torch.sum(wrapped_env.rew_buf).item())
            commands = env.unwrapped._commands
            command_active_axes = torch.abs(commands) > 1.0e-6
            command_nonzero_axis_counts += torch.sum(command_active_axes, dim=0)
            active_axis_count = torch.sum(command_active_axes, dim=1)
            multi_axis_command_samples += int(torch.count_nonzero(active_axis_count > 1).item())
            stand_command_samples += int(torch.count_nonzero(active_axis_count == 0).item())
            lin_vel_error_sq_sum += float(
                torch.sum(torch.square(commands[:, :2] - robot.data.root_lin_vel_b[:, :2])).item()
            )
            lin_vel_error_sq_by_axis += torch.sum(
                torch.square(commands[:, :2] - robot.data.root_lin_vel_b[:, :2]), dim=0
            )
            yaw_rate_error_sq_sum += float(
                torch.sum(torch.square(commands[:, 2] - robot.data.root_ang_vel_b[:, 2])).item()
            )
            base_height = robot.data.root_pos_w[:, 2] - env.unwrapped._terrain.env_origins[:, 2]
            min_base_height = min(min_base_height, float(torch.min(base_height).item()))
            max_base_height = max(max_base_height, float(torch.max(base_height).item()))
            base_height_sum += float(torch.sum(base_height).item())
            command_linear_speed_sq_sum += float(torch.sum(torch.square(commands[:, :2])).item())
            actual_linear_speed_sq_sum += float(
                torch.sum(torch.square(robot.data.root_lin_vel_b[:, :2])).item()
            )
            actual_linear_velocity_sum += torch.sum(robot.data.root_lin_vel_b, dim=0)
            command_yaw_rate_sq_sum += float(torch.sum(torch.square(commands[:, 2])).item())
            actual_yaw_rate_sq_sum += float(torch.sum(torch.square(robot.data.root_ang_vel_b[:, 2])).item())
            actual_yaw_rate_sum += float(torch.sum(robot.data.root_ang_vel_b[:, 2]).item())
            action_sq_sum += float(torch.sum(torch.square(actions)).item())
            clipped_actions = torch.clamp(actions, -env.unwrapped.cfg.action_clip, env.unwrapped.cfg.action_clip)
            clipped_action_sq_sum += float(torch.sum(torch.square(clipped_actions)).item())
            action_sum += torch.sum(actions, dim=0)
            clipped_action_sum += torch.sum(clipped_actions, dim=0)
            joint_positions = robot.data.joint_pos[:, env.unwrapped._actuated_joint_ids]
            default_joint_positions = robot.data.default_joint_pos[:, env.unwrapped._actuated_joint_ids]
            joint_deviations = joint_positions - default_joint_positions
            joint_abs_deviations = torch.abs(joint_deviations)
            joint_velocities = robot.data.joint_vel[:, env.unwrapped._actuated_joint_ids]
            joint_position_sum += torch.sum(joint_positions, dim=0)
            joint_abs_deviation_sum += torch.sum(joint_abs_deviations, dim=0)
            joint_deviation_sq_sum += torch.sum(torch.square(joint_deviations), dim=0)
            joint_abs_deviation_max = torch.maximum(
                joint_abs_deviation_max, torch.amax(joint_abs_deviations, dim=0)
            )
            joint_velocity_sq_sum += float(torch.sum(torch.square(joint_velocities)).item())
            yaw_mask = torch.abs(commands[:, 2]) > 1.0e-6
            if torch.any(yaw_mask):
                yaw_sample_count = int(torch.count_nonzero(yaw_mask).item())
                yaw_command_samples += yaw_sample_count
                yaw_joint_abs_deviation_sum += torch.sum(joint_abs_deviations[yaw_mask], dim=0)
                yaw_joint_deviation_sq_sum += torch.sum(torch.square(joint_deviations[yaw_mask]), dim=0)
                yaw_joint_abs_deviation_max = torch.maximum(
                    yaw_joint_abs_deviation_max,
                    torch.amax(joint_abs_deviations[yaw_mask], dim=0),
                )
                foot_offset_w = (
                    robot.data.body_pos_w[yaw_mask][:, robot_foot_ids]
                    - robot.data.root_pos_w[yaw_mask].unsqueeze(1)
                )
                root_quat_w = robot.data.root_quat_w[yaw_mask].unsqueeze(1).expand(-1, num_feet, -1)
                foot_position_b = math_utils.quat_apply_inverse(
                    root_quat_w.reshape(-1, 4), foot_offset_w.reshape(-1, 3)
                ).reshape(-1, num_feet, 3)
                yaw_foot_position_body_sum += torch.sum(foot_position_b, dim=0)
                yaw_foot_lateral_sq_sum += torch.sum(torch.square(foot_position_b[:, :, 1]), dim=0)
                yaw_foot_abs_lateral_max = torch.maximum(
                    yaw_foot_abs_lateral_max,
                    torch.amax(torch.abs(foot_position_b[:, :, 1]), dim=0),
                )
                projected_gravity = robot.data.projected_gravity_b[yaw_mask]
                yaw_projected_gravity_abs_sum += torch.sum(torch.abs(projected_gravity[:, :2]), dim=0)
                body_tilt = torch.acos(torch.clamp(-projected_gravity[:, 2], min=-1.0, max=1.0))
                yaw_body_tilt_max = torch.maximum(yaw_body_tilt_max, torch.amax(body_tilt))
            saturated_action_samples += int(
                torch.count_nonzero(torch.abs(actions) >= env.unwrapped.cfg.action_clip).item()
            )
            action_samples += actions.numel()
            soft_limits = robot.data.soft_joint_pos_limits[:, env.unwrapped._actuated_joint_ids]
            processed_targets = env.unwrapped._processed_actions
            joint_target_limit_violations += int(
                torch.count_nonzero(
                    (processed_targets < soft_limits[..., 0]) | (processed_targets > soft_limits[..., 1])
                ).item()
            )
            joint_ranges = torch.clamp(soft_limits[..., 1] - soft_limits[..., 0], min=1.0e-9)
            joint_position_near_limit_samples += int(
                torch.count_nonzero(
                    (joint_positions - soft_limits[..., 0] < 0.02 * joint_ranges)
                    | (soft_limits[..., 1] - joint_positions < 0.02 * joint_ranges)
                ).item()
            )
            effort_limits = robot.data.joint_effort_limits[:, env.unwrapped._actuated_joint_ids]
            applied_torques = torch.abs(robot.data.applied_torque[:, env.unwrapped._actuated_joint_ids])
            torque_saturation_samples += int(
                torch.count_nonzero(applied_torques >= 0.95 * torch.clamp(effort_limits, min=1.0e-9)).item()
            )
            joint_samples += joint_positions.numel()
            foot_forces = torch.linalg.vector_norm(
                contact_sensor.data.net_forces_w[:, contact_foot_ids], dim=-1
            )
            foot_contact_state = torch.where(
                foot_forces >= contact_on_force,
                torch.ones_like(foot_contact_state),
                torch.where(foot_forces <= contact_off_force, torch.zeros_like(foot_contact_state), foot_contact_state),
            )
            touchdowns = foot_contact_state & ~previous_foot_contact_state
            liftoffs = ~foot_contact_state & previous_foot_contact_state
            foot_contacts = foot_contact_state
            planar_foot_speeds = torch.linalg.vector_norm(
                robot.data.body_lin_vel_w[:, robot_foot_ids, :2], dim=-1
            )
            foot_contact_samples += int(torch.count_nonzero(foot_contacts).item())
            foot_contact_possible += foot_contacts.numel()
            contacting_foot_planar_speed_sum += float(torch.sum(planar_foot_speeds * foot_contacts).item())
            per_foot_contact_samples += torch.sum(foot_contacts, dim=0)
            per_foot_touchdowns += torch.sum(touchdowns, dim=0)
            per_foot_liftoffs += torch.sum(liftoffs, dim=0)
            per_foot_stance_origin_speed_sum += torch.sum(planar_foot_speeds * foot_contacts, dim=0)
            per_foot_stance_samples += torch.sum(foot_contacts, dim=0)
            foot_origin_height = (
                robot.data.body_pos_w[:, robot_foot_ids, 2] - env.unwrapped._terrain.env_origins[:, 2:3]
            )
            swing_origin_height_max = torch.where(
                ~foot_contacts,
                torch.maximum(swing_origin_height_max, foot_origin_height),
                swing_origin_height_max,
            )
            completed_height = torch.where(
                touchdowns & torch.isfinite(swing_origin_height_max),
                swing_origin_height_max,
                torch.zeros_like(swing_origin_height_max),
            )
            per_foot_completed_swing_height_sum += torch.sum(completed_height, dim=0)
            per_foot_completed_swings += torch.sum(
                touchdowns & torch.isfinite(swing_origin_height_max), dim=0
            )
            swing_origin_height_max = torch.where(
                touchdowns, torch.full_like(swing_origin_height_max, float("-inf")), swing_origin_height_max
            )
            support_counts = torch.sum(foot_contacts, dim=1)
            support_count_histogram += torch.bincount(support_counts, minlength=num_feet + 1)
            if num_feet == 4:
                diagonal_same_state_samples[0] += torch.sum(foot_contacts[:, 0] == foot_contacts[:, 2])
                diagonal_same_state_samples[1] += torch.sum(foot_contacts[:, 1] == foot_contacts[:, 3])
                diagonal_cross_opposite_samples += torch.sum(foot_contacts[:, 0] != foot_contacts[:, 1])
                mask_env0 = sum(int(foot_contact_state[0, index].item()) << index for index in range(4))
                if not contact_sequence_env0 or contact_sequence_env0[-1]["mask"] != mask_env0:
                    contact_sequence_env0.append({"step": steps, "mask": mask_env0})
            previous_foot_contact_state = foot_contact_state.clone()
            finite = finite and all(
                torch.isfinite(value).all().item()
                for value in (actions, wrapped_env.rew_buf, robot.data.root_pos_w, robot.data.joint_pos)
            )
            if args_cli.num_steps > 0 and steps >= args_cli.num_steps:
                break

    transitions = max(1, steps * wrapped_env.num_envs)
    metrics = {
        "checkpoint": resume_path,
        "num_envs": wrapped_env.num_envs,
        "steps_per_env": steps,
        "total_transitions": steps * wrapped_env.num_envs,
        "total_resets": total_resets,
        "total_terminations": total_terminations,
        "total_timeouts": total_timeouts,
        "resets_per_1000_transitions": 1000.0 * total_resets / transitions,
        "mean_reward_per_step": reward_sum / transitions,
        "linear_velocity_tracking_rmse_m_s": (lin_vel_error_sq_sum / transitions) ** 0.5,
        "linear_velocity_tracking_rmse_by_axis_m_s": (
            torch.sqrt(lin_vel_error_sq_by_axis / transitions).tolist()
        ),
        "yaw_rate_tracking_rmse_rad_s": (yaw_rate_error_sq_sum / transitions) ** 0.5,
        "minimum_base_height_m": min_base_height,
        "maximum_base_height_m": max_base_height,
        "mean_base_height_m": base_height_sum / transitions,
        "command_linear_speed_rms_m_s": (command_linear_speed_sq_sum / transitions) ** 0.5,
        "command_nonzero_axis_fraction": (command_nonzero_axis_counts / transitions).tolist(),
        "multi_axis_command_fraction": multi_axis_command_samples / transitions,
        "stand_command_fraction": stand_command_samples / transitions,
        "actual_linear_speed_rms_m_s": (actual_linear_speed_sq_sum / transitions) ** 0.5,
        "mean_actual_linear_velocity_body_m_s": (actual_linear_velocity_sum / transitions).tolist(),
        "command_yaw_rate_rms_rad_s": (command_yaw_rate_sq_sum / transitions) ** 0.5,
        "actual_yaw_rate_rms_rad_s": (actual_yaw_rate_sq_sum / transitions) ** 0.5,
        "mean_actual_yaw_rate_rad_s": actual_yaw_rate_sum / transitions,
        "action_rms": (action_sq_sum / (transitions * wrapped_env.num_actions)) ** 0.5,
        "clipped_action_rms": (clipped_action_sq_sum / (transitions * wrapped_env.num_actions)) ** 0.5,
        "action_saturation_fraction": saturated_action_samples / max(1, action_samples),
        "joint_target_outside_soft_limit_fraction": joint_target_limit_violations / max(1, joint_samples),
        "joint_position_near_soft_limit_fraction": joint_position_near_limit_samples / max(1, joint_samples),
        "torque_saturation_fraction_95pct": torque_saturation_samples / max(1, joint_samples),
        "mean_action_by_joint": (action_sum / transitions).tolist(),
        "mean_clipped_action_by_joint": (clipped_action_sum / transitions).tolist(),
        "mean_joint_position_rad": (joint_position_sum / transitions).tolist(),
        "actuated_joint_names": list(env.unwrapped.cfg.actuated_joint_names),
        "mean_abs_joint_deviation_rad": (joint_abs_deviation_sum / transitions).tolist(),
        "rms_joint_deviation_rad": torch.sqrt(joint_deviation_sq_sum / transitions).tolist(),
        "max_abs_joint_deviation_rad": joint_abs_deviation_max.tolist(),
        "joint_velocity_rms_rad_s": (
            joint_velocity_sq_sum / (transitions * wrapped_env.num_actions)
        ) ** 0.5,
        "foot_contact_fraction": foot_contact_samples / max(1, foot_contact_possible),
        "mean_contacting_foot_planar_speed_m_s": (
            contacting_foot_planar_speed_sum / max(1, foot_contact_samples)
        ),
        "contact_detection": {
            "method": "net-force hysteresis",
            "on_threshold_n": contact_on_force,
            "off_threshold_n": contact_off_force,
        },
        "foot_metric_semantics": {
            "contact_body_names": list(env.unwrapped.cfg.foot_link_names),
            "planar_speed": "distal-link rigid-body origin proxy; not a collision contact-point velocity",
            "swing_height": "distal-link origin height above terrain; not sole clearance",
            "contact_point_metrics_available": False,
        },
        "per_foot_contact_duty_factor": (per_foot_contact_samples / transitions).tolist(),
        "per_foot_touchdown_count": per_foot_touchdowns.tolist(),
        "per_foot_liftoff_count": per_foot_liftoffs.tolist(),
        "per_foot_mean_stance_link_origin_planar_speed_m_s": (
            per_foot_stance_origin_speed_sum / torch.clamp(per_foot_stance_samples, min=1.0)
        ).tolist(),
        "per_foot_mean_completed_swing_link_origin_max_height_m": (
            per_foot_completed_swing_height_sum / torch.clamp(per_foot_completed_swings, min=1.0)
        ).tolist(),
        "per_foot_completed_swing_count": per_foot_completed_swings.tolist(),
        "support_foot_count_fraction": (support_count_histogram / transitions).tolist(),
        "diagonal_pair_same_contact_state_fraction": (
            diagonal_same_state_samples / transitions
        ).tolist() if num_feet == 4 else None,
        "diagonal_group_opposite_state_fraction": float(diagonal_cross_opposite_samples / transitions)
        if num_feet == 4 else None,
        "contact_state_rle_env0": contact_sequence_env0,
        "yaw_command_posture_diagnostics": {
            "samples": yaw_command_samples,
            "joint_mean_abs_deviation_rad": (
                yaw_joint_abs_deviation_sum / max(1, yaw_command_samples)
            ).tolist(),
            "joint_rms_deviation_rad": torch.sqrt(
                yaw_joint_deviation_sq_sum / max(1, yaw_command_samples)
            ).tolist(),
            "joint_max_abs_deviation_rad": yaw_joint_abs_deviation_max.tolist(),
            "foot_link_names": list(env.unwrapped.cfg.foot_link_names),
            "mean_foot_position_body_m": (
                yaw_foot_position_body_sum / max(1, yaw_command_samples)
            ).tolist(),
            "foot_lateral_rms_m": torch.sqrt(
                yaw_foot_lateral_sq_sum / max(1, yaw_command_samples)
            ).tolist(),
            "foot_lateral_abs_max_m": yaw_foot_abs_lateral_max.tolist(),
            "mean_abs_projected_gravity_xy": (
                yaw_projected_gravity_abs_sum / max(1, yaw_command_samples)
            ).tolist(),
            "max_body_tilt_rad": float(yaw_body_tilt_max.item()),
        } if yaw_command_samples else None,
        "finite": finite,
    }
    rendered_metrics = json.dumps(metrics, indent=2, ensure_ascii=True)
    print("PLAY_METRICS_BEGIN")
    print(rendered_metrics)
    print("PLAY_METRICS_END")
    if args_cli.metrics_output is not None:
        args_cli.metrics_output.parent.mkdir(parents=True, exist_ok=True)
        args_cli.metrics_output.write_text(rendered_metrics + "\n", encoding="utf-8")

    if keyboard_controller is not None:
        keyboard_controller.close()
    wrapped_env.close()


if __name__ == "__main__":
    main()
    simulation_app.close()
