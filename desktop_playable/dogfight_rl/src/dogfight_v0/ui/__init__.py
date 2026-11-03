"""GUI-only presentation components.

Importing this package is safe before Kit starts; :mod:`omni.ui` is imported
lazily by :meth:`BattleHUD.build` only.
"""

from .battle_hud import BattleHUD

__all__ = ["BattleHUD"]

