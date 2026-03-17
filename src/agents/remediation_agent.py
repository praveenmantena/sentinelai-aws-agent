from __future__ import annotations

import json
import time
from typing import Any

from src.agent_base import AgentBase
from src.config import CONFIG
from src.models import AgentObservation, IncidentContext
from src.services.bedrock_service import BedrockService
from src.telemetry import log_event


_FALLBACK_STEPS = [
    "Throttle non-critical Lambda concurrency or enable reserved concurrency to reduce connection spikes.",
    "Switch the impacted workload to RDS Proxy or reduce connection pool size in application settings.",
    "Review the most recent deployment and roll back if the latency regression aligns with the alarm timestamp.",
    "Create a follow-up action item to add a CloudWatch dashboard tracking DB connections and API latency together.",
]


class RemediationAgent(AgentBase):
    def __init__(self, bedrock_service: BedrockService) -> None:
        super().__init__("remediation-agent")
        self.bedrock_service = bedrock_service

    def _parse_steps(self, text: str) -> list[str] | None:
        try:
            candidate = json.loads(text)
            if isinstance(candidate, list) and all(isinstance(s, str) for s in candidate):
                return candidate
        except json.JSONDecodeError:
            pass
        start = text.find("[")
        end = text.rfind("]")
        if start != -1 and end != -1 and end > start:
            try:
                candidate = json.loads(text[start : end + 1])
                if isinstance(candidate, list) and all(isinstance(s, str) for s in candidate):
                    return candidate
            except json.JSONDecodeError:
                pass
        return None

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        reasoning = state.get("reasoning", {})
        root_cause = reasoning.get("probable_root_cause", "")
        diagnosis = reasoning.get("diagnosis", "")

        prompt = (
            "You are a principal SRE. Based on the incident details below, return a JSON array "
            "of 4 to 6 concise, actionable remediation steps an on-call engineer should take right now. "
            "Return only the JSON array, no other text.\n\n"
            f"Incident title: {incident.title}\n"
            f"Incident description: {incident.description}\n"
            f"Probable root cause: {root_cause}\n"
            f"Diagnosis: {diagnosis}"
        )
        model_response = self.bedrock_service.invoke(
            prompt=prompt,
            system_prompt="You are a principal site reliability engineer. Return only valid JSON.",
            temperature=0.2,
        )
        state.setdefault("model_responses", []).append({"agent": self.name, **model_response})
        state.setdefault("dependency_status", {})["bedrock_remediation"] = model_response.get("mode", "unknown")

        remediation_steps = self._parse_steps(model_response["text"]) or _FALLBACK_STEPS

        if CONFIG.enable_auto_remediation:
            remediation_steps = list(remediation_steps) + [
                "Automatic remediation is enabled; invoke the pre-approved rollback runbook after operator approval."
            ]

        state["remediation_plan"] = remediation_steps
        summary = "Prepared a remediation plan with immediate mitigation and long-term prevention steps."
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, remediation_suggestions=remediation_steps)
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details={"remediation_plan": remediation_steps, "reasoning": reasoning},
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
