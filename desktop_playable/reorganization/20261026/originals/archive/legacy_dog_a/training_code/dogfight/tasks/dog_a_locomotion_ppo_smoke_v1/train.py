"""Train the bounded DogA locomotion PPO smoke test with RSL-RL."""
from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from shared.paths import load_project_yaml

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import time
from collections import deque
from datetime import datetime
from pathlib import Path

from isaaclab.app import AppLauncher

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--config", type=Path, default=_project_root / "02_training/configs/dog_a_locomotion_ppo_smoke_v1.yaml")
parser.add_argument("--num-envs", type=int, default=None)
parser.add_argument("--max-iterations", type=int, default=None)
parser.add_argument("--output-dir", type=Path, default=None)
parser.add_argument("--resume", type=Path, default=None, help="Resume model and optimizer; max-iterations is additional updates")
parser.add_argument("--actor-output-scale", type=float, default=None,
                    help="Scale every actor output before action clipping; overrides config actor_output_scale")
parser.add_argument("--min-action-std", type=float, default=None,
                    help="On resume, raise scalar action standard deviations to this exploration floor")
parser.add_argument(
    "--reset-body-yaw-command-columns", action="store_true",
    help="On resume, zero first-layer vy/yaw-command weights (observation columns 10 and 11)",
)
AppLauncher.add_app_launcher_args(parser)
args_cli = parser.parse_args()
if args_cli.actor_output_scale is not None and not 0.0 < args_cli.actor_output_scale <= 1.0:
    parser.error("--actor-output-scale must be in (0, 1]")
if args_cli.min_action_std is not None:
    if args_cli.resume is None or not 0.0 < args_cli.min_action_std <= 2.0:
        parser.error("--min-action-std requires --resume and a value in (0, 2]")
os.environ["DOG_A_LOCOMOTION_TASK_CFG"] = str(args_cli.config.resolve())
# Foot-slip, swing-clearance, air-time rewards and per-foot telemetry all depend
# on real contact state.  Keep the sensor enabled in training, not only eval.
os.environ["DOG_A_ENABLE_CONTACT_SENSOR"] = "1"
simulation_app = AppLauncher(args_cli).app

import carb  # noqa: E402
import torch  # noqa: E402
import yaml  # noqa: E402
from rsl_rl.runners import OnPolicyRunner  # noqa: E402

from isaaclab_rl.rsl_rl import (  # noqa: E402
    RslRlOnPolicyRunnerCfg,
    RslRlPpoActorCriticCfg,
    RslRlPpoAlgorithmCfg,
)

from dogfight.tasks.dog_a_locomotion_ppo_smoke_v1.action_audit_wrapper import ActionAuditRslRlVecEnvWrapper  # noqa: E402

from dogfight.tasks.dog_a_locomotion_ppo_smoke_v1.env import (  # noqa: E402
    ACTUATOR_PATH,
    POSE_PATH,
    DogALocomotionPpoSmokeEnv,
    DogALocomotionPpoSmokeEnvCfg,
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class GpuSampler:
    def __init__(self):
        self.samples_mib: list[int] = []

    def sample(self):
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                check=True, capture_output=True, text=True,
            )
            self.samples_mib.append(int(result.stdout.splitlines()[0].strip()))
        except Exception:
            pass

    def start(self):
        self.sample()

    def close(self):
        self.sample()


