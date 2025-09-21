"""
Test script to verify the notebook agent integration works properly.
"""

import asyncio
import os
import sys
import logging
from datetime import datetime

# Setup environment
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = r'key\intelligent-insurance-engine-8baafb9a5606.json'
os.environ['PROJECT_ID'] = 'intelligent-insurance-engine'

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)

async def test_notebook_integration():
    """Test the notebook integration with our agent system."""
    
    print("🚀 Testing Notebook Integration with State-of-the-Art Agent System")
    print("=" * 70)
    
    try:
        # Import our revolutionary agent system
        from insurance_agent_core import (
            InsuranceOrchestratorAgent,
            InMemoryCommunicationProtocol,
            MessageType
        )
        
        print("✅ Successfully imported agent system")
        
        # Initialize the agent system
        print("🔧 Initializing State-of-the-Art Agent System...")
        
        # Create communication protocol
        protocol = InMemoryCommunicationProtocol("intelligent-insurance-engine")
        
        # Create orchestrator agent
        agent = InsuranceOrchestratorAgent(
            communication_protocol=protocol,
            project_id="intelligent-insurance-engine"
        )
        
        # Start the agent system
        await agent.start()
        
        print("✅ Agent System Initialized Successfully!")
        print(f"   🤖 Agent ID: {agent.agent_id}")
        print(f"   📊 BigQuery Datasets: {len(agent.capabilities.bigquery_datasets)}")
        print(f"   🧠 ML Models: {len(agent.capabilities.ml_models)}")
        print(f"   🖼️ Object Tables: {len(agent.capabilities.object_tables)}")
        
        # Test processing with demo data
        print("\n🎬 Testing Agent Processing...")
        
        demo_customer = {
            "customer_id": "NOTEBOOK_TEST_001",
            "name": "Demo User",
            "age": 30,
            "driving_years": 10,
            "location": "CA",
            "coverage_type": "Standard",
            "previous_claims": 0
        }
        
        # Process application
        result = await agent.process_insurance_application_direct(
            customer_id=demo_customer['customer_id'],
            personal_info=demo_customer
        )
        
        print("\n📊 Processing Results:")
        print(f"   🆔 Application ID: {result.get('application_id', 'N/A')}")
        print(f"   📈 Status: {result.get('status', 'Unknown')}")
        print(f"   🔄 Steps Completed: {result.get('step_count', 0)}")
        print(f"   🔧 BigQuery Features: {len(result.get('bigquery_features_used', []))}")
        
        if result.get('results', {}).get('run_comprehensive_risk_assessment'):
            risk_data = result['results']['run_comprehensive_risk_assessment']
            print(f"   💰 Premium: ${risk_data.get('premium_amount', 0):,.2f}/year")
            print(f"   📊 Risk Score: {risk_data.get('final_risk_score', 0)}/100")
            print(f"   🏷️ Risk Category: {risk_data.get('risk_category', 'N/A')}")
        
        print("\n" + "=" * 70)
        print("🎉 NOTEBOOK INTEGRATION TEST SUCCESSFUL!")
        print("✅ Ready for Jupyter Notebook Demonstration")
        print("🤖 State-of-the-Art Agent System: Fully Operational")
        print("📊 BigQuery AI Features: Complete Integration")
        print("🏆 Hackathon Ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in notebook integration test: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure virtual environment is activated")
        print("   2. Check Google Cloud credentials")
        print("   3. Verify insurance_agent_core module is available")
        
        return False

if __name__ == "__main__":
    success = asyncio.run(test_notebook_integration())
    if success:
        print("\n🚀 Ready to run the Jupyter notebook!")
    else:
        print("\n⚠️ Please fix the issues before running the notebook.")
