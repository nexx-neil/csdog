from __future__ import annotations


from collections.abc import Mapping
from typing import Any


class BattleHUD:
    """Screen-space view of ``BattleManager.get_match_state()``.

    The HUD owns widget text only. It never owns or mutates gameplay health;
    every displayed value is rebuilt from the supplied match-state snapshot.
    ``omni.ui`` is intentionally imported only inside :meth:`build`, keeping
    headless battle imports independent of GUI extensions.
    """

    AGENT_IDS = ("dog_a", "dog_b", "dog_c")
    DISPLAY_NAMES = {"dog_a": "DOG A", "dog_b": "DOG B", "dog_c": "DOG C"}
    WINDOW_TITLE = "Dogfight Battle HUD"
    HEIGHT = 72.0
    TOP_MARGIN = 28.0

    def __init__(self) -> None:
        self._ui: Any | None = None
        self._window: Any | None = None
        self._agent_labels: dict[str, Any] = {}
        self._round_label: Any | None = None
        # Render cache for tests/introspection; it is never a gameplay source.
        self._rendered_text: dict[str, str] = {}
        self._round_text = "TIME 0.0 s | ROUND ACTIVE"

    @property
    def is_built(self) -> bool:
        return self._window is not None

    @property
    def window(self) -> Any | None:
        return self._window

    def build(self) -> None:
        if self.is_built:
            return
        import omni.ui as ui

        self._ui = ui
        flags = (
            ui.WINDOW_FLAGS_NO_TITLE_BAR
            | ui.WINDOW_FLAGS_NO_RESIZE
            | ui.WINDOW_FLAGS_NO_MOVE
            | ui.WINDOW_FLAGS_NO_SCROLLBAR
            | ui.WINDOW_FLAGS_NO_COLLAPSE
            | ui.WINDOW_FLAGS_NO_DOCKING
        )
        self._window = ui.Window(
            self.WINDOW_TITLE,
            width=max(720.0, ui.Workspace.get_main_window_width()),
            height=self.HEIGHT,
            position_x=0.0,
            position_y=self.TOP_MARGIN,
            padding_x=12.0,
            padding_y=6.0,
            flags=flags,
            visible=True,
            raster_policy=ui.RasterPolicy.NEVER,
        )
        self._window.detachable = False
        with self._window.frame:
            with ui.ZStack():
                ui.Rectangle(style={"background_color": 0xDD181818, "border_color": 0xFF555555, "border_width": 1})
                with ui.VStack(spacing=2, style={"margin": 6}):
                    with ui.HStack(spacing=8, height=32):
                        for index, agent_id in enumerate(self.AGENT_IDS):
                            if index:
                                ui.Label("|", width=14, alignment=ui.Alignment.CENTER,
                                         style={"font_size": 18, "color": 0xFF888888})
                            self._agent_labels[agent_id] = ui.Label(
                                f"{self.DISPLAY_NAMES[agent_id]} | HP -- / -- | WAITING",
                                alignment=ui.Alignment.CENTER,
                                style={"font_size": 18, "color": 0xFFE6E6E6},
                            )
                    self._round_label = ui.Label(
                        self._round_text,
                        height=20,
                        alignment=ui.Alignment.CENTER,
                        style={"font_size": 14, "color": 0xFFB8B8B8},
                    )

    def update(self, match_state: Mapping[str, Any]) -> None:
        """Render one authoritative BattleManager match-state snapshot."""
        max_health = float(match_state["max_health"])
        agents = match_state["agents"]
        for agent_id in self.AGENT_IDS:
            state = agents[agent_id]
            health = float(state["health"])
            alive = bool(state["alive"])
            text = self.format_agent_status(agent_id, health, max_health, alive)
            self._rendered_text[agent_id] = text
            label = self._agent_labels.get(agent_id)
            if label is not None:
                label.text = text
                label.style = {"font_size": 18, "color": self._status_color(health, max_health, alive)}

        self._round_text = self.format_round_status(match_state)
        if self._round_label is not None:
            self._round_label.text = self._round_text
        self._fit_to_main_window()

    def reset(self, match_state: Mapping[str, Any] | None = None) -> None:
        """Refresh after a round reset; no independent HP reset is performed."""
        if match_state is not None:
            self.update(match_state)

    def destroy(self) -> None:
        if self._window is not None:
            self._window.destroy()
        self._window = None
        self._agent_labels.clear()
        self._round_label = None
        self._ui = None

    def get_display_text(self, agent_id: str) -> str:
        return self._rendered_text.get(agent_id, "")

    def get_round_text(self) -> str:
        return self._round_text

    @classmethod
    def format_agent_status(cls, agent_id: str, health: float, max_health: float, alive: bool) -> str:
        status = "ALIVE" if alive else "DEAD"
        return (
            f"{cls.DISPLAY_NAMES.get(agent_id, agent_id.upper())} | "
            f"HP {cls._format_health(health)} / {cls._format_health(max_health)} | {status}"
        )

    @staticmethod
    def format_round_status(match_state: Mapping[str, Any]) -> str:
        time_s = float(match_state["time_s"])
        if not bool(match_state["round_over"]):
            return f"TIME {time_s:.1f} s | ROUND ACTIVE"
        winner = match_state.get("winner")
        if winner is not None:
            return f"TIME {time_s:.1f} s | WINNER: {str(winner).replace('_', ' ').upper()}"
        return f"TIME {time_s:.1f} s | DRAW"

    @staticmethod
    def _format_health(value: float) -> str:
        return str(int(value)) if float(value).is_integer() else f"{value:.1f}"

    @staticmethod
    def _status_color(health: float, max_health: float, alive: bool) -> int:
        if not alive:
            return 0xFF5555FF  # ABGR: red
        if max_health > 0.0 and health / max_health <= 0.25:
            return 0xFF55AAFF  # ABGR: orange
        return 0xFF75E675  # ABGR: green

    def _fit_to_main_window(self) -> None:
        if self._window is None or self._ui is None:
            return
        width = self._ui.Workspace.get_main_window_width()
        if width > 0.0:
            self._window.width = max(720.0, width)
        self._window.position_x = 0.0
        self._window.position_y = self.TOP_MARGIN

