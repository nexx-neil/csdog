#!/usr/bin/env bash
# Generate a new inference-only video; never run PPO or replace the release.
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lesson_checkpoint="$lesson_root/outputs/motion_foundation/lesson12_candidate/candidate.pt"
lesson_stamp="$(date +%Y%m%d_%H%M%S_%N)"
lesson_output="$lesson_root/outputs/motion_foundation/lesson12_preview_$lesson_stamp"
printf 'Inference-only adaptive-clearance candidate. New video directory: %s\n' "$lesson_output"
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/analysis/motion_foundation_20261107/render_residual_preview.py" \
    --stage clean --checkpoint "$lesson_checkpoint" --speed-commands \
    --output "$lesson_output" --headless --device cuda:0
