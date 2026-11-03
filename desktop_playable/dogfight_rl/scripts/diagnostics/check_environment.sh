#!/usr/bin/env bash
# Read-only golden-environment check. It never installs or changes packages.
set -euo pipefail

PROJECT_DIR="$(dirname -- "$(readlink -f -- "${BASH_SOURCE[0]}")")"
while [[ ! -f "$PROJECT_DIR/src/dogfight/common/paths.py" ]]; do
    [[ "$PROJECT_DIR" != / ]] || { echo "Cannot locate Dogfight project root" >&2; exit 1; }
    PROJECT_DIR="$(dirname -- "$PROJECT_DIR")"
done
CONDA_EXE="${CONDA_EXE:-$HOME/miniconda3/bin/conda}"

if [[ ! -x "$CONDA_EXE" ]]; then
    echo "DOGFIGHT ENVIRONMENT CHECK FAILED"
    echo "Conda executable not found: $CONDA_EXE"
    exit 1
fi

exec env -u PYTHONPATH -u LD_LIBRARY_PATH PYTHONNOUSERSITE=1 \
    "$CONDA_EXE" run --no-capture-output -n dogfight \
    python "$PROJECT_DIR/scripts/diagnostics/check_environment.py"
