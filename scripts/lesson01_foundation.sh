#!/usr/bin/env bash
# User-operated first training lesson. Running this script performs five PPO updates.
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lesson_initialization="$lesson_root/outputs/motion_foundation/initialization/legacy_to_obs54_v2.pt"
lesson_reference="$lesson_root/outputs/motion_foundation/validation/legacy_reference_v2.json"
for lesson_input in "$lesson_initialization" "$lesson_initialization.metadata.json" "$lesson_reference"; do
    if [[ ! -f "$lesson_input" ]]; then
        printf 'Missing lesson input: %s\n' "$lesson_input" >&2
        exit 1
    fi
done
mkdir -p "$lesson_root/outputs/motion_foundation"
lesson_stamp="$(date +%Y%m%d_%H%M%S_%N)"
lesson_log="$lesson_root/outputs/motion_foundation/lesson01_$lesson_stamp.log"
printf 'Lesson 01: 256 environments, 128 steps per rollout, 5 PPO updates, fixed lr=1e-5.\n'
printf 'After training: automatic 14-case regression; failure stops this candidate.\n'
printf 'Full terminal log: %s\n' "$lesson_log"
bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/rsl_rl/train.py" \
    --task CSDog-Motion-Foundation-Direct-v0 \
    --resume_path "$lesson_initialization" \
    --policy_only_resume \
    --num_envs 256 \
    --max_iterations 5 \
    --segment_iterations 5 \
    --resume_learning_rate 1e-5 \
    --lr_bounds 1e-6 1e-5 \
    --validation_reference "$lesson_reference" \
    --seed 42 \
    --device cuda:0 \
    --headless \
    --run_name lesson01_foundation5_h128_e256 \
    agent.num_steps_per_env=128 2>&1 | tee "$lesson_log"
