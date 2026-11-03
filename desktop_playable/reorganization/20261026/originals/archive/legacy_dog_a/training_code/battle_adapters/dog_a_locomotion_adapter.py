from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from pathlib import Path
from typing import Any

from dogfight_v0.battle.types import VelocityCommand
from dogfight_v0.config.battle_cfg import BattleConfig


EXPECTED_JOINT_ORDER = (
    "FL_HIP", "FR_HIP", "RL_HIP", "RR_HIP",
    "FL_THIGH", "FR_THIGH", "RL_THIGH", "RR_THIGH",
    "FL_CALF", "FR_CALF", "RL_CALF", "RR_CALF",
)
OBSERVATION_DIMENSION = 48
ACTION_DIMENSION = 12


class DogALocomotionAdapter:
    """Keep every Dog A policy/articulation detail behind VelocityCommand.

    The trained Dog A convention is ``(body lateral-right, body forward,
    yaw-rate)``. DOGFIGHT V0 is ``(body forward, body left, yaw-rate)``.
    The conversion therefore deliberately is ``(-vy, vx, yaw_rate)``.
    """

    def __init__(
        self,
        environment: Any,
        actor: Any,
        config: BattleConfig,
        *,
        actor_output_scale: float,
        checkpoint_path: str | Path,
    ) -> None:
        if not 0.0 < actor_output_scale <= 1.0:
            raise ValueError("actor_output_scale must be in (0, 1]")
        self.environment = environment
        self.actor = actor
        self.config = config
        self.actor_output_scale = float(actor_output_scale)
        self.checkpoint_path = Path(checkpoint_path).resolve()
        self._command = VelocityCommand()
        self._policy_command = (0.0, 0.0, 0.0)
        self._last_observation: Any = None
        self._last_action: Any = None
        self._policy_reset_count = 0
        self._validate_environment()

    @classmethod
    def from_checkpoint(
        cls,
        environment: Any,
        checkpoint_path: str | Path,
        task_config: dict[str, Any],
        config: BattleConfig,
    ) -> "DogALocomotionAdapter":
        from shared.policy import load_actor
        checkpoint_path = Path(checkpoint_path).resolve()
        actor, actor_output_scale = load_actor(checkpoint_path, task_config, environment.device)
        return cls(
            environment,
            actor,
            config,
            actor_output_scale=float(actor_output_scale),
            checkpoint_path=checkpoint_path,
        )

    @property
    def command(self) -> VelocityCommand:
        value = self._command
        return VelocityCommand(value.vx, value.vy, value.yaw_rate)

    @property
    def policy_command(self) -> tuple[float, float, float]:
        return self._policy_command

    @property
    def last_action(self) -> Any:
        return self._last_action

    @property
    def policy_reset_count(self) -> int:
        return self._policy_reset_count

    @property
    def articulation(self) -> Any:
        return self.environment._robot

    def reset(self) -> None:
        import torch

        self._command = VelocityCommand()
        self._policy_command = (0.0, 0.0, 0.0)
        self.environment._fixed_vx_cmd = 0.0
        self.environment._fixed_vy_cmd = 0.0
        self.environment._commands.zero_()
        for name in ("_actions", "_previous_actions", "_raw_policy_actions", "_scaled_policy_actions"):
            value = getattr(self.environment, name, None)
            if value is not None:
                value.zero_()
        if hasattr(self.actor, "reset"):
            self.actor.reset()
        self._last_action = torch.zeros(
            (self.environment.num_envs, ACTION_DIMENSION), device=self.environment.device
        )
        self._last_observation, _ = self.environment.reset()
        # DirectRLEnv reset may reapply training-time sampled commands.
        self.environment._commands.zero_()
        self._last_observation = None
        self._policy_reset_count += 1

    def set_command(self, command: VelocityCommand) -> None:
        vx = max(-self.config.max_vx, min(self.config.max_vx, float(command.vx)))
        vy = max(-self.config.max_vy, min(self.config.max_vy, float(command.vy)))
        yaw_rate = max(
            -self.config.max_yaw_rate,
            min(self.config.max_yaw_rate, float(command.yaw_rate)),
        )
        self._command = VelocityCommand(vx, vy, yaw_rate)
        # Verified existing policy semantics: -X is anatomical left; +Y is forward.
        self._policy_command = (-vy, vx, yaw_rate)
        env = self.environment
        env._fixed_vx_cmd = self._policy_command[0]
        env._fixed_vy_cmd = self._policy_command[1]
        env._commands[:, 0] = self._policy_command[0]
        env._commands[:, 1] = self._policy_command[1]
        env._commands[:, 2] = self._policy_command[2]
        self._last_observation = None

    def compute_action(self, observation: Any = None) -> object:
        import torch

        if observation is None:
            observation = self.environment._get_observations()
        policy_observation = observation["policy"] if isinstance(observation, dict) else observation
        if policy_observation.shape[-1] != OBSERVATION_DIMENSION:
            raise RuntimeError(f"Dog A observation dimension mismatch: {policy_observation.shape}")
        expected = torch.tensor(
            self._policy_command, dtype=policy_observation.dtype, device=policy_observation.device
        )
        if not torch.allclose(policy_observation[:, 9:12], expected.expand_as(policy_observation[:, 9:12])):
            raise RuntimeError("Dog A command buffer did not reach policy observation columns 9:12")
        with torch.inference_mode():
            raw_action = self.actor(policy_observation)
            action = torch.clamp(raw_action * self.actor_output_scale, -1.0, 1.0)
        if action.shape[-1] != ACTION_DIMENSION or not bool(torch.isfinite(action).all()):
            raise RuntimeError(f"invalid Dog A policy action: shape={tuple(action.shape)}")
        self._last_observation = observation
        self._last_action = action
        return action

    def step(self, dt: float) -> None:
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        expected_dt = float(self.environment.step_dt)
        if abs(float(dt) - expected_dt) > 1.0e-6:
            raise ValueError(f"Dog A requires its trained control dt {expected_dt:g}s, got {dt:g}s")
        action = self.compute_action(self._last_observation)
        observation, _reward, terminated, truncated, _extras = self.environment.step(action)
        if bool((terminated | truncated).any()):
            raise RuntimeError("Dog A terminated or timed out during battle locomotion")
        self._last_observation = observation

    def _validate_environment(self) -> None:
        joint_names = tuple(self.environment._robot.joint_names)
        if joint_names != EXPECTED_JOINT_ORDER:
            raise RuntimeError(f"Dog A joint order mismatch: {joint_names}")
        if int(self.environment.num_envs) != 1:
            raise ValueError("Dog A V0 adapter requires exactly one environment")
        if str(self.environment._command_frame) != "body":
            raise RuntimeError("Dog A checkpoint requires body-frame commands")
