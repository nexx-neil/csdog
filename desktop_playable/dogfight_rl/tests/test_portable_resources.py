"""Current resources resolve independently of cwd; archived resources are rejected."""
from io import StringIO
from pathlib import Path
import importlib.util
import pytest
from dogfight.common.paths import ROOT, MODEL, LOGS, CHECKPOINTS, load_project_yaml

def test_nested_resource_config_from_unrelated_directory(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    data = load_project_yaml(StringIO("""asset_urdf: model/robot.urdf
nested:
  - checkpoint: runs/locomotion/example.pt
  - url: https://example.invalid/asset.usd
  - system: /usr/lib/example
  - label: LEFT
  - count: 12
"""))
    assert Path(data["asset_urdf"]).is_file()
    assert Path(data["asset_urdf"]) == MODEL / "robot.urdf"
    assert data["nested"] == [
        {"checkpoint": str(ROOT / "runs/locomotion/example.pt")},
        {"url": "https://example.invalid/asset.usd"},
        {"system": "/usr/lib/example"}, {"label": "LEFT"}, {"count": 12}]
    assert LOGS == ROOT / "runs"
    assert CHECKPOINTS == ROOT / "runs/locomotion"

@pytest.mark.parametrize("prefix", ["01_robots", "02_training", "03_battle"])
def test_archived_yaml_cannot_be_consumed_as_current(prefix):
    with pytest.raises(ValueError, match="Archived layout"):
        load_project_yaml(StringIO(f"asset: {prefix}/example"))

def test_imports_use_only_maintained_sources():
    import dogfight.training.reward_terms as rewards
    import dogfight.training.ppo as ppo
    import dogfight_v0
    for module in [rewards, ppo, dogfight_v0]:
        assert Path(module.__file__).is_relative_to(ROOT / "src")
    assert importlib.util.find_spec("dogfight.tasks") is None
    assert importlib.util.find_spec("dogfight_v0.agents.dog_a_factory") is None
