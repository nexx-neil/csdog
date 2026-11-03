from __future__ import annotations


from pathlib import Path

from dogfight_v0.agents.proxy_agent import ProxyAgent
from dogfight_v0.arena.spawn_manager import SpawnManager
from dogfight_v0.arena.test_map import TestMap
from dogfight_v0.battle.battle_manager import BattleManager
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.scripted_policy import ScriptedBattlePolicy
from dogfight_v0.battle.visibility_service import VisibilityService
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.config.battle_cfg import BattleConfig
from dogfight_v0.logging.battle_logger import BattleLogger
from dogfight_v0.navigation.simple_navigation import SimpleNavigation


def create_isaac_battle(
    sim,
    log_root: str | Path,
    config: BattleConfig | None = None,
    echo: bool = True,
    seed: int | None = None,
    arena_map: TestMap | None = None,
):
    """Create a battle in an already-launched Isaac Sim application."""
    from dogfight_v0.sim.physx_ray_query import IsaacPhysXRayQuery
    from dogfight_v0.sim.scene import build_test_scene

    config = config or BattleConfig()
    arena_map = arena_map or TestMap()
    pose_writer = build_test_scene(arena_map, config)
    sim.reset()
    pose_writer.initialize()
    sim.set_camera_view((9.0, -10.0, 9.0), (0.0, 0.0, 0.0))
    agents = {
        agent_id: ProxyAgent(
            agent_id,
            f"/World/Agents/{agent_id}",
            config.muzzle_height_m,
            config.muzzle_forward_offset_m,
            pose_writer,
            arena_map.is_position_valid,
        )
        for agent_id in ("dog_a", "dog_b", "dog_c")
    }
    ray_query = IsaacPhysXRayQuery()
    logger = BattleLogger(log_root, echo=echo)
    manager = BattleManager(
        config=config,
        arena_map=arena_map,
        spawn_manager=SpawnManager(),
        agents=agents,
        navigation=SimpleNavigation(config),
        intel=IntelService(config.intel_period_s),
        visibility=VisibilityService(config, ray_query, agents),
        weapon=WeaponService(config, ray_query),
        health=HealthSystem(config.max_health),
        policies={agent_id: ScriptedBattlePolicy(config) for agent_id in agents},
        logger=logger,
    )
    manager.reset(seed=seed)
    manager.start_round()
    sim.step(render=False)
    return manager
