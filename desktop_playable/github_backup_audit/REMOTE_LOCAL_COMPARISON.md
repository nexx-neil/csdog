# GitHub 远端与本地对比

审计：2026-11-03T17:21:24.094188+08:00

远端 https://github.com/nexx-neil/csdog 。本报告只读查询，无 fetch/clone/checkout/提交/推送。归档仅在内存展开。GitHub API branches/tree/releases 均返回403 rate limit exceeded，以下使用 ls-remote 与按提交固定的 codeload 源码归档独立验证。Release API 内容未验证。

## 本机 Git 真实状态

工作区根不是Git仓库，业务Git在 `/home/zxq/robot_projects/dogfight_rl/.git`。remote -v 为空：本地未配置该GitHub remote。不能将本地 main 误认为远端 main。

```text

  backup/pre-v0.2b-gates-20260920 01fe058 WIP: snapshot existing RealDog integration before V0.2-B gates
  main                            6d87182 Dogfight V0.1 battle skeleton - 15/15 PASS
  v0.2-hud                        42d762b Dogfight V0.2-A GUI HUD and RealDog adapter skeletons
* v0.2-real-dog-a                 d94aba2 Add Real Dog A pre-battle gate validation


## v0.2-real-dog-a
 M .gitignore
 M AGENTS.md
 D assets/dog_a/.asset_hash
 D assets/dog_a/README.md
 D assets/dog_a/config.yaml
 D assets/dog_a/configuration/dog_a_base.usd
 D assets/dog_a/configuration/dog_a_physics.usd
 D assets/dog_a/configuration/dog_a_robot.usd
 D assets/dog_a/configuration/dog_a_sensor.usd
 D assets/dog_a/dog_a.usd
 D assets/dog_a/urdf/dog_a_import.urdf
 D assets/dog_a/usd_attempt_002_named_joints/.asset_hash
 D assets/dog_a/usd_attempt_002_named_joints/config.yaml
 D assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_base.usd
 D assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_physics.usd
 D assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_robot.usd
 D assets/dog_a/usd_attempt_002_named_joints/configuration/dog_a_sensor.usd
 D assets/dog_a/usd_attempt_002_named_joints/dog_a.usd
 D assets/dog_a_symmetric_v1/generation/generate_symmetric_model.py
 D assets/dog_a_symmetric_v1/generation/generation_summary.json
 D assets/dog_a_symmetric_v1/generation/mesh_generation_manifest.json
 D assets/dog_a_symmetric_v1/manifest/original_assets_sha256_after.json
 D assets/dog_a_symmetric_v1/manifest/original_assets_sha256_before.json
 D assets/dog_a_symmetric_v1/meshes/FL_CALF.STL
 D assets/dog_a_symmetric_v1/meshes/FL_HIP.STL
 D assets/dog_a_symmetric_v1/meshes/FL_THIGH.STL
 D assets/dog_a_symmetric_v1/meshes/FR_CALF_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/FR_HIP_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/FR_THIGH_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/RL_CALF.STL
 D assets/dog_a_symmetric_v1/meshes/RL_HIP.STL
 D assets/dog_a_symmetric_v1/meshes/RL_THIGH.STL
 D assets/dog_a_symmetric_v1/meshes/RR_CALF_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/RR_HIP_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/RR_THIGH_MIRRORED.STL
 D assets/dog_a_symmetric_v1/meshes/base_link_symmetric.STL
 D assets/dog_a_symmetric_v1/urdf/dog_a_symmetric_v1.urdf
 D assets/dog_a_symmetric_v1/usd/.asset_hash
 D assets/dog_a_symmetric_v1/usd/config.yaml
 D assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_base.usd
 D assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_physics.usd
 D assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_robot.usd
 D assets/dog_a_symmetric_v1/usd/configuration/dog_a_symmetric_v1_sensor.usd
 D assets/dog_a_symmetric_v1/usd/dog_a_symmetric_v1.usd
 D configs/back_gait_primitive_recovery.yaml
 D configs/dog_a_bidirectional_lateral_ppo.yaml
 D configs/dog_a_bidirectional_x_ppo.yaml
 D configs/dog_a_body_xy_transition_ppo.yaml
 D configs/dog_a_dynamic_equilibrium_compensation.yaml
 D configs/dog_a_locomotion_ppo_smoke_v1.yaml
 D configs/dog_a_original_locomotion_ppo_smoke.yaml
 D configs/dog_a_original_straight_ppo.yaml
 D configs/dog_a_standing_pose.yaml
 D configs/dog_a_standing_pose_v2.yaml
 D configs/dog_a_symmetric_v1_implicit_actuator.yaml
 D configs/dog_a_symmetric_v1_standing_pose.yaml
 D configs/dog_a_x_anti_slip_ppo.yaml
 D configs/dog_a_x_command_transition_ppo.yaml
 D configs/dog_a_x_left_focus_ppo.yaml
 D configs/dog_a_x_left_reexplore_ppo.yaml
 D configs/dog_a_x_mixed_drift_ppo.yaml
 D configs/dog_a_x_right_recovery_ppo.yaml
 D configs/dog_a_xy_discrete_transition_ppo.yaml
 D configs/dog_a_yaxis_recovery_400.yaml
 D configs/pd_alpha_equilibrium.yaml
 D configs/pd_symmetric_v1_01.yaml
 D configs/pd_symmetric_v1_02.yaml
 D configs/pd_v2_01.yaml
 D configs/pd_v2_02.yaml
 D configs/yaxis_reward_recovery_A.yaml
 D configs/yaxis_reward_recovery_B.yaml
 D docs/BASE_FRAME_ANALYSIS.md
 D docs/DEV_LOG.md
 D docs/DOGFIGHT_V02A_HUD.md
 D docs/DOGFIGHT_V0_README.md
 D docs/DOG_A_LOCOMOTION_PPO_SMOKE_TEST.md
 D docs/DOG_A_MODEL_FORENSIC_AUDIT.md
 D docs/DOG_A_SYMMETRIC_JOINT_DIRECTION_REPORT.md
 D docs/DOG_A_SYMMETRIC_STATIC_EQUILIBRIUM.md
 D docs/DOG_A_SYMMETRIC_V1_GENERATION.md
 D docs/DOG_A_V0_NORMALIZATION.md
 D docs/DROP_TEST_REPORT.md
 D docs/DYNAMIC_CONTACT_DIAGNOSIS.md
 D docs/JOINT_DIRECTION_REPORT.md
 D docs/JOINT_MAP.md
 D docs/MIRRORED_STANDING_POSE_SEARCH.md
 D docs/ORIGINAL_URDF_LOCOMOTION_PPO_SMOKE_TEST.md
 D docs/PD_ALPHA_EQUILIBRIUM_DIAGNOSIS.md
 D docs/PD_DYNAMIC_EQUILIBRIUM_COMPENSATION.md
 D docs/PD_STANDING_REPORT.md
 D docs/PD_SYMMETRIC_V1_REPORT.md
 D docs/PD_V2_STANDING_REPORT.md
 D docs/PROJECT_ISSUES_AND_ATTEMPTS_REPORT.md
 D docs/STANDING_GEOMETRY_ANALYSIS.md
 D docs/STANDING_GEOMETRY_V2_FINAL_REPORT.md
 D docs/STANDING_POSE_SEARCH_REPORT.md
 D docs/STATIC_CONTACT_DIAGNOSIS.md
 D docs/STRAIGHT_PPO_TRAINING.md
 D docs/TRUE_FOOT_JACOBIAN.md
 D docs/URDF_AUDIT_REPORT.md
 D docs/URDF_IMPORT_RECORD.md
 D dogfight/analysis/analyze_implicit_standing.py
 D dogfight/analysis/dog_a_symmetric_static_equilibrium.py
 D dogfight/geometry/foot_contact_solver.py
 D dogfight/robots/dog_a_cfg.py
 D dogfight/robots/prepare_dog_a_import_urdf.py
 D dogfight/tasks/__init__.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/__init__.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/action_audit_wrapper.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/env.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/evaluate.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/reward_terms.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/train.py
 D dogfight/tasks/dog_a_locomotion_ppo_smoke_v1/validate.py
 D dogfight/tests/analyze_contact_dynamics.py
 D dogfight/tests/analyze_dynamic_equilibrium.py
 D dogfight/tests/analyze_pd_alpha_equilibrium.py
 D dogfight/tests/analyze_pd_v2_02.py
 D dogfight/tests/back_gait_reward_sanity.py
 D dogfight/tests/base_frame_analysis.py
 D dogfight/tests/collider_foot_point_micro.py
 D dogfight/tests/contact_dynamics_diagnosis.py
 D dogfight/tests/contact_force_sanity.py
 D dogfight/tests/dog_a_symmetric_free_drop.py
 D dogfight/tests/dog_a_symmetric_joint_direction_test.py
 D dogfight/tests/dog_a_symmetric_runtime_audit.py
 D dogfight/tests/dog_a_x_reward_sanity.py
 D dogfight/tests/dog_a_xy_reward_sanity.py
 D dogfight/tests/drop_test.py
 D dogfight/tests/fk_jacobian_micro.py
 D dogfight/tests/identify_dynamic_equilibrium_sensitivity.py
 D dogfight/tests/implicit_actuator_symmetric_v1.py
 D dogfight/tests/joint_direction_test.py
 D dogfight/tests/mirrored_standing_pose_search.py
 D dogfight/tests/pd_alpha_equilibrium_trial.py
 D dogfight/tests/pd_dynamic_equilibrium_trial.py
 D dogfight/tests/pd_stand_test.py
 D dogfight/tests/pd_stand_v2.py
 D dogfight/tests/pd_stand_v2_02.py
 D dogfight/tests/pd_symmetric_v1.py
 D dogfight/tests/prefilter_dynamic_equilibrium.py
 D dogfight/tests/runtime_initial_state_diagnosis.py
 D dogfight/tests/spawn_robot.py
 D dogfight/tests/standing_pose_preview.py
 D dogfight/tests/standing_pose_search_v2.py
 D dogfight/tests/static_contact_diagnosis.py
 D run_training.sh
 D scripts/analyze_dog_a_four_direction.py
 D scripts/check_environment.py
 D scripts/check_environment.sh
 D scripts/compare_dog_a_x_directions.py
 D scripts/evaluate_dog_a_x_directions.sh
 D scripts/manage_nvidia_apt_hold.sh
 D scripts/resume_dog_a_x_700_from_300.sh
 D scripts/resume_dog_a_x_finetune_300_from_999.sh
 D scripts/resume_dog_a_x_straight_500_from_1599.sh
 D scripts/resume_dog_a_x_transition_300_from_1299.sh
 D scripts/resume_dog_a_xy_500_from_2099.sh
 D scripts/resume_dog_a_yaxis_recovery_400.sh
 D scripts/run_yaxis_reward_recovery_smoke.sh
 D scripts/select_best_back_gait_checkpoint.py
 D scripts/select_best_training_checkpoint.py
 D scripts/train_back_gait_primitive_recovery_400.sh
 D scripts/train_original_dog_a_straight.py
 D scripts/v0/run_dog_a_battle_integration_test.py
 D scripts/v0/run_dog_a_v0_smoke_test.py
 D scripts/v0/run_v02_hud_smoke_tests.py
 D scripts/v0/run_v02b_prebattle_gates.py
 D scripts/v0/run_v0_battle_demo.py
 D scripts/v0/run_v0_gui.py
 D scripts/v0/run_v0_headless.py
 D scripts/v0/run_v0_smoke_tests.py
 D scripts/validate_back_gait_five_direction_fresh_reset_gui.sh
 D scripts/validate_back_gait_primitive_config.py
 D scripts/validate_back_gait_primitive_fresh_reset_gui.sh
 D scripts/validate_dog_a_yaxis_recovery_400_gui.sh
 D scripts/validate_yaxis_recovery_configs.py
 D scripts/validate_yaxis_reward_recovery_gui.sh
 D scripts/visualize_dog_a_left_stop_right.sh
 D scripts/visualize_dog_a_straightness_left_stop_right.sh
 D scripts/visualize_dog_a_transition_left_stop_right.sh
 D scripts/visualize_dog_a_xy_continuous.sh
 D source/dogfight_v0/README.md
 D source/dogfight_v0/config/extension.toml
 D source/dogfight_v0/dogfight_v0/__init__.py
 D source/dogfight_v0/dogfight_v0/agents/__init__.py
 D source/dogfight_v0/dogfight_v0/agents/agent_interface.py
 D source/dogfight_v0/dogfight_v0/agents/dog_a_factory.py
 D source/dogfight_v0/dogfight_v0/agents/dog_a_locomotion_adapter.py
 D source/dogfight_v0/dogfight_v0/agents/locomotion_interface.py
 D source/dogfight_v0/dogfight_v0/agents/proxy_agent.py
 D source/dogfight_v0/dogfight_v0/agents/real_dog_agent.py
 D source/dogfight_v0/dogfight_v0/agents/real_locomotion_adapter.py
 D source/dogfight_v0/dogfight_v0/arena/__init__.py
 D source/dogfight_v0/dogfight_v0/arena/map_interface.py
 D source/dogfight_v0/dogfight_v0/arena/spawn_manager.py
 D source/dogfight_v0/dogfight_v0/arena/test_map.py
 D source/dogfight_v0/dogfight_v0/battle/__init__.py
 D source/dogfight_v0/dogfight_v0/battle/battle_manager.py
 D source/dogfight_v0/dogfight_v0/battle/health_system.py
 D source/dogfight_v0/dogfight_v0/battle/intel_service.py
 D source/dogfight_v0/dogfight_v0/battle/interfaces.py
 D source/dogfight_v0/dogfight_v0/battle/ray_query.py
 D source/dogfight_v0/dogfight_v0/battle/scripted_policy.py
 D source/dogfight_v0/dogfight_v0/battle/types.py
 D source/dogfight_v0/dogfight_v0/battle/visibility_service.py
 D source/dogfight_v0/dogfight_v0/battle/weapon_service.py
 D source/dogfight_v0/dogfight_v0/config/__init__.py
 D source/dogfight_v0/dogfight_v0/config/battle_cfg.py
 D source/dogfight_v0/dogfight_v0/logging/__init__.py
 D source/dogfight_v0/dogfight_v0/logging/battle_logger.py
 D source/dogfight_v0/dogfight_v0/navigation/__init__.py
 D source/dogfight_v0/dogfight_v0/navigation/navigation_interface.py
 D source/dogfight_v0/dogfight_v0/navigation/simple_navigation.py
 D source/dogfight_v0/dogfight_v0/runtime.py
 D source/dogfight_v0/dogfight_v0/sim/__init__.py
 D source/dogfight_v0/dogfight_v0/sim/physx_ray_query.py
 D source/dogfight_v0/dogfight_v0/sim/scene.py
 D source/dogfight_v0/dogfight_v0/ui/__init__.py
 D source/dogfight_v0/dogfight_v0/ui/battle_hud.py
 D source/dogfight_v0/pyproject.toml
 D source/dogfight_v0/setup.py
 M tests/conftest.py
 D tests/test_dog_a_interface.py
 M tests/test_hud.py
 M tests/test_intel_5s.py
 M tests/test_navigation.py
 M tests/test_real_adapters.py
 M tests/test_round.py
 M tests/test_spawn.py
 M tests/test_visibility.py
 M tests/test_weapon.py
?? DOGFIGHT_THREE_DOG_DELIVERY.md
?? DOGFIGHT_V0_2_DELIVERY.md
?? README.md
?? assets/csdog_12dof/README.md
?? assets/csdog_12dof/collision_sole_candidate/csdog.usda
?? assets/csdog_12dof/collision_sole_candidate/rejected_001.usda
?? assets/csdog_12dof/collision_sole_candidate/rejected_002.usda
?? assets/csdog_12dof/import_v1/.asset_hash
?? assets/csdog_12dof/import_v1/config.yaml
?? assets/csdog_12dof/import_v1/configuration/csdog_base.usd
?? assets/csdog_12dof/import_v1/configuration/csdog_physics.usd
?? assets/csdog_12dof/import_v1/configuration/csdog_robot.usd
?? assets/csdog_12dof/import_v1/configuration/csdog_sensor.usd
?? assets/csdog_12dof/import_v1/csdog.usd
?? assets/csdog_12dof/peer_teleop_v1/IMPORT_MANIFEST.json
?? assets/csdog_12dof/peer_teleop_v1/model/README.md
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl
?? assets/csdog_12dof/peer_teleop_v1/model/robot.urdf
?? assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf
?? assets/csdog_12dof/peer_teleop_v1/policies/v1/identity.json
?? assets/csdog_12dof/peer_teleop_v1/usd/.asset_hash
?? assets/csdog_12dof/peer_teleop_v1/usd/config.yaml
?? assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_base.usd
?? assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_physics.usd
?? assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_robot.usd
?? assets/csdog_12dof/peer_teleop_v1/usd/configuration/csdog_sensor.usd
?? assets/csdog_12dof/peer_teleop_v1/usd/csdog.usd
?? assets/ui/dogfight_teleop.svg
?? configs/autoppo/csdog-autoppo-lab.service
?? configs/autoppo/curriculum.yaml
?? configs/autoppo/evaluation.yaml
?? configs/autoppo/search_space.yaml
?? configs/autoppo/system.yaml
?? configs/battle/extension.toml
?? configs/locomotion/csdog_ppo/model_audit.json
?? configs/locomotion/csdog_ppo/stage1.json
?? configs/locomotion/csdog_ppo/stage2.json
?? configs/locomotion/curriculum_v6/default.json
?? configs/locomotion/curriculum_v6_1/default.json
?? configs/robots/csdog_12dof.yaml
?? configs/robots/dog_a_teleop.yaml
?? configs/teleop/default.yaml
?? configs/teleop/fsm_battle.yaml
?? configs/teleop/single_dog.yaml
?? csdog_ppo_tuning_v5/README.md
?? csdog_ppo_tuning_v5/analyze_history.py
?? csdog_ppo_tuning_v5/best_config.yaml
?? csdog_ppo_tuning_v5/configs/baseline.yaml
?? csdog_ppo_tuning_v5/configs/evaluation.yaml
?? csdog_ppo_tuning_v5/configs/search_space.yaml
?? csdog_ppo_tuning_v5/configs/trial_001_control.yaml
?? csdog_ppo_tuning_v5/configs/trial_002.yaml
?? csdog_ppo_tuning_v5/configs/trial_003.yaml
?? csdog_ppo_tuning_v5/configs/trial_004.yaml
?? csdog_ppo_tuning_v5/finish.py
?? csdog_ppo_tuning_v5/plot_initial_kl.py
?? csdog_ppo_tuning_v5/refine_metrics.py
?? csdog_ppo_tuning_v5/report.py
?? csdog_ppo_tuning_v5/search.py
?? csdog_ppo_tuning_v5/verify_export.py
?? docs/BATTLE_GUIDE.md
?? docs/BATTLE_PACKAGE.md
?? docs/FIRST_PERSON_VIEW.md
?? docs/FSM_BATTLE_V1_DELIVERY.md
?? docs/LOCOMOTION_PPO.md
?? docs/TELEOP_POLICY_AUDIT.md
?? docs/TRAINING_GUIDE.md
?? launch.py
?? pyproject.toml
?? scripts/autoppo/audit_physics.py
?? scripts/autoppo/autoppo.py
?? scripts/autoppo/finalize_validation.py
?? scripts/autoppo/install_service.py
?? scripts/autoppo/smoke_test.py
?? scripts/autoppo/v7.py
?? scripts/autoppo/verify_launch.py
?? scripts/autoppo/write_reports.py
?? scripts/battle/run_v02_hud_smoke_tests.py
?? scripts/battle/run_v0_battle_demo.py
?? scripts/battle/run_v0_gui.py
?? scripts/battle/run_v0_headless.py
?? scripts/battle/run_v0_smoke_tests.py
?? scripts/diagnostics/analyze_csdog_aligned_v3.py
?? scripts/diagnostics/analyze_csdog_experiment.py
?? scripts/diagnostics/analyze_csdog_spot_v2.py
?? scripts/diagnostics/check_environment.py
?? scripts/diagnostics/check_environment.sh
?? scripts/diagnostics/convert_csdog.py
?? scripts/diagnostics/csdog_aligned_dynamics.py
?? scripts/diagnostics/csdog_aligned_fixture.py
?? scripts/diagnostics/csdog_aligned_joint_properties.py
?? scripts/diagnostics/csdog_aligned_pd_probe.py
?? scripts/diagnostics/csdog_aligned_unload.py
?? scripts/diagnostics/csdog_physics_check.py
?? scripts/diagnostics/csdog_reward_gate.py
?? scripts/diagnostics/csdog_spot_gate.py
?? scripts/diagnostics/csdog_spot_v4_balance.py
?? scripts/diagnostics/curriculum_supervisor.py
?? scripts/diagnostics/curriculum_v6_1_supervisor.py
?? scripts/diagnostics/curriculum_v6_3_manager.py
?? scripts/diagnostics/manage_nvidia_apt_hold.sh
?? scripts/diagnostics/official_train_check.py
?? scripts/diagnostics/plot_spot_v4_validation.py
?? scripts/diagnostics/run_csdog_aligned_evaluations.py
?? scripts/diagnostics/seal_csdog_aligned_v3.py
?? scripts/diagnostics/seal_csdog_task.py
?? scripts/diagnostics/seal_v7_validation.py
?? scripts/diagnostics/v6_1_comparison_report.py
?? scripts/diagnostics/v6_1_contact_report.py
?? scripts/diagnostics/v6_1_experiment_batch.py
?? scripts/diagnostics/v6_1_finalize.py
?? scripts/diagnostics/v6_1_history_batch.py
?? scripts/diagnostics/v6_1_repair_report.py
?? scripts/diagnostics/v6_3_ab_report.py
?? scripts/diagnostics/v6_3_failure_analysis.py
?? scripts/diagnostics/v6_3_history.py
?? scripts/diagnostics/v6_3_history_report.py
?? scripts/diagnostics/v6_3_launch_report.py
?? scripts/diagnostics/v7_collision_probe.py
?? scripts/diagnostics/v7_lift_probe.py
?? scripts/diagnostics/verify_integrity.py
?? scripts/diagnostics/verify_training_runtime.py
?? scripts/diagnostics/write_csdog_aligned_report.py
?? scripts/diagnostics/write_csdog_aligned_reward_report.py
?? scripts/diagnostics/write_csdog_report.py
?? scripts/diagnostics/write_csdog_spot_report.py
?? scripts/evaluate/csdog_12dof.py
?? scripts/evaluate/csdog_curriculum_v6.py
?? scripts/evaluate/csdog_curriculum_v6_1.py
?? scripts/evaluate/csdog_spot_aligned_v3.py
?? scripts/evaluate/csdog_spot_v2.py
?? scripts/evaluate/csdog_spot_v4.py
?? scripts/evaluate/csdog_spot_v5.py
?? scripts/launch_dogfight_fsm.sh
?? scripts/launch_dogfight_teleop.sh
?? scripts/teleop/dogfight-fsm.desktop
?? scripts/teleop/dogfight-teleop.desktop
?? scripts/teleop/run.py
?? scripts/teleop/summarize_fsm_validation.py
?? scripts/teleop/verify_attached_gui.py
?? scripts/teleop/verify_desktop_launch.py
?? scripts/teleop/verify_fsm_gui.py
?? scripts/teleop/verify_keyboard_gui.py
?? scripts/teleop/verify_three_dog_gui.py
?? scripts/train/csdog_12dof.py
?? scripts/train/csdog_curriculum_v6.py
?? scripts/train/csdog_curriculum_v6_1.py
?? scripts/train/csdog_curriculum_v6_3.py
?? scripts/train/csdog_spot_aligned_v3.py
?? scripts/train/csdog_spot_v2.py
?? scripts/train/csdog_spot_v4.py
?? scripts/train/csdog_spot_v5.py
?? setup.py
?? src/dogfight/__init__.py
?? src/dogfight/autoppo/__init__.py
?? src/dogfight/autoppo/checkpoint_bank.py
?? src/dogfight/autoppo/config.py
?? src/dogfight/autoppo/curriculum_manager.py
?? src/dogfight/autoppo/evaluation.py
?? src/dogfight/autoppo/experiment_manager.py
?? src/dogfight/autoppo/gait_audit.py
?? src/dogfight/autoppo/motion_evaluator.py
?? src/dogfight/autoppo/phase_v7_manager.py
?? src/dogfight/autoppo/phase_v7_search.py
?? src/dogfight/autoppo/plots.py
?? src/dogfight/autoppo/recovery_manager.py
?? src/dogfight/autoppo/resource_monitor.py
?? src/dogfight/autoppo/rewards.py
?? src/dogfight/autoppo/runtime.py
?? src/dogfight/autoppo/search_optimizer.py
?? src/dogfight/autoppo/storage.py
?? src/dogfight/autoppo/stride.py
?? src/dogfight/autoppo/train_runner.py
?? src/dogfight/common/__init__.py
?? src/dogfight/common/paths.py
?? src/dogfight/fsm/__init__.py
?? src/dogfight/fsm/controller.py
?? src/dogfight/fsm/navigation.py
?? src/dogfight/fsm/perception.py
?? src/dogfight/fsm/physical_validation.py
?? src/dogfight/fsm/visualization.py
?? src/dogfight/locomotion/LICENSE.NVIDIA
?? src/dogfight/locomotion/README.md
?? src/dogfight/locomotion/THIRD_PARTY_NOTICES.md
?? src/dogfight/locomotion/__init__.py
?? src/dogfight/locomotion/budget.py
?? src/dogfight/locomotion/control_validation/__init__.py
?? src/dogfight/locomotion/control_validation/kinematics.py
?? src/dogfight/locomotion/curriculum_v6/OLD_EXPERIMENT_ANALYSIS.md
?? src/dogfight/locomotion/curriculum_v6/README.md
?? src/dogfight/locomotion/curriculum_v6/__init__.py
?? src/dogfight/locomotion/curriculum_v6/commands.py
?? src/dogfight/locomotion/curriculum_v6/config.py
?? src/dogfight/locomotion/curriculum_v6/evaluation.py
?? src/dogfight/locomotion/curriculum_v6/rewards.py
?? src/dogfight/locomotion/curriculum_v6/runner.py
?? src/dogfight/locomotion/curriculum_v6/supervisor.py
?? src/dogfight/locomotion/curriculum_v6_1/__init__.py
?? src/dogfight/locomotion/curriculum_v6_1/config.py
?? src/dogfight/locomotion/curriculum_v6_1/contacts.py
?? src/dogfight/locomotion/curriculum_v6_1/evaluation.py
?? src/dogfight/locomotion/curriculum_v6_1/events.py
?? src/dogfight/locomotion/curriculum_v6_1/rewards.py
?? src/dogfight/locomotion/curriculum_v6_1/runner.py
?? src/dogfight/locomotion/curriculum_v6_1/supervisor.py
?? src/dogfight/locomotion/curriculum_v6_3/__init__.py
?? src/dogfight/locomotion/curriculum_v6_3/config.py
?? src/dogfight/locomotion/curriculum_v6_3/evaluation.py
?? src/dogfight/locomotion/curriculum_v6_3/evaluation_version.py
?? src/dogfight/locomotion/curriculum_v6_3/rewards.py
?? src/dogfight/locomotion/curriculum_v6_3/runner.py
?? src/dogfight/locomotion/curriculum_v6_3/stride.py
?? src/dogfight/locomotion/curriculum_v6_3/supervisor.py
?? src/dogfight/locomotion/env_cfg.py
?? src/dogfight/locomotion/mdp.py
?? src/dogfight/locomotion/model_audit.py
?? src/dogfight/locomotion/phase_guided_v7/__init__.py
?? src/dogfight/locomotion/phase_guided_v7/evaluation.py
?? src/dogfight/locomotion/phase_guided_v7/kernel.py
?? src/dogfight/locomotion/phase_guided_v7/plots.py
?? src/dogfight/locomotion/phase_guided_v7/reporting.py
?? src/dogfight/locomotion/phase_guided_v7/runtime.py
?? src/dogfight/locomotion/phase_guided_v7/trace_metrics.py
?? src/dogfight/locomotion/phase_guided_v7/train.py
?? src/dogfight/locomotion/ppo_cfg.py
?? src/dogfight/locomotion/robot_cfg.py
?? src/dogfight/locomotion/runner.py
?? src/dogfight/locomotion/spot_aligned_v3/__init__.py
?? src/dogfight/locomotion/spot_aligned_v3/budget.py
?? src/dogfight/locomotion/spot_aligned_v3/calibration.py
?? src/dogfight/locomotion/spot_aligned_v3/config.py
?? src/dogfight/locomotion/spot_aligned_v3/rewards.py
?? src/dogfight/locomotion/spot_aligned_v3/runner.py
?? src/dogfight/locomotion/spot_v2/__init__.py
?? src/dogfight/locomotion/spot_v2/budget.py
?? src/dogfight/locomotion/spot_v2/config.py
?? src/dogfight/locomotion/spot_v2/contacts.py
?? src/dogfight/locomotion/spot_v2/rewards.py
?? src/dogfight/locomotion/spot_v2/runner.py
?? src/dogfight/locomotion/spot_v4/__init__.py
?? src/dogfight/locomotion/spot_v4/cli.py
?? src/dogfight/locomotion/spot_v4/config.py
?? src/dogfight/locomotion/spot_v4/contracts.py
?? src/dogfight/locomotion/spot_v4/diagnostic_ik.py
?? src/dogfight/locomotion/spot_v4/evaluation.py
?? src/dogfight/locomotion/spot_v4/gait.py
?? src/dogfight/locomotion/spot_v4/rewards.py
?? src/dogfight/locomotion/spot_v4/runner.py
?? src/dogfight/locomotion/spot_v4/runtime.py
?? src/dogfight/locomotion/spot_v5/__init__.py
?? src/dogfight/locomotion/spot_v5/audit.py
?? src/dogfight/locomotion/spot_v5/config.py
?? src/dogfight/locomotion/spot_v5/evaluation.py
?? src/dogfight/locomotion/spot_v5/telemetry.py
?? src/dogfight/robots/__init__.py
?? src/dogfight/robots/csdog_12dof.py
?? src/dogfight/teleop/__init__.py
?? src/dogfight/teleop/agent.py
?? src/dogfight/teleop/combat.py
?? src/dogfight/teleop/config.py
?? src/dogfight/teleop/first_person.py
?? src/dogfight/teleop/hud.py
?? src/dogfight/teleop/keyboard.py
?? src/dogfight/teleop/laser.py
?? src/dogfight/teleop/maps.py
?? src/dogfight/teleop/multi_hud.py
?? src/dogfight/teleop/multi_runtime.py
?? src/dogfight/teleop/policy.py
?? src/dogfight/teleop/runtime.py
?? src/dogfight/training/__init__.py
?? src/dogfight/training/action_audit_wrapper.py
?? src/dogfight/training/checkpoints.py
?? src/dogfight/training/deployment.py
?? src/dogfight/training/ppo.py
?? src/dogfight/training/reward_terms.py
?? src/dogfight/training/telemetry.py
?? src/dogfight_v0/__init__.py
?? src/dogfight_v0/agents/__init__.py
?? src/dogfight_v0/agents/agent_interface.py
?? src/dogfight_v0/agents/locomotion_interface.py
?? src/dogfight_v0/agents/proxy_agent.py
?? src/dogfight_v0/agents/real_dog_agent.py
?? src/dogfight_v0/agents/real_locomotion_adapter.py
?? src/dogfight_v0/arena/__init__.py
?? src/dogfight_v0/arena/map_interface.py
?? src/dogfight_v0/arena/spawn_manager.py
?? src/dogfight_v0/arena/test_map.py
?? src/dogfight_v0/battle/__init__.py
?? src/dogfight_v0/battle/battle_manager.py
?? src/dogfight_v0/battle/health_system.py
?? src/dogfight_v0/battle/intel_service.py
?? src/dogfight_v0/battle/interfaces.py
?? src/dogfight_v0/battle/ray_query.py
?? src/dogfight_v0/battle/scripted_policy.py
?? src/dogfight_v0/battle/types.py
?? src/dogfight_v0/battle/visibility_service.py
?? src/dogfight_v0/battle/weapon_service.py
?? src/dogfight_v0/config/__init__.py
?? src/dogfight_v0/config/battle_cfg.py
?? src/dogfight_v0/logging/__init__.py
?? src/dogfight_v0/logging/battle_logger.py
?? src/dogfight_v0/navigation/__init__.py
?? src/dogfight_v0/navigation/navigation_interface.py
?? src/dogfight_v0/navigation/simple_navigation.py
?? src/dogfight_v0/runtime.py
?? src/dogfight_v0/sim/__init__.py
?? src/dogfight_v0/sim/physx_ray_query.py
?? src/dogfight_v0/sim/scene.py
?? src/dogfight_v0/ui/__init__.py
?? src/dogfight_v0/ui/battle_hud.py
?? tests/test_autoppo_gait.py
?? tests/test_autoppo_system.py
?? tests/test_curriculum_v6.py
?? tests/test_curriculum_v6_1.py
?? tests/test_curriculum_v6_3.py
?? tests/test_first_person.py
?? tests/test_fsm_battle.py
?? tests/test_locomotion_task.py
?? tests/test_phase_guided_v7.py
?? tests/test_phase_v7_manager.py
?? tests/test_phase_v7_search.py
?? tests/test_phase_v7_trace.py
?? tests/test_portable_resources.py
?? tests/test_project_paths.py
?? tests/test_robot_boundary.py
?? tests/test_spot_aligned_budget.py
?? tests/test_spot_v2_budget.py
?? tests/test_spot_v4.py
?? tests/test_spot_v5_tuning.py
?? tests/test_teleop_v02.py
?? tests/test_three_dog_teleop.py
?? tests/test_training_tools.py


```

