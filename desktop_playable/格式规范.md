# DOGFIGHT V0 Interface Specification

> Project: Three-quadruped autonomous combat simulation  
> Scope: V0 battle framework only  
> Goal: decouple map, battle rules, navigation, perception, and future locomotion policies so the concrete map and real quadruped models can be replaced later without rewriting the battle system.

---

## 1. V0 Goal

V0 is **not** the final map, **not** the final quadruped model, and **not** the final reinforcement-learning battle policy.

V0 only needs to prove this complete chain:

```text
3 Proxy Agents
    ↓
spawn / reset
    ↓
every 5 s publish last-known positions
    ↓
set navigation goal
    ↓
agent moves toward goal
    ↓
target enters FOV
    ↓
LOS check
    ↓
return target + distance + yaw_error
    ↓
agent adjusts yaw
    ↓
fire
    ↓
raycast hit test
    ↓
damage / death / round result
```

The concrete arena layout must remain replaceable.

---

## 2. Non-Goals for V0

Do **not** implement these in V0:

- final CS-style map
- final quadruped URDF/USD models
- PPO locomotion training
- battle RL training
- self-play
- RGB/depth camera perception
- ballistic projectile simulation
- recoil
- pitch aiming
- magazine/reload system
- distributed simulation across three PCs
- ROS integration
- Gazebo / MuJoCo sim2sim
- complex NavMesh if a simple proxy navigation method is sufficient

All of these should remain possible later through interfaces.

---

## 3. Architecture

```text
                    BattleManager
                         │
          ┌──────────────┼──────────────┐
          │              │              │
          ↓              ↓              ↓
      HealthSystem   IntelService   WeaponService
          │              │              │
          └──────────────┼──────────────┘
                         ↓
                 VisibilityService
                         │
                         ↓
                  NavigationService
                         │
                         ↓
                    DogAgent API
                         │
              ┌──────────┴──────────┐
              ↓                     ↓
         ProxyAgent            RealDogAgent
                                  │
                         LocomotionInterface
                                  │
                        vx / vy / yaw_rate
                                  │
                       future PPO policy
```

The battle layer must never directly control individual joints.

---

## 4. Global Conventions

### 4.1 Coordinate convention

Use a single convention everywhere:

```text
+X = forward
+Y = left
+Z = up
```

### 4.2 Units

```text
position      = meter
distance      = meter
linear speed  = m/s
angle         = rad
angular speed = rad/s
time          = second
health        = dimensionless integer/float
```

### 4.3 Yaw error

`yaw_error_rad` must be normalized to:

```text
[-pi, +pi]
```

Recommended meaning:

```text
yaw_error_rad > 0  -> target is to the left
yaw_error_rad < 0  -> target is to the right
yaw_error_rad = 0  -> target is centered
```

### 4.4 Agent IDs

V0 canonical IDs:

```text
dog_a
dog_b
dog_c
```

Never infer behavior from the ID itself.

### 4.5 No hard-coded map assumptions

Battle code must not contain assumptions such as:

```text
dog_a is always north
dog_b is always west
dog_c is always east
```

Spawn assignment must be data-driven.

---

## 5. Core Data Types

The exact Python implementation may use `dataclass`, `NamedTuple`, or typed dictionaries, but semantics must remain stable.

### 5.1 Pose2D

```python
@dataclass
class Pose2D:
    x: float
    y: float
    yaw: float
```

### 5.2 VelocityCommand

This is the **future locomotion contract**.

```python
@dataclass
class VelocityCommand:
    vx: float
    vy: float
    yaw_rate: float
```

Semantics:

- `vx`: body-frame forward velocity command
- `vy`: body-frame lateral velocity command
- `yaw_rate`: body-frame yaw angular velocity command

### 5.3 IntelRecord

```python
@dataclass
class IntelRecord:
    agent_id: str
    x: float
    y: float
    timestamp_s: float
    alive: bool
```

Important: this is a **snapshot**, not continuous tracking.

### 5.4 VisibilityResult

```python
@dataclass
class VisibilityResult:
    observer_id: str
    target_id: str
    visible: bool
    in_fov: bool
    line_of_sight: bool
    distance_m: float
    yaw_error_rad: float
```

### 5.5 ShotResult

```python
@dataclass
class ShotResult:
    shooter_id: str
    fired: bool
    hit: bool
    hit_agent_id: str | None
    hit_object_path: str | None
    distance_m: float | None
    damage: float
    timestamp_s: float
```

### 5.6 AgentState

