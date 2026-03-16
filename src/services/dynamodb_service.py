from __future__ import annotations

from decimal import Decimal
from typing import Any

try:
    import boto3
except Exception:
    boto3 = None

from src.config import CONFIG
from src.models import IncidentContext, InvestigationResult
from src.telemetry import log_event


class DynamoDBService:
    def __init__(self) -> None:
        resource = boto3.resource("dynamodb", region_name=CONFIG.aws_region) if boto3 else None
        self.table = resource.Table(CONFIG.incidents_table) if resource else None
        self._memory: dict[str, dict[str, Any]] = {}

    def get_incident_history(self, incident: IncidentContext) -> dict[str, Any] | None:
        log_event("memory.fetch", incident_id=incident.incident_id)
        if not self.table:
            return self._memory.get(incident.incident_id)
        try:
            response = self.table.get_item(Key={"incident_id": incident.incident_id})
            return response.get("Item")
        except Exception as error:
            log_event("memory.fetch.fallback", incident_id=incident.incident_id, reason=str(error))
            return self._memory.get(incident.incident_id)

    def save_result(self, result: InvestigationResult) -> None:
        payload = result.to_dict()
        log_event("memory.save", incident_id=result.incident.incident_id, confidence=result.confidence)
        if not self.table:
            self._memory[result.incident.incident_id] = payload
            return
        try:
            self.table.put_item(Item=self._to_dynamodb_compatible(payload))
        except Exception as error:
            log_event("memory.save.fallback", incident_id=result.incident.incident_id, reason=str(error))
            self._memory[result.incident.incident_id] = payload

    def _to_dynamodb_compatible(self, value: Any) -> Any:
        if isinstance(value, float):
            return Decimal(str(value))
        if isinstance(value, list):
            return [self._to_dynamodb_compatible(item) for item in value]
        if isinstance(value, dict):
            return {key: self._to_dynamodb_compatible(item) for key, item in value.items()}
        return value
