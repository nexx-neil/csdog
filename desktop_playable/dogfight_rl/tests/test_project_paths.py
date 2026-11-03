"""Migration contracts: root resolution, immutable outputs, missing models."""
import json
from pathlib import Path
import subprocess
import sys
import pytest
ROOT = Path(__file__).resolve().parents[1]

def launch(*args):
    return subprocess.run([sys.executable, str(ROOT/'launch.py'), *args], cwd='/tmp', capture_output=True, text=True)

def test_training_paths_from_unrelated_working_directory():
    result = launch('train','--dry-run','--max-iterations','1')
    assert result.returncode == 0, result.stderr
    command = json.loads(result.stdout)['command']
    assert Path(command[2]).is_file()
    assert Path(command[2]) == ROOT/'scripts/train/csdog_12dof.py'
    assert '--resume' not in command and '--checkpoint' not in command
    result = launch('train')
    assert result.returncode == 2
    assert '--iterations' in result.stderr and '--run-name' in result.stderr


def test_existing_output_is_rejected(tmp_path):
    output = tmp_path/'existing.json'
    output.write_text('preserve')
    result = launch('evaluate','--dry-run','--output',str(output))
    assert result.returncode == 2
    assert output.read_text() == 'preserve'

@pytest.mark.parametrize('task', ['train-b','validate-b','train-c','validate-c'])
def test_missing_robot_cannot_claim_to_run(task):
    result=launch(task,'--dry-run')
    assert result.returncode == 2
    assert '本机缺少' in result.stderr

def test_legacy_snapshots_are_archived_and_current_package_is_unique():
    import hashlib
    for old, sample in [
        ('logs', 'back_gait_primitive_recovery/model_final.pt'),
        ('dogfight/tasks', 'dog_a_locomotion_ppo_smoke_v1/train.py'),
        ('source', 'dogfight_v0/dogfight_v0/config/battle_cfg.py')]:
        archived = ROOT.parent/'archive/legacy_compatibility'/old
        assert archived.is_dir() and not archived.is_symlink()
        assert (archived/sample).is_file()
        assert not (ROOT/old).exists()
    original = ROOT.parent/'archive/legacy_compatibility/logs/back_gait_primitive_recovery/model_final.pt'
    canonical = ROOT.parent/'archive/legacy_dog_a/checkpoints_and_runs/back_gait_primitive_recovery/model_final.pt'
    assert hashlib.sha256(original.read_bytes()).digest() == hashlib.sha256(canonical.read_bytes()).digest()

@pytest.mark.parametrize('task', ['train-a', 'validate-a', 'gui-a'])
def test_legacy_entry_cannot_start_new_model(task):
    result = launch(task)
    assert result.returncode == 2
    assert '旧模型入口已归档' in result.stderr
