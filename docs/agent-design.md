# Agent Design

## Orchestrator Agent

Coordinates execution order, shares state between agents, and finalizes the investigation result.

## Incident Detection Agent

Normalizes EventBridge or API payloads into a consistent incident context and records basic metadata.

## Log Analysis Agent

Pulls recent CloudWatch logs, sends the incident plus raw evidence to Bedrock, and returns a concise summary of failure signals.

## Knowledge Retrieval Agent

Builds a retrieval query from the incident title and description, then fetches relevant runbooks from Bedrock Knowledge Base.

## Reasoning Agent

Combines incident context, logs, and retrieved documents into a root-cause explanation and confidence score.

## Remediation Agent

Outputs immediate mitigation steps plus follow-up hardening recommendations. It can be extended to trigger runbooks or SSM Automation documents.

## Memory Agent

Loads prior investigation context from DynamoDB and persists the final investigation for historical reasoning.

## Design principles

- Each agent has one clear responsibility.
- Shared mutable state is limited to the orchestration layer.
- Observations are captured per agent for explainability.
- AWS service calls stay inside service adapters to simplify testing.
