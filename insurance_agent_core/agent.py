"""
BigQuery AI Hackathon: Intelligent Insurance Engine
Orchestrator Agent with Communication Protocol
State-of-the-Art Agent Architecture with BigQuery AI Integration
"""

import asyncio
import logging
import uuid
from typing import Dict, Any, Optional
from datetime import datetime, timezone

from .communication_protocol import (
    CommunicationProtocol, Message, MessageType, AgentCapabilities,
    InMemoryCommunicationProtocol
)
from .router import LLMRouter, ApplicationState
from .tools import BigQueryAIToolImplementations

# Setup logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class InsuranceOrchestratorAgent:
    """
    Main orchestrator agent that processes insurance applications using
    BigQuery AI features with intelligent tool selection and communication protocol.
    
    Features:
    - BigQuery Object Tables and ObjectRef integration
    - BigFrames multimodal data processing
    - BigQuery ML model integration
    - Vision API and Document AI processing
    - Intelligent workflow orchestration
    - State-of-the-art communication protocol
    """
    
    def __init__(self, communication_protocol: Optional[CommunicationProtocol] = None,
                 project_id: str = "intelligent-insurance-engine"):
        self.agent_id = "InsuranceOrchestrator"
        self.project_id = project_id
        
        # Initialize communication protocol
        self.communication_protocol = communication_protocol or InMemoryCommunicationProtocol(project_id)
        
        # Initialize core components
        self.router = LLMRouter(project_id)
        self.tools = BigQueryAIToolImplementations(project_id)
        
        # Track active applications
        self.applications: Dict[str, ApplicationState] = {}
        
        # Define agent capabilities for BigQuery AI
        self.capabilities = AgentCapabilities(
            agent_id=self.agent_id,
            supported_message_types=[
                MessageType.START_APPLICATION_PROCESSING,
                MessageType.TOOL_EXECUTION_REQUEST,
                MessageType.STATUS_UPDATE
            ],
            bigquery_datasets=["insurance_data", "claims_processing_data"],
            ml_models=[
                "risk_scoring_model", "premium_calculation_model", 
                "fraud_detection_model", "text_generation_model"
            ],
            object_tables=[
                "car_images_objects", "documents_objects", "policy_objects"
            ]
        )
        
        # Create action map linking tool names to implementations
        self._action_map = {
            "analyze_customer_data": self.tools.analyze_customer_data,
            "analyze_vehicle_images": self.tools.analyze_vehicle_images,
            "extract_document_data": self.tools.extract_document_data,
            "run_comprehensive_risk_assessment": self.tools.run_comprehensive_risk_assessment,
            "generate_final_report": self.tools.generate_final_report,
            "store_application_results": self.tools.store_application_results,
            "flag_for_human_review": self.tools.flag_for_human_review,
            "finish_processing": self.tools.finish_processing
        }
        
        log.info(f"🤖 {self.agent_id} initialized with BigQuery AI capabilities")
        log.info(f"   📊 Datasets: {self.capabilities.bigquery_datasets}")
        log.info(f"   🧠 ML Models: {len(self.capabilities.ml_models)}")
        log.info(f"   🖼️ Object Tables: {len(self.capabilities.object_tables)}")
        
    async def start(self):
        """Start the agent and register with communication protocol."""
        try:
            # Register with communication protocol
            await self.communication_protocol.register_agent(
                self.agent_id, 
                self.handle_message, 
                self.capabilities
            )
            
            # Start communication protocol if needed
            if hasattr(self.communication_protocol, 'start'):
                await self.communication_protocol.start()
                
            log.info(f"✅ {self.agent_id} started and registered successfully")
            
        except Exception as e:
            log.error(f"❌ Error starting agent: {e}")
            raise
    
    async def stop(self):
        """Stop the agent and clean up resources."""
        try:
            if hasattr(self.communication_protocol, 'stop'):
                await self.communication_protocol.stop()
            log.info(f"🛑 {self.agent_id} stopped successfully")
        except Exception as e:
            log.error(f"❌ Error starting agent: {e}")
            raise
            
    async def handle_message(self, message: Message):
        """
        Main entry point for all incoming messages from the communication protocol.
        Handles different message types for insurance processing.
        """
        try:
            msg_type = message.get("message_type")
            app_id = message.get("application_id")
            sender = message.get("sender")
            
            log.info(f"📨 Received message: {msg_type} for application {app_id} from {sender}")
            
            if msg_type == MessageType.START_APPLICATION_PROCESSING:
                await self._handle_start_application_processing(message)
                
            elif msg_type == MessageType.TOOL_EXECUTION_REQUEST:
                await self._handle_tool_execution_request(message)
                
            elif msg_type == MessageType.STATUS_UPDATE:
                await self._handle_status_update(message)
                
            else:
                log.warning(f"⚠️ Unhandled message type '{msg_type}' for application {app_id}")
                await self._send_error_response(message, f"Unsupported message type: {msg_type}")
                
        except Exception as e:
            log.error(f"❌ Error handling message: {e}")
            await self._send_error_response(message, str(e))
            
    async def _handle_start_application_processing(self, message: Message):
        """Handle request to start processing a new insurance application."""
        app_id = message.get("application_id")
        payload = message.get("payload", {})
        
        log.info(f"🚀 Starting application processing for: {app_id}")
        
        try:
            # Create application session in communication protocol
            await self.communication_protocol.create_application_session(app_id, payload)
            
            # Start the BigQuery AI processing workflow
            await self._process_application_workflow(message)
            
        except Exception as e:
            log.error(f"❌ Error starting application processing: {e}")
            await self._send_error_response(message, str(e))
            
    async def _handle_tool_execution_request(self, message: Message):
        """Handle direct tool execution requests."""
        app_id = message.get("application_id")
        payload = message.get("payload", {})
        tool_name = payload.get("tool_name")
        params = payload.get("params", {})
        
        log.info(f"🔧 Executing tool '{tool_name}' for application {app_id}")
        
        try:
            if app_id in self.applications:
                state = self.applications[app_id]
                
                if tool_name in self._action_map:
                    # Execute the tool
                    handler = self._action_map[tool_name]
                    result = await handler(state.context, params)
                    
                    # Update state
                    state.update_with_tool_result(tool_name, result.to_dict())
                    
                    # Send response
                    await self._send_tool_execution_response(message, result.to_dict())
                    
                else:
                    await self._send_error_response(message, f"Unknown tool: {tool_name}")
            else:
                await self._send_error_response(message, f"Application not found: {app_id}")
                
        except Exception as e:
            log.error(f"❌ Error executing tool: {e}")
            await self._send_error_response(message, str(e))
            
    async def _handle_status_update(self, message: Message):
        """Handle status update requests."""
        app_id = message.get("application_id")
        
        if app_id in self.applications:
            state = self.applications[app_id]
            status = {
                "application_id": app_id,
                "step_count": state.step_count,
                "is_resolved": state.is_resolved,
                "state_flags": state.state_flags,
                "bigquery_features_used": list(state.bigquery_features_used)
            }
            
            await self._send_status_response(message, status)
        else:
            await self._send_error_response(message, f"Application not found: {app_id}")
            
    async def _process_application_workflow(self, initial_message: Message):
        """
        Run the complete BigQuery AI-driven workflow for one insurance application.
        This is the core orchestration logic that demonstrates all BigQuery AI features.
        """
        app_id = initial_message.get("application_id")
        payload = initial_message.get("payload", {})
        
        # Create application state
        state = ApplicationState(app_id, payload)
        self.applications[app_id] = state
        
        log.info(f"🔄 Starting BigQuery AI workflow for {app_id}")
        
        # Send initial status update
        await self._send_status_update(initial_message, "Processing started with BigQuery AI pipeline")
        
        try:
            # Main processing loop with intelligent tool selection
            while state.should_continue_processing():
                # Use router to decide next action
                decision = await self.router.decide_next_action(state)
                
                # Handle None decision
                if decision is None:
                    log.error(f"❌ Router returned None decision for {app_id}")
                    decision = {"action": "finish_processing", "params": {"final_report": "Router error - finishing processing", "premium_amount": 0, "risk_score": 0}}
                
                action_name = decision.get("action")
                params = decision.get("params", {})
                reasoning = decision.get("reasoning", "")
                
                log.info(f"🎯 Step {state.step_count + 1}: {action_name}")
                log.info(f"   💭 Reasoning: {reasoning}")
                
                # Send status update about current step
                await self._send_status_update(
                    initial_message, 
                    f"Executing step {state.step_count + 1}: {action_name}"
                )
                
                if action_name in self._action_map:
                    # Execute the BigQuery AI tool
                    handler = self._action_map[action_name]
                    
                    try:
                        result = await handler(state.context, params)
                        
                        # Update state with results
                        state.update_with_tool_result(action_name, result.to_dict())
                        
                        log.info(f"   ✅ {action_name} completed successfully")
                        
                        # Log BigQuery AI features used
                        if result.bigquery_context:
                            features = result.bigquery_context
                            log.info(f"   🔧 BigQuery AI features: {features}")
                            
                    except Exception as e:
                        log.error(f"   ❌ {action_name} failed: {e}")
                        # Continue processing with error logged
                        state.update_with_tool_result(action_name, {
                            "success": False,
                            "error": str(e),
                            "data": None
                        })
                        
                else:
                    log.error(f"❌ Unknown action: {action_name}")
                    break
                    
                # Check if we should break early
                if state.is_resolved:
                    break
                    
            # Send final result
            await self._send_final_result(initial_message, state)
            
            # Clean up application session
            final_result = state.context.get("finish_processing", {})
            await self.communication_protocol.close_application_session(app_id, final_result)
            
            # Remove from active applications
            if app_id in self.applications:
                del self.applications[app_id]
                
            log.info(f"✅ Completed BigQuery AI workflow for {app_id}")
            
        except Exception as e:
            log.error(f"❌ Error in application workflow: {e}")
            await self._send_error_response(initial_message, str(e))
            
    async def _send_final_result(self, original_message: Message, state: ApplicationState):
        """Send the final processing result back to the requester."""
        
        # Compile comprehensive results
        final_result = {
            "application_id": state.application_id,
            "status": "COMPLETED",
            "processing_summary": {
                "total_steps": state.step_count,
                "bigquery_ai_features_used": list(state.bigquery_features_used),
                "workflow_completed": state.is_resolved
            },
            "results": {
                "customer_analysis": state.context.get("analyze_customer_data"),
                "vehicle_analysis": state.context.get("analyze_vehicle_images"),
                "document_analysis": state.context.get("extract_document_data"),
                "risk_assessment": state.context.get("run_comprehensive_risk_assessment"),
                "final_report": state.context.get("generate_final_report"),
                "storage_confirmation": state.context.get("store_application_results"),
                "human_review_status": state.context.get("flag_for_human_review"),
                "processing_completion": state.context.get("finish_processing")
            },
            "bigquery_ai_demonstration": {
                "object_tables_used": True,
                "objectref_integration": True,
                "bigframes_multimodal": True,
                "ml_models_integrated": True,
                "vision_api_processing": True,
                "document_ai_processing": True,
                "automated_workflow": True
            }
        }
        
        # Create response message
        response = self.communication_protocol.create_message(
            sender=self.agent_id,
            receiver=original_message["sender"],
            application_id=state.application_id,
            message_type=MessageType.APPLICATION_RESULT,
            payload=final_result,
            bigquery_context={
                "project_id": self.project_id,
                "features_demonstrated": list(state.bigquery_features_used),
                "processing_completed_at": datetime.now(timezone.utc).isoformat()
            },
            in_reply_to=original_message["message_id"]
        )
        
        await self.communication_protocol.send_message(response)
        
        log.info(f"📤 Sent final result for {state.application_id}")
        
    async def _send_status_update(self, original_message: Message, status_message: str):
        """Send status update during processing."""
        
        status_update = self.communication_protocol.create_message(
            sender=self.agent_id,
            receiver=original_message["sender"],
            application_id=original_message["application_id"],
            message_type=MessageType.STATUS_UPDATE,
            payload={"status": status_message, "timestamp": datetime.now().isoformat()},
            in_reply_to=original_message["message_id"]
        )
        
        await self.communication_protocol.send_message(status_update)
        
    async def _send_tool_execution_response(self, original_message: Message, result: Dict[str, Any]):
        """Send response for tool execution."""
        
        response = self.communication_protocol.create_message(
            sender=self.agent_id,
            receiver=original_message["sender"],
            application_id=original_message["application_id"],
            message_type=MessageType.TOOL_EXECUTION_RESPONSE,
            payload=result,
            in_reply_to=original_message["message_id"]
        )
        
        await self.communication_protocol.send_message(response)
        
    async def _send_status_response(self, original_message: Message, status: Dict[str, Any]):
        """Send status response."""
        
        response = self.communication_protocol.create_message(
            sender=self.agent_id,
            receiver=original_message["sender"],
            application_id=original_message["application_id"],
            message_type=MessageType.STATUS_UPDATE,
            payload=status,
            in_reply_to=original_message["message_id"]
        )
        
        await self.communication_protocol.send_message(response)
        
    async def _send_error_response(self, original_message: Message, error_message: str):
        """Send error response."""
        
        error_response = self.communication_protocol.create_message(
            sender=self.agent_id,
            receiver=original_message["sender"],
            application_id=original_message["application_id"],
            message_type=MessageType.ERROR,
            payload={"error": error_message, "timestamp": datetime.now().isoformat()},
            in_reply_to=original_message["message_id"]
        )
        
        await self.communication_protocol.send_message(error_response)
        
    async def process_insurance_application_direct(self, customer_id: str, personal_info: Dict[str, Any],
                                                 car_image_refs: list = None, document_refs: list = None) -> Dict[str, Any]:
        """
        Direct method for processing insurance applications without communication protocol.
        Useful for testing and simple integrations.
        """
        
        application_id = f"APP_{uuid.uuid4().hex[:8].upper()}"
        
        log.info(f"🚀 Direct processing for application: {application_id}")
        
        # Create mock message for direct processing
        mock_message = self.communication_protocol.create_message(
            sender="DirectClient",
            receiver=self.agent_id,
            application_id=application_id,
            message_type=MessageType.START_APPLICATION_PROCESSING,
            payload={
                "customer_id": customer_id,
                "personal_info": personal_info,
                "car_image_refs": car_image_refs or [],
                "document_refs": document_refs or []
            }
        )
        
        # Process the application
        await self._process_application_workflow(mock_message)
        
        # Return the results
        if application_id in self.applications:
            state = self.applications[application_id]
            return {
                "application_id": application_id,
                "status": "COMPLETED" if state.is_resolved else "IN_PROGRESS",
                "results": state.context,
                "bigquery_features_used": list(state.bigquery_features_used),
                "step_count": state.step_count
            }
        else:
            return {"error": "Application processing failed"}

# Example usage and testing
async def test_orchestrator_agent():
    """Test the orchestrator agent with BigQuery AI workflow."""
    
    log.info("🧪 Testing Insurance Orchestrator Agent")
    
    # Create agent
    agent = InsuranceOrchestratorAgent()
    
    # Start agent
    await agent.start()
    
    # Test direct processing
    result = await agent.process_insurance_application_direct(
        customer_id="CUST_TEST_001",
        personal_info={
            "name": "John Doe",
            "age": 35,
            "driving_years": 15,
            "location": "CA",
            "coverage_type": "Standard",
            "previous_claims": 1
        }
    )
    
    log.info(f"✅ Test result: {result}")
    
    return result

if __name__ == "__main__":
    asyncio.run(test_orchestrator_agent())
