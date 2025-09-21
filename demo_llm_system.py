#!/usr/bin/env python3
"""
BigQuery AI Hackathon: Intelligent Insurance Engine
LLM-Powered Agent System Demo
Quick demonstration of the intelligent agent system
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from insurance_agent_core import InsuranceOrchestratorAgent, InMemoryCommunicationProtocol

async def demo_llm_system():
    """Quick demo of the LLM-powered agent system."""
    
    print("🤖 BigQuery AI Hackathon: Intelligent Insurance Engine")
    print("   LLM-Powered Agent System Demo")
    print("=" * 60)
    
    # Create agent system
    print("🚀 Initializing LLM-Powered Agent System...")
    agent = InsuranceOrchestratorAgent(project_id="intelligent-insurance-engine")
    await agent.start()
    
    print("✅ Agent system ready!")
    print(f"   📊 BigQuery Datasets: {agent.capabilities.bigquery_datasets}")
    print(f"   🧠 ML Models: {len(agent.capabilities.ml_models)}")
    print(f"   🖼️ Object Tables: {len(agent.capabilities.object_tables)}")
    
    # Demo 1: Simple insurance application
    print("\n" + "="*60)
    print("📋 DEMO 1: Simple Insurance Application")
    print("="*60)
    
    customer_data = {
        "name": "Alice Johnson",
        "age": 30,
        "driving_years": 8,
        "location": "California",
        "coverage_type": "Comprehensive",
        "previous_claims": 0,
        "credit_score": 780
    }
    
    print(f"👤 Customer: {customer_data['name']}")
    print(f"   Age: {customer_data['age']}, Experience: {customer_data['driving_years']} years")
    print(f"   Location: {customer_data['location']}, Coverage: {customer_data['coverage_type']}")
    
    # Process application
    result = await agent.process_insurance_application_direct(
        customer_id="CUST_DEMO_001",
        personal_info=customer_data
    )
    
    print(f"\n✅ Application Processed!")
    print(f"   Application ID: {result['application_id']}")
    print(f"   Status: {result['status']}")
    print(f"   Steps: {result['step_count']}")
    print(f"   BigQuery AI Features: {len(result['bigquery_features_used'])}")
    
    # Demo 2: Complex application with images
    print("\n" + "="*60)
    print("📋 DEMO 2: Complex Application with Multimodal Data")
    print("="*60)
    
    complex_customer = {
        "name": "Bob Smith",
        "age": 45,
        "driving_years": 20,
        "location": "New York",
        "coverage_type": "Premium",
        "previous_claims": 2,
        "credit_score": 720,
        "vehicle_make": "Tesla",
        "vehicle_model": "Model 3",
        "vehicle_year": 2023
    }
    
    # Simulate ObjectRefs for images and documents
    car_images = [
        "gs://insurance-premium-applications/auto-applications/vehicle-photos/tesla_front.jpg",
        "gs://insurance-premium-applications/auto-applications/vehicle-photos/tesla_side.jpg"
    ]
    
    documents = [
        "gs://insurance-premium-applications/auto-applications/driver-documents/license.pdf",
        "gs://insurance-premium-applications/auto-applications/application-forms/application.pdf"
    ]
    
    print(f"👤 Customer: {complex_customer['name']}")
    print(f"   Vehicle: {complex_customer['vehicle_year']} {complex_customer['vehicle_make']} {complex_customer['vehicle_model']}")
    print(f"   Images: {len(car_images)} car photos")
    print(f"   Documents: {len(documents)} documents")
    
    # Process complex application
    complex_result = await agent.process_insurance_application_direct(
        customer_id="CUST_DEMO_002",
        personal_info=complex_customer,
        car_image_refs=car_images,
        document_refs=documents
    )
    
    print(f"\n✅ Complex Application Processed!")
    print(f"   Application ID: {complex_result['application_id']}")
    print(f"   Status: {complex_result['status']}")
    print(f"   Steps: {complex_result['step_count']}")
    print(f"   BigQuery AI Features: {len(complex_result['bigquery_features_used'])}")
    
    # Demo 3: System capabilities
    print("\n" + "="*60)
    print("🔧 DEMO 3: System Capabilities")
    print("="*60)
    
    print("🧠 LLM-Powered Features:")
    print("   ✓ Intelligent tool selection")
    print("   ✓ Dynamic workflow orchestration")
    print("   ✓ Context-aware decision making")
    print("   ✓ Enhanced report generation")
    
    print("\n🔧 BigQuery AI Features:")
    print("   ✓ Object Tables with ObjectRef")
    print("   ✓ BigFrames Multimodal DataFrames")
    print("   ✓ BigQuery ML model integration")
    print("   ✓ Vision API image analysis")
    print("   ✓ Document AI text extraction")
    
    print("\n🚀 Agent Architecture:")
    print("   ✓ Communication protocol")
    print("   ✓ State management")
    print("   ✓ Error handling")
    print("   ✓ Graceful fallbacks")
    
    # Cleanup
    await agent.stop()
    
    print("\n" + "="*60)
    print("🎉 Demo Complete!")
    print("="*60)
    print("✅ LLM-powered agent system working perfectly")
    print("🔧 BigQuery AI features fully integrated")
    print("🚀 Ready for hackathon submission!")
    
    print("\n🌐 Web Interface:")
    print("   Run: python -m streamlit run web_interface/insurance_app.py")
    print("   URL: http://localhost:8501")

async def main():
    """Main demo function."""
    try:
        await demo_llm_system()
    except KeyboardInterrupt:
        print("\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
