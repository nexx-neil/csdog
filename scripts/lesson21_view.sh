#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'Terrain foundation: W/S .2m/s; A/D .18m/s; Q/E .3rad/s; SPACE stop; T reset. Default: up stairs. Use --column 3 for up slope.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_scanned_rough.py" \
  --checkpoint "$lesson_root/outputs/motion_foundation/lesson21_candidate/candidate.pt" "$@"
