# 项目整理迁移清单

2026-10-26 建立；这是本次实际清单，不补造此前 path_migration 证据。

覆盖 3783 个普通文件，包含未跟踪源码/权重。所有文件与目标目录位于设备 66307，采用 rename，同盘不复制大型数据。

Git 原状态与二进制 diff：reorganization/20261026/git_*before*。未执行提交/reset/clean。

修改前按文件保存原文至 reorganization/20261026/originals；changes.json 记录前后摘要；created.json 记录新增文件；moves_done.json 记录已完成移动。回滚先校验现状，保护后续编辑，再按反序移回并恢复原文。

旧训练环境/配置/全量run成套归档；通用奖励和动作审计提取为唯一正式模块；真实旧模型适配器归档。历史脚本不保证旧命令直接执行，复现限制见归档说明。

| 原路径 | 新路径 | 分类 |
|---|---|---|
| `dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_factory.py` | `archive/legacy_dog_a/training_code/battle_adapters/dog_a_factory.py` | legacy_model |
| `dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/dog_a_locomotion_adapter.py` | `archive/legacy_dog_a/training_code/battle_adapters/dog_a_locomotion_adapter.py` | legacy_model |
| `dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0/agents/real_dog_agent.py` | `archive/legacy_dog_a/training_code/battle_adapters/real_dog_agent.py` | legacy_model |
| `dogfight_rl/03_battle/source/dogfight_v0/dogfight_v0` | `dogfight_rl/src/dogfight_v0` | current_battle |
| `dogfight_rl/03_battle/source/dogfight_v0/pyproject.toml` | `dogfight_rl/pyproject.toml` | current_packaging |
| `dogfight_rl/03_battle/source/dogfight_v0/setup.py` | `dogfight_rl/setup.py` | current_packaging |
| `dogfight_rl/03_battle/source/dogfight_v0/config/extension.toml` | `dogfight_rl/configs/battle/extension.toml` | current_extension |
| `dogfight_rl/03_battle/source/dogfight_v0/README.md` | `dogfight_rl/docs/BATTLE_PACKAGE.md` | current_docs |
| `dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/reward_terms.py` | `dogfight_rl/src/dogfight/training/reward_terms.py` | reusable_training |
| `dogfight_rl/02_training/python/dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/action_audit_wrapper.py` | `dogfight_rl/src/dogfight/training/action_audit_wrapper.py` | reusable_training |
| `dogfight_rl/01_robots/assets` | `archive/legacy_dog_a/assets` | legacy_model |
| `dogfight_rl/01_robots/configs` | `archive/legacy_dog_a/configs/robots` | legacy_config |
| `dogfight_rl/01_robots/python/dogfight` | `archive/legacy_dog_a/training_code/dogfight` | legacy_model_code |
| `dogfight_rl/02_training/python/dogfight/tasks` | `archive/legacy_dog_a/training_code/dogfight/tasks` | legacy_training |
| `dogfight_rl/02_training/configs` | `archive/legacy_dog_a/configs/training` | legacy_config |
| `dogfight_rl/02_training/deployment` | `archive/legacy_dog_a/training_code/deployment` | legacy_deployment |
| `dogfight_rl/02_training/scripts` | `archive/legacy_dog_a/training_code/scripts` | legacy_training |
| `dogfight_rl/02_training/logs/back_gait_primitive_recovery` | `archive/legacy_dog_a/checkpoints_and_runs/back_gait_primitive_recovery` | historical_run |
| `dogfight_rl/02_training/logs/back_gait_primitive_recovery_training.log` | `archive/legacy_dog_a/checkpoints_and_runs/back_gait_primitive_recovery_training.log` | historical_run |
| `dogfight_rl/02_training/logs/base_frame_analysis` | `archive/legacy_dog_a/checkpoints_and_runs/base_frame_analysis` | historical_run |
| `dogfight_rl/02_training/logs/dog_a_locomotion_ppo_smoke_v1` | `archive/legacy_dog_a/checkpoints_and_runs/dog_a_locomotion_ppo_smoke_v1` | historical_run |
| `dogfight_rl/02_training/logs/dog_a_symmetric_static_equilibrium` | `archive/legacy_dog_a/checkpoints_and_runs/dog_a_symmetric_static_equilibrium` | historical_run |
| `dogfight_rl/02_training/logs/dog_a_symmetric_v1` | `archive/legacy_dog_a/checkpoints_and_runs/dog_a_symmetric_v1` | historical_run |
| `dogfight_rl/02_training/logs/drop_test` | `archive/legacy_dog_a/checkpoints_and_runs/drop_test` | historical_run |
| `dogfight_rl/02_training/logs/dynamic_contact_diagnosis` | `archive/legacy_dog_a/checkpoints_and_runs/dynamic_contact_diagnosis` | historical_run |
| `dogfight_rl/02_training/logs/external_home` | `archive/historical_validation/anymal/external_home` | historical_run |
| `dogfight_rl/02_training/logs/external_isaaclab` | `archive/historical_validation/anymal/external_isaaclab` | historical_run |
| `dogfight_rl/02_training/logs/implicit_actuator_symmetric_v1` | `archive/legacy_dog_a/checkpoints_and_runs/implicit_actuator_symmetric_v1` | historical_run |
| `dogfight_rl/02_training/logs/joint_direction_test` | `archive/legacy_dog_a/checkpoints_and_runs/joint_direction_test` | historical_run |
| `dogfight_rl/02_training/logs/lateral_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/lateral_ppo` | historical_run |
| `dogfight_rl/02_training/logs/locomotion_smoke_test` | `archive/legacy_dog_a/checkpoints_and_runs/locomotion_smoke_test` | historical_run |
| `dogfight_rl/02_training/logs/migration_smoke` | `archive/legacy_dog_a/checkpoints_and_runs/migration_smoke` | historical_run |
| `dogfight_rl/02_training/logs/model_forensic_audit` | `archive/legacy_dog_a/checkpoints_and_runs/model_forensic_audit` | historical_run |
| `dogfight_rl/02_training/logs/path_migration_20261025_physical_smoke` | `archive/legacy_dog_a/checkpoints_and_runs/path_migration_20261025_physical_smoke` | historical_run |
| `dogfight_rl/02_training/logs/path_migration_20261025_smoke` | `archive/legacy_dog_a/checkpoints_and_runs/path_migration_20261025_smoke` | historical_run |
| `dogfight_rl/02_training/logs/pd_alpha_equilibrium` | `archive/legacy_dog_a/checkpoints_and_runs/pd_alpha_equilibrium` | historical_run |
| `dogfight_rl/02_training/logs/pd_dynamic_equilibrium` | `archive/legacy_dog_a/checkpoints_and_runs/pd_dynamic_equilibrium` | historical_run |
| `dogfight_rl/02_training/logs/pd_stand` | `archive/legacy_dog_a/checkpoints_and_runs/pd_stand` | historical_run |
| `dogfight_rl/02_training/logs/pd_stand_v2` | `archive/legacy_dog_a/checkpoints_and_runs/pd_stand_v2` | historical_run |
| `dogfight_rl/02_training/logs/pd_symmetric_v1` | `archive/legacy_dog_a/checkpoints_and_runs/pd_symmetric_v1` | historical_run |
| `dogfight_rl/02_training/logs/rsl_rl` | `archive/legacy_dog_a/checkpoints_and_runs/rsl_rl` | historical_run |
| `dogfight_rl/02_training/logs/standing_geometry_v2` | `archive/legacy_dog_a/checkpoints_and_runs/standing_geometry_v2` | historical_run |
| `dogfight_rl/02_training/logs/standing_pose_preview` | `archive/legacy_dog_a/checkpoints_and_runs/standing_pose_preview` | historical_run |
| `dogfight_rl/02_training/logs/static_contact_diagnosis` | `archive/legacy_dog_a/checkpoints_and_runs/static_contact_diagnosis` | historical_run |
| `dogfight_rl/02_training/logs/straight_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/straight_ppo` | historical_run |
| `dogfight_rl/02_training/logs/v0` | `archive/legacy_compatibility/training_log_snapshots/v0` | historical_run |
| `dogfight_rl/02_training/logs/v0_2b` | `archive/legacy_compatibility/training_log_snapshots/v0_2b` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_candidate_2300_neg.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_candidate_2300_neg.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_candidate_2300_pos.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_candidate_2300_pos.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_candidate_3500_neg.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_candidate_3500_neg.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_candidate_3500_pos.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_candidate_3500_pos.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_ppo` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_probe_short.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_probe_short.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_reward_sanity.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_reward_sanity.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_neg.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_smoke_vx_neg.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_pos.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_smoke_vx_pos.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_smoke_vx_zero.json` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_smoke_vx_zero.json` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_train_smoke_16env_13iter` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter_v2` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_train_smoke_16env_13iter_v2` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_train_smoke_16env_13iter_v3` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_train_smoke_16env_13iter_v3` | historical_run |
| `dogfight_rl/02_training/logs/x_anti_slip_train_smoke_256env_1iter` | `archive/legacy_dog_a/checkpoints_and_runs/x_anti_slip_train_smoke_256env_1iter` | historical_run |
| `dogfight_rl/02_training/logs/x_bidirectional_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/x_bidirectional_ppo` | historical_run |
| `dogfight_rl/02_training/logs/xy_body_frame_diagnosis` | `archive/legacy_dog_a/checkpoints_and_runs/xy_body_frame_diagnosis` | historical_run |
| `dogfight_rl/02_training/logs/xy_body_frame_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/xy_body_frame_ppo` | historical_run |
| `dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_adapt_50iter.log` | `archive/legacy_dog_a/checkpoints_and_runs/xy_body_frame_ppo_smoke_adapt_50iter.log` | historical_run |
| `dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_adapt_plus_200iter.log` | `archive/legacy_dog_a/checkpoints_and_runs/xy_body_frame_ppo_smoke_adapt_plus_200iter.log` | historical_run |
| `dogfight_rl/02_training/logs/xy_body_frame_ppo_smoke_reset_ycmd_200iter.log` | `archive/legacy_dog_a/checkpoints_and_runs/xy_body_frame_ppo_smoke_reset_ycmd_200iter.log` | historical_run |
| `dogfight_rl/02_training/logs/xy_discrete_ppo` | `archive/legacy_dog_a/checkpoints_and_runs/xy_discrete_ppo` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_recovery_400` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_recovery_400` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_recovery_400.zip` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_recovery_400.zip` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_recovery_400_training.log` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_recovery_400_training.log` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_400` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_400` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_400.zip` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_400.zip` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_400_training.log` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_400_training.log` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_A` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_A` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_A_training.log` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_A_training.log` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_B` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_B` | historical_run |
| `dogfight_rl/02_training/logs/yaxis_reward_recovery_B_training.log` | `archive/legacy_dog_a/checkpoints_and_runs/yaxis_reward_recovery_B_training.log` | historical_run |
| `dogfight_rl/02_training/historical_tests` | `archive/historical_validation/training_copies` | historical_validation |
| `dogfight_rl/03_battle/scripts/v0/__pycache__` | `archive/legacy_compatibility/battle_script_cache/__pycache__` | legacy_diagnostics |
| `dogfight_rl/03_battle/scripts/v0/run_dog_a_battle_integration_test.py` | `archive/legacy_dog_a/diagnostics/battle/run_dog_a_battle_integration_test.py` | legacy_diagnostics |
| `dogfight_rl/03_battle/scripts/v0/run_dog_a_v0_smoke_test.py` | `archive/legacy_dog_a/diagnostics/battle/run_dog_a_v0_smoke_test.py` | legacy_diagnostics |
| `dogfight_rl/03_battle/scripts/v0/run_v02_hud_smoke_tests.py` | `dogfight_rl/scripts/battle/run_v02_hud_smoke_tests.py` | current_battle_script |
| `dogfight_rl/03_battle/scripts/v0/run_v02b_prebattle_gates.py` | `archive/legacy_dog_a/diagnostics/battle/run_v02b_prebattle_gates.py` | legacy_diagnostics |
| `dogfight_rl/03_battle/scripts/v0/run_v0_battle_demo.py` | `dogfight_rl/scripts/battle/run_v0_battle_demo.py` | current_battle_script |
| `dogfight_rl/03_battle/scripts/v0/run_v0_gui.py` | `dogfight_rl/scripts/battle/run_v0_gui.py` | current_battle_script |
| `dogfight_rl/03_battle/scripts/v0/run_v0_headless.py` | `dogfight_rl/scripts/battle/run_v0_headless.py` | current_battle_script |
| `dogfight_rl/03_battle/scripts/v0/run_v0_smoke_tests.py` | `dogfight_rl/scripts/battle/run_v0_smoke_tests.py` | current_battle_script |
| `dogfight_rl/03_battle/logs` | `archive/historical_validation/battle_previous` | historical_battle |
| `dogfight_rl/assets` | `archive/legacy_compatibility/assets` | compatibility_snapshot |
| `dogfight_rl/configs` | `archive/legacy_compatibility/configs` | compatibility_snapshot |
| `dogfight_rl/scripts` | `archive/legacy_compatibility/scripts` | compatibility_snapshot |
| `dogfight_rl/source` | `archive/legacy_compatibility/source` | compatibility_snapshot |
| `dogfight_rl/dogfight` | `archive/legacy_compatibility/dogfight` | compatibility_snapshot |
| `dogfight_rl/logs` | `archive/legacy_compatibility/logs` | compatibility_snapshot |
| `dogfight_rl/checkpoints` | `archive/legacy_compatibility/checkpoints` | compatibility_snapshot |
| `dogfight_rl/videos` | `archive/legacy_compatibility/videos` | compatibility_snapshot |
| `dogfight_rl/shared/paths.py` | `dogfight_rl/src/dogfight/common/paths.py` | current_common |
| `dogfight_rl/shared/policy.py` | `archive/legacy_dog_a/training_code/shared/policy.py` | legacy_deployment |
| `dogfight_rl/shared/scripts` | `dogfight_rl/scripts/diagnostics` | current_diagnostics |
| `dogfight_rl/migration` | `archive/migration_backups/previous_migration` | historical_migration |
| `dogfight_env_freeze` | `archive/environment_records/dogfight_env_freeze` | environment_record |
| `dogfight_env_info` | `archive/environment_records/dogfight_env_info` | environment_record |
| `dogfight_final_tests` | `archive/historical_validation/dogfight_final_tests` | historical_validation |
| `dogfight_rl/docs/environment/freeze_snapshot` | `archive/environment_records/docs_freeze_snapshot` | environment_snapshot |
| `dogfight_rl/docs/environment/env_info` | `archive/environment_records/docs_env_info` | environment_snapshot |
| `dogfight_rl/run_training.sh` | `archive/environment_records/run_training.sh` | historical_environment_entry |
| `dogfight_rl/tests/test_dog_a_interface.py` | `archive/legacy_dog_a/diagnostics/test_dog_a_interface.py` | legacy_mock_test |
| `dogfight_rl/reorganization` | `reorganization/20261026/initial_command_outputs` | task_evidence |
| `dogfight_rl/01_robots` | `archive/legacy_compatibility/layout_remainders/01_robots` | historical_layout_remainder |
| `dogfight_rl/02_training` | `archive/legacy_compatibility/layout_remainders/02_training` | historical_layout_remainder |
| `dogfight_rl/03_battle` | `archive/legacy_compatibility/layout_remainders/03_battle` | historical_layout_remainder |
| `dogfight_rl/shared` | `archive/legacy_compatibility/layout_remainders/shared` | historical_layout_remainder |

逐文件路径、大小、SHA256、inode 见 [manifest.json](reorganization/20261026/manifest.json)，该 JSON 是完整逐文件清单。没有任何删除计划自动执行。
