#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'Flat diagonal trot: W .95m/s (measured about .90); S -.5; A/D .4; Q/E .8rad/s; C quick6cm crouch; R rise; SPACE stop.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_trot_bounded_skills.py" \
  --checkpoint "$lesson_root/outputs/motion_foundation/lesson27_candidate/candidate.pt" "$@"
