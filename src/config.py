from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    bedrock_model_id: str = os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0")
    knowledge_base_id: str = os.getenv("BEDROCK_KNOWLEDGE_BASE_ID", "")
    knowledge_bucket: str = os.getenv("KNOWLEDGE_BUCKET", "")
    incidents_table: str = os.getenv("INCIDENTS_TABLE", "sentinelai-aws-agent-incidents")
    log_group_name: str = os.getenv("LOG_GROUP_NAME", "/aws/lambda/sentinelai-aws-agent")
    api_stage: str = os.getenv("API_STAGE", "prod")
    environment: str = os.getenv("APP_ENV", "local")
    enable_auto_remediation: bool = os.getenv("ENABLE_AUTO_REMEDIATION", "false").lower() == "true"
    max_log_events: int = int(os.getenv("MAX_LOG_EVENTS", "50"))
    max_documents: int = int(os.getenv("MAX_DOCUMENTS", "5"))


CONFIG = AppConfig()
