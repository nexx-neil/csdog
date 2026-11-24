#!/usr/bin/env bash
# One candidate; reuse lesson02 control as the unchanged, same-parent/same-budget comparator.
set -euo pipefail
lesson_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
lesson_parent="$lesson_root/logs/rsl_rl/csdog_motion_foundation/2026-11-06_15-21-31_lesson01_foundation5_h128_e256/model_final.pt"
lesson_reference="$lesson_root/outputs/motion_foundation/validation/legacy_reference_v2.json"
bash "$lesson_root/scripts/motion_python.sh" - "$lesson_root" <<'PY'
import hashlib,json,sys
from pathlib import Path
root=Path(sys.argv[1])
experiment=json.loads((root/'outputs/motion_foundation/lesson02_ab_20261106_154408_697378/experiment.json').read_text())
control=experiment['arms']['control']
if control['status']!='TRAIN_AND_REGRESSION_PASS':
    raise RuntimeError('Reusable control did not pass')
run=Path(control['run_directory'])
metadata=json.loads((run/'model_final.pt.metadata.json').read_text())
digest=lambda path:hashlib.sha256(Path(path).read_bytes()).hexdigest()
assert digest(experiment['parent_checkpoint'])==experiment['parent_sha256']
assert digest(experiment['reference'])==experiment['reference_sha256']
assert digest(run/'model_final.pt')==metadata['checkpoint_sha256']
assert metadata['parent_sha256']==experiment['parent_sha256'] and metadata['updates_in_this_run']==10
assert json.loads((run/'validation_0010.json').read_text())['regression_gate']['status']=='PASS'
for path,value in metadata['source_files_sha256'].items():
    if digest(root/path)!=value:
        raise RuntimeError(f'Source changed since reusable control: {path}. Re-audit before comparing.')
print(f'Reusing unchanged 10-update control: {run}',flush=True)
print('Candidate reloads lesson01; yaw width stays 0.25; only contact_schedule weight changes 2.0 -> 3.0.',flush=True)
PY
if [[ "${1:-}" == "--check-only" ]]; then
    printf 'Preflight PASS. No training started.\n'
    exit 0
fi
if [[ $# -ne 0 ]]; then
    printf 'Usage: bash lesson03_contact_schedule.sh [--check-only]\n' >&2
    exit 1
fi
mkdir -p "$lesson_root/outputs/motion_foundation"
lesson_stamp="$(date +%Y%m%d_%H%M%S_%N)"
lesson_log="$lesson_root/outputs/motion_foundation/lesson03_$lesson_stamp.log"
printf 'Full terminal log: %s\n' "$lesson_log"
bash "$lesson_root/scripts/motion_python.sh" "$lesson_root/scripts/rsl_rl/train.py" \
    --task CSDog-Motion-Foundation-Direct-v0 \
    --resume_path "$lesson_parent" --policy_only_resume \
    --num_envs 256 --max_iterations 10 --segment_iterations 5 \
    --resume_learning_rate 1e-5 --lr_bounds 1e-6 1e-5 \
    --validation_reference "$lesson_reference" \
    --seed 42 --device cuda:0 --headless \
    --run_name lesson03_contact3_h128_e256 \
    agent.num_steps_per_env=128 \
    env.tracking_ang_vel_std=0.25 \
    env.reward_scales.contact_schedule=3.0 2>&1 | tee "$lesson_log"
