from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.api.handler import lambda_handler, process_incident


def assert_true(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    event_path = ROOT / "evaluation" / "api_request.json"
    event = json.loads(event_path.read_text(encoding="utf-8"))

    result = process_incident(event)

    required_top_level = [
        "incident",
        "diagnosis",
        "probable_root_cause",
        "confidence",
        "remediation_plan",
        "dependency_status",
    ]
    for key in required_top_level:
        assert_true(key in result, f"Missing key in result: {key}")

    dependency_status = result.get("dependency_status", {})
    for key in ["cloudwatch_logs", "bedrock_runtime", "bedrock_knowledge_base", "overall_mode"]:
        assert_true(key in dependency_status, f"Missing dependency status key: {key}")

    valid_response = lambda_handler({"body": json.dumps(event)}, context={})
    assert_true(valid_response.get("statusCode") == 200, "Expected lambda_handler to return 200 for valid payload")

    invalid_response = lambda_handler({"body": "{invalid-json"}, context={})
    assert_true(invalid_response.get("statusCode") == 400, "Expected lambda_handler to return 400 for invalid JSON")

    print("Smoke check passed: API shape, dependency status, and error handling are valid.")


if __name__ == "__main__":
    main()
