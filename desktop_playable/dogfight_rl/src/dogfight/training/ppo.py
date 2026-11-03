"""Existing RSL-RL/PPO integration; call only after AppLauncher starts Isaac Sim."""
def make_runner_config(ppo, *, device, iterations, experiment_name):
    from isaaclab_rl.rsl_rl import RslRlOnPolicyRunnerCfg, RslRlPpoActorCriticCfg, RslRlPpoAlgorithmCfg
    return RslRlOnPolicyRunnerCfg(
        seed=int(ppo["seed"]),
        device=device,
        num_steps_per_env=int(ppo["num_steps_per_env"]),
        max_iterations=iterations,
        obs_groups={"policy": ["policy"], "critic": ["policy"]},
        clip_actions=1.0,
        save_interval=int(ppo["save_interval"]),
        experiment_name=experiment_name,
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

def create_runner(environment, runner_config, *, log_dir, actor_output_scale=1.0, safety_callback=None):
    """Wrap an explicitly created environment; no model or checkpoint defaults."""
    from rsl_rl.runners import OnPolicyRunner
    from .action_audit_wrapper import ActionAuditRslRlVecEnvWrapper
    wrapped = ActionAuditRslRlVecEnvWrapper(environment, clip_actions=runner_config.clip_actions,
        actor_output_scale=actor_output_scale, safety_callback=safety_callback)
    return OnPolicyRunner(wrapped, runner_config.to_dict(), log_dir=str(log_dir), device=runner_config.device)
