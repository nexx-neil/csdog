#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'Fast single axes: W/S .5m/s; A/D .35m/s; Q/E .6rad/s. Combined axes use normal limits. C lowers 6cm; R rises.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_guarded_skills.py" \
    --profile responsive --speed fast --checkpoint "$lesson_root/outputs/motion_foundation/lesson13_candidate/candidate.pt" --device cuda:0 "$@"
