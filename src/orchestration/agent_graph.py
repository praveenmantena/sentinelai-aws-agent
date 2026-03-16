from __future__ import annotations

from typing import Any

from src.agent_base import AgentBase
from src.models import AgentObservation, IncidentContext, InvestigationResult
from src.strands_runtime import StrandsWorkflow
from src.services.dynamodb_service import DynamoDBService
from src.telemetry import log_event, metric, trace_span


class AgentGraph:
    def __init__(self, agents: list[AgentBase], dynamodb_service: DynamoDBService) -> None:
        self.agents = agents
        self.dynamodb_service = dynamodb_service

    def run(self, incident: IncidentContext, initial_state: dict[str, Any]) -> tuple[list[AgentObservation], dict[str, Any]]:
        observations: list[AgentObservation] = []
        state = dict(initial_state)
        with trace_span("agent-graph", incident_id=incident.incident_id):
            workflow = StrandsWorkflow()
            for agent in self.agents:
                workflow.add_task(
                    name=agent.name,
                    run=lambda workflow_state, current_agent=agent: current_agent.execute(
                        incident=incident,
                        state=workflow_state,
                    ),
                )

            state = workflow.execute(**state)
            for agent in self.agents:
                task_result = state.get(agent.name)
                if isinstance(task_result, AgentObservation):
                    observations.append(task_result)
                    state[agent.name] = task_result.to_dict()
            metric("InvestigationCompleted", 1, unit="Count", severity=incident.severity)
            log_event("investigation.completed", incident_id=incident.incident_id, observations=len(observations))
        return observations, state

    def finalize(self, incident: IncidentContext, observations: list[AgentObservation], state: dict[str, Any]) -> InvestigationResult:
        reasoning = state.get("reasoning", {})
        result = InvestigationResult(
            incident=incident,
            diagnosis=reasoning.get("diagnosis", observations[-1].summary if observations else "No diagnosis generated."),
            probable_root_cause=reasoning.get("probable_root_cause", "Insufficient evidence"),
            remediation_plan=state.get("remediation_plan", []),
            confidence=float(reasoning.get("confidence", 0.5)),
            retrieved_documents=state.get("retrieved_documents", []),
            agent_trace=observations,
            model_responses=state.get("model_responses", []),
        )
        self.dynamodb_service.save_result(result)
        return result
