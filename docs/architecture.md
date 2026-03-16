# Architecture

SentinelAI AWS Agent uses an event-driven incident response architecture on AWS.

## Flow

1. A CloudWatch alarm changes state.
2. EventBridge routes the event to the Lambda AI Agent Service.
3. The Lambda runtime invokes a Strands-compatible multi-agent workflow.
4. The workflow loads incident history from DynamoDB, fetches logs from CloudWatch, retrieves runbooks from Bedrock Knowledge Base, reasons over the combined context with Bedrock, and emits remediation guidance.
5. API Gateway exposes the same investigation path for ad hoc incident analysis.

## Production considerations

- Bedrock provides model inference for log analysis and reasoning.
- Bedrock Knowledge Base adds retrieval grounded in runbooks stored in S3 and indexed into OpenSearch Serverless.
- DynamoDB stores incident memory and supports future replay, learning loops, and trend analysis.
- CloudWatch logs carry structured telemetry including agent decisions, latency metrics, retrieved documents, and model outputs.
- IAM roles are scoped to Bedrock invocation, knowledge retrieval, S3 read, DynamoDB access, and Lambda logging.

## Diagrams

- Overall system: ../diagrams/system_architecture.png
- Agent workflow: ../diagrams/agent_architecture.png
- RAG flow: ../diagrams/rag_flow.png
- AWS service integration: ../diagrams/aws_service_integration.png
