from __future__ import annotations

import time
from typing import Any

from src.agent_base import AgentBase
from src.config import CONFIG
from src.models import AgentObservation, IncidentContext
from src.telemetry import log_event


class RemediationAgent(AgentBase):
    def __init__(self) -> None:
        super().__init__("remediation-agent")

    def run(self, incident: IncidentContext, state: dict[str, Any]) -> AgentObservation:
        started = time.perf_counter()
        reasoning = state.get("reasoning", {})
        remediation_steps = [
            "Throttle non-critical Lambda concurrency or enable reserved concurrency to reduce connection spikes.",
            "Switch the impacted workload to RDS Proxy or reduce connection pool size in application settings.",
            "Review the most recent deployment and roll back if the latency regression aligns with the alarm timestamp.",
            "Create a follow-up action item to add a CloudWatch dashboard tracking DB connections and API latency together.",
        ]
        if CONFIG.enable_auto_remediation:
            remediation_steps.append("Automatic remediation is enabled; invoke the pre-approved rollback runbook after operator approval.")
        state["remediation_plan"] = remediation_steps
        summary = "Prepared a remediation plan with immediate mitigation and long-term prevention steps."
        log_event("agent.decision", agent=self.name, incident_id=incident.incident_id, remediation_suggestions=remediation_steps)
        return AgentObservation(
            agent_name=self.name,
            summary=summary,
            details={"remediation_plan": remediation_steps, "reasoning": reasoning},
            latency_ms=round((time.perf_counter() - started) * 1000, 2),
        )
