#!/usr/bin/env bash
set -euo pipefail
motion_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="$motion_root/source/stackforce_simready_generated_robot_lab${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONUNBUFFERED=1
cd "$motion_root"
exec "${CSDOG_PYTHON:-python3}" "$@"
