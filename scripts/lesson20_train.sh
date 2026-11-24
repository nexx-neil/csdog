#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/run_trot_course.py" \
  --mode train --checkpoint "$lesson_root/outputs/motion_foundation/lesson16_candidate/candidate.pt" \
  --output "$lesson_root/outputs/motion_foundation/lesson20_train_$(date +%Y%m%d_%H%M%S)" \
  --max-updates 100 --segment 25 --num-envs 256 --headless "$@"