```python
@dataclass
class AgentState:
    agent_id: str
    pose: Pose2D
    health: float
    alive: bool
    last_velocity_command: VelocityCommand
```

---

## 6. MapInterface

The battle system must know **what services the map provides**, not what the final map looks like.

```python
class MapInterface(Protocol):

    def load(self) -> None:
        ...

    def reset(self, seed: int | None = None) -> None:
        ...

    def get_bounds(self) -> tuple[float, float, float, float]:
        # Returns: min_x, max_x, min_y, max_y
        ...

    def get_spawn_points(self) -> list[Pose2D]:
        ...

    def get_navigation_data(self):
        # May return waypoint graph, navmesh handle, or simple V0 data
        ...

    def is_position_valid(self, x: float, y: float) -> bool:
        ...
```

Requirements:

- No battle logic inside the map.
- No fixed assumption about number/location of walls.
- Final map can be swapped without changing Intel/Weapon/Health/BattleManager.
- V0 may use a simple flat floor plus 1-2 test walls.

---

## 7. SpawnManager

```python
class SpawnManagerInterface(Protocol):

    def assign_spawns(
        self,
        agent_ids: list[str],
        spawn_points: list[Pose2D],
        seed: int | None = None,
    ) -> dict[str, Pose2D]:
        ...

    def respawn(self, agent_id: str) -> Pose2D:
        ...
```

V0 requirements:

- Must support exactly 3 agents.
- Must not rely on fixed Dog A/B/C geographic positions.
- Must be able to randomize later.
- Spawn points should be map data, not battle-code constants.

---

## 8. AgentInterface

This is the single abstraction used by battle code.

```python
class AgentInterface(Protocol):

    @property
    def agent_id(self) -> str:
        ...

    def reset(self, pose: Pose2D) -> None:
        ...

    def get_pose(self) -> Pose2D:
        ...

    def get_forward_vector_world(self) -> tuple[float, float, float]:
        ...

    def get_muzzle_origin_world(self) -> tuple[float, float, float]:
        ...

    def set_velocity_command(self, command: VelocityCommand) -> None:
        ...

    def stop(self) -> None:
        ...

    def update(self, dt: float) -> None:
        ...

    def is_alive(self) -> bool:
        ...
```

V0 implementation:

```text
ProxyAgent
```

Future implementation:

```text
RealDogAgent
```

Battle code must not care which implementation is active.

---

## 9. ProxyAgent

The V0 proxy can be a simple box/capsule or light articulation.

Requirements:

- unique visual identity for A/B/C
- position and yaw available
- can receive `VelocityCommand`
- can stop
- has a forward direction
- has a muzzle origin
- supports collision
- can be hit by raycast
- does not require a learned policy

The proxy movement implementation may initially be simple/kinematic, provided it preserves the same external interface used later by the real dog.

---

## 10. LocomotionInterface

This interface is reserved for the future trained quadrupeds.

```python
class LocomotionInterface(Protocol):

    def reset(self) -> None:
        ...

    def set_command(self, command: VelocityCommand) -> None:
        ...

    def compute_action(self, observation) -> object:
        # Future return value: 12 joint position targets / actuator actions
        ...

    def step(self, dt: float) -> None:
        ...
```

Hard contract:

Battle/navigation code outputs only:

```text
vx
vy
yaw_rate
```

It must never emit direct 12-DOF joint commands.

This makes each teammate free to train a different locomotion policy/model.

---

## 11. NavigationInterface

```python
class NavigationInterface(Protocol):

    def set_goal(
        self,
        agent_id: str,
        target_xy: tuple[float, float],
    ) -> None:
        ...

    def clear_goal(self, agent_id: str) -> None:
        ...

    def has_goal(self, agent_id: str) -> bool:
        ...

    def goal_reached(self, agent_id: str) -> bool:
        ...

    def compute_command(
        self,
        agent: AgentInterface,
        dt: float,
    ) -> VelocityCommand:
        ...
```

V0 implementation options:

```text
direct goal seeking
or
small waypoint graph + A*
```

Do not force ROS or a heavy navigation stack in V0.

Future replacement may be:

```text
A*
NavMesh
DWA
MPC
RL navigation
```

without changing BattleManager or DogAgent APIs.

---

## 12. IntelService

This implements the **5-second intelligence snapshot** mechanic.

```python
class IntelServiceInterface(Protocol):

    def reset(self, start_time_s: float = 0.0) -> None:
        ...

    def update(
        self,
        current_time_s: float,
        agents: dict[str, AgentInterface],
    ) -> bool:
        # Returns True only when a new intel snapshot is published.
        ...

    def get_last_known_position(
        self,
        requester_id: str,
        target_id: str,
    ) -> IntelRecord | None:
        ...

    def get_snapshot_for(
        self,
        requester_id: str,
    ) -> dict[str, IntelRecord]:
        ...
```

