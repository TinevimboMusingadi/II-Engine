"""
BigQuery AI Hackathon: Intelligent Insurance Engine
LLM Router for Intelligent Tool Selection with Gemini 2.5 Flash Lite
State-of-the-Art Agent Decision Making
"""

from typing import Dict, Any, List, Optional
import json
import logging
from datetime import datetime
import os
import asyncio

# Import Gemini for intelligent routing
try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("⚠️ Gemini API not available, using fallback router")

log = logging.getLogger(__name__)

class ApplicationState:
    """
    Manages the state of a single insurance application throughout processing.
    Tracks BigQuery AI operations and multimodal data processing.
    """
    
    def __init__(self, application_id: str, initial_payload: Dict[str, Any]):
        self.application_id = application_id
        self.is_resolved = False
        self.step_count = 0
        self.max_steps = 10  # Prevent infinite loops
        
        # Track processing history
        self.history: List[Dict[str, Any]] = []
        
        # Store all collected data from BigQuery AI operations
        self.context: Dict[str, Any] = {
            "initial_payload": initial_payload,
            "customer_id": initial_payload.get("customer_id"),
            "personal_info": initial_payload.get("personal_info", {}),
            "car_image_refs": initial_payload.get("car_image_refs", []),
            "document_refs": initial_payload.get("document_refs", [])
        }
        
        # Track BigQuery AI features used
        self.bigquery_features_used = set()
        
        # State tracking for workflow
        self.state_flags = {
            "customer_analyzed": False,
            "vehicle_analyzed": False, 
            "documents_processed": False,
            "risk_assessed": False,
            "report_generated": False,
            "results_stored": False,
            "human_review_flagged": False
        }
        
        log.info(f"🆕 Created application state for: {application_id}")
        
    def update_with_tool_result(self, tool_name: str, result: Dict[str, Any]):
        """Update state with tool execution results."""
        self.context[tool_name] = result.get("data")
        self.step_count += 1
        
        # Update BigQuery context tracking
        if "bigquery_context" in result:
            self.bigquery_features_used.update(
                result["bigquery_context"].get("ml_models_used", [])
            )
            self.bigquery_features_used.update(
                result["bigquery_context"].get("object_tables_used", [])
            )
            
        # Update state flags based on tool execution
        if tool_name == "analyze_customer_data":
            self.state_flags["customer_analyzed"] = True
        elif tool_name == "analyze_vehicle_images":
            self.state_flags["vehicle_analyzed"] = True
        elif tool_name == "extract_document_data":
            self.state_flags["documents_processed"] = True
        elif tool_name == "run_comprehensive_risk_assessment":
            self.state_flags["risk_assessed"] = True
        elif tool_name == "generate_final_report":
            self.state_flags["report_generated"] = True
        elif tool_name == "store_application_results":
            self.state_flags["results_stored"] = True
        elif tool_name == "flag_for_human_review":
            self.state_flags["human_review_flagged"] = True
        elif tool_name == "finish_processing":
            self.is_resolved = True
            
        # Add to history
        self.history.append({
            "step": self.step_count,
            "tool": tool_name,
            "timestamp": datetime.now().isoformat(),
            "success": result.get("success", False),
            "bigquery_features": list(self.bigquery_features_used)
        })
        
        log.info(f"📝 State updated for {self.application_id}: {tool_name} -> Step {self.step_count}")
        
    def get_current_state_summary(self) -> str:
        """Get a summary of current state for LLM context."""
        completed_steps = [flag for flag, status in self.state_flags.items() if status]
        pending_steps = [flag for flag, status in self.state_flags.items() if not status]
        
        return f"""
        Application State Summary for {self.application_id}:
        - Step: {self.step_count}/{self.max_steps}
        - Completed: {completed_steps}
        - Pending: {pending_steps}
        - BigQuery AI Features Used: {list(self.bigquery_features_used)}
        - Customer ID: {self.context.get('customer_id')}
        - Available Data: {list(self.context.keys())}
        """
        
    def should_continue_processing(self) -> bool:
        """Check if processing should continue."""
        return not self.is_resolved and self.step_count < self.max_steps

