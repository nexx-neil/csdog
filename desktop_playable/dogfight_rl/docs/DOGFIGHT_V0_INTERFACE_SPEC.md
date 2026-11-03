# DOGFIGHT V0 Interface Specification

API version: `DOGFIGHT_V0_API = 0.1`

This in-project document records the implemented contract. The authoritative
input specification is `/home/zxq/下载/DOGFIGHT_V0_INTERFACE_SPEC.md`; the V0
implementation was audited against all 28 sections of that document.

## Stable contracts

- Coordinates: +X forward, +Y left, +Z up; meters, seconds, radians.
- Locomotion command: `VelocityCommand(vx, vy, yaw_rate)` in the body frame.
- Canonical IDs: `dog_a`, `dog_b`, `dog_c`; IDs carry no map semantics.
- `yaw_error_rad` is normalized to `[-pi, +pi]`, positive to the left.
- Intel is a timestamped periodic snapshot; it is not continuous tracking.
- Visibility requires alive, range, horizontal FOV, and clear LOS.
- Weapon is a closest-hit instantaneous PhysX raycast with range/cooldown.
- Health owns HP/death; BattleManager owns round timer/winner/draw/reset.
- Battle and navigation never emit joint commands.

## Interface locations

| Contract | Implementation path |
| --- | --- |
| Core data structures | `source/dogfight_v0/dogfight_v0/battle/types.py` |
| MapInterface | `source/dogfight_v0/dogfight_v0/arena/map_interface.py` |
| SpawnManagerInterface | `source/dogfight_v0/dogfight_v0/arena/spawn_manager.py` |
| AgentInterface | `source/dogfight_v0/dogfight_v0/agents/agent_interface.py` |
| LocomotionInterface | `source/dogfight_v0/dogfight_v0/agents/locomotion_interface.py` |
| NavigationInterface | `source/dogfight_v0/dogfight_v0/navigation/navigation_interface.py` |
| Intel/Visibility/Weapon/Health/Battle/Policy protocols | `source/dogfight_v0/dogfight_v0/battle/interfaces.py` |

## Dead-agent rule

At the next intel tick a dead target remains in the snapshot with its last
pose and `alive=false`. Requesters never receive themselves. Dead agents stop,
cannot see, navigate, or fire, and are excluded from winner evaluation.

## Timeout rule

V0 declares a draw when `round_time_limit_s` is reached with more than one
agent alive. This is centralized in `BattleManager` and configured by
`BattleConfig`.