V0 behavior:

```text
INTEL_PERIOD_S = 5.0
```

At `t = 0, 5, 10, 15...` seconds, store the exact current XY positions of all alive agents.

Between updates:

- keep the previous snapshot
- do not continuously update an enemy's position
- navigation may use stale information
- direct visibility can still provide current target angle when target is actually visible

Future hooks:

```text
intel position noise
intel delay
partial intel
team intel
different update period
```

These must be configuration changes, not API rewrites.

---

## 13. VisibilityService

This implements:

```text
FOV test
+
line-of-sight test
+
distance
+
yaw error
```

```python
class VisibilityServiceInterface(Protocol):

    def observe_target(
        self,
        observer: AgentInterface,
        target: AgentInterface,
    ) -> VisibilityResult:
        ...

    def observe_all(
        self,
        observer: AgentInterface,
        candidates: list[AgentInterface],
    ) -> list[VisibilityResult]:
        ...
```

Visibility definition:

A target is visible only when:

```text
observer alive
AND
target alive
AND
target inside max vision range
AND
target inside horizontal FOV
AND
LOS ray is not blocked by another object
```

Required output:

```text
visible
distance_m
yaw_error_rad
target_id
```

Configuration:

```python
VISION_MAX_RANGE_M
VISION_HALF_FOV_RAD
```

V0 may select reasonable test defaults, but they must live in config.

---

## 14. WeaponService

V0 weapon = instantaneous raycast weapon.

```python
class WeaponServiceInterface(Protocol):

    def can_fire(
        self,
        shooter_id: str,
        current_time_s: float,
    ) -> bool:
        ...

    def fire(
        self,
        shooter: AgentInterface,
        agents: dict[str, AgentInterface],
        current_time_s: float,
    ) -> ShotResult:
        ...

    def reset(self) -> None:
        ...
```

V0 behavior:

1. origin = shooter's muzzle origin
2. direction = shooter's forward direction
3. cast a physics ray
4. use the closest hit
5. wall/obstacle hit -> no agent damage
6. agent hit -> return target ID
7. HealthSystem applies damage
8. cooldown prevents infinite fire rate

Config:

```text
WEAPON_RANGE_M
WEAPON_DAMAGE
WEAPON_COOLDOWN_S
```

V0 does not require:

```text
projectile rigid bodies
gravity drop
recoil
magazine
reload
pitch aiming
```

---

## 15. HealthSystem

```python
class HealthSystemInterface(Protocol):

    def reset(self, agent_ids: list[str]) -> None:
        ...

    def get_health(self, agent_id: str) -> float:
        ...

    def is_alive(self, agent_id: str) -> bool:
        ...

    def apply_damage(
        self,
        target_id: str,
        amount: float,
        source_id: str | None = None,
    ) -> float:
        # Returns new health.
        ...

    def kill(self, agent_id: str) -> None:
        ...
```

Config:

```text
MAX_HEALTH
```

---

## 16. BattleManager

BattleManager orchestrates the match but does not own low-level physics control.

```python
class BattleManagerInterface(Protocol):

    def reset(self, seed: int | None = None) -> None:
        ...

    def start_round(self) -> None:
        ...

    def step(self, dt: float) -> None:
        ...

    def is_round_over(self) -> bool:
        ...

    def get_alive_agents(self) -> list[str]:
        ...

    def get_winner(self) -> str | None:
        ...

    def get_match_state(self) -> dict:
        ...
```

Responsibilities:

```text
spawn
round timer
intel update
agent navigation update
visibility query
fire requests
damage
death
winner/draw
logging
```

Must not contain:

```text
URDF joint names
12-DOF action generation
specific final map coordinates
hard-coded walls
PPO implementation
```

---

## 17. Future Battle Policy Interface

V0 can use scripted logic, but reserve this API now.

```python
@dataclass
class BattleObservation:
    self_state: AgentState
    intel: dict[str, IntelRecord]
    visible_targets: list[VisibilityResult]

@dataclass
class BattleAction:
    navigation_target_xy: tuple[float, float] | None
    velocity_override: VelocityCommand | None
    fire: bool

class BattlePolicyInterface(Protocol):

    def reset(self) -> None:
        ...

    def act(self, observation: BattleObservation) -> BattleAction:
        ...
```