class IntelligentLLMRouter:
    """
    Intelligent router that uses LLM reasoning to select the next tool.
    Optimized for BigQuery AI insurance processing workflow.
    """
    
    def __init__(self):
        self.workflow_knowledge = {
            "start_sequence": ["analyze_customer_data"],
            "data_collection": ["analyze_vehicle_images", "extract_document_data"],
            "analysis_phase": ["run_comprehensive_risk_assessment"],
            "reporting_phase": ["generate_final_report"],
            "completion_phase": ["store_application_results", "flag_for_human_review", "finish_processing"]
        }
        
    async def decide_next_action(self, state: ApplicationState) -> Dict[str, Any]:
        """
        Decide the next action using intelligent workflow logic.
        In production, this would call an LLM with the full context.
        """
        
        # Safety check
        if not state.should_continue_processing():
            return {"action": "finish_processing", "params": self._get_finish_params(state)}
            
        # Workflow logic based on current state
        if not state.state_flags["customer_analyzed"]:
            return self._decide_customer_analysis(state)
            
        elif not state.state_flags["vehicle_analyzed"] and not state.state_flags["documents_processed"]:
            return self._decide_data_collection(state)
            
        elif not state.state_flags["risk_assessed"]:
            return self._decide_risk_assessment(state)
            
        elif not state.state_flags["report_generated"]:
            return self._decide_report_generation(state)
            
        elif not state.state_flags["results_stored"]:
            return self._decide_storage(state)
            
        else:
            return self._decide_completion(state)
            
    def _decide_customer_analysis(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on customer analysis step."""
        return {
            "action": "analyze_customer_data",
            "params": {
                "customer_id": state.context.get("customer_id"),
                "personal_info": state.context.get("personal_info", {})
            },
            "reasoning": "Starting workflow by analyzing customer data using BigQuery multimodal processing"
        }
        
    def _decide_data_collection(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on data collection steps."""
        # Prioritize vehicle images if available
        if state.context.get("car_image_refs") and not state.state_flags["vehicle_analyzed"]:
            return {
                "action": "analyze_vehicle_images",
                "params": {
                    "car_image_refs": state.context.get("car_image_refs", [])
                },
                "reasoning": "Analyzing vehicle images using BigQuery Vision API and Object Tables"
            }
            
        # Process documents if available
        elif state.context.get("document_refs") and not state.state_flags["documents_processed"]:
            return {
                "action": "extract_document_data", 
                "params": {
                    "document_refs": state.context.get("document_refs", [])
                },
                "reasoning": "Extracting document data using BigQuery Document AI and Object Tables"
            }
            
        # If no images or documents, proceed with defaults
        else:
            # Ensure both are marked as processed
            if not state.state_flags["vehicle_analyzed"]:
                return {
                    "action": "analyze_vehicle_images",
                    "params": {"car_image_refs": []},
                    "reasoning": "No vehicle images provided, using default vehicle data"
                }
            else:
                return {
                    "action": "extract_document_data",
                    "params": {"document_refs": []},
                    "reasoning": "No documents provided, using default document data"
                }
                
    def _decide_risk_assessment(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on risk assessment step."""
        customer_data = state.context.get("analyze_customer_data", {}).get("structured_data", {})
        vehicle_data = state.context.get("analyze_vehicle_images", {})
        document_data = state.context.get("extract_document_data", {})
        
        # Merge customer data with document data
        merged_customer_data = {**customer_data, **document_data}
        
        return {
            "action": "run_comprehensive_risk_assessment",
            "params": {
                "customer_data": merged_customer_data,
                "vehicle_data": vehicle_data
            },
            "reasoning": "Running comprehensive risk assessment using BigQuery ML models"
        }
        
    def _decide_report_generation(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on report generation step."""
        return {
            "action": "generate_final_report",
            "params": {
                "risk_assessment": state.context.get("run_comprehensive_risk_assessment", {}),
                "customer_analysis": state.context.get("analyze_customer_data", {}),
                "vehicle_data": state.context.get("analyze_vehicle_images", {})
            },
            "reasoning": "Generating comprehensive final report using BigQuery AI text generation"
        }
        
    def _decide_storage(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on storage step."""
        return {
            "action": "store_application_results",
            "params": {
                "application_id": state.application_id,
                "customer_id": state.context.get("customer_id"),
                "risk_assessment": state.context.get("run_comprehensive_risk_assessment", {}),
                "car_image_refs": state.context.get("car_image_refs", []),
                "document_refs": state.context.get("document_refs", [])
            },
            "reasoning": "Storing application results in BigQuery with ObjectRef audit trail"
        }
        
    def _decide_completion(self, state: ApplicationState) -> Dict[str, Any]:
        """Decide on completion steps."""
        risk_assessment = state.context.get("run_comprehensive_risk_assessment", {})
        
        # Check if human review is needed
        needs_review = (
            risk_assessment.get("fraud_probability", 0) > 0.7 or
            risk_assessment.get("final_risk_score", 0) > 80
        )
        
        if needs_review and not state.state_flags["human_review_flagged"]:
            return {
                "action": "flag_for_human_review",
                "params": {
                    "application_id": state.application_id,
                    "customer_id": state.context.get("customer_id"),
                    "risk_assessment": risk_assessment,
                    "reasons": self._get_review_reasons(risk_assessment)
                },
                "reasoning": "Flagging for human review due to high risk or fraud indicators"
            }
        else:
            return {"action": "finish_processing", "params": self._get_finish_params(state)}
            
    def _get_review_reasons(self, risk_assessment: Dict[str, Any]) -> List[str]:
        """Get reasons for human review."""
        reasons = []
        if risk_assessment.get("fraud_probability", 0) > 0.7:
            reasons.append("High fraud probability detected")
        if risk_assessment.get("final_risk_score", 0) > 80:
            reasons.append("Very high risk score")
        return reasons
        
    def _get_finish_params(self, state: ApplicationState) -> Dict[str, Any]:
        """Get parameters for finishing processing."""
        risk_assessment = state.context.get("run_comprehensive_risk_assessment", {})
        final_report_data = state.context.get("generate_final_report", {})
        
        return {
            "final_report": final_report_data.get("report", "Report generation failed"),
            "premium_amount": risk_assessment.get("premium_amount", 0),
            "risk_score": risk_assessment.get("final_risk_score", 0),
            "application_id": state.application_id
        }

class SimplifiedRouter:
    """
    Simplified rule-based router for demonstration.
    Follows the optimal BigQuery AI workflow sequence.
    """
    
    async def decide_next_action(self, state: ApplicationState) -> Dict[str, Any]:
        """Simple sequential workflow for BigQuery AI insurance processing."""
        
        log.info(f"🤔 Router deciding next action for {state.application_id} at step {state.step_count}")
        
        # Define the optimal workflow sequence
        workflow_sequence = [
            ("analyze_customer_data", "Analyze customer data using BigQuery multimodal processing"),
            ("analyze_vehicle_images", "Analyze vehicle images using BigQuery Vision API"), 
            ("extract_document_data", "Extract document data using BigQuery Document AI"),
            ("run_comprehensive_risk_assessment", "Run risk assessment using BigQuery ML models"),
            ("generate_final_report", "Generate final report using BigQuery AI"),
            ("store_application_results", "Store results in BigQuery with ObjectRef audit"),
            ("check_human_review", "Check if human review is needed"),
            ("finish_processing", "Complete processing workflow")
        ]
        
        # Get current step
        if state.step_count < len(workflow_sequence):
            action_name, reasoning = workflow_sequence[state.step_count]
            
            # Special handling for human review check
            if action_name == "check_human_review":
                risk_assessment = state.context.get("run_comprehensive_risk_assessment", {})
                needs_review = (
                    risk_assessment.get("fraud_probability", 0) > 0.7 or
                    risk_assessment.get("final_risk_score", 0) > 80
                )
                
                if needs_review:
                    return {
                        "action": "flag_for_human_review",
                        "params": {
                            "application_id": state.application_id,
                            "customer_id": state.context.get("customer_id"),
                            "risk_assessment": risk_assessment,
                            "reasons": ["High risk or fraud indicators detected"]
                        },
                        "reasoning": "High risk detected - flagging for human review"
                    }
                else:
                    # Skip to finish processing
                    action_name = "finish_processing"
                    reasoning = "No human review needed - completing processing"
            
            # Get parameters for the action
            params = self._get_action_parameters(action_name, state)
            
            log.info(f"🎯 Router selected: {action_name} - {reasoning}")
            
            return {
                "action": action_name,
                "params": params,
                "reasoning": reasoning
            }
        else:
            # Fallback to finish processing
            return {
                "action": "finish_processing", 
                "params": self._get_action_parameters("finish_processing", state),
                "reasoning": "Workflow complete - finishing processing"
            }
            
    def _get_action_parameters(self, action_name: str, state: ApplicationState) -> Dict[str, Any]:
        """Get parameters for a specific action based on current state."""
        
        if action_name == "analyze_customer_data":
            return {
                "customer_id": state.context.get("customer_id"),
                "personal_info": state.context.get("personal_info", {})
            }
            
        elif action_name == "analyze_vehicle_images":
            return {
                "car_image_refs": state.context.get("car_image_refs", [])
            }
            
        elif action_name == "extract_document_data":
            return {
                "document_refs": state.context.get("document_refs", [])
            }
            
        elif action_name == "run_comprehensive_risk_assessment":
            customer_data = state.context.get("analyze_customer_data", {})
            vehicle_data = state.context.get("analyze_vehicle_images", {})
            document_data = state.context.get("extract_document_data", {})
            
            # Extract structured data safely
            if isinstance(customer_data, dict) and "data" in customer_data:
                customer_structured = customer_data["data"].get("structured_data", {}) if isinstance(customer_data["data"], dict) else {}
            else:
                customer_structured = customer_data.get("structured_data", {}) if isinstance(customer_data, dict) else {}
            
            # Extract vehicle data safely
            if isinstance(vehicle_data, dict) and "data" in vehicle_data:
                vehicle_structured = vehicle_data["data"] if isinstance(vehicle_data["data"], dict) else {}
            else:
                vehicle_structured = vehicle_data if isinstance(vehicle_data, dict) else {}
            
            # Extract document data safely
            if isinstance(document_data, dict) and "data" in document_data:
                document_structured = document_data["data"] if isinstance(document_data["data"], dict) else {}
            else:
                document_structured = document_data if isinstance(document_data, dict) else {}
            
            # Merge customer and document data
            merged_customer_data = {**customer_structured, **document_structured}
            
            return {
                "customer_data": merged_customer_data,
                "vehicle_data": vehicle_structured
            }
            
        elif action_name == "generate_final_report":
            return {
                "risk_assessment": state.context.get("run_comprehensive_risk_assessment", {}),
                "customer_analysis": state.context.get("analyze_customer_data", {}),
                "vehicle_data": state.context.get("analyze_vehicle_images", {})
            }
            
        elif action_name == "store_application_results":
            return {
                "application_id": state.application_id,
                "customer_id": state.context.get("customer_id"),
                "risk_assessment": state.context.get("run_comprehensive_risk_assessment", {}),
                "car_image_refs": state.context.get("car_image_refs", []),
                "document_refs": state.context.get("document_refs", [])
            }
            
        elif action_name == "finish_processing":
            risk_assessment = state.context.get("run_comprehensive_risk_assessment", {})
            if not isinstance(risk_assessment, dict):
                risk_assessment = {}
                
            final_report_data = state.context.get("generate_final_report", {})
            if not isinstance(final_report_data, dict):
                final_report_data = {}
            
            return {
                "final_report": final_report_data.get("report", "Report generation completed"),
                "premium_amount": risk_assessment.get("premium_amount", 0),
                "risk_score": risk_assessment.get("final_risk_score", 0),
                "application_id": state.application_id
            }
            
        else:
            return {}

# Use the simplified router for now
LLMRouter = SimplifiedRouter

if __name__ == "__main__":
    # Test the router
    import asyncio
    
    async def test_router():
        router = LLMRouter()
        
        # Create test state
        state = ApplicationState("APP_TEST_001", {
            "customer_id": "CUST_001",
            "personal_info": {"name": "John Doe", "age": 35}
        })
        
        print("🧪 Testing router decision making...")
        
        for step in range(5):
            decision = await router.decide_next_action(state)
            print(f"Step {step + 1}: {decision['action']} - {decision['reasoning']}")
            
            # Simulate tool execution result
            state.update_with_tool_result(decision['action'], {
                "success": True,
                "data": {"test": "result"},
                "bigquery_context": {"ml_models_used": ["test_model"]}
            })
            
            if state.is_resolved:
                break
                
        print("✅ Router test completed")
    
    asyncio.run(test_router())
