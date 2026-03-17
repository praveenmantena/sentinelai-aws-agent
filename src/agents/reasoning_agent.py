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

    def _extract_reasoning(self, text: str) -> dict[str, Any]:
        parsed: dict[str, Any] = {}
        try:
            candidate = json.loads(text)
            if isinstance(candidate, dict):
                parsed = candidate
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    candidate = json.loads(text[start : end + 1])
                    if isinstance(candidate, dict):
                        parsed = candidate
                except json.JSONDecodeError:
                    parsed = {}

        diagnosis = str(parsed.get("diagnosis") or text).strip()
        probable_root_cause = str(parsed.get("probable_root_cause") or "Insufficient evidence from current signals.").strip()

        try:
            confidence = float(parsed.get("confidence", 0.55))
        except (TypeError, ValueError):
            confidence = 0.55
        confidence = min(max(confidence, 0.0), 1.0)

        return {
            "diagnosis": diagnosis,
            "probable_root_cause": probable_root_cause,
            "confidence": confidence,
        }

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
        state["reasoning"] = self._extract_reasoning(text)
        state.setdefault("dependency_status", {})["bedrock_runtime"] = model_response.get("mode", "unknown")
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, reasoning=text[:240])
        return AgentObservation(
            agent_name=self.name,
            summary=state["reasoning"]["diagnosis"],
            details=state["reasoning"],
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