V0 implementation:

```text
ScriptedBattlePolicy
```

Future implementations:

```text
PPOBattlePolicy
IPPOBattlePolicy
MAPPOBattlePolicy
SelfPlayPolicy
```

---

## 18. ScriptedBattlePolicy for V0

A minimal reference state machine:

```text
NO_VISIBLE_TARGET
    ↓
read latest Intel snapshot
    ↓
choose one target
    ↓
navigate toward last-known position
    ↓
scan / rotate if goal reached

TARGET_VISIBLE
    ↓
read yaw_error
    ↓
|yaw_error| > aim threshold?
    YES -> yaw correction
    NO  -> fire

TARGET_LOST
    ↓
resume last-known-position navigation
```

This scripted baseline is required before RL battle training.

---

## 19. Configuration Interface

All important gameplay values must live in one config layer.

Suggested fields:

```python
@dataclass
class BattleConfig:
    intel_period_s: float
    vision_max_range_m: float
    vision_half_fov_rad: float

    weapon_range_m: float
    weapon_damage: float
    weapon_cooldown_s: float

    max_health: float
    round_time_limit_s: float

    aim_tolerance_rad: float
    goal_reached_tolerance_m: float

    max_vx: float
    max_vy: float
    max_yaw_rate: float
```

Do not scatter magic numbers through implementation files.

---

## 20. Logging / Telemetry Interface

V0 should log enough information for debugging and future course reports.

Recommended event types:

```text
ROUND_START
ROUND_END
SPAWN
INTEL_UPDATE
NAV_GOAL_SET
NAV_GOAL_REACHED
TARGET_VISIBLE
TARGET_LOST
SHOT_FIRED
SHOT_HIT
DAMAGE
DEATH
WINNER
ERROR
```

Recommended event record:

```python
@dataclass
class BattleEvent:
    timestamp_s: float
    event_type: str
    agent_id: str | None
    target_id: str | None
    data: dict
```

Output may initially be JSONL/CSV/text logs.

---

## 21. Open-Source Reuse Boundary

The project may reuse compatible architecture or code from open-source projects, but the local validated Isaac Lab environment must remain authoritative.

### MARLadona

Use primarily for:

```text
external Isaac Lab extension layout
multi-agent organization
agent-separated observations/actions
multi-agent reset/scene patterns
```

Do not force its exact Isaac Lab dependency versions into the current environment.

### isaac-fighter

Use primarily for:

```text
multi-agent combat environment structure
round lifecycle
arena/boundary logic patterns
per-agent state
future self-play/checkpoint pool design
```

Do not import humanoid-specific combat logic.

### Arena-Rosnav

Use primarily for:

```text
map/scenario/spawn/goal/navigation abstraction ideas
```

Do not add ROS as a V0 dependency only for this reason.

### License rule

Before copying source code:

1. read the upstream LICENSE
2. preserve required notices
3. record source file/repository/commit
4. create/update `THIRD_PARTY_NOTICES.md`
5. prefer adaptation over large blind code copies

---

## 22. Suggested Project Layout

```text
dogfight_rl/
├── source/
│   └── dogfight_v0/
│       ├── dogfight_v0/
│       │   ├── arena/
│       │   │   ├── map_interface.py
│       │   │   ├── test_map.py
│       │   │   └── spawn_manager.py
│       │   │
│       │   ├── agents/
│       │   │   ├── agent_interface.py
│       │   │   ├── proxy_agent.py
│       │   │   └── locomotion_interface.py
│       │   │
│       │   ├── navigation/
│       │   │   ├── navigation_interface.py
│       │   │   └── simple_navigation.py
│       │   │
│       │   ├── battle/
│       │   │   ├── battle_manager.py
│       │   │   ├── intel_service.py
│       │   │   ├── visibility_service.py
│       │   │   ├── weapon_service.py
│       │   │   ├── health_system.py
│       │   │   ├── scripted_policy.py
│       │   │   └── types.py
│       │   │
│       │   ├── config/
│       │   │   └── battle_cfg.py
│       │   │
│       │   └── logging/
│       │       └── battle_logger.py
│       │
│       └── config/
│           └── extension.toml
│
├── scripts/
│   └── v0/
│       ├── run_v0_gui.py
│       ├── run_v0_headless.py
│       └── run_v0_smoke_tests.py
│
├── tests/
│   ├── test_spawn.py
│   ├── test_intel_5s.py
│   ├── test_visibility.py
│   ├── test_weapon.py
│   ├── test_navigation.py
│   └── test_round.py
│
├── docs/
│   └── DOGFIGHT_V0_INTERFACE_SPEC.md
│
└── THIRD_PARTY_NOTICES.md
```

