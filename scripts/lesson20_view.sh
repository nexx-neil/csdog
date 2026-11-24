#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'Development preview: W .8; S -.5; A/D .4m/s; Q/E .8rad/s; C quick6cm crouch; R rise. Jump not enabled.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_trot_skills.py" \
  --checkpoint "$lesson_root/outputs/motion_foundation/lesson20_candidate/candidate.pt" "$@"
