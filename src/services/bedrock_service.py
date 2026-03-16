from __future__ import annotations

import json
from typing import Any

try:
    import boto3
except Exception:
    boto3 = None

from src.config import CONFIG
from src.telemetry import log_event


class BedrockService:
    def __init__(self) -> None:
        self.client = boto3.client("bedrock-runtime", region_name=CONFIG.aws_region) if boto3 else None

    def invoke(self, prompt: str, system_prompt: str | None = None, temperature: float = 0.1) -> dict[str, Any]:
        log_event("bedrock.invoke", model_id=CONFIG.bedrock_model_id, prompt_preview=prompt[:300])
        if not self.client:
            text = (
                "Mock Bedrock response: elevated 5xx rates correlate with downstream latency spikes. "
                "Investigate database connection saturation and roll back the last configuration change if needed."
            )
            return {"text": text, "raw": {"mock": True}}

        try:
            body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 700,
                "temperature": temperature,
                "system": system_prompt or "You are an AWS incident response assistant.",
                "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
            }
            response = self.client.invoke_model(modelId=CONFIG.bedrock_model_id, body=json.dumps(body))
            payload = json.loads(response["body"].read())
            content = payload.get("content", [])
            text = "\n".join(item.get("text", "") for item in content if item.get("type") == "text")
            return {"text": text, "raw": payload}
        except Exception as error:
            log_event("bedrock.invoke.fallback", reason=str(error))
            text = (
                "Mock Bedrock response: elevated 5xx rates correlate with downstream latency spikes. "
                "Investigate database connection saturation and roll back the last configuration change if needed."
            )
            return {"text": text, "raw": {"mock": True, "reason": str(error)}}
