
# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))
from dogfight_v0.battle.types import RayHit


class IsaacPhysXRayQuery:
    """Thin adapter around Isaac Sim 5.1 PhysX closest-hit scene query."""

    def __init__(self) -> None:
        import omni.physx

        self._interface = omni.physx.get_physx_scene_query_interface()

    def raycast_closest(self, origin, direction, max_distance: float) -> RayHit:
        hit = self._interface.raycast_closest(origin, direction, max_distance)
        if not hit.get("hit", False):
            return RayHit(False)
        path_value = hit.get("rigidBody") or hit.get("collision")
        path = str(path_value) if path_value is not None else None
        return RayHit(True, path, float(hit["distance"]))