## 远端引用

```text

0ac3f5c59ea6719581bfc0f492583db5aa7237fd	HEAD
2acb747c13ec0cd4f4390977ea14f4721d64056f	refs/heads/codex/csdog-v2-locomotion
36dc1e429ed84e9e7ba44cc7600b940a26978142	refs/heads/csdog-v2-teleop-v0.1.0-assets
0ac3f5c59ea6719581bfc0f492583db5aa7237fd	refs/heads/main
14777e3bc1231855c552726c57c86d6ccb8fa8bc	refs/tags/csdog-v2-teleop-v0.1.0
2acb747c13ec0cd4f4390977ea14f4721d64056f	refs/tags/csdog-v2-teleop-v0.1.0^{}


```

本地分支 `v0.2-real-dog-a` HEAD d94aba2；初始折叠状态为11修改、221删除、52未跟踪项（目录会折叠，不等于文件数）。删除多为重组后的旧路径，不能执行 git add -A 将其直接变成远端历史删除。

## 固定提交内容逐项核对

### main

提交 `0ac3f5c59ea6719581bfc0f492583db5aa7237fd`；归档 SHA256 `29a31714523a8f7db5d42f93dbfa3830ffe94f23f4ace66704c9e140746c1d5c`。

已读取 173 个文件，展开逻辑字节 25674355。

