from __future__ import annotations

# Locate the single project root even when invoked by absolute filename.
from pathlib import Path as _ProjectPath
import sys as _project_sys
_project_root = next(p for p in _ProjectPath(__file__).resolve().parents if (p / "shared" / "paths.py").is_file())
for _entry in (_project_root, _project_root / "03_battle/source/dogfight_v0"):
    if str(_entry) not in _project_sys.path:
        _project_sys.path.insert(0, str(_entry))

from dataclasses import asdict

from dogfight_v0.agents.agent_interface import AgentInterface
from dogfight_v0.arena.map_interface import MapInterface
from dogfight_v0.arena.spawn_manager import SpawnManagerInterface
from dogfight_v0.battle.health_system import HealthSystem
from dogfight_v0.battle.intel_service import IntelService
from dogfight_v0.battle.interfaces import BattlePolicyInterface
from dogfight_v0.battle.types import AgentState, BattleObservation, VelocityCommand
from dogfight_v0.battle.visibility_service import VisibilityService
from dogfight_v0.battle.weapon_service import WeaponService
from dogfight_v0.config.battle_cfg import BattleConfig
from dogfight_v0.logging.battle_logger import BattleLogger
from dogfight_v0.navigation.navigation_interface import NavigationInterface


class BattleManager:
    """Orchestrates battle rules using only high-level agent contracts."""

    def __init__(
        self,
        config: BattleConfig,
        arena_map: MapInterface,
        spawn_manager: SpawnManagerInterface,
        agents: dict[str, AgentInterface],
        navigation: NavigationInterface,
        intel: IntelService,
        visibility: VisibilityService,
        weapon: WeaponService,
        health: HealthSystem,
        policies: dict[str, BattlePolicyInterface],
        logger: BattleLogger,
    ) -> None:
        if set(agents) != {"dog_a", "dog_b", "dog_c"}:
            raise ValueError("V0 canonical agents must be dog_a, dog_b, dog_c")
        if set(policies) != set(agents):
            raise ValueError("Each agent requires a policy")
        self.config = config
        self.map = arena_map
        self.spawn_manager = spawn_manager
        self.agents = agents
        self.navigation = navigation
        self.intel = intel
        self.visibility = visibility
        self.weapon = weapon
        self.health = health
        self.policies = policies
        self.logger = logger
        self.time_s = 0.0
        self._round_over = False
        self._winner: str | None = None
        self._draw = False
        self._started = False
        self._visible_pairs: set[tuple[str, str]] = set()
        self._selected_targets: dict[str, str | None] = {}
        self._reached_agents: set[str] = set()

    def reset(self, seed: int | None = None) -> None:
        if not getattr(self.map, "loaded", False):
            self.map.load()
        self.map.reset(seed)
        assignments = self.spawn_manager.assign_spawns(list(self.agents), self.map.get_spawn_points(), seed)
        self.health.reset(list(self.agents))
        self.intel.reset(0.0)
        self.weapon.reset()
        if hasattr(self.navigation, "reset"):
            self.navigation.reset()  # type: ignore[attr-defined]
        for policy in self.policies.values():
            policy.reset()
        self.time_s = 0.0
        self._round_over = False
        self._winner = None
        self._draw = False
        self._started = False
        self._visible_pairs.clear()
        self._selected_targets.clear()
        self._reached_agents.clear()
        for agent_id, pose in assignments.items():
            agent = self.agents[agent_id]
            agent.reset(pose)
            self._set_agent_alive(agent, True)
            self.logger.log(0.0, "SPAWN", agent_id=agent_id, x=pose.x, y=pose.y, yaw=pose.yaw)

    def start_round(self) -> None:
        if self._round_over:
            raise RuntimeError("Reset before starting a completed round")
        self._started = True
        self.logger.log(self.time_s, "ROUND_START")
        if self.intel.update(self.time_s, self.agents):
            self._log_intel_update()

    def step(self, dt: float) -> None:
        if not self._started:
            raise RuntimeError("start_round() must be called before step()")
        if self._round_over:
            return
        if dt <= 0.0:
            raise ValueError("dt must be positive")
        self.time_s += dt
        if self.intel.update(self.time_s, self.agents):
            self._log_intel_update()

        pending_fire: list[str] = []
        for agent_id, agent in self.agents.items():
            if not self.health.is_alive(agent_id):
                agent.stop()
                continue
            results = self.visibility.observe_all(agent, list(self.agents.values()))
            self._log_visibility_transitions(agent_id, results)
            # Intel positions remain immutable between five-second snapshots.
            # A death is a public battle event, so dead IDs can be removed
            # immediately without leaking continuously updated positions.
            intel = {
                target_id: record
                for target_id, record in self.intel.get_snapshot_for(agent_id).items()
                if self.health.is_alive(target_id)
            }
            observation = BattleObservation(
                AgentState(agent_id, agent.get_pose(), self.health.get_health(agent_id), True, agent.last_velocity_command),
                intel,
                results,
            )
            action = self.policies[agent_id].act(observation)
            selected_target = getattr(self.policies[agent_id], "target_id", None)
            if self._selected_targets.get(agent_id) != selected_target:
                self._selected_targets[agent_id] = selected_target
                self.logger.log(
                    self.time_s,
                    "TARGET_SELECTED",
                    agent_id=agent_id,
                    target_id=selected_target,
                )
            command = action.velocity_override
            if action.navigation_target_xy is not None:
                old_goal = getattr(self.navigation, "get_goal", lambda _: None)(agent_id)
                if old_goal != action.navigation_target_xy:
                    self.navigation.set_goal(agent_id, action.navigation_target_xy)
                    self.logger.log(self.time_s, "NAV_GOAL_SET", agent_id=agent_id, target_xy=action.navigation_target_xy)
                if self.navigation.goal_reached(agent_id):
                    command = VelocityCommand(0.0, 0.0, self.config.scan_yaw_rate)
                elif command is None:
                    command = self.navigation.compute_command(agent, dt)
            if command is None:
                command = VelocityCommand()
            agent.set_velocity_command(command)
            if action.fire:
                pending_fire.append(agent_id)

        for agent in self.agents.values():
            agent.update(dt)
            agent_id = agent.agent_id
            if self.navigation.has_goal(agent_id):
                self.navigation.compute_command(agent, dt)
                reached = self.navigation.goal_reached(agent_id)
                if reached and agent_id not in self._reached_agents:
                    self._reached_agents.add(agent_id)
                    self.logger.log(self.time_s, "NAV_GOAL_REACHED", agent_id=agent_id)
                elif not reached:
                    self._reached_agents.discard(agent_id)

        for shooter_id in pending_fire:
            self._process_fire(shooter_id)
        self._evaluate_round()

    def is_round_over(self) -> bool:
        return self._round_over

    def get_alive_agents(self) -> list[str]:
        return [agent_id for agent_id in self.agents if self.health.is_alive(agent_id)]

    def get_winner(self) -> str | None:
        return self._winner

    def get_match_state(self) -> dict:
        return {
            "time_s": self.time_s,
            "round_over": self._round_over,
            "winner": self._winner,
            "draw": self._draw,
            "max_health": self.config.max_health,
            "agents": {
                agent_id: {
                    "pose": asdict(agent.get_pose()),
                    "health": self.health.get_health(agent_id),
                    "alive": self.health.is_alive(agent_id),
                    "last_velocity_command": asdict(agent.last_velocity_command),
                }
                for agent_id, agent in self.agents.items()
            },
        }

    def apply_damage(self, target_id: str, amount: float, source_id: str | None = None) -> float:
        was_alive = self.health.is_alive(target_id)
        health = self.health.apply_damage(target_id, amount, source_id)
        self.logger.log(self.time_s, "DAMAGE", agent_id=target_id, target_id=source_id, amount=amount, health=health)
        if was_alive and not self.health.is_alive(target_id):
            self._set_agent_alive(self.agents[target_id], False)
            self.logger.log(self.time_s, "DEATH", agent_id=target_id, target_id=source_id)
        return health

    def _process_fire(self, shooter_id: str) -> None:
        result = self.weapon.fire(self.agents[shooter_id], self.agents, self.time_s)
        if not result.fired:
            return
        self.logger.log(self.time_s, "SHOT_FIRED", agent_id=shooter_id,
                        hit_object_path=result.hit_object_path, distance_m=result.distance_m)
        if result.hit and result.hit_agent_id is not None:
            self.logger.log(self.time_s, "SHOT_HIT", agent_id=shooter_id,
                            target_id=result.hit_agent_id, damage=result.damage, distance_m=result.distance_m)
            self.apply_damage(result.hit_agent_id, result.damage, shooter_id)

    def _evaluate_round(self) -> None:
        alive = self.get_alive_agents()
        if len(alive) <= 1:
            self._finish_round(alive[0] if alive else None, draw=not alive)
        elif self.time_s >= self.config.round_time_limit_s:
            self._finish_round(None, draw=True)

    def _finish_round(self, winner: str | None, draw: bool) -> None:
        self._round_over, self._winner, self._draw = True, winner, draw
        for agent in self.agents.values():
            agent.stop()
        self.logger.log(self.time_s, "ROUND_END", winner=winner, draw=draw)
        if winner is not None:
            self.logger.log(self.time_s, "WINNER", agent_id=winner)

    def _log_intel_update(self) -> None:
        snapshots = {
            requester: {target: asdict(record) for target, record in self.intel.get_snapshot_for(requester).items()}
            for requester in self.agents
        }
        self.logger.log(self.time_s, "INTEL_UPDATE", snapshots=snapshots)

    def _log_visibility_transitions(self, observer_id: str, results) -> None:
        now = {(observer_id, result.target_id) for result in results if result.visible}
        previous = {pair for pair in self._visible_pairs if pair[0] == observer_id}
        result_by_target = {result.target_id: result for result in results}
        for pair in sorted(now - previous):
            result = result_by_target[pair[1]]
            self.logger.log(self.time_s, "TARGET_VISIBLE", agent_id=pair[0], target_id=pair[1],
                            distance_m=result.distance_m, yaw_error_rad=result.yaw_error_rad)
        for pair in sorted(previous - now):
            self.logger.log(self.time_s, "TARGET_LOST", agent_id=pair[0], target_id=pair[1])
        self._visible_pairs.difference_update(previous)
        self._visible_pairs.update(now)

    @staticmethod
    def _set_agent_alive(agent: AgentInterface, alive: bool) -> None:
        setter = getattr(agent, "set_alive", None)
        if setter is not None:
            setter(alive)
