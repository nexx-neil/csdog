#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'New development profile: W .6; S -.5; A/D +/-.4m/s; Q/E +/-.8rad/s; C smooth6cm crouch; R stand. Mixed axes retain old limits.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_guarded_skills.py" \
    --profile agile --speed agile --checkpoint "$lesson_root/outputs/motion_foundation/lesson13_candidate/candidate.pt" --device cuda:0 "$@"
