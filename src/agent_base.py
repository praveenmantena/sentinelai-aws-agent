from __future__ import annotations

from typing import Any

from src.models import AgentObservation, IncidentContext
from src.telemetry import metric, trace_span


class AgentExecutionError(RuntimeError):
    pass


class AgentBase:
    def __init__(self, name: str) -> None:
        self.name = name

    def execute(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        with trace_span(self.name, incident_id=incident.incident_id):
            result = self.run(incident=incident, state=state)
            metric("AgentLatency", result.latency_ms, agent=self.name)
            return result

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        raise NotImplementedError
