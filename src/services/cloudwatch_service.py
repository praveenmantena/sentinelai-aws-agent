from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

try:
    import boto3
except Exception:
    boto3 = None

from src.config import CONFIG
from src.models import IncidentContext
from src.telemetry import log_event


class CloudWatchService:
    def __init__(self) -> None:
        self.logs_client = boto3.client("logs", region_name=CONFIG.aws_region) if boto3 else None

    def get_incident_logs(self, incident: IncidentContext) -> list[dict[str, Any]]:
        log_group = incident.log_group or CONFIG.log_group_name
        log_event("cloudwatch.logs.requested", incident_id=incident.incident_id, log_group=log_group)
        if not self.logs_client:
            return [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "ERROR Connection pool exhausted for aurora-prod cluster",
                    "mode": "fallback",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "WARN API latency p95 breached threshold after deployment 2026.03.16.2",
                    "mode": "fallback",
                },
            ]

        try:
            end_time = int(datetime.now(timezone.utc).timestamp() * 1000)
            start_time = int((datetime.now(timezone.utc) - timedelta(minutes=20)).timestamp() * 1000)
            response = self.logs_client.filter_log_events(
                logGroupName=log_group,
                startTime=start_time,
                endTime=end_time,
                limit=CONFIG.max_log_events,
            )
            log_event("cloudwatch.logs.mode", incident_id=incident.incident_id, mode="live")
            return [
                {"timestamp": item.get("timestamp"), "message": item.get("message", "")}
                for item in response.get("events", [])
            ]
        except Exception as error:
            log_event("cloudwatch.logs.fallback", incident_id=incident.incident_id, reason=str(error))
            return [
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "ERROR Connection pool exhausted for aurora-prod cluster",
                    "mode": "fallback",
                },
                {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": "WARN API latency p95 breached threshold after deployment 2026.03.16.2",
                    "mode": "fallback",
                },
            ]
