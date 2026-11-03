
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
import sys
from pathlib import Path

PROJECT_ROOT = next(p for p in Path(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
sys.path.insert(0, str(PROJECT_ROOT / "03_battle/source" / "dogfight_v0"))

import pytest

from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.arena.test_map import TestMap
from dogfight_v0.battle.ray_query import AnalyticRayQuery
from dogfight_v0.battle.visibility_service import VisibilityService
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.config.battle_cfg import BattleConfig


@pytest.fixture
def core():
    config = BattleConfig()
    arena = TestMap()
    agents = {
        name: ProxyAgent(name, f"/World/Agents/{name}", position_validator=arena.is_position_valid)
        for name in ("dog_a", "dog_b", "dog_c")
    }
    query = AnalyticRayQuery(arena.walls, agents, config.agent_hit_radius_m)
    return {
        "config": config,
        "map": arena,
        "agents": agents,
        "query": query,
        "visibility": VisibilityService(config, query, agents),
        "weapon": WeaponService(config, query),
    }

