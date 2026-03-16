from __future__ import annotations

import time
from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext
from src.services.bedrock_service import BedrockService
from src.services.cloudwatch_service import CloudWatchService
from src.telemetry import log_event


class LogAnalysisAgent(AgentBase):
    def __init__(self, cloudwatch_service: CloudWatchService, bedrock_service: BedrockService) -> None:
        super().__init__("log-analysis-agent")
        self.cloudwatch_service = cloudwatch_service
        self.bedrock_service = bedrock_service

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        logs = self.cloudwatch_service.get_incident_logs(incident)
        prompt = (
            "Analyze the following operational log lines and summarize the likely failure mode.\n\n"
            f"Incident title: {incident.title}\n"
            f"Incident description: {incident.description}\n"
            f"Logs: {logs}"
        )
        model_response = self.bedrock_service.invoke(prompt=prompt, system_prompt="Summarize logs for an SRE incident responder.")
        state["logs"] = logs
        state.setdefault("model_responses", []).append({"agent": self.name, **model_response})
        summary = model_response["text"]
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, log_count=len(logs))
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details={"logs": logs},
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
