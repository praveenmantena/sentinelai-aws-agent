from __future__ import annotations

import time
from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext
from src.services.dynamodb_service import DynamoDBService
from src.telemetry import log_event


class MemoryAgent(AgentBase):
    def __init__(self, dynamodb_service: DynamoDBService) -> None:
        super().__init__("memory-agent")
        self.dynamodb_service = dynamodb_service

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        history = self.dynamodb_service.get_incident_history(incident)
        state["incident_history"] = history or {}
        summary = "Loaded prior incident history from memory." if history else "No prior incident history found; starting a new incident record."
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, has_history=bool(history))
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details={"history": history or {}},
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