class TrainingSafetyMonitor:
    """Abort only on sustained, unambiguously unsafe training behavior."""

    def __init__(self, physx_errors: list[dict]):
        self.physx_errors = physx_errors
        self.steps = 0
        self.saturation = deque(maxlen=120)
        self.falls = deque(maxlen=600)
        self.reward = deque(maxlen=600)
        self.lateral_progress = deque(maxlen=600)
        self.best_reward_window: float | None = None
        self.reward_collapse_windows = 0

    def __call__(self, wrapped, raw_actions, scaled_actions, result):
        observations, rewards, _dones, _extras = result
        self.steps += 1
        floating = [raw_actions, scaled_actions, rewards, observations["policy"]]
        if any(not bool(torch.isfinite(value).all()) for value in floating):
            raise RuntimeError("SAFETY STOP: NaN/Inf in actions, rewards, or observations")
        if self.physx_errors:
            raise RuntimeError(f"SAFETY STOP: PhysX error: {self.physx_errors[-1]}")

        base = wrapped.unwrapped
        self.saturation.append(float((scaled_actions.abs() > 1.0).float().mean()))
        self.falls.append(float(base.reset_terminated.float().mean()))
        self.reward.append(float(rewards.mean()))
        metrics = base.last_step_metrics
        target_vx = metrics["target_vx_body"]
        actual_vx = metrics["actual_vx_body"]
        lateral = target_vx.abs() > 0.08
        if bool(lateral.any()):
            progress = torch.sign(target_vx[lateral]) * actual_vx[lateral]
            self.lateral_progress.append(float(progress.mean()))

        if len(self.saturation) == self.saturation.maxlen and sum(self.saturation) / len(self.saturation) > 0.98:
            raise RuntimeError("SAFETY STOP: actions remained almost fully saturated")
        if len(self.falls) == self.falls.maxlen and sum(self.falls) / len(self.falls) > 0.02:
            raise RuntimeError("SAFETY STOP: sustained high fall rate")
        if len(self.lateral_progress) == self.lateral_progress.maxlen:
            if sum(self.lateral_progress) / len(self.lateral_progress) < -0.05:
                raise RuntimeError("SAFETY STOP: LEFT/RIGHT motion persistently reversed")

        if self.steps % self.reward.maxlen == 0 and len(self.reward) == self.reward.maxlen:
            current = sum(self.reward) / len(self.reward)
            if self.best_reward_window is None or current > self.best_reward_window:
                self.best_reward_window = current
                self.reward_collapse_windows = 0
            elif self.best_reward_window > 0.0 and current < 0.25 * self.best_reward_window:
                self.reward_collapse_windows += 1
                if self.reward_collapse_windows >= 2:
                    raise RuntimeError(
                        f"SAFETY STOP: sustained reward collapse ({current:.6g} vs best {self.best_reward_window:.6g})"
                    )
            else:
                self.reward_collapse_windows = 0


