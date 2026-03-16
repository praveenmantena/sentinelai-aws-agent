from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any


class ApprovalStore:
    def __init__(self, store_path: str = "data/approvals.json") -> None:
        self.path = Path(store_path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}

    def _save(self, payload: dict[str, Any]) -> None:
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def get_incident_approvals(self, incident_id: str) -> dict[str, Any]:
        data = self._load()
        return data.get(incident_id, {})

    def save_incident_approvals(
        self,
        incident_id: str,
        title: str,
        approvals: list[dict[str, Any]],
        approved_by: str,
    ) -> None:
        data = self._load()
        data[incident_id] = {
            "incident_id": incident_id,
            "incident_title": title,
            "approved_by": approved_by,
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "approvals": approvals,
        }
        self._save(data)

    def all(self) -> dict[str, Any]:
        return self._load()
