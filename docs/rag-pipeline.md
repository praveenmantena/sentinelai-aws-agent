# RAG Pipeline

SentinelAI AWS Agent uses Retrieval Augmented Generation to ground incident diagnosis in operational evidence and runbook content.

## Sequence

1. Accept a CloudWatch alarm or external incident request.
2. Extract the incident title, severity, description, and log source.
3. Retrieve recent CloudWatch log events.
4. Query Bedrock Knowledge Base for relevant runbooks and troubleshooting guides.
5. Merge logs and retrieved documents into a Bedrock reasoning prompt.
6. Generate a diagnosis, root-cause explanation, confidence score, and remediation plan.
7. Persist the final result to DynamoDB for future context.

## Why this matters

- Logs provide near-real-time evidence.
- Retrieved runbooks provide grounded operational guidance.
- Model reasoning synthesizes evidence into a usable operator response.
- Stored incident history enables continuous improvement of future investigations.
