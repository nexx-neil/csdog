"""Independent csdog_12dof manager-based velocity task."""
import gymnasium as gym
gym.register(id='Dogfight-CSDog-Velocity-Flat-v0', entry_point='isaaclab.envs:ManagerBasedRLEnv',disable_env_checker=True,
 kwargs={'env_cfg_entry_point':'dogfight.locomotion.env_cfg:CSDogEnvCfg',
 'rsl_rl_cfg_entry_point':'dogfight.locomotion.ppo_cfg:CSDogPPORunnerCfg'})
