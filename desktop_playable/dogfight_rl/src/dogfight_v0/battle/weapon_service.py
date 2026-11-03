from __future__ import annotations


from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.battle.ray_query import RayQueryInterface, agent_id_from_path
from dogfight_v0.battle.types import ShotResult
from dogfight_v0.config.battle_cfg import BattleConfig


class WeaponService:
    def __init__(self, config: BattleConfig, ray_query: RayQueryInterface) -> None:
        self.config = config
        self.ray_query = ray_query
        self.reset()

    def reset(self) -> None:
        self._last_fire_s: dict[str, float] = {}

    def can_fire(self, shooter_id: str, current_time_s: float) -> bool:
        last = self._last_fire_s.get(shooter_id)
        return last is None or current_time_s - last >= self.config.weapon_cooldown_s - 1e-9

    def fire(self, shooter: AgentInterface, agents: dict[str, AgentInterface], current_time_s: float) -> ShotResult:
        if not shooter.is_alive() or not self.can_fire(shooter.agent_id, current_time_s):
            return ShotResult(shooter.agent_id, False, False, None, None, None, 0.0, current_time_s)
        self._last_fire_s[shooter.agent_id] = current_time_s
        hit = self.ray_query.raycast_closest(
            shooter.get_muzzle_origin_world(), shooter.get_forward_vector_world(), self.config.weapon_range_m
        )
        hit_agent_id = agent_id_from_path(hit.object_path, agents)
        if hit_agent_id == shooter.agent_id:
            hit_agent_id = None
        did_hit = hit_agent_id is not None and agents[hit_agent_id].is_alive()
        return ShotResult(
            shooter.agent_id, True, did_hit, hit_agent_id if did_hit else None,
            hit.object_path, hit.distance_m, self.config.weapon_damage if did_hit else 0.0, current_time_s,
        )

