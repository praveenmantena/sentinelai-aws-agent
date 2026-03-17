# Hackathon Judge Q&A Cheat Sheet

## 1) What real-world problem does this solve?

SentinelAI reduces incident triage time for AWS operations teams. During an alarm, engineers usually pivot between CloudWatch alarms, logs, and runbooks manually. This system consolidates that workflow and returns a structured diagnosis plus remediation guidance.

## 2) Where is GenAI actually used?

GenAI (Amazon Bedrock) is used in two places:

- Log summarization (`LogAnalysisAgent`)
- Root-cause reasoning with confidence (`ReasoningAgent`)

Everything else (event normalization, orchestration, persistence, approvals) is deterministic application logic.

## 3) How do you ensure the demo is trustworthy if dependencies fail?

The response includes `dependency_status` per dependency and `overall_mode` (`live` or `fallback`).
The UI surfaces execution mode explicitly, so fallback behavior is visible and not hidden.

## 4) Why this architecture?

The multi-agent architecture maps to incident-response responsibilities:

- Incident detection
- Memory lookup
- Log analysis
- Knowledge retrieval
- Reasoning
- Remediation planning

This keeps the flow explainable, modular, and easy to extend for future production hardening.

## 5) What AWS services are used and why?

- **Lambda** for event-driven execution
- **EventBridge + API Gateway** for event-driven and on-demand entry
- **CloudWatch Logs** for evidence retrieval
- **Bedrock + Bedrock KB** for GenAI reasoning and grounding
- **DynamoDB** for incident memory and result persistence
- **S3** for runbook knowledge source

## 6) What measurable impact do you expect?

Primary metric: MTTR reduction from faster triage and consistent remediation output.

## 7) What would you improve next after hackathon?

- Tighten IAM/CORS/network policies for production
- Add test coverage (unit + integration)
- Add stronger schema validation and typed state contracts
- Add richer observability dashboards and SLO metrics
