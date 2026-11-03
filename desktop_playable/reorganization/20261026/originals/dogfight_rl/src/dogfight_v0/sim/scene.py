from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from math import cos, sin

from dogfight_v0.arena.test_map import TestMap
from dogfight_v0.battle.types import Pose2D
from dogfight_v0.config.battle_cfg import BattleConfig


AGENT_COLORS = {
    "dog_a": (0.85, 0.12, 0.12),
    "dog_b": (0.10, 0.35, 0.90),
    "dog_c": (0.12, 0.75, 0.25),
}


class IsaacPoseWriter:
    def __init__(self, proxy_height_m: float) -> None:
        from isaacsim.core.prims import SingleRigidPrim

        self._proxy_height_m = proxy_height_m
        self._prims: dict[str, SingleRigidPrim] = {}

    def register(self, prim_path: str) -> None:
        from isaacsim.core.prims import SingleRigidPrim

        self._prims[prim_path] = SingleRigidPrim(prim_path, name=prim_path.rsplit("/", 1)[-1])

    def initialize(self) -> None:
        for prim in self._prims.values():
            prim.initialize()

    def __call__(self, prim_path: str, pose: Pose2D) -> None:
        prim = self._prims[prim_path]
        half = pose.yaw / 2.0
        prim.set_world_pose(
            position=(pose.x, pose.y, self._proxy_height_m / 2.0),
            orientation=(cos(half), 0.0, 0.0, sin(half)),
        )


def build_test_scene(arena_map: TestMap, config: BattleConfig) -> IsaacPoseWriter:
    """Create visible/collidable V0 geometry in the current Isaac stage."""
    import isaaclab.sim as sim_utils

    sim_utils.GroundPlaneCfg(size=(14.0, 12.0)).func("/World/TestMap/Ground", sim_utils.GroundPlaneCfg(size=(14.0, 12.0)))
    wall_cfg = lambda wall: sim_utils.CuboidCfg(
        size=wall.size,
        collision_props=sim_utils.CollisionPropertiesCfg(),
        visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=(0.35, 0.35, 0.38)),
    )
    for wall in arena_map.walls:
        cfg = wall_cfg(wall)
        cfg.func(wall.path, cfg, translation=wall.center)

    proxy_paths = {agent_id: f"/World/Agents/{agent_id}" for agent_id in AGENT_COLORS}
    for agent_id, path in proxy_paths.items():
        cfg = sim_utils.CuboidCfg(
            size=(0.75, 0.48, config.proxy_height_m),
            rigid_props=sim_utils.RigidBodyPropertiesCfg(
                kinematic_enabled=True,
                disable_gravity=True,
            ),
            collision_props=sim_utils.CollisionPropertiesCfg(),
            mass_props=sim_utils.MassPropertiesCfg(mass=8.0),
            visual_material=sim_utils.PreviewSurfaceCfg(diffuse_color=AGENT_COLORS[agent_id]),
        )
        cfg.func(path, cfg, translation=(0.0, 0.0, config.proxy_height_m / 2.0))
    writer = IsaacPoseWriter(config.proxy_height_m)
    for path in proxy_paths.values():
        writer.register(path)
    arena_map.load()
    return writer
