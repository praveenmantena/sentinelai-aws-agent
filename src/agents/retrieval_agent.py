from __future__ import annotations

import time
from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext
from src.services.knowledgebase_service import KnowledgeBaseService
from src.telemetry import log_event


class KnowledgeRetrievalAgent(AgentBase):
    def __init__(self, knowledgebase_service: KnowledgeBaseService) -> None:
        super().__init__("knowledge-retrieval-agent")
        self.knowledgebase_service = knowledgebase_service

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        retrieval_query = incident.query or f"{incident.title} {incident.description}"
        documents = self.knowledgebase_service.retrieve(retrieval_query)
        state["retrieved_documents"] = documents
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, documents=len(documents))
        summary = f"Retrieved {len(documents)} relevant knowledge documents."
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details={"documents": documents},
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
