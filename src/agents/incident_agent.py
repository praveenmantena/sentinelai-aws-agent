from __future__ import annotations

import time
from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext
from src.telemetry import log_event


class IncidentDetectionAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__("incident-detection-agent")

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        summary = f"Incident {incident.incident_id} received from {incident.source} with severity {incident.severity}."
        details = {
            "alarm_name": incident.alarm_name,
            "resource_arn": incident.resource_arn,
            "description": incident.description,
        }
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, summary=summary)
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details=details,
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
