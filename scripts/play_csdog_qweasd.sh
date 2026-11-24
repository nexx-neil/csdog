#!/usr/bin/env bash
set -euo pipefail

repo_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_dir"

conda_env="${CSDOG_CONDA_ENV:-dogfight}"
if [[ -n "${CONDA_EXE:-}" ]]; then
  conda_sh="$(dirname "$(dirname "$CONDA_EXE")")/etc/profile.d/conda.sh"
elif [[ -f "$HOME/miniconda3/etc/profile.d/conda.sh" ]]; then
  conda_sh="$HOME/miniconda3/etc/profile.d/conda.sh"
elif [[ -f "$HOME/anaconda3/etc/profile.d/conda.sh" ]]; then
  conda_sh="$HOME/anaconda3/etc/profile.d/conda.sh"
else
  echo "Cannot locate conda.sh. Activate the Isaac environment first, or set CONDA_EXE." >&2
  exit 1
fi

source "$conda_sh"
conda activate "$conda_env"

checkpoint="logs/rsl_rl/csdog_v2_teleop/2026-10-29_17-42-40_qweasd_mixed100/model_final.pt"
if [[ ! -f "$checkpoint" ]]; then
  echo "Missing release checkpoint: $repo_dir/$checkpoint" >&2
  echo "Extract the csdog-v2-teleop-v0.1.0 resource bundle at the repository root." >&2
  exit 1
fi

exec python scripts/rsl_rl/play.py \
  --task CSDog-V2-Teleop-Direct-v0 \
  --checkpoint "$checkpoint" \
  --num_envs 1 \
  --num_steps 0 \
  --keyboard \
  --follow-robot \
  "$@"
