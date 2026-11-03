
# Locate the maintained source tree independently of the caller working directory.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "src/dogfight/common/paths.py").is_file())
_project_sys.path.insert(0, str(_project_root / "src"))
from dogfight_v0.ui import BattleHUD


def make_state(health=(100.0, 100.0, 100.0), alive=(True, True, True)):
    ids = BattleHUD.AGENT_IDS
    return {
        "time_s": 12.34,
        "round_over": False,
        "winner": None,
        "draw": False,
        "max_health": 100.0,
        "agents": {
            agent_id: {"health": hp, "alive": is_alive}
            for agent_id, hp, is_alive in zip(ids, health, alive, strict=True)
        },
    }


def test_hud_formats_authoritative_snapshot_without_building_ui():
    hud = BattleHUD()
    state = make_state(health=(100.0, 80.0, 0.0), alive=(True, True, False))
    hud.update(state)
    assert hud.get_display_text("dog_a") == "DOG A | HP 100 / 100 | ALIVE"
    assert hud.get_display_text("dog_b") == "DOG B | HP 80 / 100 | ALIVE"
    assert hud.get_display_text("dog_c") == "DOG C | HP 0 / 100 | DEAD"
    assert hud.get_round_text() == "TIME 12.3 s | ROUND ACTIVE"


def test_hud_round_result_format():
    hud = BattleHUD()
    state = make_state()
    state.update(round_over=True, winner="dog_a")
    hud.update(state)
    assert hud.get_round_text() == "TIME 12.3 s | WINNER: DOG A"
    state.update(winner=None, draw=True)
    hud.update(state)
    assert hud.get_round_text() == "TIME 12.3 s | DRAW"

