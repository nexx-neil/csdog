#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

source /home/ni/miniconda3/etc/profile.d/conda.sh
conda activate dogfight

exec python scripts/rsl_rl/play.py \
  --task CSDog-V2-Teleop-Direct-v0 \
  --checkpoint logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt \
  --num_envs 1 \
  --num_steps 0 \
  --keyboard \
  --follow-robot \
  "$@"