|远端路径|字节|SHA256|本地对应/结论|
|---|---:|---|---|
|`.gitignore`|509|`e1e04fc428d89037939f5466956c793f688ec0d6b6ee36500363cb2278a4e603`|同路径不同，禁止覆盖远端|
|`CURRENT.md`|7051|`dee0a53041f89266656dedb8e8176592435e7164e85c639663fa5e1271d3a7d2`|本地同路径不存在；保留远端历史|
|`HANDOFF.md`|9997|`b75e525eaf9438670bef0e6aed2d1e571b39bad85a6ea7da8ddcd6b0fa87b0b9`|本地同路径不存在；保留远端历史|
|`PARAMETERS.md`|7837|`07cf55994e88a3a50497cd49cb982b46e527dbf548fb7d86a92ce19ebe1a3ced`|本地同路径不存在；保留远端历史|
|`README.md`|2764|`817c4229150b4a88b2df113da7989b97bb88c13c1d7a17238a916c18f1342a16`|同路径不同，禁止覆盖远端|
|`assets/Stackforce-simready-generated_robot-isaac-lab.zip`|10326712|`cab2e4728ad6f595dbc26ea4c3669bf9606033f793384cb0b60a7154cd145c0f`|本地同路径不存在；保留远端历史|
|`assets/local_mu3x59rz_5j49gz_urdf_stl.zip`|2909905|`98f7742e33f6f9e5b4f88adefda0fcaf82827f3afdca129d4afc59639ec22c55`|本地同路径不存在；保留远端历史|
|`config/csdog_v2_urdf_expectations.json`|876|`fb37256f303192563a761a2a1443bdf4c087555fe9ceef36399f67ae9d05a243`|本地同路径不存在；保留远端历史|
|`config/experiments/csdog_v2_abc.json`|2223|`598acf1054f2c88b6232921d04317df89bf88358ee2582a5dd1d383244172c9e`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_AUDIT_AND_TRAINING_PLAN.md`|9414|`5e94a79f526fcdaaf0eee2f6c763a6e90230961c53bc5390f32a16453686a0a7`|本地同路径不存在；保留远端历史|
|`docs/LINUX_FIRST_RUN.md`|2988|`fa8ea8aee3a9abfe842e46eaa8e3d49cdd0874296fc2817980c365405a8dd481`|本地同路径不存在；保留远端历史|
|`docs/MODEL_TO_URDF_AND_LOCOMOTION.md`|11736|`5b28059a20f8e7f295a0ce884e8d2734b8cbb12524b0a37b5bd0de7d4950f6af`|本地同路径不存在；保留远端历史|
|`docs/MODEL_VALIDATION.md`|1722|`2170270d8bb6de7c061dbb2c57e83b4145573d31eeb9d0c42d643bb97f7b970f`|本地同路径不存在；保留远端历史|
|`experiments/2026-09-17_LINUX_BASELINE_AND_PPO_SMOKE.md`|9266|`24378044acf22b48a2ac35d8b093d1ac09e651e68bb7f74682ef2fe5aa7d739f`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_GATES.md`|872|`00586a31e2a3508fe92e92d86c462b769c8154beedcbd67d50b894a2478850ca`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_STATIC_AUDIT.md`|3142|`d1b1aa01b823cdf85cdfccbb7b2a007c81513206c0d01c691aadb43fd2192990`|本地同路径不存在；保留远端历史|
|`experiments/TEMPLATE.md`|745|`46a984127d093b1aded0e5acd3a1d36134f58aa9f38764dccf4e4b9ebb3034d1`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_forward_metrics.json`|2426|`dadcb49b72dbfccbe4653b43c4127e3f37fd1b3edff659daa4f3499374378e63`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_lateral_metrics.json`|2443|`5601aba822cc45d604c20843333ee25a7f421a1df0bcf3a46181ff687d3767a5`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_yaw_metrics.json`|2460|`9f431d35b8c028039032097487163a48140b99e3b2f8a9e008faa365de3c3b6c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_forward_metrics.json`|2455|`c78a856b6ecde5dd7c2b60c902201dd5e4d9952d84ec9718d1173a78a614c014`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_lateral_metrics.json`|2457|`0fa3b6d4907b497b625c549166d9245438c6ff9a3744bffebfa5c56a33e0f820`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_stand_metrics.json`|2442|`a3b822449a786000719f6f09105bafc9168aad97a66c15ea4eec23bd226b6f7f`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_yaw_metrics.json`|2421|`838e18c63f22412890ef51de3f408351fcaa53c36e75fd3ad14eebfb78c5dece`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_forward_metrics.json`|2428|`cefbc079ed5aa591aa1fe115202256e547fb24b1556c5de8143b58ad2230ca73`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_lateral_metrics.json`|2440|`59e21721d98dbe046fbe7748c8e873f8abba6ef71a29bb27cd8f0b2f42b5c1d0`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_yaw_metrics.json`|2451|`d43eb5c558ddad95276d9fc774844cdba5218e22bf2b7f5072a56588112c3042`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v16_lateral_015_metrics.json`|2443|`c28d9ea7d04886235366dd0311fd5befc391bdd8229f4e599add6f058351292c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v16_lateral_050_metrics.json`|2458|`22cb75c3b20a8c96e01b5cc94c3a8c228ce28585de1739bb96268f42a336bc5d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v17_lateral_015_metrics.json`|2431|`ace660af817cbc39c4408a0f790b0c2904a978d781ae49cfc56f881a0a0ea628`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v17_lateral_030_metrics.json`|2437|`f3fcb8ae8f7928bb242b16ac9e916d3010c2cc8066a1dba3d2055c0e362f2945`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/fixed_command_sampling_smoke.json`|2351|`cebab844deb13930c58ef330a04d30278d03d3fd75f77e997a64b2e8ce0c910d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/nominal_pose_v7_height_threshold_30s.json`|3378|`c635568b265c86ba9be123e238ce656b3d8c20656be68654acd6fbf20572a3d4`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/single_axis_sampling_smoke.json`|2465|`664817cabe0e5565357d27edf23991fb255ad813f46d8c29e83fa08b22043cd6`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_gate_pipeline.json`|1205|`2039a86e3c560339834acc9ea3ca35626fe94c62d7f5cc03752c8eda5680e6ab`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_static_audit.json`|18131|`999427430cfe800b147d7c051527a61823e51cad0e24922eaa8daea05a1a6960`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/locomotion_source_audit.json`|3679|`c313f1d2e44db0cd7d01c0f266f192022ee944c8bab07f446b1988c4f402e516`|本地同路径不存在；保留远端历史|
|`scripts/audit_urdf.py`|16909|`a30461f1cd5deeb991696713771492f1b111a28d30d89b0a5981bde8b2330f64`|本地同路径不存在；保留远端历史|
|`scripts/diagnose_joint_directions.py`|7003|`e09ad1cd89e2238eecc794be55bc25c8403fb21ebbce839d8eaf3f2ba23b5125`|本地同路径不存在；保留远端历史|
|`scripts/diagnose_zero_pose.py`|10964|`7c5064d407cfe95f6fd62e260e1364a4e6d112c987f416a6b1809d72e953fb9d`|本地同路径不存在；保留远端历史|
|`scripts/evaluate_fixed_commands.py`|5435|`8cf8258588867535ed33bc76f79e3800d98c8746d79d0be2f0b6919f8ae9b3e6`|本地同路径不存在；保留远端历史|
|`scripts/list_envs.py`|1060|`95ea3948e736dc821f93024eb2a6a7db66011b689d1eb8a3326469ef813fed0d`|本地同路径不存在；保留远端历史|
|`scripts/random_agent.py`|1151|`07bc418e53decf0e92b649b05e14cab48bbca6f2647e3d60be36362dfa34b0e3`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/cli_args.py`|1963|`fc1077b0cfe7c51fd8ee2ab240320116147286c1f6f4207899f09bfff713d295`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/play.py`|33963|`43013b0fd107daa486866c2ab946349df9c5a29f980ea6d91891ea0b93752b08`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/train.py`|21755|`1fb2760135f9da1279d82d7348754bce8a84ff20326fbae19aa3b70c73683e07`|本地同路径不存在；保留远端历史|
|`scripts/run_csdog_v2_gates.py`|3776|`3a70ae0e780433fb431269cbac3112a9e7314873b83e4e5110b7ec403798d0a3`|本地同路径不存在；保留远端历史|
|`scripts/zero_agent.py`|1538|`c705dbef43ee67c62d1c36ced634dca67b58466b5d57c7061f275b3555978796`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/pyproject.toml`|94|`7f4d920bc75d4e2c9f5e73f3215b4a4bcc3f52f4f641de3a2a28d8b6b3d03b9f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/setup.py`|346|`d2f03b778cfb952a0f5cf7d0455dfa440be1c6de6ac788f85101bce2e3fb3e41`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/__init__.py`|20|`5084f413dea9293a22c593b440cc08e44adf9817d015fee77fb8cb0bb5a129f0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/README.md`|1243|`ce359d2f2556a1bc6b3f67611637005574edf78922e92d87df0a5fc1c3075c42`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/base_collision.stl`|1484|`9c93aa72fd27c40d50539c5cbf45d5e0418986f6f0a09481c363969ed5eb6079`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_pitch_collision.stl`|190484|`04945bf61bf4f2e49ca242de5069a1fab2bda87e2da1b5704bbd2a04ce100b80`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_roll_collision.stl`|236484|`a942c5e921a3b5bbd17f2f53a5fcf439526b8aec6eaed38cc92575b16b904043`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_knee_collision.stl`|53684|`cb0146a5bc3f73180ed02082054dd9fb8cd634c3abd3f38b75aee8090f1a3beb`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_pitch_collision.stl`|190634|`cba39b20e1a2e078ea98122d99c3fb5a86dd87ee0b2b8d2cbce268208dfca5d8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_roll_collision.stl`|236984|`c3a5d8e7282b55c3d114e46ad34c29f34ff6c4927b009de3dd07ac2ebe27b957`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_knee_collision.stl`|53734|`7fa626081e4394d74cc615afe4c0e51323013875c607dc57e2a38c4be6df6c23`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_pitch_collision.stl`|197184|`b276f7c04b288794a97f3a78fb1acc404a9e0123cd90002424cdf36bb1710666`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_roll_collision.stl`|236234|`cdd1f1a41f4160d680d91290f3b219ac997ea544758b08d419601daebfb22fa4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_knee_collision.stl`|53634|`6418e0c18075866d356c1bdc3dcf4f364fedc16caa219e65345382c1e5bacf31`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_pitch_collision.stl`|190784|`6f1fc0b7b00902bdd611ec403f03d5eacfbfe165350470699bf2dbfce7c926c7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_roll_collision.stl`|237534|`b5ac7b6b6beb836cf1d5d18e3f8ec08ae87133cb0bc0d875757a02a35f53e04f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_knee_collision.stl`|53984|`eda21673b014b7b392d1f1ebbc0aa31dabd3d4a351244a92a135f8aeb46c9dd8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf`|12505|`20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_001_solid_001.stl`|173484|`972596c70fed3f0bad4593e12cfac299f4255aa89200c7acdc8ae5059d47f970`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_002_solid_002.stl`|126884|`2c445d59cfac5f7111b9a957defc062475bb852926f9cb2e97306567e8191c2a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_003_solid_003.stl`|66484|`78bc62e747c3974dbef1b1fda1f13b7ccbf6ba82aed3196c05e9074252018a4c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_004_solid_004.stl`|98684|`34b090a0aa237ef30c3e50cd646cd3a6f2864574af7ab3ed14badf798507d1a3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_005_solid_005.stl`|141584|`e20a936288a8b82cb547e156528aee6438e04b9b2636c376eb9c55fa1f4f088c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_006_solid_006.stl`|120884|`f1f52fe62f3fce7dfddfcd86c8d5c6663876724e08b54310b59450df2b9c289c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_007_solid_007.stl`|176884|`7d80a7e0a017094178875a5661ddaa5d88eb4466e4afdd1fb61238f8b01c8b50`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_008_solid_008.stl`|72884|`5302f9e4f909ec345a36983f2fd39542753911aab5786815c5bf189502e73fc3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_009_solid_009.stl`|77284|`347edd8316b1adc47af7c288c499a88b0054d65915e206629968ea03fc51f692`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_010_solid_010.stl`|126884|`168efbb968eb7ffafe268b9427fd781788f42fbc90973edc928b182067d63a04`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_011_solid_011.stl`|66484|`3d73932d4dc326339212b2890743178138ad484866dabcec2eb0467576f86d71`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_012_solid_012.stl`|98684|`13bc7fd77d70bb8b0a262ea6d9f3bdf9720b7aebd69d1b8008dc34563157f914`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_013_solid_013.stl`|141584|`2c2aad90c398267fbca00e62a062090e109a9465708ccf56b3aaf60cf0fd9f3d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_014_solid_014.stl`|120884|`33d189a0cf4221156d0154aa83f44feb0cef0b040f48ca141807762bfa0b3c5b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_015_solid_015.stl`|176884|`873859bb083adbcdfc2ce8a7b94b717b80e4452915b2db1b9debd385c3f04e31`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_016_solid_016.stl`|126884|`05953591f889e896603aa31db25ddbe2190d04d8965b62fc8403d6dafa10a1a1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_017_solid_017.stl`|66484|`7c628885c1506dfe10fc2ce1582ccb88bcd6e8abf1c47fcddd595b35c2b8d14b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_018_solid_018.stl`|98684|`8824cee99aee4a9ad024fa02c03c2d7bc3645d990724fa4b266322add8ec0260`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_019_solid_019.stl`|141584|`27186e0f5a15af39960bf37541c7a872426d97d3bb576463896569b6be9d23fa`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_020_solid_020.stl`|120884|`743f03a8174edbc80df5a32f813b4382f2595399b8b31655919041605b00a49c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_021_solid_021.stl`|176884|`e9b62328aff0e3188790ddb0f181bd9b02bd099f38bbb55c4347c6a2178acf03`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_022_solid_022.stl`|77284|`a10ba0ab5c7be42de19eba6fda2b5f018d74bce282d709e770f67e6d66ddfd01`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_023_solid_023.stl`|37484|`a9edb11eb95be7980c7b26a931ff1d375e3d99937cfe74b3818f104499522b84`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_024_solid_024.stl`|38634|`8e56cb5ddf6a76d70e698e3f2ee619e4266574bb352cc086f2fc924692fce790`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_025_solid_025.stl`|126884|`8c9723c897e082195575dd7dc320e0043f7ca862aef4fc178c492a2baf62db12`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_026_solid_026.stl`|66484|`b02362cda21cd214dc60061a1d95c0ff0d37bd51fbb03d3e462883284af1ca34`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_027_solid_027.stl`|98684|`0105d70295ac72e01fc45778ca1710447e01542091e00dac8586ad1316806cd4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_028_solid_028.stl`|141584|`c20e75dfedd29c1d0320668ca3c1745b075f22dfa892628c4fb8b90327933be3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_029_solid_029.stl`|120884|`fb89b0cac2af9041f374b03ca7343bd3f6a985f5362cb22dc14cdee7cdd25da2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_030_solid_030.stl`|176884|`b9d87196070c50baa50cead598545b214763c43d854a1db532286593171571da`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_031_solid_031.stl`|72884|`2d750dab7a2ca34ec6e09324c2533b6d43802907f1ca137cff380a6b34b00ace`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_032_solid_032.stl`|77284|`d4778d33de70e62e68d878d770be99b6195e41f5793533bbab6e0ee3dbcfca7e`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_033_solid_033.stl`|126884|`c413ebc7bb5d5b6fdf9095b233bf480534d91a05f5e67d14dcde0ca71b906c1d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_034_solid_034.stl`|66484|`b1058e0f065e78f7121dc59f5b3c9ec4830cf1f86d14869d6ec90cf2d0988c52`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_035_solid_035.stl`|98684|`1ce0d15f35dc71c49bddbe42b5857f166a9b2941a203ecee34e64efe8e8ab115`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_036_solid_036.stl`|141584|`6fb49c64c3941d623dae290fc31e51e19890d7428fbf43351260e6f092690fa4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_037_solid_037.stl`|120884|`74b9c1f84a125e7c18b73a5e9942bf30008d37eac08fdbba901488806450b4f1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_038_solid_038.stl`|176884|`42232f5e8a6eb65254c1b74ab96cc80488474867c4c905bb5b0efad48a8e306a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_039_solid_039.stl`|126884|`fbfb92108a24b9ec18ed1b8d8b15ff15fb350080a10c9f52d5f4d65b0a1c63ab`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_040_solid_040.stl`|66484|`47e71dc23d9538fdffebdeae0a1ad1469cf25e6f657e0f8988b3a3f5e9b1b44b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_041_solid_041.stl`|98684|`ab522cfecdd052c5d85d83a89d6cae7ae6d79913b784f94f80b7f9731739b186`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_042_solid_042.stl`|141584|`73d073c3c6903926dcb2cf1d227e52a0b7f0c547bc6ac978a7cee2c045f324c9`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_043_solid_043.stl`|120884|`4aba4cb69173573ae6a3301f9f6d6763870e61fad64e23b6c171dd1726663153`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_044_solid_044.stl`|176884|`c789e30c241bfa24c026cebd12bce078f3d0966e5ba782d260b3ea478af38aef`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_045_solid_045.stl`|77284|`5e442ba85dc5d1c15b344ef63689091208f8b7ba3f190f1dd8e0dacac8cd1572`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_046_solid_046.stl`|37484|`dd341d276c85a5ab00751a069ef33c5e72ac19974eb348431767f1dd87b5c470`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_047_solid_047.stl`|38634|`1e453a937e45172566d22138fe85cdb8bdb9bc9549e7052e52e3f1cfcf432467`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_048_solid_048.stl`|126884|`5e37e69671423171cb7fb03a6766f404f9189ba52d8f3ebbcc503aaba51bb514`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_049_solid_049.stl`|66484|`8b0f0db3773e0da4f445da6d50710815d70952dfb55d51928111311747f556aa`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_050_solid_050.stl`|98684|`26fb45030c4101bcc2fceb09643f8a2fe4e7f000987a61da8b9fcf78d1a0aba1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_051_solid_051.stl`|141584|`8547bf2afe065c6c517786245ccbfbbf521bd388bb084faa49bb83565731fd52`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_052_solid_052.stl`|120884|`35b6d2bd1d4b22c4ec1fe5e022193d5fcdc9615d63eaf3f9e478020ca2bb0dce`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_053_solid_053.stl`|176884|`7cb2fddd1a887627a39352f708cad62a0d8e5c0ae47657db7cd8d15a589f6f1d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_054_solid_054.stl`|72884|`fdf87b3f053ef8014cbfe1d21cf09cda835ee49a5c573ef432a56343e49b5445`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_055_solid_055.stl`|77284|`70daf25a7eab987d5fe4c46dd3860dd47163317512061374b0d174d15af75326`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_056_solid_056.stl`|126884|`4c8eaf760f53a951a20a5537d46a393061df11d147a66fd8f3ea8cc495879f9f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_057_solid_057.stl`|66484|`1c1e5a3d3a59d2d0462d253ff97446343553e44fd77a7ffd3cf5c1c0438c4bc1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_058_solid_058.stl`|98684|`be50f19f45df79b7e4fed917aa3b159ddcfb0367c4a9cbcd25cbf0bca15be6f8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_059_solid_059.stl`|141584|`d179182ee079b1deab43b6f36aaa8543930f3dae119ae3c0e875a8d832d4b10a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_060_solid_060.stl`|120884|`9f84628b9669611c038bece36ea73d8cade9450100a5ca35fa9426fb92d69d51`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_061_solid_061.stl`|176884|`a20b7d70d48ce640c80e5544a89d610dad126ded6ffffb0dd7630b59cf89c9d4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_062_solid_062.stl`|126884|`e557851d5842ebde1d4f35916a0b9a8ea15fe57d1ae0a2006ab6c85ed4bfaae0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_063_solid_063.stl`|66484|`2e1966f50312ed27e193501531e47d82256510879cdd43c7f8fd7a6521e0dca3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_064_solid_064.stl`|98684|`5c88a593f22de54559b40dfb0387911f40c1195afdf0d68f1fdc22b44b283005`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_065_solid_065.stl`|141584|`8402005f32d86b6c044ab4f46f4a92c01d17bca2ca99306780856ad6ce7026e6`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_066_solid_066.stl`|120884|`41d9b414cf819996a61788c068a79e329e3e1ae5b5bf449d10e954efb156981f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_067_solid_067.stl`|176884|`6f0e540100d0d89b8ddf7557b516ffe4aa3f77f6c97fe0efd6c81b0bd8de6e90`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_068_solid_068.stl`|77284|`11da2f349f055fa17c222c7dbf986e9bfa87c9336df5606620cbb82d708d5c4a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_069_solid_069.stl`|37484|`f010f898b58c5efbba4bc9e47917e87d08a5ed3e2adb0e3a4651cac25dd6d63d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_070_solid_070.stl`|38634|`5046b99f042c2ba0b34cde89601be1dc50da2ab3d574fa2db9b6b499985ba333`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_071_solid_071.stl`|126884|`b861bd860c49d097fab781ea9bfda6a5fb03570b7016c2c1c7f6bfdfdc78dfcd`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_072_solid_072.stl`|66484|`5c56057553bffd300c0209684e72e09d939f975bf275e93d293a1528d8fd3305`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_073_solid_073.stl`|98684|`d451e02114eb9aac613db4a0805ce59e38eedcec1977db38bd817d8dd1b40fc2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_074_solid_074.stl`|141584|`1f14a2a8dfc6ed8d61bf0d6353c88004ff185f52fbbe7d37741b368850e93ec1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_075_solid_075.stl`|120884|`fa457f094dd7ac9fe479589715772b2f48658f61ad1c822c5203a1ef328ba7f1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_076_solid_076.stl`|176884|`bb10e515b4f4c7a4178570bda4a8833cb721b0bb9718a80b1d65aaef0b912721`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_077_solid_077.stl`|72884|`f0eb0a48f8cf1f4000700a59189b66cce4c86a7b92e9fcdfd9808f3c620c24ae`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_078_solid_078.stl`|77284|`3c98ac2c77b3cd1da7569e4433c799c959f1991ad2b679c55df5190139e98284`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_079_solid_079.stl`|126884|`16287910012e71c1666f7fe25031cd36f673d9402e09af47e2f690e45422d96d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_080_solid_080.stl`|66484|`d417b1fe151ea0f869bf37dcea3fcd5b9ba0724962b2c5737772434bcbff3cc2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_081_solid_081.stl`|98684|`788a6d6fd58bcab2ba779691ad5eefb2e22dd0bc36075f788d9a2490e38f9c77`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_082_solid_082.stl`|141584|`a063d135b9a70fee2fab4a0c20a1182665f194e5abd186d45dfea8718c573861`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_083_solid_083.stl`|120884|`289ae918a69d107d8559e481856e9c93ad68a7027c7d3a16730dc52989cefb61`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_084_solid_084.stl`|176884|`8722ea721227665921857c4dde2ba95a366c2ffc87133e5a2afe8f2adbb8ac23`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_085_solid_085.stl`|126884|`7245d2c4e2ba5543fa8c9b6aed05c617104923b8aad39e0b92b22987590a5b1a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_086_solid_086.stl`|66484|`21d9492818bf7dec7db373c8795106aa8b8d40dc5dd310d278adc4b8be2d8ae9`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_087_solid_087.stl`|98684|`1af0cdc6a1825d7a66022daff2c768185d538241854df0c8137be81ce3322086`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_088_solid_088.stl`|141584|`13475d9b53edddf8350f03b32dbb60b6239e6281c84a300569ab720ae738d652`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_089_solid_089.stl`|120884|`9134deca6d37781ce1f52c42de14d371251957dc781879a39e88262d9826976a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_090_solid_090.stl`|176884|`5215ad956ce41d07acbc5691dfdc085e9417a1fa94a0b53ccd92786a2fb8cd29`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_091_solid_091.stl`|77284|`73874f0e25e874da0abadc0dd5aee7f01997afcecf43fba6cd15812fe54bdef0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_092_solid_092.stl`|37484|`59acd46d543156b856669fcd9e82066ad78e7cc1bb6f74f7bdb5e95bd62b36cd`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_093_solid_093.stl`|38634|`ab1a51aaf381e91dbc21809a020216b30dcac4fc023bed52c5b14f051c738b97`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/urdf/generated_robot.urdf`|50586|`5bf1ba77366f9cf9296680eac40e49d161d5bdce4363cdca545672a58a8e37d7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/__init__.py`|21|`57bd2ad61971d773b0b8bca5218f862d7ea63a7a24eafc2584959f70db800338`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/__init__.py`|53|`15ac838bbfecd49c54e48f7a24382c0d0382d286dd341a04b5afd468c9c6784b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/__init__.py`|471|`ff4a9ef2ba58f632d54efc56d467c4b074bfef1e395f7bf3e401c34548385533`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/__init__.py`|1|`01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/rsl_rl_ppo_cfg.py`|358|`92aff17f02cadf6710bed0bb488c4b3ff75c0cb9029c7e1c27a20503bd0d909c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/csdog_v2_env_cfg.py`|4983|`5353680f87ee3c2eef49f207d58995f2e3e2832fe1c0998479e1bc805f2eb710`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/__init__.py`|416|`94664e4ae8e65793a067e8bd0936e91d2bd2cd8e0dc08f7ce6c378611023d432`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/__init__.py`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/rsl_rl_ppo_cfg.py`|961|`85a246014f0e2763bdc8090b874afd519e24824252f8ae27535ccc4976041bd7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/custom_rewards.py`|683|`2705610c68e3f9d7ab6125059bd5a8608f8a7b10134a800e1f33349abae3633f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env.py`|15556|`16e22b5b63fb8551b35e775607aa9868b7ae99b2dd475279b3efd120ebe5d691`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env_cfg.py`|7809|`b10879991c4c4d7318c79e20b49321c454329527736844e521e3aa245fc3ee07`|本地同路径不存在；保留远端历史|
|`tests/test_urdf_audit.py`|2118|`d1f1ffe4d4fb1cedb97de2ac57d390382e98872edf10c4e85ded846b3f5bea7c`|本地同路径不存在；保留远端历史|

### csdog-v2-teleop-v0.1.0-assets

提交 `36dc1e429ed84e9e7ba44cc7600b940a26978142`；归档 SHA256 `6c862cdfc5fef91bf2a792137a6749097bbfb04bc886a77a756414b634ee7ead`。

已读取 1 个文件，展开逻辑字节 12580464。

|远端路径|字节|SHA256|本地对应/结论|
|---|---:|---|---|
|`csdog-v2-teleop-v0.1.0-complete.tar.gz`|12580464|`162e292cd99fd9cf803d2ad5325eeca517db3bc0b09ed425cb40600ecbc1c6a7`|历史完整包；见下方包内核验|

历史包 `csdog-v2-teleop-v0.1.0-complete.tar.gz` 内含 260 个普通文件，逻辑字节 30159538。

|包内文件|字节|SHA256|当前资源对应核验|
|---|---:|---|---|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_PHASE_GAIT_PROGRESS_2026-10-29.md`|6330|`f98299c5173f1aa51e2d9c5545ec5ec6d4689f666184401e3d77ae1c4d183f75`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_TURN_STYLE_PROGRESS_2026-10-29.md`|3278|`c8483e52605c8a2d545efd7648d0052b84e73bbaf5e05956b922889c900c829e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_V0_1_RELEASE_REPORT.md`|7550|`24d4df12386edab0e0e122e0f453fe8c48a1d58865e99acd28c551aa81db6929`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_QWEASD_TELEOP.md`|3093|`552d4b52d621fce33259e56885f82dde75d2c7f427024ca411716670bbd28fec`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/MODEL_TO_URDF_AND_LOCOMOTION.md`|11736|`5b28059a20f8e7f295a0ce884e8d2734b8cbb12524b0a37b5bd0de7d4950f6af`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/LINUX_FIRST_RUN.md`|2988|`fa8ea8aee3a9abfe842e46eaa8e3d49cdd0874296fc2817980c365405a8dd481`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_OPERATOR_RUNBOOK.md`|1916|`023709886da536749ecec4d29399f93b5f2f65ed2ee121833427c69119964999`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_AUDIT_AND_TRAINING_PLAN.md`|9414|`5e94a79f526fcdaaf0eee2f6c763a6e90230961c53bc5390f32a16453686a0a7`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/MODEL_VALIDATION.md`|1722|`2170270d8bb6de7c061dbb2c57e83b4145573d31eeb9d0c42d643bb97f7b970f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/docs/CSDOG_V2_PROGRESS_2026-10-29.md`|1409|`0ac9aa17abf9e03279104283e36d39b45024617d511b557c072c04983cf22a81`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/exported/policies/policy.onnx`|454543|`84f777c2dd485099a6b96cc0b4bb4fe1c4a66124345d83d32602990925f68773`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt`|2722815|`283c0ed7ca6500ea0e8f01edc16512b27381ff556790e95900f623584dfa29f7`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/policies/v1/model_final.pt|
|`csdog-v2-teleop-v0.1.0/logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt.metadata.json`|501|`bc34ff208f827f594e071750ab33b1e244526f3b003e5f453d0b7283e2432c59`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/HANDOFF.md`|9997|`b75e525eaf9438670bef0e6aed2d1e571b39bad85a6ea7da8ddcd6b0fa87b0b9`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/assets/local_mu3x59rz_5j49gz_urdf_stl.zip`|2909905|`98f7742e33f6f9e5b4f88adefda0fcaf82827f3afdca129d4afc59639ec22c55`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/assets/Stackforce-simready-generated_robot-isaac-lab.zip`|10326712|`cab2e4728ad6f595dbc26ea4c3669bf9606033f793384cb0b60a7154cd145c0f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/PARAMETERS.md`|8857|`d7f78b118936eb51f7ff08b3422a0e97cbcbd9fa27cf417eee8a9366628898d7`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/CURRENT.md`|7890|`d35aec660f1be101ba5113caaa6298bcc3e20897cb1de794b2db421448fa225d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/tests/test_urdf_audit.py`|2295|`e7b9a8a6b27783160c3a09ba1dc9872f586c537f01cfc8222bddcd7b1c2b8477`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/config/csdog_v2_urdf_expectations.json`|1098|`1d7cfb54e9b8038929b965d63235261c415292021943254af67a5804443672dd`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/config/releases/csdog_v2_teleop_v0.1.0.json`|1429|`48416c44185bb0f362f23d70d1dab591e01d4e3fa34f31532ec799c686170895`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/config/experiments/csdog_v2_abc.json`|2251|`17baee3c60ff3018956c60331dcbab40f59bf71a2ac2133542af67c68fc6a55f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/config/csdog_v2_hardware_profile.json`|3188|`29a1e265ba8f81eb5a8f7bf738703e54b0d08c4e09da85bb40a098d02b505cba`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/README.md`|2764|`817c4229150b4a88b2df113da7989b97bb88c13c1d7a17238a916c18f1342a16`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/evaluate_fixed_commands.py`|5435|`8cf8258588867535ed33bc76f79e3800d98c8746d79d0be2f0b6919f8ae9b3e6`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/zero_agent.py`|1538|`c705dbef43ee67c62d1c36ced634dca67b58466b5d57c7061f275b3555978796`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/random_agent.py`|1151|`07bc418e53decf0e92b649b05e14cab48bbca6f2647e3d60be36362dfa34b0e3`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/diagnose_zero_pose.py`|11167|`d11e1ebeb68c284e2b330c1afcb247a834c7e7221502123b5fcd8b9d7d4035bb`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/diagnose_joint_directions.py`|7424|`a3cf64ba39a52da5ad6b2cc8ca852d27eb33dc4e06ad1461f79aed4b4d46828a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/rsl_rl/cli_args.py`|1963|`fc1077b0cfe7c51fd8ee2ab240320116147286c1f6f4207899f09bfff713d295`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/rsl_rl/play.py`|44575|`527a3898b9a07665315220297368c7b20d4c7c356b44485495eb30948647e654`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/rsl_rl/train.py`|23601|`e146922b82007d70727c2cbeac1a90305b616c1b4476b6196b72bfc307e1d836`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/search_csdog_v2_standing_pose.py`|6829|`3a076a8c866f2aa577ed7bc5cae7d26f0c616d6d20161fe0e628d8188e0fc4c5`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/prepare_csdog_v2_sim_urdf.py`|7310|`7493cab53c882e5d1580b90f5916226b061f931f573138899ee8f734b84a0139`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/play_csdog_qweasd.sh`|1122|`2f08fd01a5a4a6782ad932b21ad239baf392171773b8c13f98a3bef56ae0369b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/migrate_csdog_v2_phase_checkpoint.py`|2791|`72f30491e8bb41149d421092cb0718e0f2f06aa31498d548653a74191708ad89`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/audit_urdf.py`|20064|`0f98f2e8a587c6fa46d3c06acfeb1cbd34029b6b9fdeceb817719fd81e03db3c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/list_envs.py`|1060|`95ea3948e736dc821f93024eb2a6a7db66011b689d1eb8a3326469ef813fed0d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/scripts/run_csdog_v2_gates.py`|5625|`2ca6347d83c64ada1986a11c6145d346fbdb83b79384a4ea12976e02491cc319`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/forward_030.json`|14579|`5a9b682c1c6b224d66bd691dd74d1a871e4f4e529795a09e7812e98e0085a235`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/lateral_030.json`|13138|`500dd59c6108d821f12fae9d0eed148967bca775cbd3e825bb54a5a7a6dcc4f0`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/forward_015.json`|14520|`9a03d5ed509639aa4ffca4e49c0c65944b8d75ddc2a79daf55c9292adc9da1b9`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/lateral_015.json`|12767|`1568a92f465d3efeff278033c12cd376a40c0cb6404fdb9e93c5dffc2369de74`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/yaw_030.json`|20333|`6134949d003b8c8b508331a865e2d197c150cf8f77c0dcc75bdd28e352f4cb66`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_matrix/stand.json`|14100|`f65b68888ee63e165b02358a570ca4d8ae4ac7f7bb1844938e1edb188076641c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_xyz_yaw_right_030.json`|25012|`a9402d969ada783e22e2cb8fb2e12463cf249e461a199d25ad1647e463ac4730`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100_summary.json`|3556|`85ea3464157ed96a7635c536f329564744883f94459705b1571e9c3861c75fed`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/forward_030.json`|13782|`d3c80491fd60f491aa4fb225644a418bacee16bb0baae8b903008cbac60751cc`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/lateral_030.json`|17989|`975ad7a32cd5b97b8e7b85a7e943a9f79b261c8d4195553bc8e1616b4b0a51e7`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/forward_015.json`|14717|`2e907e1cdaa5ed81eb7fb0bcf721dbc6fc9eda09c642be77f256cb58d8afaf9d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/lateral_015.json`|17172|`15d337d0e1f584f4bce4289ba63b1f6984bf19f097d4081cb571d0e8a8f5f4c5`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/yaw_030.json`|14084|`ed0632c38685a43667c76ae42c1b936d9bf80ecfd988e09ed98ecd7d6026fb83`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_matrix/stand.json`|15334|`3e387cb4f3c262e2366e3961fe351d16606e98de33836859f7c020d8bf3a54b8`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_xy_left_030.json`|23231|`c871d7771bc7ee355e5e83c2f64472718567b39c1e63c2d6c184e850d8890989`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_a_backward_030.json`|22628|`7611a9cfb6c84a79649a6acdaf970aae8ed0976cd729a452de9b225f55e4a26b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_xy_right_030.json`|23329|`5b73e6eef950172e57bade5bee5aa5e1b98e1a638b5f7a964402a1053d37fe9e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/locomotion_source_audit.json`|3679|`c313f1d2e44db0cd7d01c0f266f192022ee944c8bab07f446b1988c4f402e516`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_summary.json`|3448|`188454415aad168bcffc420c1e28a4e7b011adc77361fa1953bca35d8624519b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_joint_directions_010.json`|19962|`6c98e3faf22c98b260d298adae175dbeb1b117a67e095a6d37387f04e9be9dc2`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_static_audit.json`|18857|`3ef21e17f79b43a01fdc03a617386584f7ef1180c67549b54956c34c260e8434`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_gate_pipeline.json`|1256|`1ee2ebe1b3652c656be754d0c70ade46fd2c648e6611dbda058115a524a44cc5`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_standing_pose_grid.json`|104424|`dda9e2b9b6127deb54872c160a241e41dc237a417811b17d96049a8724d25f71`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_final_command_evaluation.json`|3445|`1246a86ddea76b5f0da38318901ca05a415b2c7a8e5a6f8b703da57ce53159af`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_zero_pose_5s.json`|5148|`8d8e811feca0b9083b7abcc7076b76b9df0e40d3282bb64c7a47df31eec2a038`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50/yaw_plus_030.json`|20306|`06ab589e309f16a46dff0cb7a4161a7a34f47a2957345be11332e8564a0bc378`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50/yaw_minus_030.json`|17316|`3dcd4997703e47dfd3252317b9a512beff7a55e4894dadae4c6071d0f5a5aebc`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/forward_030.json`|43656|`38591477d1e9f03c9e5c563adeb3aea33b152aa7806699b33c82cf862d4665a1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/lateral_030.json`|36857|`0f06ec6e821b5d2774c2ac2dd1a5f5b816e083c6751d792d6f303219643a02ff`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/forward_015.json`|41109|`f691cf34485850ad67498db470206eaade39b147eeed704335ef1eb73e8ccb1f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/lateral_015.json`|39701|`1d26cf32a11d70251713834dc82be3a8600b1c9e9d1663178bc09fb15ecef373`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/yaw_030.json`|45323|`13ebec634f649bd684124f3591c10b8c9edfcf50461094ab180186a21e04f202`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/final_command_metrics/stand.json`|31215|`67f31f296e4a92cdaf2d638e763a9cfd74622a925f38f4247736e2d9513201ae`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_gates.json`|1209|`f8fcefde24f3aa0bc72db5acadb2a441ac6e69682d0111146b6b7cccd4b0f8e2`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_xyz_yaw_left_030.json`|25038|`1c0b248b19202c44886aa87a65715c47b5cf20d19ad6eb07d525392b1b0d02ed`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_style_refine50_summary.json`|3488|`9762066b09f53334e108a0596a78a929722d99e38e9743d6a410077f1a14379d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100_summary.json`|3529|`f8b6c0b01d35258d85a5ee038844d13caf8477f9c734f4d5dd5930ae1752ca84`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_joint_directions_005.json`|19937|`e986d0762302d3b081ed07a78494af29700fc022380906e8d92b62abb6c4181c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/backward_030.json`|12247|`0b984c3ffaf14d9001c4c54f42dfa212030a159091b7f204946a19ec6ebed805`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_minus_030.json`|10564|`d0c295143efadf94f14c01029b79fc378f1588930d324c6b97e6e40f48042a41`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/forward_030.json`|13280|`d887cd6015bc74d3d9478827c84ecac8b27a15212d83a9069341ae6c740d7b4f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_030.json`|13277|`9048d6cb16f5d7ac7bf1f2dc75b535d4c030a8a5af3f47ccfa93f5286c62db21`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/yaw_minus_030.json`|12924|`7bacf53e55b6ea225e0c7b1b4dc561346dac1bd7070bee98e729e463975cd958`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/forward_015.json`|13248|`14e91a10a86d5b96bc3012e8daa0c95e4f2845bae7682c54924f55d3c11e9af4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_015.json`|9943|`d19c8c0c4095109c22bff7d7e4485ccd5eaa9d97fa57c29fcd46146a6572b3fb`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/yaw_030.json`|17016|`9a5f856815b67cee740a5050819fc23b8bd2d1efed38a5287e9760367e3d0b2e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/stand.json`|12111|`fdfa1c80402bbe574dd3ef1ff620639b1ece8be1570f89630b8a88a0551fd868`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_posture_baseline/yaw_plus_030.json`|20400|`b27eeb2f3a807dab2beebdb7320732cdf0189605338d561d1dd144064aecd7da`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/turn_posture_baseline/yaw_minus_030.json`|16327|`e4191950d18d0d6b1d447d47efe35c1e534113f388313ce487f7d9cbd093f94d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_commands/lateral_yaw_020_030.json`|19332|`4d385f5374ef2a77c86b01e121285c157fa6bf094a7efd7fa97e92e6f93b0888`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_commands/forward_040.json`|15020|`0bc77a2e721379de97279b6284c0641a65396b294cd15ff6a4a3c7cc177a8d2c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_commands/forward_yaw_030.json`|17532|`8a08f7f2cf516cc649a06f476552741ec2676e02fa1dc28c8bdc955578e0d7cb`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_commands/forward_lateral_030_020.json`|14828|`24ff2ee998f25308ca15aed4bcd9746fb60161642e7b109f3544a40a771a9258`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_commands/yaw_040.json`|14222|`b1492a3da11668910c393f03640bc411eb09dd24c85746128057080fb234e995`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_pd_stand_30s.json`|5158|`e700dcff148751cdfb00060f2cf312b157f3bc81fbf68881b2cc804936350e6f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/csdog_v2_phase_a_forward_030.json`|24332|`a3c7ab7cf7e03b7758b0b24d879f05460c5a246c501da53eb8a10596790583da`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_reverse/yaw_right_035.json`|17107|`f2e9ff8af4e4177b8cfae8b6965c03666a9196b3056a8daa6af322d057709376`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_reverse/backward_yaw_right_030.json`|20860|`21ff4160c0c0f267dd54bdbfb8d790d4ef58fb4f07b33b27120b4fb42a9e01be`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_reverse/right_022.json`|15422|`aeadd1a8c4608f404c2609fd9f9c224a3249803298cf425d2b1c90dfe50a10bd`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/qweasd_mixed100_reverse/backward_035.json`|17151|`554f500598eef55292d3be678ed6f456236071f80160f742fbd4d537eeba6130`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/backward_030.json`|13637|`6dd4f6283379ab4cf879c2f896912fcbd85cb039844bf98e5e02efeb2937265e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_minus_030.json`|10251|`4b70d960807b3656f65744094c1476279eb21e8f4ccc74407454b0319704647e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/forward_030.json`|13733|`fe0269d781ae28c49a78a251d53b8b7af077ac53d61ab65694e04296475dbff6`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_030.json`|10388|`3fb36786edc4d3128e4fbb223563f6216bc0400637a2ced629e743dcb1b88521`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/yaw_minus_030.json`|13573|`8c6ab3bf13085eae0173ae20b4c3ab2a3f4fa16bfbb36f8522ffe0c0ebeb8e72`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/forward_015.json`|15268|`7df17e7970222bb6fbbdae40cc6b299c991f0863cf7c00c93ead9035a1f6fe2c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_015.json`|11852|`86dd4d8afbc0d64e80454af8a38015ec2e4fae26a6cd05d4113b19e0684f421d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/yaw_030.json`|15552|`32ff75337377749d9b7fd1f8ed40fadfec18ae50042d1cc15a66e1320b991dac`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/stand.json`|13402|`0d9c7cc9dc93a6b3de1ed19f9459fd202ec4bab31ef893430462ae2abb136175`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v12_lateral_metrics.json`|2443|`5601aba822cc45d604c20843333ee25a7f421a1df0bcf3a46181ff687d3767a5`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v13_stand_metrics.json`|2442|`a3b822449a786000719f6f09105bafc9168aad97a66c15ea4eec23bd226b6f7f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v13_forward_metrics.json`|2455|`c78a856b6ecde5dd7c2b60c902201dd5e4d9952d84ec9718d1173a78a614c014`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v12_yaw_metrics.json`|2460|`9f431d35b8c028039032097487163a48140b99e3b2f8a9e008faa365de3c3b6c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v17_lateral_015_metrics.json`|2431|`ace660af817cbc39c4408a0f790b0c2904a978d781ae49cfc56f881a0a0ea628`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v15_lateral_metrics.json`|2440|`59e21721d98dbe046fbe7748c8e873f8abba6ef71a29bb27cd8f0b2f42b5c1d0`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v16_lateral_050_metrics.json`|2458|`22cb75c3b20a8c96e01b5cc94c3a8c228ce28585de1739bb96268f42a336bc5d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v16_lateral_015_metrics.json`|2443|`c28d9ea7d04886235366dd0311fd5befc391bdd8229f4e599add6f058351292c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/nominal_pose_v7_height_threshold_30s.json`|3378|`c635568b265c86ba9be123e238ce656b3d8c20656be68654acd6fbf20572a3d4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v15_forward_metrics.json`|2428|`cefbc079ed5aa591aa1fe115202256e547fb24b1556c5de8143b58ad2230ca73`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v13_lateral_metrics.json`|2457|`0fa3b6d4907b497b625c549166d9245438c6ff9a3744bffebfa5c56a33e0f820`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v12_forward_metrics.json`|2426|`dadcb49b72dbfccbe4653b43c4127e3f37fd1b3edff659daa4f3499374378e63`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v17_lateral_030_metrics.json`|2437|`f3fcb8ae8f7928bb242b16ac9e916d3010c2cc8066a1dba3d2055c0e362f2945`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/single_axis_sampling_smoke.json`|2465|`664817cabe0e5565357d27edf23991fb255ad813f46d8c29e83fa08b22043cd6`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v13_yaw_metrics.json`|2421|`838e18c63f22412890ef51de3f408351fcaa53c36e75fd3ad14eebfb78c5dece`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/fixed_command_sampling_smoke.json`|2351|`cebab844deb13930c58ef330a04d30278d03d3fd75f77e997a64b2e8ce0c910d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/results/2026-09-17/commanded_v15_yaw_metrics.json`|2451|`d43eb5c558ddad95276d9fc774844cdba5218e22bf2b7f5072a56588112c3042`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-09-17_LINUX_BASELINE_AND_PPO_SMOKE.md`|9266|`24378044acf22b48a2ac35d8b093d1ac09e651e68bb7f74682ef2fe5aa7d739f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_GATES.md`|897|`6eda35ed38ccbce0c178782d1a1c6c7e3481a8e1fbbb95cc5900be0cc489a9e9`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_FINAL_COMMAND_EVALUATION.md`|551|`414191a3a81695152a00e1b8e4111eb8ab9dedbfcab9d8ec43028d31c9876c7c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_PHASE_GAIT_COUPLING_FINAL.md`|598|`da53ba3a1171b89ac680f0d73de3647209b6b9c90b5d7dd85b3f8f2b077b65e4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_TURN_STYLE_REFINE50.md`|608|`30a766e1f5d3494d5d0289abee700e8263882e6addfab319325fff1b97caa942`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_STATIC_AUDIT.md`|3343|`9d0b1256592e7693d8222aefceeeda21bd3295a9cba49be34c8335357786b046`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_PHASE_GAIT_OPTIMIZER_REFINE100.md`|573|`363549250af03c480f8b9801202a2d537bca190a425664f65ab1bab762c3921c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/2026-10-29_CSDOG_V2_QWEASD_MIXED100.md`|519|`c5ad731d873c90c11ea674545a672dc225cdb4b9a6a307e80749df348b73b4aa`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/experiments/TEMPLATE.md`|745|`46a984127d093b1aded0e5acd3a1d36134f58aa9f38764dccf4e4b9ebb3034d1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/setup.py`|346|`d2f03b778cfb952a0f5cf7d0455dfa440be1c6de6ac788f85101bce2e3fb3e41`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf`|12505|`20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot.urdf|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot_sim.urdf`|18907|`4806d4e0c2db659a37e9f595d739df60121d2640895f505a0aec4277779566d1`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/robot_sim.urdf|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/README.md`|1693|`676f3b2d0e7926328ba0cdc887d034d29e7771e9f15947a3456281b6d11dd7fb`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/README.md|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_pitch_collision.stl`|190484|`04945bf61bf4f2e49ca242de5069a1fab2bda87e2da1b5704bbd2a04ce100b80`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_pitch_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_roll_collision.stl`|236984|`c3a5d8e7282b55c3d114e46ad34c29f34ff6c4927b009de3dd07ac2ebe27b957`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_roll_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_knee_collision.stl`|53634|`6418e0c18075866d356c1bdc3dcf4f364fedc16caa219e65345382c1e5bacf31`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_knee_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_knee_collision.stl`|53684|`cb0146a5bc3f73180ed02082054dd9fb8cd634c3abd3f38b75aee8090f1a3beb`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_knee_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_knee_collision.stl`|53984|`eda21673b014b7b392d1f1ebbc0aa31dabd3d4a351244a92a135f8aeb46c9dd8`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_knee_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_roll_collision.stl`|236484|`a942c5e921a3b5bbd17f2f53a5fcf439526b8aec6eaed38cc92575b16b904043`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lf_hip_roll_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/base_collision.stl`|1484|`9c93aa72fd27c40d50539c5cbf45d5e0418986f6f0a09481c363969ed5eb6079`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/base_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_pitch_collision.stl`|190784|`6f1fc0b7b00902bdd611ec403f03d5eacfbfe165350470699bf2dbfce7c926c7`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_pitch_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_roll_collision.stl`|236234|`cdd1f1a41f4160d680d91290f3b219ac997ea544758b08d419601daebfb22fa4`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_roll_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_pitch_collision.stl`|197184|`b276f7c04b288794a97f3a78fb1acc404a9e0123cd90002424cdf36bb1710666`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rf_hip_pitch_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_roll_collision.stl`|237534|`b5ac7b6b6beb836cf1d5d18e3f8ec08ae87133cb0bc0d875757a02a35f53e04f`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_rr_hip_roll_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_knee_collision.stl`|53734|`7fa626081e4394d74cc615afe4c0e51323013875c607dc57e2a38c4be6df6c23`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_knee_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_pitch_collision.stl`|190634|`cba39b20e1a2e078ea98122d99c3fb5a86dd87ee0b2b8d2cbce268208dfca5d8`|dogfight_rl/assets/csdog_12dof/peer_teleop_v1/model/meshes/link_lr_hip_pitch_collision.stl|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/urdf/generated_robot.urdf`|50586|`5bf1ba77366f9cf9296680eac40e49d161d5bdce4363cdca545672a58a8e37d7`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_002_solid_002.stl`|126884|`2c445d59cfac5f7111b9a957defc062475bb852926f9cb2e97306567e8191c2a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_047_solid_047.stl`|38634|`1e453a937e45172566d22138fe85cdb8bdb9bc9549e7052e52e3f1cfcf432467`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_011_solid_011.stl`|66484|`3d73932d4dc326339212b2890743178138ad484866dabcec2eb0467576f86d71`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_017_solid_017.stl`|66484|`7c628885c1506dfe10fc2ce1582ccb88bcd6e8abf1c47fcddd595b35c2b8d14b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_063_solid_063.stl`|66484|`2e1966f50312ed27e193501531e47d82256510879cdd43c7f8fd7a6521e0dca3`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_076_solid_076.stl`|176884|`bb10e515b4f4c7a4178570bda4a8833cb721b0bb9718a80b1d65aaef0b912721`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_087_solid_087.stl`|98684|`1af0cdc6a1825d7a66022daff2c768185d538241854df0c8137be81ce3322086`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_071_solid_071.stl`|126884|`b861bd860c49d097fab781ea9bfda6a5fb03570b7016c2c1c7f6bfdfdc78dfcd`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_030_solid_030.stl`|176884|`b9d87196070c50baa50cead598545b214763c43d854a1db532286593171571da`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_048_solid_048.stl`|126884|`5e37e69671423171cb7fb03a6766f404f9189ba52d8f3ebbcc503aaba51bb514`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_006_solid_006.stl`|120884|`f1f52fe62f3fce7dfddfcd86c8d5c6663876724e08b54310b59450df2b9c289c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_031_solid_031.stl`|72884|`2d750dab7a2ca34ec6e09324c2533b6d43802907f1ca137cff380a6b34b00ace`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_033_solid_033.stl`|126884|`c413ebc7bb5d5b6fdf9095b233bf480534d91a05f5e67d14dcde0ca71b906c1d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_015_solid_015.stl`|176884|`873859bb083adbcdfc2ce8a7b94b717b80e4452915b2db1b9debd385c3f04e31`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_014_solid_014.stl`|120884|`33d189a0cf4221156d0154aa83f44feb0cef0b040f48ca141807762bfa0b3c5b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_072_solid_072.stl`|66484|`5c56057553bffd300c0209684e72e09d939f975bf275e93d293a1528d8fd3305`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_067_solid_067.stl`|176884|`6f0e540100d0d89b8ddf7557b516ffe4aa3f77f6c97fe0efd6c81b0bd8de6e90`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_059_solid_059.stl`|141584|`d179182ee079b1deab43b6f36aaa8543930f3dae119ae3c0e875a8d832d4b10a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_005_solid_005.stl`|141584|`e20a936288a8b82cb547e156528aee6438e04b9b2636c376eb9c55fa1f4f088c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_020_solid_020.stl`|120884|`743f03a8174edbc80df5a32f813b4382f2595399b8b31655919041605b00a49c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_088_solid_088.stl`|141584|`13475d9b53edddf8350f03b32dbb60b6239e6281c84a300569ab720ae738d652`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_062_solid_062.stl`|126884|`e557851d5842ebde1d4f35916a0b9a8ea15fe57d1ae0a2006ab6c85ed4bfaae0`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_019_solid_019.stl`|141584|`27186e0f5a15af39960bf37541c7a872426d97d3bb576463896569b6be9d23fa`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_068_solid_068.stl`|77284|`11da2f349f055fa17c222c7dbf986e9bfa87c9336df5606620cbb82d708d5c4a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_093_solid_093.stl`|38634|`ab1a51aaf381e91dbc21809a020216b30dcac4fc023bed52c5b14f051c738b97`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_036_solid_036.stl`|141584|`6fb49c64c3941d623dae290fc31e51e19890d7428fbf43351260e6f092690fa4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_077_solid_077.stl`|72884|`f0eb0a48f8cf1f4000700a59189b66cce4c86a7b92e9fcdfd9808f3c620c24ae`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_023_solid_023.stl`|37484|`a9edb11eb95be7980c7b26a931ff1d375e3d99937cfe74b3818f104499522b84`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_009_solid_009.stl`|77284|`347edd8316b1adc47af7c288c499a88b0054d65915e206629968ea03fc51f692`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_012_solid_012.stl`|98684|`13bc7fd77d70bb8b0a262ea6d9f3bdf9720b7aebd69d1b8008dc34563157f914`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_073_solid_073.stl`|98684|`d451e02114eb9aac613db4a0805ce59e38eedcec1977db38bd817d8dd1b40fc2`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_039_solid_039.stl`|126884|`fbfb92108a24b9ec18ed1b8d8b15ff15fb350080a10c9f52d5f4d65b0a1c63ab`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_025_solid_025.stl`|126884|`8c9723c897e082195575dd7dc320e0043f7ca862aef4fc178c492a2baf62db12`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_013_solid_013.stl`|141584|`2c2aad90c398267fbca00e62a062090e109a9465708ccf56b3aaf60cf0fd9f3d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_064_solid_064.stl`|98684|`5c88a593f22de54559b40dfb0387911f40c1195afdf0d68f1fdc22b44b283005`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_003_solid_003.stl`|66484|`78bc62e747c3974dbef1b1fda1f13b7ccbf6ba82aed3196c05e9074252018a4c`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_090_solid_090.stl`|176884|`5215ad956ce41d07acbc5691dfdc085e9417a1fa94a0b53ccd92786a2fb8cd29`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_034_solid_034.stl`|66484|`b1058e0f065e78f7121dc59f5b3c9ec4830cf1f86d14869d6ec90cf2d0988c52`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_075_solid_075.stl`|120884|`fa457f094dd7ac9fe479589715772b2f48658f61ad1c822c5203a1ef328ba7f1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_083_solid_083.stl`|120884|`289ae918a69d107d8559e481856e9c93ad68a7027c7d3a16730dc52989cefb61`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_035_solid_035.stl`|98684|`1ce0d15f35dc71c49bddbe42b5857f166a9b2941a203ecee34e64efe8e8ab115`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_037_solid_037.stl`|120884|`74b9c1f84a125e7c18b73a5e9942bf30008d37eac08fdbba901488806450b4f1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_038_solid_038.stl`|176884|`42232f5e8a6eb65254c1b74ab96cc80488474867c4c905bb5b0efad48a8e306a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_086_solid_086.stl`|66484|`21d9492818bf7dec7db373c8795106aa8b8d40dc5dd310d278adc4b8be2d8ae9`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_045_solid_045.stl`|77284|`5e442ba85dc5d1c15b344ef63689091208f8b7ba3f190f1dd8e0dacac8cd1572`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_092_solid_092.stl`|37484|`59acd46d543156b856669fcd9e82066ad78e7cc1bb6f74f7bdb5e95bd62b36cd`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_050_solid_050.stl`|98684|`26fb45030c4101bcc2fceb09643f8a2fe4e7f000987a61da8b9fcf78d1a0aba1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_022_solid_022.stl`|77284|`a10ba0ab5c7be42de19eba6fda2b5f018d74bce282d709e770f67e6d66ddfd01`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_018_solid_018.stl`|98684|`8824cee99aee4a9ad024fa02c03c2d7bc3645d990724fa4b266322add8ec0260`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_082_solid_082.stl`|141584|`a063d135b9a70fee2fab4a0c20a1182665f194e5abd186d45dfea8718c573861`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_079_solid_079.stl`|126884|`16287910012e71c1666f7fe25031cd36f673d9402e09af47e2f690e45422d96d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_057_solid_057.stl`|66484|`1c1e5a3d3a59d2d0462d253ff97446343553e44fd77a7ffd3cf5c1c0438c4bc1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_028_solid_028.stl`|141584|`c20e75dfedd29c1d0320668ca3c1745b075f22dfa892628c4fb8b90327933be3`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_040_solid_040.stl`|66484|`47e71dc23d9538fdffebdeae0a1ad1469cf25e6f657e0f8988b3a3f5e9b1b44b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_010_solid_010.stl`|126884|`168efbb968eb7ffafe268b9427fd781788f42fbc90973edc928b182067d63a04`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_084_solid_084.stl`|176884|`8722ea721227665921857c4dde2ba95a366c2ffc87133e5a2afe8f2adbb8ac23`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_021_solid_021.stl`|176884|`e9b62328aff0e3188790ddb0f181bd9b02bd099f38bbb55c4347c6a2178acf03`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_080_solid_080.stl`|66484|`d417b1fe151ea0f869bf37dcea3fcd5b9ba0724962b2c5737772434bcbff3cc2`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_085_solid_085.stl`|126884|`7245d2c4e2ba5543fa8c9b6aed05c617104923b8aad39e0b92b22987590a5b1a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_069_solid_069.stl`|37484|`f010f898b58c5efbba4bc9e47917e87d08a5ed3e2adb0e3a4651cac25dd6d63d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_029_solid_029.stl`|120884|`fb89b0cac2af9041f374b03ca7343bd3f6a985f5362cb22dc14cdee7cdd25da2`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_052_solid_052.stl`|120884|`35b6d2bd1d4b22c4ec1fe5e022193d5fcdc9615d63eaf3f9e478020ca2bb0dce`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_046_solid_046.stl`|37484|`dd341d276c85a5ab00751a069ef33c5e72ac19974eb348431767f1dd87b5c470`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_016_solid_016.stl`|126884|`05953591f889e896603aa31db25ddbe2190d04d8965b62fc8403d6dafa10a1a1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_042_solid_042.stl`|141584|`73d073c3c6903926dcb2cf1d227e52a0b7f0c547bc6ac978a7cee2c045f324c9`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_001_solid_001.stl`|173484|`972596c70fed3f0bad4593e12cfac299f4255aa89200c7acdc8ae5059d47f970`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_049_solid_049.stl`|66484|`8b0f0db3773e0da4f445da6d50710815d70952dfb55d51928111311747f556aa`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_008_solid_008.stl`|72884|`5302f9e4f909ec345a36983f2fd39542753911aab5786815c5bf189502e73fc3`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_089_solid_089.stl`|120884|`9134deca6d37781ce1f52c42de14d371251957dc781879a39e88262d9826976a`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_032_solid_032.stl`|77284|`d4778d33de70e62e68d878d770be99b6195e41f5793533bbab6e0ee3dbcfca7e`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_054_solid_054.stl`|72884|`fdf87b3f053ef8014cbfe1d21cf09cda835ee49a5c573ef432a56343e49b5445`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_070_solid_070.stl`|38634|`5046b99f042c2ba0b34cde89601be1dc50da2ab3d574fa2db9b6b499985ba333`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_074_solid_074.stl`|141584|`1f14a2a8dfc6ed8d61bf0d6353c88004ff185f52fbbe7d37741b368850e93ec1`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_058_solid_058.stl`|98684|`be50f19f45df79b7e4fed917aa3b159ddcfb0367c4a9cbcd25cbf0bca15be6f8`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_027_solid_027.stl`|98684|`0105d70295ac72e01fc45778ca1710447e01542091e00dac8586ad1316806cd4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_081_solid_081.stl`|98684|`788a6d6fd58bcab2ba779691ad5eefb2e22dd0bc36075f788d9a2490e38f9c77`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_007_solid_007.stl`|176884|`7d80a7e0a017094178875a5661ddaa5d88eb4466e4afdd1fb61238f8b01c8b50`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_053_solid_053.stl`|176884|`7cb2fddd1a887627a39352f708cad62a0d8e5c0ae47657db7cd8d15a589f6f1d`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_061_solid_061.stl`|176884|`a20b7d70d48ce640c80e5544a89d610dad126ded6ffffb0dd7630b59cf89c9d4`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_091_solid_091.stl`|77284|`73874f0e25e874da0abadc0dd5aee7f01997afcecf43fba6cd15812fe54bdef0`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_026_solid_026.stl`|66484|`b02362cda21cd214dc60061a1d95c0ff0d37bd51fbb03d3e462883284af1ca34`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_004_solid_004.stl`|98684|`34b090a0aa237ef30c3e50cd646cd3a6f2864574af7ab3ed14badf798507d1a3`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_066_solid_066.stl`|120884|`41d9b414cf819996a61788c068a79e329e3e1ae5b5bf449d10e954efb156981f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_078_solid_078.stl`|77284|`3c98ac2c77b3cd1da7569e4433c799c959f1991ad2b679c55df5190139e98284`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_043_solid_043.stl`|120884|`4aba4cb69173573ae6a3301f9f6d6763870e61fad64e23b6c171dd1726663153`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_060_solid_060.stl`|120884|`9f84628b9669611c038bece36ea73d8cade9450100a5ca35fa9426fb92d69d51`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_044_solid_044.stl`|176884|`c789e30c241bfa24c026cebd12bce078f3d0966e5ba782d260b3ea478af38aef`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_041_solid_041.stl`|98684|`ab522cfecdd052c5d85d83a89d6cae7ae6d79913b784f94f80b7f9731739b186`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_065_solid_065.stl`|141584|`8402005f32d86b6c044ab4f46f4a92c01d17bca2ca99306780856ad6ce7026e6`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_055_solid_055.stl`|77284|`70daf25a7eab987d5fe4c46dd3860dd47163317512061374b0d174d15af75326`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_051_solid_051.stl`|141584|`8547bf2afe065c6c517786245ccbfbbf521bd388bb084faa49bb83565731fd52`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_056_solid_056.stl`|126884|`4c8eaf760f53a951a20a5537d46a393061df11d147a66fd8f3ea8cc495879f9f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_024_solid_024.stl`|38634|`8e56cb5ddf6a76d70e698e3f2ee619e4266574bb352cc086f2fc924692fce790`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/__init__.py`|21|`57bd2ad61971d773b0b8bca5218f862d7ea63a7a24eafc2584959f70db800338`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/__init__.py`|53|`15ac838bbfecd49c54e48f7a24382c0d0382d286dd341a04b5afd468c9c6784b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/__init__.py`|2139|`49abe91d89a5decafd04f20913f306c36eae02463e2061e4f7bc2a9321bf5e95`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/csdog_v2_env_cfg.py`|12740|`6338cf876fdbf6720ea5795c75ad36f55f7f1bb1c10899181dfbd04978864190`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/__init__.py`|1|`01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/rsl_rl_ppo_cfg.py`|1245|`f0c7744fd0232704dc51252ccd53631a6d12cd4b2419b8f988bb894f759bc267`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/__init__.py`|416|`94664e4ae8e65793a067e8bd0936e91d2bd2cd8e0dc08f7ce6c378611023d432`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env.py`|26787|`7161ef90c29b691c8c14bd478b1b84f4e9144997b3aa8c0eceafff53b23529f8`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env_cfg.py`|8425|`7177d57853ca88135e6f13159f6b5b25d00283ebed55b870ced3697066a426ef`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/custom_rewards.py`|683|`2705610c68e3f9d7ab6125059bd5a8608f8a7b10134a800e1f33349abae3633f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/__init__.py`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/rsl_rl_ppo_cfg.py`|961|`85a246014f0e2763bdc8090b874afd519e24824252f8ae27535ccc4976041bd7`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/__init__.py`|20|`5084f413dea9293a22c593b440cc08e44adf9817d015fee77fb8cb0bb5a129f0`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/source/stackforce_simready_generated_robot_lab/pyproject.toml`|94|`7f4d920bc75d4e2c9f5e73f3215b4a4bcc3f52f4f641de3a2a28d8b6b3d03b9f`|不属于当前17项导入源文件的同字节资源/其他历史代码|
|`csdog-v2-teleop-v0.1.0/.gitignore`|509|`e1e04fc428d89037939f5466956c793f688ec0d6b6ee36500363cb2278a4e603`|不属于当前17项导入源文件的同字节资源/其他历史代码|

