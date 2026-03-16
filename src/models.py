from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any
import uuid


@dataclass
class IncidentContext:
    incident_id: str
    source: str
    severity: str
    title: str
    description: str
    resource_arn: str | None = None
    alarm_name: str | None = None
    log_group: str | None = None
    query: str | None = None
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_event(cls, event: dict[str, Any]) -> "IncidentContext":
        detail = event.get("detail", {})
        alarm_name = detail.get("alarmName") or detail.get("alarm_name")
        description = detail.get("state", {}).get("reason") or detail.get("description") or "Operational incident detected"
        severity = detail.get("severity") or detail.get("state", {}).get("value") or "UNKNOWN"
        resource_arn = detail.get("alarmArn") or detail.get("resourceArn")
        log_group = detail.get("logGroupName") or event.get("log_group")
        return cls(
            incident_id=detail.get("incidentId") or str(uuid.uuid4()),
            source=event.get("source", "manual"),
            severity=str(severity),
            title=detail.get("title") or alarm_name or event.get("title") or "Cloud incident",
            description=description,
            resource_arn=resource_arn,
            alarm_name=alarm_name,
            log_group=log_group,
            query=event.get("query") or detail.get("query"),
            metadata=detail,
        )

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AgentObservation:
    agent_name: str
    summary: str
    details: dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InvestigationResult:
    incident: IncidentContext
    diagnosis: str
    probable_root_cause: str
    remediation_plan: list[str]
    confidence: float
    retrieved_documents: list[dict[str, Any]] = field(default_factory=list)
    agent_trace: list[AgentObservation] = field(default_factory=list)
    model_responses: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["incident"] = self.incident.to_dict()
        data["agent_trace"] = [item.to_dict() for item in self.agent_trace]
        return data
