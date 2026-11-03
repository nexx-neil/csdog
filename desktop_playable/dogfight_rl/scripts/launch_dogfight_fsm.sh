#!/usr/bin/env bash
# Reuse the locally verified desktop environment and locking/failure handling.
set -uo pipefail
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$PROJECT_ROOT/scripts/launch_dogfight_teleop.sh" --config "$PROJECT_ROOT/configs/teleop/fsm_battle.yaml" "$@"
