from __future__ import annotations

from typing import Any

from src.models import AgentObservation, IncidentContext
from src.orchestration.agent_graph import AgentGraph


class OrchestratorAgent:
    def __init__(self, agent_graph: AgentGraph) -> None:
        self.agent_graph = agent_graph

    def execute(self, incident: IncidentContext, initial_state: dict[str, Any] | None = None) -> tuple[list[AgentObservation], dict[str, Any]]:
        return self.agent_graph.run(incident=incident, initial_state=initial_state or {})
