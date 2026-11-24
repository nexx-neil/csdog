#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'W/S 0.2m/s; A/D 0.18m/s; Q/E .3rad/s; SPACE stop; T reset; ESC exit. Up slope: --column 3.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_anchored_terrain.py" \
  --checkpoint "$lesson_root/outputs/motion_foundation/lesson22_candidate/candidate.pt" --seed 1091 "$@"
