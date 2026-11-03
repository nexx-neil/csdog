from __future__ import annotations


import json
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4
from dogfight.common.paths import LOGS

from dogfight_v0.battle.types import BattleEvent


class BattleLogger:
    def __init__(self, root: str | Path = LOGS / "battle", run_name: str | None = None, echo: bool = True) -> None:
        stamp = run_name or datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
        self.log_dir = Path(root).resolve() / stamp
        self.log_dir.mkdir(parents=True, exist_ok=False)
        self.events_path = self.log_dir / "events.jsonl"
        self.echo = echo
        self.events: list[BattleEvent] = []

    def log(self, timestamp_s: float, event_type: str, agent_id: str | None = None,
            target_id: str | None = None, **data: Any) -> BattleEvent:
        event = BattleEvent(timestamp_s, event_type, agent_id, target_id, data)
        self.events.append(event)
        with self.events_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(event.to_dict(), ensure_ascii=False, sort_keys=True) + "\n")
        if self.echo:
            fields = [f"[V0] {event_type}"]
            if agent_id is not None:
                fields.append(f"agent={agent_id}")
            if target_id is not None:
                fields.append(f"target={target_id}")
            fields.extend(f"{key}={value}" for key, value in data.items())
            print(" ".join(fields), flush=True)
        return event

