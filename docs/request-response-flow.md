# Request to Response Flow

```mermaid
flowchart TD
    A[CloudWatch Alarm or API Request] --> B[API Gateway / EventBridge]
    B --> C[Lambda Handler: src/api/handler.py]
    C --> D[Build Incident Context]
    D --> E[Orchestrator Agent]

    E --> F1[Incident Detection Agent]
    E --> F2[Memory Agent]
    E --> F3[Log Analysis Agent]
    E --> F4[Knowledge Retrieval Agent]
    E --> F5[Reasoning Agent]
    E --> F6[Remediation Agent]

    F2 --> G1[DynamoDB: fetch history]
    F3 --> G2[CloudWatch Logs]
    F3 --> G3[Bedrock Runtime]
    F4 --> G4[Bedrock Knowledge Base]
    F5 --> G3

    F1 --> H[Shared Investigation State]
    F2 --> H
    F3 --> H
    F4 --> H
    F5 --> H
    F6 --> H

    H --> I[Finalize Investigation Result]
    I --> J[DynamoDB: save result]
    I --> K[Structured Logs + Metrics]
    I --> L[JSON Response]

    L --> M[Web UI / Consumer]
```

## Notes

- Entry can be event-driven (CloudWatch -> EventBridge) or request-driven (API Gateway).
- The orchestrator executes agents in sequence and accumulates explainable trace data.
- Response includes diagnosis, probable root cause, remediation plan, confidence, and agent trace.
