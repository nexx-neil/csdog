
from dataclasses import dataclass
from math import radians


@dataclass(frozen=True, slots=True)
class BattleConfig:
    intel_period_s: float = 5.0
    vision_max_range_m: float = 20.0
    vision_half_fov_rad: float = radians(60.0)
    weapon_range_m: float = 20.0
    weapon_damage: float = 34.0
    weapon_cooldown_s: float = 1.0
    max_health: float = 100.0
    round_time_limit_s: float = 120.0
    aim_tolerance_rad: float = radians(3.0)
    goal_reached_tolerance_m: float = 0.35
    max_vx: float = 1.2
    max_vy: float = 0.8
    max_yaw_rate: float = 1.8
    scan_yaw_rate: float = 0.6
    proxy_height_m: float = 0.5
    muzzle_height_m: float = 0.45
    muzzle_forward_offset_m: float = 0.55
    agent_hit_radius_m: float = 0.40
    simulation_dt_s: float = 1.0 / 60.0

    def __post_init__(self) -> None:
        positive = (
            "intel_period_s", "vision_max_range_m", "vision_half_fov_rad",
            "weapon_range_m", "weapon_damage", "weapon_cooldown_s",
            "max_health", "round_time_limit_s", "aim_tolerance_rad",
            "goal_reached_tolerance_m", "max_vx", "max_vy", "max_yaw_rate",
            "simulation_dt_s",
        )
        for name in positive:
            if getattr(self, name) <= 0.0:
                raise ValueError(f"{name} must be positive")
