"""
BigQuery AI Hackathon: Intelligent Insurance Engine
Communication Protocol for Agent System
Novel State-of-the-Art Agent Architecture
"""

from typing import Dict, Any, Optional, TypedDict, Callable, Awaitable
from dataclasses import dataclass, field
import uuid
import asyncio
import json
from datetime import datetime, timezone
from enum import Enum
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class MessageType(str, Enum):
    """Standardized message types for insurance processing."""
    START_APPLICATION_PROCESSING = "start_application_processing"
    APPLICATION_RESULT = "application_result"
    TOOL_EXECUTION_REQUEST = "tool_execution_request"
    TOOL_EXECUTION_RESPONSE = "tool_execution_response"
    HUMAN_REVIEW_REQUIRED = "human_review_required"
    STATUS_UPDATE = "status_update"
    ERROR = "error"

class Message(TypedDict):
    """Standardized message format for agent communication with BigQuery AI context."""
    message_id: str
    sender: str
    receiver: str
    application_id: str  # Unique ID for each insurance application
    message_type: MessageType
    payload: Dict[str, Any]
    timestamp: str
    in_reply_to: Optional[str]
    bigquery_context: Optional[Dict[str, Any]]  # BigQuery-specific context

@dataclass
class AgentCapabilities:
    """Defines what an agent can do in the BigQuery AI ecosystem."""
    agent_id: str
    supported_message_types: list[MessageType]
    bigquery_datasets: list[str]
    ml_models: list[str]
    object_tables: list[str]

class CommunicationProtocol:
    """
    Advanced communication protocol for BigQuery AI agents.
    Handles message routing, state management, and BigQuery integration.
    """
    
    def __init__(self, project_id: str = "intelligent-insurance-engine"):
        self.project_id = project_id
        self.agents: Dict[str, Dict[str, Any]] = {}
        self.message_queues: Dict[str, asyncio.Queue] = {}
        self.active_applications: Dict[str, Dict[str, Any]] = {}
        self.message_history: Dict[str, list[Message]] = {}
        
    async def register_agent(self, agent_id: str, handler: Callable[[Message], Awaitable[None]], 
                           capabilities: AgentCapabilities):
        """Register an agent with the communication protocol."""
        self.agents[agent_id] = {
            "handler": handler,
            "capabilities": capabilities,
            "status": "active",
            "registered_at": datetime.now(timezone.utc).isoformat()
        }
        self.message_queues[agent_id] = asyncio.Queue()
        
        log.info(f"🤖 Agent '{agent_id}' registered with capabilities: {capabilities.supported_message_types}")
        
    async def send_message(self, message: Message):
        """Send a message through the protocol with BigQuery context awareness."""
        # Add message ID and timestamp if not present
        if not message.get("message_id"):
            message["message_id"] = str(uuid.uuid4())
        if not message.get("timestamp"):
            message["timestamp"] = datetime.now(timezone.utc).isoformat()
            
        # Store message in history
        app_id = message["application_id"]
        if app_id not in self.message_history:
            self.message_history[app_id] = []
        self.message_history[app_id].append(message)
        
        # Route message to appropriate agent
        receiver = message["receiver"]
        if receiver in self.agents:
            await self.message_queues[receiver].put(message)
            log.info(f"📨 Message sent: {message['message_type']} from {message['sender']} to {receiver}")
        else:
            log.error(f"❌ Unknown receiver: {receiver}")
            
    async def start_message_processing(self):
        """Start processing messages for all registered agents."""
        tasks = []
        for agent_id in self.agents:
            task = asyncio.create_task(self._process_agent_messages(agent_id))
            tasks.append(task)
        await asyncio.gather(*tasks)
        
    async def _process_agent_messages(self, agent_id: str):
        """Process messages for a specific agent."""
        queue = self.message_queues[agent_id]
        handler = self.agents[agent_id]["handler"]
        
        while True:
            try:
                message = await queue.get()
                await handler(message)
                queue.task_done()
            except Exception as e:
                log.error(f"❌ Error processing message for {agent_id}: {e}")
                
    def create_message(self, sender: str, receiver: str, application_id: str, 
                      message_type: MessageType, payload: Dict[str, Any],
                      bigquery_context: Optional[Dict[str, Any]] = None,
                      in_reply_to: Optional[str] = None) -> Message:
        """Create a standardized message with BigQuery context."""
        return Message(
            message_id=str(uuid.uuid4()),
            sender=sender,
            receiver=receiver,
            application_id=application_id,
            message_type=message_type,
            payload=payload,
            timestamp=datetime.now(timezone.utc).isoformat(),
            in_reply_to=in_reply_to,
            bigquery_context=bigquery_context or {
                "project_id": self.project_id,
                "dataset_id": "insurance_data",
                "session_id": str(uuid.uuid4())
            }
        )
        
    async def create_application_session(self, application_id: str, initial_data: Dict[str, Any]):
        """Create a new application session with BigQuery context."""
        session = {
            "application_id": application_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "bigquery_session": {
                "project_id": self.project_id,
                "dataset_id": "insurance_data",
                "temp_tables": [],
                "object_refs": []
            },
            "data": initial_data,
            "message_count": 0,
            "last_activity": datetime.now(timezone.utc).isoformat()
        }
        
        self.active_applications[application_id] = session
        log.info(f"🆕 Created application session: {application_id}")
        return session
        
    def get_application_context(self, application_id: str) -> Optional[Dict[str, Any]]:
        """Get the current context for an application."""
        return self.active_applications.get(application_id)
        
    def update_application_context(self, application_id: str, updates: Dict[str, Any]):
        """Update the context for an application."""
        if application_id in self.active_applications:
            self.active_applications[application_id]["data"].update(updates)
            self.active_applications[application_id]["last_activity"] = datetime.now(timezone.utc).isoformat()
            log.info(f"📝 Updated context for application: {application_id}")
            
    async def close_application_session(self, application_id: str, final_result: Dict[str, Any]):
        """Close an application session and clean up resources."""
        if application_id in self.active_applications:
            session = self.active_applications[application_id]
            session["status"] = "completed"
            session["final_result"] = final_result
            session["completed_at"] = datetime.now(timezone.utc).isoformat()
            
            # Clean up temporary BigQuery resources
            bigquery_session = session.get("bigquery_session", {})
            temp_tables = bigquery_session.get("temp_tables", [])
            
            if temp_tables:
                log.info(f"🧹 Cleaning up {len(temp_tables)} temporary BigQuery tables for {application_id}")
                # Note: Actual cleanup would happen in the BigQuery tools
                
            log.info(f"✅ Closed application session: {application_id}")