### codex/csdog-v2-locomotion

提交 `2acb747c13ec0cd4f4390977ea14f4721d64056f`；归档 SHA256 `edaec6f8bf9b2f37e5e02e594a3b569b19a990984cc646826b9ad5a5b69fe73c`。

已读取 257 个文件，展开逻辑字节 26981679。

|远端路径|字节|SHA256|本地对应/结论|
|---|---:|---|---|
|`.gitignore`|509|`e1e04fc428d89037939f5466956c793f688ec0d6b6ee36500363cb2278a4e603`|同路径不同，禁止覆盖远端|
|`CURRENT.md`|7890|`d35aec660f1be101ba5113caaa6298bcc3e20897cb1de794b2db421448fa225d`|本地同路径不存在；保留远端历史|
|`HANDOFF.md`|9997|`b75e525eaf9438670bef0e6aed2d1e571b39bad85a6ea7da8ddcd6b0fa87b0b9`|本地同路径不存在；保留远端历史|
|`PARAMETERS.md`|8857|`d7f78b118936eb51f7ff08b3422a0e97cbcbd9fa27cf417eee8a9366628898d7`|本地同路径不存在；保留远端历史|
|`README.md`|2764|`817c4229150b4a88b2df113da7989b97bb88c13c1d7a17238a916c18f1342a16`|同路径不同，禁止覆盖远端|
|`assets/Stackforce-simready-generated_robot-isaac-lab.zip`|10326712|`cab2e4728ad6f595dbc26ea4c3669bf9606033f793384cb0b60a7154cd145c0f`|本地同路径不存在；保留远端历史|
|`assets/local_mu3x59rz_5j49gz_urdf_stl.zip`|2909905|`98f7742e33f6f9e5b4f88adefda0fcaf82827f3afdca129d4afc59639ec22c55`|本地同路径不存在；保留远端历史|
|`config/csdog_v2_hardware_profile.json`|3188|`29a1e265ba8f81eb5a8f7bf738703e54b0d08c4e09da85bb40a098d02b505cba`|本地同路径不存在；保留远端历史|
|`config/csdog_v2_urdf_expectations.json`|1098|`1d7cfb54e9b8038929b965d63235261c415292021943254af67a5804443672dd`|本地同路径不存在；保留远端历史|
|`config/experiments/csdog_v2_abc.json`|2251|`17baee3c60ff3018956c60331dcbab40f59bf71a2ac2133542af67c68fc6a55f`|本地同路径不存在；保留远端历史|
|`config/releases/csdog_v2_teleop_v0.1.0.json`|1429|`48416c44185bb0f362f23d70d1dab591e01d4e3fa34f31532ec799c686170895`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_AUDIT_AND_TRAINING_PLAN.md`|9414|`5e94a79f526fcdaaf0eee2f6c763a6e90230961c53bc5390f32a16453686a0a7`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_OPERATOR_RUNBOOK.md`|1916|`023709886da536749ecec4d29399f93b5f2f65ed2ee121833427c69119964999`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_PHASE_GAIT_PROGRESS_2026-10-29.md`|6330|`f98299c5173f1aa51e2d9c5545ec5ec6d4689f666184401e3d77ae1c4d183f75`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_PROGRESS_2026-10-29.md`|1409|`0ac9aa17abf9e03279104283e36d39b45024617d511b557c072c04983cf22a81`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_QWEASD_TELEOP.md`|3093|`552d4b52d621fce33259e56885f82dde75d2c7f427024ca411716670bbd28fec`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_TURN_STYLE_PROGRESS_2026-10-29.md`|3278|`c8483e52605c8a2d545efd7648d0052b84e73bbaf5e05956b922889c900c829e`|本地同路径不存在；保留远端历史|
|`docs/CSDOG_V2_V0_1_RELEASE_REPORT.md`|7550|`24d4df12386edab0e0e122e0f453fe8c48a1d58865e99acd28c551aa81db6929`|本地同路径不存在；保留远端历史|
|`docs/LINUX_FIRST_RUN.md`|2988|`fa8ea8aee3a9abfe842e46eaa8e3d49cdd0874296fc2817980c365405a8dd481`|本地同路径不存在；保留远端历史|
|`docs/MODEL_TO_URDF_AND_LOCOMOTION.md`|11736|`5b28059a20f8e7f295a0ce884e8d2734b8cbb12524b0a37b5bd0de7d4950f6af`|本地同路径不存在；保留远端历史|
|`docs/MODEL_VALIDATION.md`|1722|`2170270d8bb6de7c061dbb2c57e83b4145573d31eeb9d0c42d643bb97f7b970f`|本地同路径不存在；保留远端历史|
|`experiments/2026-09-17_LINUX_BASELINE_AND_PPO_SMOKE.md`|9266|`24378044acf22b48a2ac35d8b093d1ac09e651e68bb7f74682ef2fe5aa7d739f`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_FINAL_COMMAND_EVALUATION.md`|551|`414191a3a81695152a00e1b8e4111eb8ab9dedbfcab9d8ec43028d31c9876c7c`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_GATES.md`|897|`6eda35ed38ccbce0c178782d1a1c6c7e3481a8e1fbbb95cc5900be0cc489a9e9`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_PHASE_GAIT_COUPLING_FINAL.md`|598|`da53ba3a1171b89ac680f0d73de3647209b6b9c90b5d7dd85b3f8f2b077b65e4`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_PHASE_GAIT_OPTIMIZER_REFINE100.md`|573|`363549250af03c480f8b9801202a2d537bca190a425664f65ab1bab762c3921c`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_QWEASD_MIXED100.md`|519|`c5ad731d873c90c11ea674545a672dc225cdb4b9a6a307e80749df348b73b4aa`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_STATIC_AUDIT.md`|3343|`9d0b1256592e7693d8222aefceeeda21bd3295a9cba49be34c8335357786b046`|本地同路径不存在；保留远端历史|
|`experiments/2026-10-29_CSDOG_V2_TURN_STYLE_REFINE50.md`|608|`30a766e1f5d3494d5d0289abee700e8263882e6addfab319325fff1b97caa942`|本地同路径不存在；保留远端历史|
|`experiments/TEMPLATE.md`|745|`46a984127d093b1aded0e5acd3a1d36134f58aa9f38764dccf4e4b9ebb3034d1`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_forward_metrics.json`|2426|`dadcb49b72dbfccbe4653b43c4127e3f37fd1b3edff659daa4f3499374378e63`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_lateral_metrics.json`|2443|`5601aba822cc45d604c20843333ee25a7f421a1df0bcf3a46181ff687d3767a5`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v12_yaw_metrics.json`|2460|`9f431d35b8c028039032097487163a48140b99e3b2f8a9e008faa365de3c3b6c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_forward_metrics.json`|2455|`c78a856b6ecde5dd7c2b60c902201dd5e4d9952d84ec9718d1173a78a614c014`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_lateral_metrics.json`|2457|`0fa3b6d4907b497b625c549166d9245438c6ff9a3744bffebfa5c56a33e0f820`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_stand_metrics.json`|2442|`a3b822449a786000719f6f09105bafc9168aad97a66c15ea4eec23bd226b6f7f`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v13_yaw_metrics.json`|2421|`838e18c63f22412890ef51de3f408351fcaa53c36e75fd3ad14eebfb78c5dece`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_forward_metrics.json`|2428|`cefbc079ed5aa591aa1fe115202256e547fb24b1556c5de8143b58ad2230ca73`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_lateral_metrics.json`|2440|`59e21721d98dbe046fbe7748c8e873f8abba6ef71a29bb27cd8f0b2f42b5c1d0`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v15_yaw_metrics.json`|2451|`d43eb5c558ddad95276d9fc774844cdba5218e22bf2b7f5072a56588112c3042`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v16_lateral_015_metrics.json`|2443|`c28d9ea7d04886235366dd0311fd5befc391bdd8229f4e599add6f058351292c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v16_lateral_050_metrics.json`|2458|`22cb75c3b20a8c96e01b5cc94c3a8c228ce28585de1739bb96268f42a336bc5d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v17_lateral_015_metrics.json`|2431|`ace660af817cbc39c4408a0f790b0c2904a978d781ae49cfc56f881a0a0ea628`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/commanded_v17_lateral_030_metrics.json`|2437|`f3fcb8ae8f7928bb242b16ac9e916d3010c2cc8066a1dba3d2055c0e362f2945`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/fixed_command_sampling_smoke.json`|2351|`cebab844deb13930c58ef330a04d30278d03d3fd75f77e997a64b2e8ce0c910d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/nominal_pose_v7_height_threshold_30s.json`|3378|`c635568b265c86ba9be123e238ce656b3d8c20656be68654acd6fbf20572a3d4`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-09-17/single_axis_sampling_smoke.json`|2465|`664817cabe0e5565357d27edf23991fb255ad813f46d8c29e83fa08b22043cd6`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_final_command_evaluation.json`|3445|`1246a86ddea76b5f0da38318901ca05a415b2c7a8e5a6f8b703da57ce53159af`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_gate_pipeline.json`|1256|`1ee2ebe1b3652c656be754d0c70ade46fd2c648e6611dbda058115a524a44cc5`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_gates.json`|1209|`f8fcefde24f3aa0bc72db5acadb2a441ac6e69682d0111146b6b7cccd4b0f8e2`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_joint_directions_005.json`|19937|`e986d0762302d3b081ed07a78494af29700fc022380906e8d92b62abb6c4181c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_joint_directions_010.json`|19962|`6c98e3faf22c98b260d298adae175dbeb1b117a67e095a6d37387f04e9be9dc2`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_pd_stand_30s.json`|5158|`e700dcff148751cdfb00060f2cf312b157f3bc81fbf68881b2cc804936350e6f`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_a_backward_030.json`|22628|`7611a9cfb6c84a79649a6acdaf970aae8ed0976cd729a452de9b225f55e4a26b`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_a_forward_030.json`|24332|`a3c7ab7cf7e03b7758b0b24d879f05460c5a246c501da53eb8a10596790583da`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_xy_left_030.json`|23231|`c871d7771bc7ee355e5e83c2f64472718567b39c1e63c2d6c184e850d8890989`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_xy_right_030.json`|23329|`5b73e6eef950172e57bade5bee5aa5e1b98e1a638b5f7a964402a1053d37fe9e`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_xyz_yaw_left_030.json`|25038|`1c0b248b19202c44886aa87a65715c47b5cf20d19ad6eb07d525392b1b0d02ed`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_phase_xyz_yaw_right_030.json`|25012|`a9402d969ada783e22e2cb8fb2e12463cf249e461a199d25ad1647e463ac4730`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_standing_pose_grid.json`|104424|`dda9e2b9b6127deb54872c160a241e41dc237a417811b17d96049a8724d25f71`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_static_audit.json`|18857|`3ef21e17f79b43a01fdc03a617386584f7ef1180c67549b54956c34c260e8434`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/csdog_v2_zero_pose_5s.json`|5148|`8d8e811feca0b9083b7abcc7076b76b9df0e40d3282bb64c7a47df31eec2a038`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/forward_015.json`|41109|`f691cf34485850ad67498db470206eaade39b147eeed704335ef1eb73e8ccb1f`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/forward_030.json`|43656|`38591477d1e9f03c9e5c563adeb3aea33b152aa7806699b33c82cf862d4665a1`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/lateral_015.json`|39701|`1d26cf32a11d70251713834dc82be3a8600b1c9e9d1663178bc09fb15ecef373`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/lateral_030.json`|36857|`0f06ec6e821b5d2774c2ac2dd1a5f5b816e083c6751d792d6f303219643a02ff`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/stand.json`|31215|`67f31f296e4a92cdaf2d638e763a9cfd74622a925f38f4247736e2d9513201ae`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/final_command_metrics/yaw_030.json`|45323|`13ebec634f649bd684124f3591c10b8c9edfcf50461094ab180186a21e04f202`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/locomotion_source_audit.json`|3679|`c313f1d2e44db0cd7d01c0f266f192022ee944c8bab07f446b1988c4f402e516`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_commands/forward_040.json`|15020|`0bc77a2e721379de97279b6284c0641a65396b294cd15ff6a4a3c7cc177a8d2c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_commands/forward_lateral_030_020.json`|14828|`24ff2ee998f25308ca15aed4bcd9746fb60161642e7b109f3544a40a771a9258`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_commands/forward_yaw_030.json`|17532|`8a08f7f2cf516cc649a06f476552741ec2676e02fa1dc28c8bdc955578e0d7cb`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_commands/lateral_yaw_020_030.json`|19332|`4d385f5374ef2a77c86b01e121285c157fa6bf094a7efd7fa97e92e6f93b0888`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_commands/yaw_040.json`|14222|`b1492a3da11668910c393f03640bc411eb09dd24c85746128057080fb234e995`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/forward_015.json`|14717|`2e907e1cdaa5ed81eb7fb0bcf721dbc6fc9eda09c642be77f256cb58d8afaf9d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/forward_030.json`|13782|`d3c80491fd60f491aa4fb225644a418bacee16bb0baae8b903008cbac60751cc`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/lateral_015.json`|17172|`15d337d0e1f584f4bce4289ba63b1f6984bf19f097d4081cb571d0e8a8f5f4c5`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/lateral_030.json`|17989|`975ad7a32cd5b97b8e7b85a7e943a9f79b261c8d4195553bc8e1616b4b0a51e7`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/stand.json`|15334|`3e387cb4f3c262e2366e3961fe351d16606e98de33836859f7c020d8bf3a54b8`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_matrix/yaw_030.json`|14084|`ed0632c38685a43667c76ae42c1b936d9bf80ecfd988e09ed98ecd7d6026fb83`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_reverse/backward_035.json`|17151|`554f500598eef55292d3be678ed6f456236071f80160f742fbd4d537eeba6130`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_reverse/backward_yaw_right_030.json`|20860|`21ff4160c0c0f267dd54bdbfb8d790d4ef58fb4f07b33b27120b4fb42a9e01be`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_reverse/right_022.json`|15422|`aeadd1a8c4608f404c2609fd9f9c224a3249803298cf425d2b1c90dfe50a10bd`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_reverse/yaw_right_035.json`|17107|`f2e9ff8af4e4177b8cfae8b6965c03666a9196b3056a8daa6af322d057709376`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/qweasd_mixed100_summary.json`|3448|`188454415aad168bcffc420c1e28a4e7b011adc77361fa1953bca35d8624519b`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/backward_030.json`|12247|`0b984c3ffaf14d9001c4c54f42dfa212030a159091b7f204946a19ec6ebed805`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/forward_015.json`|13248|`14e91a10a86d5b96bc3012e8daa0c95e4f2845bae7682c54924f55d3c11e9af4`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/forward_030.json`|13280|`d887cd6015bc74d3d9478827c84ecac8b27a15212d83a9069341ae6c740d7b4f`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_015.json`|9943|`d19c8c0c4095109c22bff7d7e4485ccd5eaa9d97fa57c29fcd46146a6572b3fb`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_030.json`|13277|`9048d6cb16f5d7ac7bf1f2dc75b535d4c030a8a5af3f47ccfa93f5286c62db21`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/lateral_minus_030.json`|10564|`d0c295143efadf94f14c01029b79fc378f1588930d324c6b97e6e40f48042a41`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/stand.json`|12111|`fdfa1c80402bbe574dd3ef1ff620639b1ece8be1570f89630b8a88a0551fd868`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/yaw_030.json`|17016|`9a5f856815b67cee740a5050819fc23b8bd2d1efed38a5287e9760367e3d0b2e`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100/yaw_minus_030.json`|12924|`7bacf53e55b6ea225e0c7b1b4dc561346dac1bd7070bee98e729e463975cd958`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_optimizer_refine100_summary.json`|3556|`85ea3464157ed96a7635c536f329564744883f94459705b1571e9c3861c75fed`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/backward_030.json`|13637|`6dd4f6283379ab4cf879c2f896912fcbd85cb039844bf98e5e02efeb2937265e`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/forward_015.json`|15268|`7df17e7970222bb6fbbdae40cc6b299c991f0863cf7c00c93ead9035a1f6fe2c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/forward_030.json`|13733|`fe0269d781ae28c49a78a251d53b8b7af077ac53d61ab65694e04296475dbff6`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_015.json`|11852|`86dd4d8afbc0d64e80454af8a38015ec2e4fae26a6cd05d4113b19e0684f421d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_030.json`|10388|`3fb36786edc4d3128e4fbb223563f6216bc0400637a2ced629e743dcb1b88521`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/lateral_minus_030.json`|10251|`4b70d960807b3656f65744094c1476279eb21e8f4ccc74407454b0319704647e`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/stand.json`|13402|`0d9c7cc9dc93a6b3de1ed19f9459fd202ec4bab31ef893430462ae2abb136175`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/yaw_030.json`|15552|`32ff75337377749d9b7fd1f8ed40fadfec18ae50042d1cc15a66e1320b991dac`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100/yaw_minus_030.json`|13573|`8c6ab3bf13085eae0173ae20b4c3ab2a3f4fa16bfbb36f8522ffe0c0ebeb8e72`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/symmetric_phase_xyz_coupling100_summary.json`|3529|`f8b6c0b01d35258d85a5ee038844d13caf8477f9c734f4d5dd5930ae1752ca84`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_posture_baseline/yaw_minus_030.json`|16327|`e4191950d18d0d6b1d447d47efe35c1e534113f388313ce487f7d9cbd093f94d`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_posture_baseline/yaw_plus_030.json`|20400|`b27eeb2f3a807dab2beebdb7320732cdf0189605338d561d1dd144064aecd7da`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50/yaw_minus_030.json`|17316|`3dcd4997703e47dfd3252317b9a512beff7a55e4894dadae4c6071d0f5a5aebc`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50/yaw_plus_030.json`|20306|`06ab589e309f16a46dff0cb7a4161a7a34f47a2957345be11332e8564a0bc378`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/forward_015.json`|14520|`9a03d5ed509639aa4ffca4e49c0c65944b8d75ddc2a79daf55c9292adc9da1b9`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/forward_030.json`|14579|`5a9b682c1c6b224d66bd691dd74d1a871e4f4e529795a09e7812e98e0085a235`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/lateral_015.json`|12767|`1568a92f465d3efeff278033c12cd376a40c0cb6404fdb9e93c5dffc2369de74`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/lateral_030.json`|13138|`500dd59c6108d821f12fae9d0eed148967bca775cbd3e825bb54a5a7a6dcc4f0`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/stand.json`|14100|`f65b68888ee63e165b02358a570ca4d8ae4ac7f7bb1844938e1edb188076641c`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_matrix/yaw_030.json`|20333|`6134949d003b8c8b508331a865e2d197c150cf8f77c0dcc75bdd28e352f4cb66`|本地同路径不存在；保留远端历史|
|`experiments/results/2026-10-29/turn_style_refine50_summary.json`|3488|`9762066b09f53334e108a0596a78a929722d99e38e9743d6a410077f1a14379d`|本地同路径不存在；保留远端历史|
|`scripts/audit_urdf.py`|20064|`0f98f2e8a587c6fa46d3c06acfeb1cbd34029b6b9fdeceb817719fd81e03db3c`|本地同路径不存在；保留远端历史|
|`scripts/diagnose_joint_directions.py`|7424|`a3cf64ba39a52da5ad6b2cc8ca852d27eb33dc4e06ad1461f79aed4b4d46828a`|本地同路径不存在；保留远端历史|
|`scripts/diagnose_zero_pose.py`|11167|`d11e1ebeb68c284e2b330c1afcb247a834c7e7221502123b5fcd8b9d7d4035bb`|本地同路径不存在；保留远端历史|
|`scripts/evaluate_fixed_commands.py`|5435|`8cf8258588867535ed33bc76f79e3800d98c8746d79d0be2f0b6919f8ae9b3e6`|本地同路径不存在；保留远端历史|
|`scripts/list_envs.py`|1060|`95ea3948e736dc821f93024eb2a6a7db66011b689d1eb8a3326469ef813fed0d`|本地同路径不存在；保留远端历史|
|`scripts/migrate_csdog_v2_phase_checkpoint.py`|2791|`72f30491e8bb41149d421092cb0718e0f2f06aa31498d548653a74191708ad89`|本地同路径不存在；保留远端历史|
|`scripts/play_csdog_qweasd.sh`|1122|`2f08fd01a5a4a6782ad932b21ad239baf392171773b8c13f98a3bef56ae0369b`|本地同路径不存在；保留远端历史|
|`scripts/prepare_csdog_v2_sim_urdf.py`|7310|`7493cab53c882e5d1580b90f5916226b061f931f573138899ee8f734b84a0139`|本地同路径不存在；保留远端历史|
|`scripts/random_agent.py`|1151|`07bc418e53decf0e92b649b05e14cab48bbca6f2647e3d60be36362dfa34b0e3`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/cli_args.py`|1963|`fc1077b0cfe7c51fd8ee2ab240320116147286c1f6f4207899f09bfff713d295`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/play.py`|44575|`527a3898b9a07665315220297368c7b20d4c7c356b44485495eb30948647e654`|本地同路径不存在；保留远端历史|
|`scripts/rsl_rl/train.py`|23601|`e146922b82007d70727c2cbeac1a90305b616c1b4476b6196b72bfc307e1d836`|本地同路径不存在；保留远端历史|
|`scripts/run_csdog_v2_gates.py`|5625|`2ca6347d83c64ada1986a11c6145d346fbdb83b79384a4ea12976e02491cc319`|本地同路径不存在；保留远端历史|
|`scripts/search_csdog_v2_standing_pose.py`|6829|`3a076a8c866f2aa577ed7bc5cae7d26f0c616d6d20161fe0e628d8188e0fc4c5`|本地同路径不存在；保留远端历史|
|`scripts/zero_agent.py`|1538|`c705dbef43ee67c62d1c36ced634dca67b58466b5d57c7061f275b3555978796`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/pyproject.toml`|94|`7f4d920bc75d4e2c9f5e73f3215b4a4bcc3f52f4f641de3a2a28d8b6b3d03b9f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/setup.py`|346|`d2f03b778cfb952a0f5cf7d0455dfa440be1c6de6ac788f85101bce2e3fb3e41`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/__init__.py`|20|`5084f413dea9293a22c593b440cc08e44adf9817d015fee77fb8cb0bb5a129f0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/README.md`|1693|`676f3b2d0e7926328ba0cdc887d034d29e7771e9f15947a3456281b6d11dd7fb`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/base_collision.stl`|1484|`9c93aa72fd27c40d50539c5cbf45d5e0418986f6f0a09481c363969ed5eb6079`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_pitch_collision.stl`|190484|`04945bf61bf4f2e49ca242de5069a1fab2bda87e2da1b5704bbd2a04ce100b80`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_hip_roll_collision.stl`|236484|`a942c5e921a3b5bbd17f2f53a5fcf439526b8aec6eaed38cc92575b16b904043`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lf_knee_collision.stl`|53684|`cb0146a5bc3f73180ed02082054dd9fb8cd634c3abd3f38b75aee8090f1a3beb`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_pitch_collision.stl`|190634|`cba39b20e1a2e078ea98122d99c3fb5a86dd87ee0b2b8d2cbce268208dfca5d8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_hip_roll_collision.stl`|236984|`c3a5d8e7282b55c3d114e46ad34c29f34ff6c4927b009de3dd07ac2ebe27b957`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_lr_knee_collision.stl`|53734|`7fa626081e4394d74cc615afe4c0e51323013875c607dc57e2a38c4be6df6c23`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_pitch_collision.stl`|197184|`b276f7c04b288794a97f3a78fb1acc404a9e0123cd90002424cdf36bb1710666`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_hip_roll_collision.stl`|236234|`cdd1f1a41f4160d680d91290f3b219ac997ea544758b08d419601daebfb22fa4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rf_knee_collision.stl`|53634|`6418e0c18075866d356c1bdc3dcf4f364fedc16caa219e65345382c1e5bacf31`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_pitch_collision.stl`|190784|`6f1fc0b7b00902bdd611ec403f03d5eacfbfe165350470699bf2dbfce7c926c7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_hip_roll_collision.stl`|237534|`b5ac7b6b6beb836cf1d5d18e3f8ec08ae87133cb0bc0d875757a02a35f53e04f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/meshes/link_rr_knee_collision.stl`|53984|`eda21673b014b7b392d1f1ebbc0aa31dabd3d4a351244a92a135f8aeb46c9dd8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot.urdf`|12505|`20034d94c7c45094480ac8ec56c461b3deeaa7a210d9abd8c789d346ce8e362d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/csdog_v2/robot_sim.urdf`|18907|`4806d4e0c2db659a37e9f595d739df60121d2640895f505a0aec4277779566d1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_001_solid_001.stl`|173484|`972596c70fed3f0bad4593e12cfac299f4255aa89200c7acdc8ae5059d47f970`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_002_solid_002.stl`|126884|`2c445d59cfac5f7111b9a957defc062475bb852926f9cb2e97306567e8191c2a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_003_solid_003.stl`|66484|`78bc62e747c3974dbef1b1fda1f13b7ccbf6ba82aed3196c05e9074252018a4c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_004_solid_004.stl`|98684|`34b090a0aa237ef30c3e50cd646cd3a6f2864574af7ab3ed14badf798507d1a3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_005_solid_005.stl`|141584|`e20a936288a8b82cb547e156528aee6438e04b9b2636c376eb9c55fa1f4f088c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_006_solid_006.stl`|120884|`f1f52fe62f3fce7dfddfcd86c8d5c6663876724e08b54310b59450df2b9c289c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_007_solid_007.stl`|176884|`7d80a7e0a017094178875a5661ddaa5d88eb4466e4afdd1fb61238f8b01c8b50`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_008_solid_008.stl`|72884|`5302f9e4f909ec345a36983f2fd39542753911aab5786815c5bf189502e73fc3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_009_solid_009.stl`|77284|`347edd8316b1adc47af7c288c499a88b0054d65915e206629968ea03fc51f692`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_010_solid_010.stl`|126884|`168efbb968eb7ffafe268b9427fd781788f42fbc90973edc928b182067d63a04`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_011_solid_011.stl`|66484|`3d73932d4dc326339212b2890743178138ad484866dabcec2eb0467576f86d71`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_012_solid_012.stl`|98684|`13bc7fd77d70bb8b0a262ea6d9f3bdf9720b7aebd69d1b8008dc34563157f914`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_013_solid_013.stl`|141584|`2c2aad90c398267fbca00e62a062090e109a9465708ccf56b3aaf60cf0fd9f3d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_014_solid_014.stl`|120884|`33d189a0cf4221156d0154aa83f44feb0cef0b040f48ca141807762bfa0b3c5b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_015_solid_015.stl`|176884|`873859bb083adbcdfc2ce8a7b94b717b80e4452915b2db1b9debd385c3f04e31`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_016_solid_016.stl`|126884|`05953591f889e896603aa31db25ddbe2190d04d8965b62fc8403d6dafa10a1a1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_017_solid_017.stl`|66484|`7c628885c1506dfe10fc2ce1582ccb88bcd6e8abf1c47fcddd595b35c2b8d14b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_018_solid_018.stl`|98684|`8824cee99aee4a9ad024fa02c03c2d7bc3645d990724fa4b266322add8ec0260`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_019_solid_019.stl`|141584|`27186e0f5a15af39960bf37541c7a872426d97d3bb576463896569b6be9d23fa`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_020_solid_020.stl`|120884|`743f03a8174edbc80df5a32f813b4382f2595399b8b31655919041605b00a49c`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_021_solid_021.stl`|176884|`e9b62328aff0e3188790ddb0f181bd9b02bd099f38bbb55c4347c6a2178acf03`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_022_solid_022.stl`|77284|`a10ba0ab5c7be42de19eba6fda2b5f018d74bce282d709e770f67e6d66ddfd01`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_023_solid_023.stl`|37484|`a9edb11eb95be7980c7b26a931ff1d375e3d99937cfe74b3818f104499522b84`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_024_solid_024.stl`|38634|`8e56cb5ddf6a76d70e698e3f2ee619e4266574bb352cc086f2fc924692fce790`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_025_solid_025.stl`|126884|`8c9723c897e082195575dd7dc320e0043f7ca862aef4fc178c492a2baf62db12`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_026_solid_026.stl`|66484|`b02362cda21cd214dc60061a1d95c0ff0d37bd51fbb03d3e462883284af1ca34`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_027_solid_027.stl`|98684|`0105d70295ac72e01fc45778ca1710447e01542091e00dac8586ad1316806cd4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_028_solid_028.stl`|141584|`c20e75dfedd29c1d0320668ca3c1745b075f22dfa892628c4fb8b90327933be3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_029_solid_029.stl`|120884|`fb89b0cac2af9041f374b03ca7343bd3f6a985f5362cb22dc14cdee7cdd25da2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_030_solid_030.stl`|176884|`b9d87196070c50baa50cead598545b214763c43d854a1db532286593171571da`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_031_solid_031.stl`|72884|`2d750dab7a2ca34ec6e09324c2533b6d43802907f1ca137cff380a6b34b00ace`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_032_solid_032.stl`|77284|`d4778d33de70e62e68d878d770be99b6195e41f5793533bbab6e0ee3dbcfca7e`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_033_solid_033.stl`|126884|`c413ebc7bb5d5b6fdf9095b233bf480534d91a05f5e67d14dcde0ca71b906c1d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_034_solid_034.stl`|66484|`b1058e0f065e78f7121dc59f5b3c9ec4830cf1f86d14869d6ec90cf2d0988c52`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_035_solid_035.stl`|98684|`1ce0d15f35dc71c49bddbe42b5857f166a9b2941a203ecee34e64efe8e8ab115`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_036_solid_036.stl`|141584|`6fb49c64c3941d623dae290fc31e51e19890d7428fbf43351260e6f092690fa4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_037_solid_037.stl`|120884|`74b9c1f84a125e7c18b73a5e9942bf30008d37eac08fdbba901488806450b4f1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_038_solid_038.stl`|176884|`42232f5e8a6eb65254c1b74ab96cc80488474867c4c905bb5b0efad48a8e306a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_039_solid_039.stl`|126884|`fbfb92108a24b9ec18ed1b8d8b15ff15fb350080a10c9f52d5f4d65b0a1c63ab`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_040_solid_040.stl`|66484|`47e71dc23d9538fdffebdeae0a1ad1469cf25e6f657e0f8988b3a3f5e9b1b44b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_041_solid_041.stl`|98684|`ab522cfecdd052c5d85d83a89d6cae7ae6d79913b784f94f80b7f9731739b186`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_042_solid_042.stl`|141584|`73d073c3c6903926dcb2cf1d227e52a0b7f0c547bc6ac978a7cee2c045f324c9`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_043_solid_043.stl`|120884|`4aba4cb69173573ae6a3301f9f6d6763870e61fad64e23b6c171dd1726663153`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_044_solid_044.stl`|176884|`c789e30c241bfa24c026cebd12bce078f3d0966e5ba782d260b3ea478af38aef`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_045_solid_045.stl`|77284|`5e442ba85dc5d1c15b344ef63689091208f8b7ba3f190f1dd8e0dacac8cd1572`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_046_solid_046.stl`|37484|`dd341d276c85a5ab00751a069ef33c5e72ac19974eb348431767f1dd87b5c470`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_047_solid_047.stl`|38634|`1e453a937e45172566d22138fe85cdb8bdb9bc9549e7052e52e3f1cfcf432467`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_048_solid_048.stl`|126884|`5e37e69671423171cb7fb03a6766f404f9189ba52d8f3ebbcc503aaba51bb514`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_049_solid_049.stl`|66484|`8b0f0db3773e0da4f445da6d50710815d70952dfb55d51928111311747f556aa`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_050_solid_050.stl`|98684|`26fb45030c4101bcc2fceb09643f8a2fe4e7f000987a61da8b9fcf78d1a0aba1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_051_solid_051.stl`|141584|`8547bf2afe065c6c517786245ccbfbbf521bd388bb084faa49bb83565731fd52`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_052_solid_052.stl`|120884|`35b6d2bd1d4b22c4ec1fe5e022193d5fcdc9615d63eaf3f9e478020ca2bb0dce`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_053_solid_053.stl`|176884|`7cb2fddd1a887627a39352f708cad62a0d8e5c0ae47657db7cd8d15a589f6f1d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_054_solid_054.stl`|72884|`fdf87b3f053ef8014cbfe1d21cf09cda835ee49a5c573ef432a56343e49b5445`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_055_solid_055.stl`|77284|`70daf25a7eab987d5fe4c46dd3860dd47163317512061374b0d174d15af75326`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_056_solid_056.stl`|126884|`4c8eaf760f53a951a20a5537d46a393061df11d147a66fd8f3ea8cc495879f9f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_057_solid_057.stl`|66484|`1c1e5a3d3a59d2d0462d253ff97446343553e44fd77a7ffd3cf5c1c0438c4bc1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_058_solid_058.stl`|98684|`be50f19f45df79b7e4fed917aa3b159ddcfb0367c4a9cbcd25cbf0bca15be6f8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_059_solid_059.stl`|141584|`d179182ee079b1deab43b6f36aaa8543930f3dae119ae3c0e875a8d832d4b10a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_060_solid_060.stl`|120884|`9f84628b9669611c038bece36ea73d8cade9450100a5ca35fa9426fb92d69d51`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_061_solid_061.stl`|176884|`a20b7d70d48ce640c80e5544a89d610dad126ded6ffffb0dd7630b59cf89c9d4`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_062_solid_062.stl`|126884|`e557851d5842ebde1d4f35916a0b9a8ea15fe57d1ae0a2006ab6c85ed4bfaae0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_063_solid_063.stl`|66484|`2e1966f50312ed27e193501531e47d82256510879cdd43c7f8fd7a6521e0dca3`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_064_solid_064.stl`|98684|`5c88a593f22de54559b40dfb0387911f40c1195afdf0d68f1fdc22b44b283005`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_065_solid_065.stl`|141584|`8402005f32d86b6c044ab4f46f4a92c01d17bca2ca99306780856ad6ce7026e6`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_066_solid_066.stl`|120884|`41d9b414cf819996a61788c068a79e329e3e1ae5b5bf449d10e954efb156981f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_067_solid_067.stl`|176884|`6f0e540100d0d89b8ddf7557b516ffe4aa3f77f6c97fe0efd6c81b0bd8de6e90`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_068_solid_068.stl`|77284|`11da2f349f055fa17c222c7dbf986e9bfa87c9336df5606620cbb82d708d5c4a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_069_solid_069.stl`|37484|`f010f898b58c5efbba4bc9e47917e87d08a5ed3e2adb0e3a4651cac25dd6d63d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_070_solid_070.stl`|38634|`5046b99f042c2ba0b34cde89601be1dc50da2ab3d574fa2db9b6b499985ba333`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_071_solid_071.stl`|126884|`b861bd860c49d097fab781ea9bfda6a5fb03570b7016c2c1c7f6bfdfdc78dfcd`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_072_solid_072.stl`|66484|`5c56057553bffd300c0209684e72e09d939f975bf275e93d293a1528d8fd3305`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_073_solid_073.stl`|98684|`d451e02114eb9aac613db4a0805ce59e38eedcec1977db38bd817d8dd1b40fc2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_074_solid_074.stl`|141584|`1f14a2a8dfc6ed8d61bf0d6353c88004ff185f52fbbe7d37741b368850e93ec1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_075_solid_075.stl`|120884|`fa457f094dd7ac9fe479589715772b2f48658f61ad1c822c5203a1ef328ba7f1`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_076_solid_076.stl`|176884|`bb10e515b4f4c7a4178570bda4a8833cb721b0bb9718a80b1d65aaef0b912721`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_077_solid_077.stl`|72884|`f0eb0a48f8cf1f4000700a59189b66cce4c86a7b92e9fcdfd9808f3c620c24ae`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_078_solid_078.stl`|77284|`3c98ac2c77b3cd1da7569e4433c799c959f1991ad2b679c55df5190139e98284`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_079_solid_079.stl`|126884|`16287910012e71c1666f7fe25031cd36f673d9402e09af47e2f690e45422d96d`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_080_solid_080.stl`|66484|`d417b1fe151ea0f869bf37dcea3fcd5b9ba0724962b2c5737772434bcbff3cc2`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_081_solid_081.stl`|98684|`788a6d6fd58bcab2ba779691ad5eefb2e22dd0bc36075f788d9a2490e38f9c77`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_082_solid_082.stl`|141584|`a063d135b9a70fee2fab4a0c20a1182665f194e5abd186d45dfea8718c573861`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_083_solid_083.stl`|120884|`289ae918a69d107d8559e481856e9c93ad68a7027c7d3a16730dc52989cefb61`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_084_solid_084.stl`|176884|`8722ea721227665921857c4dde2ba95a366c2ffc87133e5a2afe8f2adbb8ac23`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_085_solid_085.stl`|126884|`7245d2c4e2ba5543fa8c9b6aed05c617104923b8aad39e0b92b22987590a5b1a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_086_solid_086.stl`|66484|`21d9492818bf7dec7db373c8795106aa8b8d40dc5dd310d278adc4b8be2d8ae9`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_087_solid_087.stl`|98684|`1af0cdc6a1825d7a66022daff2c768185d538241854df0c8137be81ce3322086`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_088_solid_088.stl`|141584|`13475d9b53edddf8350f03b32dbb60b6239e6281c84a300569ab720ae738d652`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_089_solid_089.stl`|120884|`9134deca6d37781ce1f52c42de14d371251957dc781879a39e88262d9826976a`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_090_solid_090.stl`|176884|`5215ad956ce41d07acbc5691dfdc085e9417a1fa94a0b53ccd92786a2fb8cd29`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_091_solid_091.stl`|77284|`73874f0e25e874da0abadc0dd5aee7f01997afcecf43fba6cd15812fe54bdef0`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_092_solid_092.stl`|37484|`59acd46d543156b856669fcd9e82066ad78e7cc1bb6f74f7bdb5e95bd62b36cd`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/meshes/part_093_solid_093.stl`|38634|`ab1a51aaf381e91dbc21809a020216b30dcac4fc023bed52c5b14f051c738b97`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/assets/robots/generated_robot/urdf/generated_robot.urdf`|50586|`5bf1ba77366f9cf9296680eac40e49d161d5bdce4363cdca545672a58a8e37d7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/__init__.py`|21|`57bd2ad61971d773b0b8bca5218f862d7ea63a7a24eafc2584959f70db800338`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/__init__.py`|53|`15ac838bbfecd49c54e48f7a24382c0d0382d286dd341a04b5afd468c9c6784b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/__init__.py`|2139|`49abe91d89a5decafd04f20913f306c36eae02463e2061e4f7bc2a9321bf5e95`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/__init__.py`|1|`01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/agents/rsl_rl_ppo_cfg.py`|1245|`f0c7744fd0232704dc51252ccd53631a6d12cd4b2419b8f988bb894f759bc267`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/csdog_v2/csdog_v2_env_cfg.py`|12740|`6338cf876fdbf6720ea5795c75ad36f55f7f1bb1c10899181dfbd04978864190`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/__init__.py`|416|`94664e4ae8e65793a067e8bd0936e91d2bd2cd8e0dc08f7ce6c378611023d432`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/__init__.py`|0|`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/agents/rsl_rl_ppo_cfg.py`|961|`85a246014f0e2763bdc8090b874afd519e24824252f8ae27535ccc4976041bd7`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/custom_rewards.py`|683|`2705610c68e3f9d7ab6125059bd5a8608f8a7b10134a800e1f33349abae3633f`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env.py`|26787|`7161ef90c29b691c8c14bd478b1b84f4e9144997b3aa8c0eceafff53b23529f8`|本地同路径不存在；保留远端历史|
|`source/stackforce_simready_generated_robot_lab/stackforce_simready_generated_robot_lab/tasks/direct/generated_robot/generated_robot_env_cfg.py`|8425|`7177d57853ca88135e6f13159f6b5b25d00283ebed55b870ced3697066a426ef`|本地同路径不存在；保留远端历史|
|`tests/test_urdf_audit.py`|2295|`e7b9a8a6b27783160c3a09ba1dc9872f586c537f01cfc8222bddcd7b1c2b8477`|本地同路径不存在；保留远端历史|

