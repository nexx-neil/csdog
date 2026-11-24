#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
printf 'Inference only. Click viewport. W/S move; A/D strafe; Q/E turn; C crouch; R stand; SPACE stop; T reset.\n'
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/play_guarded_skills.py" \
    --profile backward --checkpoint "$lesson_root/outputs/motion_foundation/lesson13_candidate/candidate.pt" --device cuda:0 "$@"
