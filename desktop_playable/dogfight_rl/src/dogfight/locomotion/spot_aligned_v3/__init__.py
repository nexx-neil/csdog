"""Independent Spot aligned 48-observation CSDog task."""
import gymnasium as gym
gym.register(id='Dogfight-CSDog-Spot-Aligned-Flat-v3',entry_point='isaaclab.envs:ManagerBasedRLEnv',disable_env_checker=True,
 kwargs={'env_cfg_entry_point':'dogfight.locomotion.spot_aligned_v3.config:AlignedEnvCfg',
 'rsl_rl_cfg_entry_point':'dogfight.locomotion.spot_aligned_v3.config:AlignedPPOCfg'})
