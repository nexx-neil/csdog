"""Dogfight V0 public API."""

from .battle.battle_manager import BattleManager
from .config.battle_cfg import BattleConfig

DOGFIGHT_V0_API = "0.1"

__all__ = ["BattleConfig", "BattleManager", "DOGFIGHT_V0_API"]

