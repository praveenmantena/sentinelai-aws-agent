from __future__ import annotations

from src.agents.incident_agent import IncidentDetectionAgent
from src.agents.log_analysis_agent import LogAnalysisAgent
from src.agents.memory_agent import MemoryAgent
from src.agents.orchestrator_agent import OrchestratorAgent
from src.agents.reasoning_agent import ReasoningAgent
from src.agents.remediation_agent import RemediationAgent
from src.agents.retrieval_agent import KnowledgeRetrievalAgent
from src.orchestration.agent_graph import AgentGraph
from src.services.bedrock_service import BedrockService
from src.services.cloudwatch_service import CloudWatchService
from src.services.dynamodb_service import DynamoDBService
from src.services.knowledgebase_service import KnowledgeBaseService


def build_application() -> OrchestratorAgent:
    bedrock_service = BedrockService()
    cloudwatch_service = CloudWatchService()
    knowledgebase_service = KnowledgeBaseService()
    dynamodb_service = DynamoDBService()

    agents = [
        IncidentDetectionAgent(),
        MemoryAgent(dynamodb_service=dynamodb_service),
        LogAnalysisAgent(cloudwatch_service=cloudwatch_service, bedrock_service=bedrock_service),
        KnowledgeRetrievalAgent(knowledgebase_service=knowledgebase_service),
        ReasoningAgent(bedrock_service=bedrock_service),
        RemediationAgent(bedrock_service=bedrock_service),
    ]
    graph = AgentGraph(agents=agents, dynamodb_service=dynamodb_service)
    return OrchestratorAgent(agent_graph=graph)
