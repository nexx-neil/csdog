#!/usr/bin/env bash
set -euo pipefail
motion_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo '第31阶段实验候选：尚未通过完整质量验收。W/S前后，A/D横移，Q/E转向，Esc退出。'
exec bash "$motion_root/scripts/motion_python.sh" "$motion_root/scripts/play_recent_contact_foothold_audited.py" --checkpoint "$motion_root/outputs/motion_foundation/lesson31_recent64_pyramid22367/candidate.pt" --kind pyramid_stairs --seed 12037 "$@"
