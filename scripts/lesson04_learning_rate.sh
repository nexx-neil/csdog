#!/usr/bin/env bash
# Compare lr=3e-5 to reusable lesson02 control lr=1e-5; all reward settings restored.
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# This is an input/source check only; it does not run lesson03 training.
bash "$lesson_root/scripts/lesson03_contact_schedule.sh" --check-only > /dev/null
printf 'Reusable control, parent checkpoint and source hashes verified.\n'
if [[ "${1:-}" == "--check-only" ]]; then
    printf 'Lesson04 plan: original rewards (contact=2.0, yaw width=0.25), lr=3e-5, 10 updates, check every 5. No training started.\n'
    exit 0
fi
if [[ $# -ne 0 ]]; then
    printf 'Usage: bash lesson04_learning_rate.sh [--check-only]\n' >&2
    exit 1
fi
lesson_parent="$lesson_root/logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256/model_final.pt"
lesson_reference="$lesson_root/outputs/motion_foundation/validation/legacy_reference_v2.json"
lesson_stamp="$(date +%Y%m%d_%H%M%S_%N)"
lesson_log="$lesson_root/outputs/motion_foundation/lesson04_$lesson_stamp.log"
printf 'Lesson04: only actual learning rate differs from reusable control: 1e-5 -> 3e-5.\n'
printf 'Full terminal log: %s\n' "$lesson_log"
bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/rsl_rl/train.py" \
    --task CSDog-Motion-Foundation-Direct-v0 \
    --resume_path "$lesson_parent" --policy_only_resume \
    --num_envs 256 --max_iterations 10 --segment_iterations 5 \
    --resume_learning_rate 3e-5 --lr_bounds 1e-6 3e-5 \
    --validation_reference "$lesson_reference" \
    --seed 42 --device cuda:0 --headless \
    --run_name lesson04_lr3e5_original_rewards_h128_e256 \
    agent.num_steps_per_env=128 \
    agent.algorithm.learning_rate=0.00003 \
    env.tracking_ang_vel_std=0.25 \
    env.reward_scales.contact_schedule=2.0 2>&1 | tee "$lesson_log"
