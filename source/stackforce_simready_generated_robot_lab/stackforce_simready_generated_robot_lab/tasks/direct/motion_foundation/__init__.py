import gymnasium as gym

gym.register(id="CSDog-Motion-Yaw-Learning-Direct-v0",entry_point=f"{__name__}.motion_yaw_learning:MotionYawLearningEnv",disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_yaw_learning:MotionYawLearningEnvCfg","rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"})

for name, env_name, cfg_name in (("Yaw", "MotionYawEnv", "MotionYawEnvCfg"), ("Yaw-Skills", "MotionYawSkillsEnv", "MotionYawSkillsEnvCfg")):
    gym.register(id=f"CSDog-Motion-{name}-Diagnostic-v0",entry_point=f"{__name__}.motion_yaw:{env_name}",disable_env_checker=True,
        kwargs={"env_cfg_entry_point":f"{__name__}.motion_yaw:{cfg_name}","rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"})

gym.register(
    id="CSDog-Motion-Agile-Skills-Diagnostic-v0",
    entry_point=f"{__name__}.motion_agile_skills:MotionAgileSkillsEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_agile_skills:MotionAgileSkillsEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)

for name, cfg_name in (("Adaptive", "MotionAdaptiveSpeedEnvCfg"), ("Exposed", "MotionExposedSpeedEnvCfg")):
    gym.register(
        id=f"CSDog-Motion-{name}-Speed-Diagnostic-v0",
        entry_point=f"{__name__}.motion_adaptive_speed:MotionAdaptiveSpeedEnv",
        disable_env_checker=True,
        kwargs={"env_cfg_entry_point":f"{__name__}.motion_adaptive_speed:{cfg_name}",
                "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
    )

gym.register(
    id="CSDog-Motion-Responsive-Skills-Diagnostic-v0",
    entry_point=f"{__name__}.motion_responsive_skills:MotionResponsiveSkillsEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":f"{__name__}.motion_responsive_skills:MotionResponsiveSkillsEnvCfg",
        "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Residual-Full-Direct-v0",
    entry_point=f"{__name__}.motion_residual:MotionResidualFullEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":f"{__name__}.motion_residual:MotionResidualFullEnvCfg",
        "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Residual-Low-Direct-v0",
    entry_point=f"{__name__}.motion_residual:MotionResidualEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point":f"{__name__}.motion_residual:MotionResidualEnvCfg",
        "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Reference-Diagnostic-v0",
    entry_point=f"{__name__}.motion_reference:MotionReferenceEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.motion_reference:MotionReferenceEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.motion_reference:MotionReferenceRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Foundation-Direct-v0",
    entry_point=f"{__name__}.motion_env:MotionFoundationEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.motion_env_cfg:MotionFoundationEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.motion_env_cfg:MotionFoundationRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Envelope-Direct-v0",
    entry_point=f"{__name__}.motion_env:MotionFoundationEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.motion_env_cfg:MotionEnvelopeEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.motion_env_cfg:MotionEnvelopeRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Calibrated-Direct-v0",
    entry_point=f"{__name__}.motion_env:MotionFoundationEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.motion_calibrated_cfg:MotionCalibratedEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.motion_calibrated_cfg:MotionCalibratedRunnerCfg",
    },
)

gym.register(
    id="CSDog-Motion-Posture-Direct-v0",
    entry_point=f"{__name__}.motion_env:MotionFoundationEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.motion_calibrated_cfg:MotionPostureEnvCfg",
        "rsl_rl_cfg_entry_point": f"{__name__}.motion_calibrated_cfg:MotionPostureRunnerCfg",
    },
)


gym.register(
    id="CSDog-Motion-Residual-Speed-Direct-v0",
    entry_point=f"{__name__}.motion_residual:MotionResidualSpeedEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_residual:MotionResidualSpeedEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Residual-Style-Direct-v0",
    entry_point=f"{__name__}.motion_residual:MotionResidualStyleEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_residual:MotionResidualStyleEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Clean-Direct-v0",
    entry_point=f"{__name__}.motion_clean:MotionCleanEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_clean:MotionCleanEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Skills-Diagnostic-v0",
    entry_point=f"{__name__}.motion_skills:MotionSkillsEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_skills:MotionSkillsEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Transfer-Direct-v0",
    entry_point=f"{__name__}.motion_transfer:MotionTransferEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_transfer:MotionTransferEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Backward-Direct-v0",
    entry_point=f"{__name__}.motion_transfer:MotionBackwardEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_transfer:MotionBackwardEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)


gym.register(
    id="CSDog-Motion-Backward-Skills-Diagnostic-v0",
    entry_point=f"{__name__}.motion_skills:MotionSkillsEnv",
    disable_env_checker=True,
    kwargs={"env_cfg_entry_point":f"{__name__}.motion_skills:MotionBackwardSkillsEnvCfg",
            "rsl_rl_cfg_entry_point":f"{__name__}.motion_reference:MotionReferenceRunnerCfg"},
)
