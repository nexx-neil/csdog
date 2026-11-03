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
    result = launch('train-a','--dry-run','--max-iterations','1')
    assert result.returncode == 0, result.stderr
    command = json.loads(result.stdout)['command']
    assert Path(command[1]).is_file()
    assert command[command.index('--config')+1].startswith(str(ROOT/'02_training'))
    assert command[command.index('--output-dir')+1].startswith(str(ROOT/'02_training/logs/new_runs'))

def test_existing_output_is_rejected(tmp_path):
    output = tmp_path/'existing.json'
    output.write_text('preserve')
    result = launch('gui-a','--dry-run','--output',str(output))
    assert result.returncode == 2
    assert output.read_text() == 'preserve'

@pytest.mark.parametrize('task', ['train-b','validate-b','train-c','validate-c'])
def test_missing_robot_cannot_claim_to_run(task):
    result=launch(task,'--dry-run')
    assert result.returncode == 2
    assert '本机缺少' in result.stderr

def test_legacy_names_are_physical_compatibility_copies():
    import hashlib
    for legacy, canonical, sample in [
        ('logs', '02_training/logs', 'back_gait_primitive_recovery/model_final.pt'),
        ('dogfight/tasks', '02_training/python/dogfight/tasks', 'dog_a_locomotion_ppo_smoke_v1/train.py'),
        ('source', '03_battle/source', 'dogfight_v0/dogfight_v0/config/battle_cfg.py'),
    ]:
        compatibility = ROOT/legacy
        assert compatibility.is_dir() and not compatibility.is_symlink()
        assert hashlib.sha256((compatibility/sample).read_bytes()).digest() == hashlib.sha256((ROOT/canonical/sample).read_bytes()).digest()