class InMemoryCommunicationProtocol(CommunicationProtocol):
    """
    In-memory implementation of the communication protocol.
    Perfect for single-instance deployments and testing.
    """
    
    def __init__(self, project_id: str = "intelligent-insurance-engine"):
        super().__init__(project_id)
        self.running = False
        
    async def start(self):
        """Start the communication protocol."""
        if not self.running:
            self.running = True
            log.info("🚀 InMemoryCommunicationProtocol started")
            # Start message processing in background
            asyncio.create_task(self.start_message_processing())
            
    async def stop(self):
        """Stop the communication protocol."""
        self.running = False
        log.info("🛑 InMemoryCommunicationProtocol stopped")

# Example usage and testing
async def test_communication_protocol():
    """Test the communication protocol with sample messages."""
    protocol = InMemoryCommunicationProtocol()
    
    # Create sample agent capabilities
    orchestrator_capabilities = AgentCapabilities(
        agent_id="InsuranceOrchestrator",
        supported_message_types=[
            MessageType.START_APPLICATION_PROCESSING,
            MessageType.TOOL_EXECUTION_REQUEST
        ],
        bigquery_datasets=["insurance_data"],
        ml_models=["risk_scoring_model", "premium_calculation_model"],
        object_tables=["car_images_objects", "documents_objects"]
    )
    
    # Mock agent handler
    async def mock_handler(message: Message):
        log.info(f"🔄 Processing message: {message['message_type']} for app {message['application_id']}")
        
    # Register agent
    await protocol.register_agent("InsuranceOrchestrator", mock_handler, orchestrator_capabilities)
    
    # Create and send a test message
    test_message = protocol.create_message(
        sender="WebInterface",
        receiver="InsuranceOrchestrator", 
        application_id="APP_TEST_001",
        message_type=MessageType.START_APPLICATION_PROCESSING,
        payload={
            "customer_id": "CUST_001",
            "personal_info": {
                "name": "John Doe",
                "age": 35,
                "location": "CA"
            }
        }
    )
    
    await protocol.send_message(test_message)
    
    # Start protocol
    await protocol.start()
    
    # Wait a bit for processing
    await asyncio.sleep(1)
    
    log.info("✅ Communication protocol test completed")

if __name__ == "__main__":
    asyncio.run(test_communication_protocol())
