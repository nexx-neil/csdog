from __future__ import annotations


from dogfight_v0.battle.types import BattleAction, BattleObservation, VelocityCommand
from dogfight_v0.config.battle_cfg import BattleConfig


class ScriptedBattlePolicy:
    def __init__(self, config: BattleConfig) -> None:
        self.config = config
        self._target_id: str | None = None

    def reset(self) -> None:
        self._target_id = None

    @property
    def target_id(self) -> str | None:
        """Currently selected enemy, exposed for logging and visualization only."""
        return self._target_id

    def act(self, observation: BattleObservation) -> BattleAction:
        visible = [item for item in observation.visible_targets if item.visible]
        if visible:
            target = min(visible, key=lambda item: (item.distance_m, item.target_id))
            self._target_id = target.target_id
            if abs(target.yaw_error_rad) > self.config.aim_tolerance_rad:
                yaw_rate = max(-self.config.max_yaw_rate, min(self.config.max_yaw_rate, 2.5 * target.yaw_error_rad))
                return BattleAction(velocity_override=VelocityCommand(0.0, 0.0, yaw_rate), fire=False)
            return BattleAction(velocity_override=VelocityCommand(), fire=True)
        candidates = [record for record in observation.intel.values() if record.alive]
        if candidates:
            selected = next((record for record in candidates if record.agent_id == self._target_id), None)
            if selected is None:
                pose = observation.self_state.pose
                selected = min(candidates, key=lambda r: ((r.x - pose.x) ** 2 + (r.y - pose.y) ** 2, r.agent_id))
                self._target_id = selected.agent_id
            return BattleAction(navigation_target_xy=(selected.x, selected.y))
        return BattleAction(velocity_override=VelocityCommand(0.0, 0.0, self.config.scan_yaw_rate))
