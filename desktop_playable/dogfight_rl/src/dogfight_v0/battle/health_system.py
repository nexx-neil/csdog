
class HealthSystem:
    def __init__(self, max_health: float) -> None:
        if max_health <= 0.0:
            raise ValueError("max_health must be positive")
        self.max_health = float(max_health)
        self._health: dict[str, float] = {}

    def reset(self, agent_ids: list[str]) -> None:
        self._health = {agent_id: self.max_health for agent_id in agent_ids}

    def get_health(self, agent_id: str) -> float:
        return self._health[agent_id]

    def is_alive(self, agent_id: str) -> bool:
        return self.get_health(agent_id) > 0.0

    def apply_damage(self, target_id: str, amount: float, source_id: str | None = None) -> float:
        del source_id
        if amount < 0.0:
            raise ValueError("damage cannot be negative")
        self._health[target_id] = max(0.0, self._health[target_id] - amount)
        return self._health[target_id]

    def kill(self, agent_id: str) -> None:
        self._health[agent_id] = 0.0

