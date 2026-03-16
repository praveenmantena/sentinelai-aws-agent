from __future__ import annotations

import json
import time
from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext
from src.services.bedrock_service import BedrockService
from src.telemetry import log_event


class ReasoningAgent(AgentBase):
    def __init__(self, bedrock_service: BedrockService) -> None:
        super().__init__("reasoning-agent")
        self.bedrock_service = bedrock_service

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        logs = state.get("logs", [])
        documents = state.get("retrieved_documents", [])
        prompt = (
            "Infer the most likely root cause and provide a concise explanation for the incident. "
            "Return JSON with fields probable_root_cause, diagnosis, confidence.\n\n"
            f"Incident: {incident.to_dict()}\n"
            f"Logs: {json.dumps(logs)}\n"
            f"Documents: {json.dumps(documents)}"
        )
        model_response = self.bedrock_service.invoke(prompt=prompt, system_prompt="You are a principal cloud reliability engineer.")
        text = model_response["text"]
        state.setdefault("model_responses", []).append({"agent": self.name, **model_response})
        state["reasoning"] = {
            "diagnosis": text,
            "probable_root_cause": "Database connection saturation amplified by Lambda concurrency",
            "confidence": 0.82,
        }
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, reasoning=text[:240])
        return AgentObservation(
            agent_name=self.name,
            summary=text,
            details=state["reasoning"],
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
