from __future__ import annotations


from dataclasses import asdict, dataclass, field
from math import pi
from typing import Any


def normalize_angle(angle: float) -> float:
    """Normalize to [-pi, pi], retaining +pi for positive odd multiples."""
    value = (angle + pi) % (2.0 * pi) - pi
    return pi if value == -pi and angle > 0.0 else value


@dataclass(slots=True)
class Pose2D:
    x: float
    y: float
    yaw: float


@dataclass(slots=True)
class VelocityCommand:
    vx: float = 0.0
    vy: float = 0.0
    yaw_rate: float = 0.0


@dataclass(frozen=True, slots=True)
class IntelRecord:
    agent_id: str
    x: float
    y: float
    timestamp_s: float
    alive: bool


@dataclass(frozen=True, slots=True)
class VisibilityResult:
    observer_id: str
    target_id: str
    visible: bool
    in_fov: bool
    line_of_sight: bool
    distance_m: float
    yaw_error_rad: float


@dataclass(frozen=True, slots=True)
class ShotResult:
    shooter_id: str
    fired: bool
    hit: bool
    hit_agent_id: str | None
    hit_object_path: str | None
    distance_m: float | None
    damage: float
    timestamp_s: float


@dataclass(slots=True)
class AgentState:
    agent_id: str
    pose: Pose2D
    health: float
    alive: bool
    last_velocity_command: VelocityCommand


@dataclass(slots=True)
class BattleObservation:
    self_state: AgentState
    intel: dict[str, IntelRecord]
    visible_targets: list[VisibilityResult]


@dataclass(slots=True)
class BattleAction:
    navigation_target_xy: tuple[float, float] | None = None
    velocity_override: VelocityCommand | None = None
    fire: bool = False


@dataclass(slots=True)
class BattleEvent:
    timestamp_s: float
    event_type: str
    agent_id: str | None = None
    target_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RayHit:
    hit: bool
    object_path: str | None = None
    distance_m: float | None = None

