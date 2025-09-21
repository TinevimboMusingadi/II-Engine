"""
BigQuery AI Hackathon: Intelligent Insurance Engine
Agent Core Module - State-of-the-Art Agent Architecture
"""

from .communication_protocol import (
    CommunicationProtocol,
    InMemoryCommunicationProtocol,
    Message,
    MessageType,
    AgentCapabilities
)

from .tools import (
    BigQueryAIToolImplementations,
    ToolResult,
    ToolSchema,
    get_insurance_tool_descriptions
)

from .router import (
    LLMRouter,
    ApplicationState,
    SimplifiedRouter,
    IntelligentLLMRouter
)

from .agent import (
    InsuranceOrchestratorAgent,
    test_orchestrator_agent
)

__version__ = "1.0.0"

__all__ = [
    # Communication Protocol
    "CommunicationProtocol",
    "InMemoryCommunicationProtocol", 
    "Message",
    "MessageType",
    "AgentCapabilities",
    
    # Tools
    "BigQueryAIToolImplementations",
    "ToolResult",
    "ToolSchema",
    "get_insurance_tool_descriptions",
    
    # Router
    "LLMRouter", 
    "ApplicationState",
    "SimplifiedRouter",
    "IntelligentLLMRouter",
    
    # Agent
    "InsuranceOrchestratorAgent",
    "test_orchestrator_agent"
]
