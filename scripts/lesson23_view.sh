#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'W/S 前后0.2米/秒；A/D 横移0.18米/秒；Q/E 缓转；空格停止，T复位，ESC退出。缓坡加 --column 3。\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_terrain_foundation.py" \
  --checkpoint "$lesson_root/outputs/motion_foundation/lesson23_candidate/candidate.pt" --seed 8573 "$@"
