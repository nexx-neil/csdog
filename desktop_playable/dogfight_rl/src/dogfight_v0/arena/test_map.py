from __future__ import annotations


from dataclasses import dataclass

from dogfight_v0.battle.types import Pose2D


@dataclass(frozen=True, slots=True)
class WallSpec:
    path: str
    center: tuple[float, float, float]
    size: tuple[float, float, float]

    @property
    def bounds_xy(self) -> tuple[float, float, float, float]:
        x, y, _ = self.center
        sx, sy, _ = self.size
        return x - sx / 2, x + sx / 2, y - sy / 2, y + sy / 2


class TestMap:
    """Small replaceable arena description. No battle rules live here."""

    def __init__(self) -> None:
        self._bounds = (-6.0, 6.0, -5.0, 5.0)
        self._spawns = [
            Pose2D(-4.2, -2.7, 0.35),
            Pose2D(4.2, -2.7, 2.79),
            Pose2D(0.0, 3.7, -1.57),
        ]
        self.walls = [
            WallSpec("/World/TestMap/Walls/wall_center", (0.0, 0.0, 0.75), (0.35, 3.2, 1.5)),
            WallSpec("/World/TestMap/Walls/wall_side", (2.6, 1.6, 0.75), (2.4, 0.35, 1.5)),
        ]
        self.loaded = False

    def load(self) -> None:
        self.loaded = True

    def reset(self, seed: int | None = None) -> None:
        del seed

    def get_bounds(self) -> tuple[float, float, float, float]:
        return self._bounds

    def get_spawn_points(self) -> list[Pose2D]:
        return [Pose2D(p.x, p.y, p.yaw) for p in self._spawns]

    def get_navigation_data(self) -> dict[str, object]:
        return {"bounds": self._bounds, "walls": tuple(self.walls)}

    def is_position_valid(self, x: float, y: float) -> bool:
        min_x, max_x, min_y, max_y = self._bounds
        if not (min_x <= x <= max_x and min_y <= y <= max_y):
            return False
        margin = 0.25
        return not any(
            lo_x - margin <= x <= hi_x + margin and lo_y - margin <= y <= hi_y + margin
            for lo_x, hi_x, lo_y, hi_y in (wall.bounds_xy for wall in self.walls)
        )

