#!/usr/bin/env bash
# Inference only: inspect the user-trained lesson 01 candidate.
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lesson_checkpoint="$lesson_root/logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256/model_final.pt"
if [[ ! -f "$lesson_checkpoint" ]]; then
    printf 'Missing lesson 01 checkpoint: %s\n' "$lesson_checkpoint" >&2
    exit 1
fi
mkdir -p "$lesson_root/outputs/motion_foundation"
lesson_stamp="$(date +%Y%m%d_%H%M%S_%N)"
lesson_metrics="$lesson_root/outputs/motion_foundation/lesson01_view_$lesson_stamp.json"
printf 'Inference only; W/S forward/back, A/D left/right, Q/E turn, SPACE clears commands.\n'
printf 'Limits match regression: x=0.4 m/s, y=0.3 m/s, yaw=0.4 rad/s.\n'
printf 'Metrics will be saved on normal exit: %s\n' "$lesson_metrics"
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/rsl_rl/play.py" \
    --task CSDog-Motion-Foundation-Direct-v0 \
    --checkpoint "$lesson_checkpoint" \
    --keyboard --follow-robot --num_envs 1 --num_steps 6000 \
    --keyboard-forward-speed 0.4 \
    --keyboard-lateral-speed 0.3 \
    --keyboard-yaw-rate 0.4 \
    --seed 42 --device cuda:0 \
    --metrics-output "$lesson_metrics" \
    env.episode_length_s=180.0
