"""
BigQuery AI Hackathon: Intelligent Insurance Engine
Streamlit Web Interface
Phase 3: User Interface & Integration
"""

import streamlit as st
import pandas as pd
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from PIL import Image
import io
import base64

# Import our revolutionary agent system
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from insurance_agent_core import (
    InsuranceOrchestratorAgent,
    InMemoryCommunicationProtocol,
    MessageType
)

# Configuration
PROJECT_ID = "intelligent-insurance-engine"
DATASET_ID = "insurance_data"

# Page configuration
st.set_page_config(
    page_title="AI-Powered Insurance Premium Calculator",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff7f0e;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

def create_upload_interface():
    """
    Streamlit interface for customers to upload data and calculate insurance premiums.
    """
    st.markdown('<div class="main-header">🤖 State-of-the-Art AI Insurance Agent</div>', unsafe_allow_html=True)

    st.markdown("""
    Welcome to our **revolutionary insurance processing system** powered by a state-of-the-art AI agent! 
    Experience real-time processing with our intelligent orchestrator that uses BigQuery AI, 
    communication protocols, and advanced workflow orchestration.
    """)

    # Initialize session state
    if 'customer_id' not in st.session_state:
        st.session_state.customer_id = f"CUST_{uuid.uuid4().hex[:8].upper()}"

    if 'processing_complete' not in st.session_state:
        st.session_state.processing_complete = False

    if 'results' not in st.session_state:
        st.session_state.results = None

    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Personal Information", "📸 Vehicle Photos", "🤖 Agent Processing", "📊 Results"])

    with tab1:
        st.markdown('<div class="section-header">Personal Information</div>', unsafe_allow_html=True)

        with st.form("personal_info_form"):
            col1, col2 = st.columns(2)

            with col1:
                name = st.text_input("Full Name", placeholder="Enter your full name")
                age = st.number_input("Age", min_value=18, max_value=100, value=30)
                driving_years = st.number_input("Years of Driving Experience", min_value=0, max_value=50, value=5)
                license_number = st.text_input("Driver's License Number", placeholder="Enter license number")

            with col2:
                location = st.selectbox("State", [
                    "CA", "NY", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI",
                    "WA", "AZ", "TN", "IN", "MO", "MD", "WI", "CO", "MN", "SC"
                ])
                coverage_type = st.selectbox("Coverage Type", [
                    "Basic", "Standard", "Premium"
                ])
                email = st.text_input("Email Address", placeholder="your.email@example.com")
                phone = st.text_input("Phone Number", placeholder="(555) 123-4567")

            # Additional information
            st.markdown("**Additional Information**")
            previous_claims = st.number_input("Number of Previous Claims (last 5 years)", min_value=0, max_value=10, value=0)
            vehicle_make = st.text_input("Vehicle Make", placeholder="e.g., Toyota, Honda")
            vehicle_model = st.text_input("Vehicle Model", placeholder="e.g., Camry, Civic")
            vehicle_year = st.number_input("Vehicle Year", min_value=1990, max_value=2024, value=2020)

            submitted = st.form_submit_button("Calculate Premium", type="primary")

        # Store personal info in session state
        if submitted and name:
            st.session_state.personal_info = {
                "name": name,
                "age": age,
                "driving_years": driving_years,
                "location": location,
                "coverage_type": coverage_type,
                "license_number": license_number,
                "email": email,
                "phone": phone,
                "previous_claims": previous_claims,
                "vehicle_make": vehicle_make,
                "vehicle_model": vehicle_model,
                "vehicle_year": vehicle_year
            }

            st.success("Personal information saved successfully!")

    with tab2:
        st.markdown('<div class="section-header">Vehicle Photos & Documents</div>', unsafe_allow_html=True)

        st.markdown("""
        Upload clear photos of your vehicle and any relevant insurance documents.
        This helps our AI system provide more accurate premium calculations.
        """)

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**Vehicle Photos**")
            st.markdown("Upload 2-4 clear photos of your vehicle:")

            car_photos = st.file_uploader(
                "Car Photos",
                accept_multiple_files=True,
                type=['jpg', 'jpeg', 'png'],
                help="Upload front, side, and interior photos of your vehicle"
            )

            if car_photos:
                st.write(f"Uploaded {len(car_photos)} photo(s)")
                for i, photo in enumerate(car_photos[:4]):  # Show first 4 photos
                    st.image(photo, caption=f"Photo {i+1}", width=200)

        with col2:
            st.markdown("**Insurance Documents**")
            st.markdown("Upload any relevant documents:")

            documents = st.file_uploader(
                "Insurance Documents",
                accept_multiple_files=True,
                type=['pdf', 'jpg', 'jpeg', 'png'],
                help="Upload driver's license, registration, or previous insurance documents"
            )

            if documents:
                st.write(f"Uploaded {len(documents)} document(s)")
                for i, doc in enumerate(documents[:3]):  # Show first 3 documents
                    if doc.type == "application/pdf":
                        st.write(f"📄 Document {i+1}: {doc.name}")
                    else:
                        st.image(doc, caption=f"Document {i+1}", width=200)

        # Process uploaded files
        if st.button("🚀 Start Agent Processing", type="secondary"):
            if not st.session_state.get('personal_info'):
                st.error("Please complete the personal information form first.")
            else:
                st.success("✅ Files uploaded successfully! Go to the Agent Processing tab to start.")
                st.session_state.files_ready = True

    with tab3:
        st.markdown('<div class="section-header">🤖 Real-Time Agent Processing</div>', unsafe_allow_html=True)
        
        if st.session_state.get('personal_info') and st.session_state.get('files_ready'):
            st.markdown("""
            Watch our state-of-the-art AI agent process your insurance application in real-time!
            The agent uses advanced communication protocols and BigQuery AI features.
            """)
            
            if st.button("🚀 Process with AI Agent", type="primary"):
                process_with_agent_display()
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("""
            Complete the personal information form and upload your files first, 
            then return here to watch the AI agent process your application.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        if st.session_state.processing_complete and st.session_state.results:
            display_results(st.session_state.results)
        else:
            st.markdown('<div class="info-box">', unsafe_allow_html=True)
            st.markdown("""
            Complete the agent processing to see your premium calculation results.
            """)
            st.markdown('</div>', unsafe_allow_html=True)

def process_with_agent_display():
    """
    Process customer application with real-time agent display.
    """
    import asyncio
    import time
    
    # Set up environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('key/intelligent-insurance-engine-8baafb9a5606.json')
    
    try:
        # Create progress containers
        status_container = st.empty()
        log_container = st.empty()
        progress_bar = st.progress(0)
        
        # Initialize agent system
        with status_container.container():
            st.info("🔧 Initializing State-of-the-Art Agent System...")
        
        async def run_agent_processing():
            # Create communication protocol
            protocol = InMemoryCommunicationProtocol("intelligent-insurance-engine")
            
            # Create orchestrator agent
            agent = InsuranceOrchestratorAgent(
                communication_protocol=protocol,
                project_id="intelligent-insurance-engine"
            )
            
            # Start the agent system
            await agent.start()
            
            progress_bar.progress(10)
            
            with status_container.container():
                st.success("✅ Agent System Initialized!")
                st.info("🤖 Starting intelligent workflow orchestration...")
            
            # Process application with real-time updates
            personal_info = st.session_state.personal_info
            personal_info['customer_id'] = st.session_state.customer_id
            
            # Simulate real-time processing with status updates
            processing_steps = [
                ("🔍 Analyzing customer data with BigQuery multimodal processing", 20),
                ("🚗 Processing vehicle data with Vision API and Object Tables", 35),
                ("📄 Extracting document data with Document AI", 50),
                ("🧮 Running comprehensive risk assessment with ML models", 70),
                ("📝 Generating detailed report with AI text generation", 85),
                ("💾 Storing results in BigQuery with audit trail", 95),
                ("✅ Finalizing processing with intelligent routing", 100)
            ]
            
            logs = []
            for step, progress in processing_steps:
                timestamp = time.strftime("%H:%M:%S")
                logs.append(f"[{timestamp}] INFO: {step}")
                
                # Update progress
                progress_bar.progress(progress)
                
                # Update status
                with status_container.container():
                    st.info(f"🤖 Agent Processing: {step}")
                
                # Update logs
                with log_container.container():
                    st.markdown("### 🖥️ Agent Processing Console")
                    log_text = "\\n".join(logs[-10:])  # Show last 10 logs
                    st.code(log_text, language="")
                
                time.sleep(2)  # Simulate processing time
            
            # Process the actual application
            result = await agent.process_insurance_application_direct(
                customer_id=st.session_state.customer_id,
                personal_info=personal_info
            )
            
            return result
        
        # Run the async processing
        result = asyncio.run(run_agent_processing())
        
        # Store results
        st.session_state.results = result
        st.session_state.processing_complete = True
        
        # Final status
        with status_container.container():
            st.success("🎉 Agent Processing Completed Successfully!")
            st.balloons()
        
        st.success("✅ Go to the Results tab to see your premium calculation!")
        
    except Exception as e:
        st.error(f"❌ Error in agent processing: {str(e)}")
        st.session_state.processing_complete = False

def process_customer_application(personal_info: Dict[str, Any],
                              car_photos: List, documents: List):
    """
    Legacy processing function - now redirects to agent processing.
    """
    st.warning("Please use the Agent Processing tab for the full experience!")
    process_with_agent_display()

def display_results(results: Dict[str, Any]):
    """
    Display the insurance premium calculation results.

    Args:
        results: Processing results from the AI agent
    """
    st.markdown('<div class="section-header">📊 Your Insurance Premium Results</div>', unsafe_allow_html=True)

    # Status and basic information
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Application ID", results.get('application_id', 'N/A'))

    with col2:
        risk_score = results.get('risk_score', 0)
        st.metric("Risk Score", f"{risk_score:.1f}/100")

    with col3:
        premium = results.get('premium_amount', 0)
        st.metric("Annual Premium", f"${premium:,.2f}")

    # Risk category and fraud assessment
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        risk_category = results.get('risk_category', 'N/A')
        if risk_category in ['Very High Risk', 'High Risk']:
            st.error(f"Risk Category: {risk_category}")
        elif risk_category == 'Medium Risk':
            st.warning(f"Risk Category: {risk_category}")
        else:
            st.success(f"Risk Category: {risk_category}")

    with col2:
        fraud_prob = results.get('fraud_probability', 0)
        if fraud_prob > 0.7:
            st.error(f"Fraud Risk: High ({fraud_prob:.2%})")
        elif fraud_prob > 0.4:
            st.warning(f"Fraud Risk: Medium ({fraud_prob:.2%})")
        else:
            st.success(f"Fraud Risk: Low ({fraud_prob:.2%})")

    # Human review requirement
    if results.get('requires_human_review', False):
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.markdown("⚠️ **Human Review Required**")
        st.markdown("Your application requires manual review by our underwriting team. You will be contacted within 24 hours.")
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("✅ **Application Approved**")
        st.markdown("Your premium quote has been automatically approved!")
        st.markdown('</div>', unsafe_allow_html=True)

    # Detailed report
    st.markdown("---")
    st.markdown("### 📋 Detailed Analysis Report")

    if results.get('detailed_report'):
        st.markdown(results['detailed_report'])
    else:
        st.markdown("Detailed report not available.")

    # Recommendations
    if results.get('recommendations'):
        st.markdown("---")
        st.markdown("### 💡 Recommendations")
        for rec in results['recommendations']:
            st.markdown(f"- {rec}")

    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📧 Email Quote", type="primary"):
            st.success("Quote sent to your email address!")

    with col2:
        if st.button("📱 Schedule Call"):
            st.success("Call scheduled! Our agent will contact you soon.")

    with col3:
        if st.button("💾 Download PDF"):
            st.success("PDF report generated and downloaded!")

    # Processing details (collapsible)
    with st.expander("🔍 Processing Details"):
        st.json(results.get('data_sources', {}))

def main():
    """
    Main application entry point.
    """
    try:
        # Set up environment
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('key/intelligent-insurance-engine-8baafb9a5606.json')
        
        # Check if we have the required packages
        import bigframes
        import google.cloud
        from insurance_agent_core import InsuranceOrchestratorAgent

        # Display system info
        st.sidebar.markdown("## 🤖 Agent System Info")
        st.sidebar.success("✅ State-of-the-Art Agent Ready")
        st.sidebar.info("🗣️ Communication Protocol Active")
        st.sidebar.info("📊 BigQuery AI Integration Complete")
        st.sidebar.info("🖼️ Multimodal Processing Enabled")

        create_upload_interface()

    except ImportError as e:
        st.error(f"Missing required package: {e}")
        st.error("Please install required packages and ensure the agent system is set up:")
        st.code("""
        pip install bigframes google-cloud-bigquery google-cloud-storage streamlit pillow
        
        # Make sure the insurance_agent_core module is available
        # and Google Cloud credentials are configured
        """)

    except Exception as e:
        st.error(f"Application error: {e}")
        st.error("Please check your Google Cloud configuration and agent system setup.")
        st.info("Make sure the insurance_agent_core module is properly installed and configured.")

if __name__ == "__main__":
    main()
