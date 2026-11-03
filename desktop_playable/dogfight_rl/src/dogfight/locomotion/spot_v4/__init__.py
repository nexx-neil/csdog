"""V4 preserves V3 policy/action contracts; reward and lifecycle repairs are isolated."""
import gymnasium as gym
gym.register(id='Dogfight-CSDog-Spot-Flat-v4',entry_point='isaaclab.envs:ManagerBasedRLEnv',disable_env_checker=True,
 kwargs={'env_cfg_entry_point':'dogfight.locomotion.spot_v4.config:V4EnvCfg','rsl_rl_cfg_entry_point':'dogfight.locomotion.spot_v4.config:V4PPOCfg'})