Adapt the layout to the existing repository if the project already has an established structure.

---

## 23. V0 Acceptance Gates

V0 is complete only if all gates below pass.

### Gate A — Environment integrity

- current validated Isaac Lab environment still launches
- no global package upgrade/downgrade
- no Isaac Lab source modification
- project runs as external extension/project code

### Gate B — Three proxies

- exactly 3 proxies load
- IDs are `dog_a`, `dog_b`, `dog_c`
- each can move independently
- each reports pose/yaw

### Gate C — 5-second intelligence

- at 5-second intervals a snapshot is generated
- between intervals enemy last-known position remains unchanged
- timestamp is recorded
- dead agents are handled consistently

### Gate D — Navigation

- an agent can receive an XY goal
- it can approach the goal using only the navigation interface
- output remains `vx / vy / yaw_rate`
- no joint-level assumptions

### Gate E — FOV and LOS

- target behind observer => not visible
- target in FOV and unblocked => visible
- wall between agents => not visible
- visible result returns distance and normalized `yaw_error_rad`

### Gate F — Weapon

- fire creates a raycast
- closest wall blocks a shot
- target hit returns correct ID
- cooldown works
- damage is applied

### Gate G — Battle loop

- all 3 agents can coexist
- health/death state works
- round can terminate
- winner or draw can be reported
- reset works without restarting Isaac Sim

### Gate H — Replaceability

A mock or test must demonstrate that `ProxyAgent` can theoretically be replaced by a `RealDogAgent` while BattleManager continues using the same Agent/Locomotion contracts.

---

## 24. Required V0 Console / Log Output

At minimum, produce readable logs such as:

```text
[V0] ROUND_START
[V0] SPAWN dog_a x=... y=... yaw=...
[V0] SPAWN dog_b x=... y=... yaw=...
[V0] SPAWN dog_c x=... y=... yaw=...

[V0] INTEL_UPDATE t=5.000
[V0] dog_a sees last_known dog_b=(..., ...)
[V0] dog_a NAV_GOAL target=(..., ...)

[V0] TARGET_VISIBLE observer=dog_a target=dog_b
[V0] distance=...
[V0] yaw_error_rad=...

[V0] SHOT_FIRED shooter=dog_a
[V0] SHOT_HIT target=dog_b damage=...
[V0] dog_b health=...

[V0] DEATH dog_b
[V0] ROUND_END winner=...
```

---

## 25. Future Integration Contract for Teammates

Each teammate eventually needs to deliver a locomotion adapter satisfying:

```text
INPUT
vx
vy
yaw_rate

OUTPUT INTERNAL TO THEIR ROBOT
12-DOF actuator/joint targets

EXTERNAL API
reset()
set_command(VelocityCommand)
step(dt)
```

They do **not** need to know the final map layout.

The battle framework does **not** need to know how their PPO policy produces joint actions.

---

## 26. Future Map Replacement Contract

A final map is accepted if it provides:

```text
MapInterface.load()
MapInterface.reset()
MapInterface.get_bounds()
MapInterface.get_spawn_points()
MapInterface.get_navigation_data()
MapInterface.is_position_valid()
```

Therefore these can all be swapped later:

```text
EmptyTestMap
TriangleArena
WarehouseArena
CSStyleArena
RandomGeneratedArena
```

without rewriting the battle system.

---

## 27. Versioning Rule

This document defines API version:

```text
DOGFIGHT_V0_API = 0.1
```

Breaking interface changes must update the API version.

Suggested future milestones:

```text
0.1  Proxy three-agent battle skeleton
0.2  Real locomotion policy adapter
0.3  Final map/navigation
0.4  Battle RL observation/action wrapper
0.5  Self-play / policy pool
1.0  Course demonstration release
```

---

## 28. Design Principle Summary

The system must preserve these boundaries:

```text
MAP
does not know PPO

BATTLE MANAGER
does not know joint names

NAVIGATION
outputs only vx / vy / yaw_rate

INTEL
publishes snapshots, not continuous enemy tracking

VISIBILITY
returns current visible-target geometry only when LOS/FOV pass

WEAPON
owns fire/raycast/cooldown, not health state

HEALTH
owns HP/death, not navigation

PROXY AGENT
can later be replaced by REAL DOG AGENT

FINAL MAP
can later replace TEST MAP
```

If these boundaries remain intact, the team can train the three dogs in parallel while the battle/map framework evolves independently.
