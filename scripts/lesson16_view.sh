#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'W .6; S -.5; A/D +/-.4m/s; Q/E +/-.8rad/s; C smooth crouch; R stand. Bounded yaw correction active.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_guarded_skills.py" \
    --profile yaw --speed agile --checkpoint "$lesson_root/outputs/motion_foundation/lesson16_candidate/candidate.pt" --device cuda:0 "$@"
