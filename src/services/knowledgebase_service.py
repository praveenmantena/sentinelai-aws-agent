from __future__ import annotations

from typing import Any

try:
    import boto3
except Exception:
    boto3 = None

from src.config import CONFIG
from src.telemetry import log_event


class KnowledgeBaseService:
    def __init__(self) -> None:
        self.client = boto3.client("bedrock-agent-runtime", region_name=CONFIG.aws_region) if boto3 else None

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        log_event("knowledgebase.retrieve", query=query, knowledge_base_id=CONFIG.knowledge_base_id)
        if not CONFIG.knowledge_base_id or not self.client:
            return [
                {
                    "title": "AWS Lambda and Aurora connection management",
                    "uri": "s3://knowledge-base/runbooks/lambda-aurora-connections.md",
                    "excerpt": "Use RDS Proxy or tune pool size when Lambda concurrency increases suddenly.",
                    "score": 0.94,
                },
                {
                    "title": "API Gateway 5xx troubleshooting",
                    "uri": "s3://knowledge-base/runbooks/api-gateway-5xx.md",
                    "excerpt": "Correlate request spikes, downstream latency, and recent deployments before scaling blindly.",
                    "score": 0.87,
                },
            ]

        try:
            response = self.client.retrieve(
                knowledgeBaseId=CONFIG.knowledge_base_id,
                retrievalQuery={"text": query},
                retrievalConfiguration={
                    "vectorSearchConfiguration": {"numberOfResults": CONFIG.max_documents}
                },
            )
            results: list[dict[str, Any]] = []
            for item in response.get("retrievalResults", []):
                results.append(
                    {
                        "title": item.get("location", {}).get("s3Location", {}).get("uri", "document"),
                        "uri": item.get("location", {}).get("s3Location", {}).get("uri", ""),
                        "excerpt": item.get("content", {}).get("text", ""),
                        "score": item.get("score", 0.0),
                    }
                )
            return results
        except Exception as error:
            log_event("knowledgebase.retrieve.fallback", reason=str(error))
            return [
                {
                    "title": "AWS Lambda and Aurora connection management",
                    "uri": "s3://knowledge-base/runbooks/lambda-aurora-connections.md",
                    "excerpt": "Use RDS Proxy or tune pool size when Lambda concurrency increases suddenly.",
                    "score": 0.94,
                },
                {
                    "title": "API Gateway 5xx troubleshooting",
                    "uri": "s3://knowledge-base/runbooks/api-gateway-5xx.md",
                    "excerpt": "Correlate request spikes, downstream latency, and recent deployments before scaling blindly.",
                    "score": 0.87,
                },
            ]
