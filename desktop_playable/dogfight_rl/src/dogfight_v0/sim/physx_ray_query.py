
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