## 合并与替换决策

远端 main 是 Stackforce/CSDog locomotion 源码布局，含 source/stackforce_simready_generated_robot_lab 与旧 scripts/rsl_rl；本机是独立 dogfight_rl/src 布局。两者不是可以直接整树覆盖的同一工作副本。历史资产分支只承载一个完整tar.gz包，不能代表当前三狗FSM和HUD已备份。

建议从远端 main 固定提交创建独立 `backup/2026-11-03-desktop-playable` 分支，在远端根下新增 `desktop_playable/dogfight_rl/`、`desktop_playable/model/`（原始设计推荐项）和 docs/desktop_playable/。完整保留 main 原有 source、scripts、assets、CURRENT/HANDOFF。仅在新命名空间补入本机启动脚本、src、configs、导入模型/策略/USD及报告；不替换同名远端README或.gitignore，可新增索引说明并审查合并根ignore。

必须新增：launch.py、teleop/fsm及其V0导入闭包、三种teleop配置、robot ABI配置、17项导入源资源+identity/import manifest+USD完整子层+图标/桌面模板。当前运行权重在远端历史包中即便同字节，仍需按当前路径恢复并校验，不能只留下不可执行的历史压缩包链接。

本次未创建分支、未改remote、未写Git索引/对象、未获取LFS对象、未发布Release。远端main的历史提交图/所有旧tag和Release页面未完整取证；本报告验证当前可见引用和相应提交快照，不冒称全GitHub历史已下载。


## 审计结束本地Git复核

HEAD仍为 `d94aba28e9de91842a972885e93c236c7c5d39cc`；折叠工作区状态仍11修改、221删除、52未跟踪项，与开头一致。五份报告位于业务Git根的外部兄弟目录，未更改业务工作区或Git引用。
