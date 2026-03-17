from __future__ import annotations

import argparse
import json
from typing import Any

from src.app import build_application
from src.config import CONFIG
from src.models import IncidentContext
from src.telemetry import log_event


def _normalize_event(event: dict[str, Any]) -> dict[str, Any]:
    body = event.get("body")
    if body is not None:
        if isinstance(body, str):
            return json.loads(body)
        if isinstance(body, dict):
            return body
    return event


def _error_response(status_code: int, message: str, details: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "error": message,
        "details": details or {},
    }
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(payload, default=str),
    }


def process_incident(event: dict[str, Any]) -> dict[str, Any]:
    normalized_event = _normalize_event(event)
    incident = IncidentContext.from_event(normalized_event)
    orchestrator = build_application()
    observations, state = orchestrator.execute(incident=incident)
    result = orchestrator.agent_graph.finalize(incident=incident, observations=observations, state=state)
    return result.to_dict()


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    log_event("lambda.invoked", event=event)
    try:
        result = process_incident(event)
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps(result, default=str),
        }
    except json.JSONDecodeError as error:
        log_event("lambda.error", error_type="json_decode_error", message=str(error))
        details = {"reason": str(error)} if CONFIG.environment != "prod" else {}
        return _error_response(400, "Invalid JSON payload", details)
    except Exception as error:  # noqa: BLE001
        log_event("lambda.error", error_type="unhandled_exception", message=str(error))
        details = {"reason": str(error)} if CONFIG.environment != "prod" else {}
        return _error_response(500, "Investigation failed", details)


def _sample_event() -> dict[str, Any]:
    return {
        "source": "aws.cloudwatch",
        "detail-type": "CloudWatch Alarm State Change",
        "detail": {
            "alarmName": "HighApi5xxRate",
            "alarmArn": "arn:aws:cloudwatch:us-east-1:123456789012:alarm:HighApi5xxRate",
            "state": {"value": "CRITICAL", "reason": "5xx error rate exceeded 5% for 5 minutes"},
            "description": "API Gateway 5xx error alarm",
            "logGroupName": "/aws/lambda/sentinelai-aws-agent",
            "severity": "SEV2",
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Run SentinelAI AWS Agent locally")
    parser.add_argument("--event-file", help="Path to a JSON event file")
    args = parser.parse_args()

    event = _sample_event()
    if args.event_file:
        with open(args.event_file, "r", encoding="utf-8") as file_handle:
            event = json.load(file_handle)

    result = process_incident(event)
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    main()
