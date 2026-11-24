#!/usr/bin/env bash
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/lesson02_yaw_ab.py" "$@"
