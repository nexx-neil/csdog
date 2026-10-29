import gymnasium as gym

from . import agents


gym.register(
    id="CSDog-V2-Calibration-Direct-v0",
    entry_point="stackforce_simready_generated_robot_lab.tasks.direct.generated_robot.generated_robot_env:GeneratedRobotEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.csdog_v2_env_cfg:CSDogV2CalibrationEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CSDogV2CalibrationPPORunnerCfg",
    },
)

gym.register(
    id="CSDog-V2-Locomotion-Direct-v0",
    entry_point="stackforce_simready_generated_robot_lab.tasks.direct.generated_robot.generated_robot_env:GeneratedRobotEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.csdog_v2_env_cfg:CSDogV2LocomotionEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CSDogV2LocomotionPPORunnerCfg",
    },
)

gym.register(
    id="CSDog-V2-Phase-Gait-Direct-v0",
    entry_point="stackforce_simready_generated_robot_lab.tasks.direct.generated_robot.generated_robot_env:GeneratedRobotEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.csdog_v2_env_cfg:CSDogV2PhaseGaitEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CSDogV2PhaseGaitPPORunnerCfg",
    },
)

gym.register(
    id="CSDog-V2-Turn-Style-Direct-v0",
    entry_point="stackforce_simready_generated_robot_lab.tasks.direct.generated_robot.generated_robot_env:GeneratedRobotEnv",
    disable_env_checker=True,
    kwargs={
        "env_cfg_entry_point": f"{__name__}.csdog_v2_env_cfg:CSDogV2TurnStyleEnvCfg",
        "rsl_rl_cfg_entry_point": f"{agents.__name__}.rsl_rl_ppo_cfg:CSDogV2TurnStylePPORunnerCfg",
    },
)
