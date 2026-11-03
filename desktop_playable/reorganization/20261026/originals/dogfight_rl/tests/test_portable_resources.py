"""Resource resolution works independently of cwd and preserves nonpath YAML values."""
from io import StringIO
from pathlib import Path
from shared.paths import ROOT, LOGS, CHECKPOINTS, load_project_yaml


def test_nested_resource_config_from_unrelated_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    data = load_project_yaml(StringIO('''asset_usd: 01_robots/assets/dog_a/dog_a.usd
nested:
  - checkpoint: 02_training/logs/example.pt
  - url: https://example.invalid/asset.usd
  - system: /usr/lib/example
  - label: LEFT
  - count: 12
'''))
    assert Path(data['asset_usd']).is_file()
    assert data['nested'] == [
        {'checkpoint': str(ROOT/'02_training/logs/example.pt')},
        {'url': 'https://example.invalid/asset.usd'},
        {'system': '/usr/lib/example'}, {'label': 'LEFT'}, {'count': 12},
    ]
    assert LOGS.is_dir() and LOGS == ROOT/'02_training/logs'
    assert CHECKPOINTS == ROOT/'02_training/checkpoints'


def test_imports_use_maintained_sources_after_materialization():
    import dogfight.geometry.foot_contact_solver as geometry
    import dogfight.tasks as tasks
    assert Path(geometry.__file__).is_relative_to(ROOT/'01_robots/python')
    assert Path(tasks.__file__).is_relative_to(ROOT/'02_training/python')