def main():
    cfg_path = args_cli.config.resolve()
    raw = load_project_yaml(cfg_path.read_text(encoding="utf-8"))
    configured_actor_output_scale = raw["actor_output_scale"] if "actor_output_scale" in raw else 1.0
    if (args_cli.actor_output_scale is not None and configured_actor_output_scale is not None
            and abs(float(configured_actor_output_scale) - args_cli.actor_output_scale) > 1.0e-12):
        raise ValueError("CLI actor_output_scale disagrees with the A/B config")
    actor_output_scale = args_cli.actor_output_scale
    if actor_output_scale is None:
        actor_output_scale = configured_actor_output_scale
    if actor_output_scale is None:
        raise ValueError("actor_output_scale must be set in the config or with --actor-output-scale")
    actor_output_scale = float(actor_output_scale)
    if not 0.0 < actor_output_scale <= 1.0:
        raise ValueError("resolved actor_output_scale must be in (0, 1]")
    out = (args_cli.output_dir or (
        (_project_root / "02_training/logs/rsl_rl/dog_a_locomotion_ppo_smoke_v1") / datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    )).resolve()
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(cfg_path, out / "task_config.yaml")
    shutil.copy2(POSE_PATH, out / "standing_pose_baseline.yaml")
    shutil.copy2(ACTUATOR_PATH, out / "implicit_actuator_baseline.yaml")

    env_cfg = DogALocomotionPpoSmokeEnvCfg()
    if args_cli.num_envs is not None:
        env_cfg.scene.num_envs = args_cli.num_envs
    env_cfg.sim.device = args_cli.device
    env_cfg.viewer.eye = (2.5, 2.5, 1.5)
    env_cfg.viewer.lookat = (0.8, 0.0, 0.1)
    env_cfg.viewer.origin_type = "env"
    env_cfg.viewer.env_index = 0
    ppo = raw["ppo"]
    iterations = args_cli.max_iterations if args_cli.max_iterations is not None else int(ppo["max_iterations"])
    agent_cfg = RslRlOnPolicyRunnerCfg(
        seed=int(ppo["seed"]),
        device=args_cli.device,
        num_steps_per_env=int(ppo["num_steps_per_env"]),
        max_iterations=iterations,
        obs_groups={"policy": ["policy"], "critic": ["policy"]},
        clip_actions=1.0,
        save_interval=int(ppo["save_interval"]),
        experiment_name="dog_a_locomotion_ppo_smoke_v1",
        logger="tensorboard",
        policy=RslRlPpoActorCriticCfg(
            init_noise_std=float(ppo["init_noise_std"]),
            actor_obs_normalization=False,
            critic_obs_normalization=False,
            actor_hidden_dims=list(ppo["actor_hidden_dims"]),
            critic_hidden_dims=list(ppo["critic_hidden_dims"]),
            activation=ppo["activation"],
        ),
        algorithm=RslRlPpoAlgorithmCfg(
            value_loss_coef=float(ppo["value_loss_coef"]),
            use_clipped_value_loss=bool(ppo["use_clipped_value_loss"]),
            clip_param=float(ppo["clip_param"]),
            entropy_coef=float(ppo["entropy_coef"]),
            num_learning_epochs=int(ppo["num_learning_epochs"]),
            num_mini_batches=int(ppo["num_mini_batches"]),
            learning_rate=float(ppo["learning_rate"]),
            schedule=ppo["schedule"],
            gamma=float(ppo["gamma"]),
            lam=float(ppo["lambda"]),
            desired_kl=float(ppo["desired_kl"]),
            max_grad_norm=float(ppo["max_grad_norm"]),
        ),
    )

    physx_errors: list[dict] = []
    cuda_errors: list[str] = []
    logger = carb.logging.acquire_logging()

    def capture(source, level, file_name, line_number, message):
        text = f"{source} {message}"
        if level >= carb.logging.LEVEL_ERROR and "physx" in text.lower():
            physx_errors.append({"03_battle/source": str(source), "message": str(message)})

    handle = logger.add_logger(capture)
    sampler = GpuSampler()
    sampler.start()
    start = time.time()
    env = None
    try:
        torch.manual_seed(agent_cfg.seed)
        env = DogALocomotionPpoSmokeEnv(env_cfg)
        preflight = env.preflight()
        preflight.update({
            "pose_sha256": sha256(POSE_PATH),
            "actuator_config_sha256": sha256(ACTUATOR_PATH),
            "training_iterations": iterations,
            "rollout_steps_per_env": agent_cfg.num_steps_per_env,
            "actor_output_scale": actor_output_scale,
            "action_pipeline": "raw_actor_output -> actor_output_scale -> clip[-1,1] -> actuator_action",
        })
        print("SMOKE TEST PREFLIGHT\n" + json.dumps(preflight, indent=2), flush=True)
        (out / "preflight.json").write_text(json.dumps(preflight, indent=2) + "\n", encoding="utf-8")
        safety_monitor = TrainingSafetyMonitor(physx_errors)
        wrapped = ActionAuditRslRlVecEnvWrapper(
            env, clip_actions=agent_cfg.clip_actions, actor_output_scale=actor_output_scale,
            safety_callback=safety_monitor,
        )
        runner = OnPolicyRunner(wrapped, agent_cfg.to_dict(), log_dir=str(out), device=agent_cfg.device)
        sampler.sample()
        runner._prepare_logging_writer()
        if args_cli.resume is not None:
            resume_path = args_cli.resume.resolve()
            loaded = torch.load(resume_path, map_location="cpu", weights_only=False)
            runner.load(str(resume_path))
            runner.current_learning_iteration = int(loaded["iter"]) + 1
            shutil.copy2(resume_path, out / f"resume_iteration_{int(loaded['iter']) + 1}.pt")
            if args_cli.min_action_std is not None or args_cli.reset_body_yaw_command_columns:
                with torch.no_grad():
                    if args_cli.min_action_std is not None:
                        if not hasattr(runner.alg.policy, "std"):
                            raise RuntimeError("policy has no scalar action std; cannot apply exploration floor")
                        runner.alg.policy.std.clamp_(min=args_cli.min_action_std)
                    if args_cli.reset_body_yaw_command_columns:
                        actor_input = runner.alg.policy.actor[0]
                        critic_input = runner.alg.policy.critic[0]
                        if not isinstance(actor_input, torch.nn.Linear) or not isinstance(critic_input, torch.nn.Linear):
                            raise RuntimeError("actor/critic input layer is not linear; cannot reset command columns")
                        actor_input.weight[:, 10:12].zero_()
                        critic_input.weight[:, 10:12].zero_()
                runner.alg.optimizer.state.clear()
                runner.alg.learning_rate = float(ppo["learning_rate"])
                for group in runner.alg.optimizer.param_groups:
                    group["lr"] = runner.alg.learning_rate
                runner.save(str(out / f"model_{runner.current_learning_iteration}_adapted_initial.pt"),
                            infos={"actor_output_scale": actor_output_scale,
                                   "min_action_std": args_cli.min_action_std,
                                   "reset_body_yaw_command_columns": args_cli.reset_body_yaw_command_columns,
                                   "optimizer_learning_rate": runner.alg.learning_rate,
                                   "optimizer_state_reset": True})
                print(f"ADAPTED CHECKPOINT: actor output scale={actor_output_scale}; "
                      f"minimum action std={args_cli.min_action_std}; "
                      f"reset body vy/yaw command columns={args_cli.reset_body_yaw_command_columns}; "
                      f"optimizer state reset, lr={runner.alg.learning_rate:g}", flush=True)
        else:
            runner.save(str(out / "model_0_initial.pt"), infos={"stage": "initial_untrained"})
        # Keep full initial episodes so custom episodic metrics use exact denominators.
        runner.learn(num_learning_iterations=iterations, init_at_random_ep_len=False)
        sampler.sample()
        final_checkpoint = out / f"model_{runner.current_learning_iteration}.pt"
        runner.save(str(final_checkpoint), infos={
            "actor_output_scale": actor_output_scale,
            "action_pipeline": "raw_actor_output -> actor_output_scale -> clip[-1,1] -> actuator_action",
        })
        shutil.copy2(final_checkpoint, out / "model_final.pt")
        # Preserve a deterministic upload path for the otherwise timestamped
        # TensorBoard event file.
        runner.writer.flush()
        event_files = sorted(out.glob("events.out.tfevents.*"))
        # The .bin name prevents TensorBoard from auto-loading this duplicate
        # alongside the live timestamped event file in the same log directory.
        tensorboard_snapshot = out / "tensorboard_event_snapshot.bin"
        if not event_files:
            raise RuntimeError("TensorBoard writer produced no event file")
        shutil.copy2(event_files[-1], tensorboard_snapshot)
        finite_checkpoint = True
        saved = torch.load(final_checkpoint, map_location="cpu", weights_only=False)
        for value in saved.get("model_state_dict", {}).values():
            if isinstance(value, torch.Tensor) and not torch.isfinite(value).all():
                finite_checkpoint = False
                break
        elapsed = time.time() - start
        telemetry = {
            "status": "completed",
            "training_iterations": iterations,
            "final_checkpoint_iteration": int(saved.get("iter", runner.current_learning_iteration)),
            "resumed_from": str(args_cli.resume.resolve()) if args_cli.resume is not None else None,
            "actor_output_scale": actor_output_scale,
            "actor_output_scale_source": "cli" if args_cli.actor_output_scale is not None else "config",
            "action_pipeline": "raw_actor_output -> actor_output_scale -> clip[-1,1] -> actuator_action",
            "min_action_std": args_cli.min_action_std,
            "reset_body_yaw_command_columns": args_cli.reset_body_yaw_command_columns,
            "total_control_steps": iterations * agent_cfg.num_steps_per_env * env.num_envs,
            "total_sim_steps": iterations * agent_cfg.num_steps_per_env * env.num_envs * env.cfg.decimation,
            "wall_clock_training_time_s": elapsed,
            "gpu_memory_samples_mib": sampler.samples_mib,
            "gpu_memory_peak_mib": max(sampler.samples_mib) if sampler.samples_mib else None,
            "torch_cuda_peak_allocated_mib": torch.cuda.max_memory_allocated() / 2**20,
            "checkpoint_finite": finite_checkpoint,
            "nan": not finite_checkpoint,
            "inf": not finite_checkpoint,
            "physx_errors": physx_errors,
            "cuda_errors": cuda_errors,
            "command_transition_counts": env.command_transition_counts(),
            "final_checkpoint": str(out / "model_final.pt"),
            "tensorboard_event_files": [str(path) for path in event_files],
            "tensorboard_event_snapshot": str(tensorboard_snapshot),
        }
        (out / "telemetry.json").write_text(json.dumps(telemetry, indent=2) + "\n", encoding="utf-8")
        print("SMOKE TEST TELEMETRY\n" + json.dumps(telemetry, indent=2), flush=True)
    except Exception as exc:
        if "cuda" in str(exc).lower():
            cuda_errors.append(repr(exc))
        failure = {
            "status": "failed", "exception": repr(exc), "physx_errors": physx_errors,
            "cuda_errors": cuda_errors, "wall_clock_s": time.time() - start,
            "gpu_memory_samples_mib": sampler.samples_mib,
        }
        (out / "telemetry.json").write_text(json.dumps(failure, indent=2) + "\n", encoding="utf-8")
        raise
    finally:
        sampler.close()
        logger.remove_logger(handle)
        if env is not None:
            env.close()


if __name__ == "__main__":
    try:
        main()
    finally:
        simulation_app.close()
