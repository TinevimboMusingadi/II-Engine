"""
BigQuery AI Hackathon: Intelligent Insurance Engine
AI Agent Orchestrator Module
Phase 2: AI Agent Core Development
"""

import bigframes.pandas as bpd
from typing import List, Dict, Any, Optional, Tuple
import json
import uuid
from datetime import datetime, timedelta
from google.cloud import bigquery
from google.cloud import storage

from bigframes_multimodal import BigFramesMultimodalProcessor
from ml_tools import InsuranceMLTools

# Configuration
PROJECT_ID = "intelligent-insurance-engine"
DATASET_ID = "insurance_data"

class InsuranceAIAgent:
    """
    Main AI Agent that orchestrates the entire premium pricing process.
    Processes multimodal insurance data and provides automated premium pricing.
    """

    def __init__(self, project_id: str = PROJECT_ID, dataset_id: str = DATASET_ID):
        """
        Initialize the AI Agent with required components.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.multimodal_processor = BigFramesMultimodalProcessor(project_id, dataset_id)
        self.ml_tools = InsuranceMLTools(project_id, dataset_id)
        self.client = bigquery.Client(project=project_id)

        # Initialize storage client for file uploads
        self.storage_client = storage.Client(project=project_id)

    def process_insurance_application(self, customer_id: str, car_image_refs: List[str] = None,
                                    document_refs: List[str] = None, personal_info: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Main agent workflow for premium pricing.

        Args:
            customer_id: Customer ID
            car_image_refs: List of car image ObjectRef strings
            document_refs: List of document ObjectRef strings
            personal_info: Personal information dictionary

        Returns:
            Dictionary containing processing results
        """
        application_id = f"APP_{uuid.uuid4().hex[:8].upper()}"

        print(f"🚀 Starting insurance application processing for customer {customer_id}")
        print(f"📋 Application ID: {application_id}")

        # Step 1: Extract information from unstructured data
        print("📊 Step 1: Analyzing customer data...")
        customer_analysis = self.multimodal_processor.analyze_customer_data(customer_id)

        if "error" in customer_analysis:
            return {
                "error": customer_analysis["error"],
                "application_id": application_id,
                "status": "FAILED"
            }

        # Merge with provided personal info
        if personal_info:
            customer_analysis["structured_data"].update(personal_info)

        # Step 2: Process car images if available
        print("🚗 Step 2: Analyzing vehicle images...")
        vehicle_data = {}
        if car_image_refs:
            vehicle_data = self.analyze_vehicle_images(car_image_refs)
        else:
            # Use default vehicle data
            vehicle_data = {
                'make': 'TOYOTA',
                'model': 'CAMRY',
                'year': 2020,
                'mileage': 50000,
                'condition': 'Good'
            }

        # Step 3: Process documents if available
        print("📄 Step 3: Processing insurance documents...")
        document_data = {}
        if document_refs:
            document_data = self.extract_personal_data(document_refs)

        # Step 4: Tool calls to ML models
        print("🧮 Step 4: Running ML model predictions...")

        # Prepare customer data for ML models
        customer_data = customer_analysis["structured_data"]
        customer_data.update(document_data)

        # Comprehensive risk assessment
        risk_assessment = self.ml_tools.comprehensive_risk_assessment(customer_data, vehicle_data)

        # Step 5: Generate comprehensive report
        print("📝 Step 5: Generating detailed report...")
        detailed_report = self.generate_detailed_report(
            risk_assessment,
            customer_analysis,
            vehicle_data
        )

        # Step 6: Store results in BigQuery
        print("💾 Step 6: Storing results...")
        self.store_application_results(application_id, customer_id, risk_assessment, car_image_refs, document_refs)

        # Step 7: Determine if human review is needed
        requires_review = risk_assessment['fraud_probability'] > 0.7 or risk_assessment['final_risk_score'] > 80

        if requires_review:
            print("⚠️ Human review required - high risk or fraud indicators detected")

        # Step 8: Human-in-the-loop notification
        if requires_review:
            self.notify_human_reviewer(customer_id, application_id, risk_assessment)

        result = {
            "application_id": application_id,
            "customer_id": customer_id,
            "status": "COMPLETED",
            "premium_amount": risk_assessment['premium_amount'],
            "risk_score": risk_assessment['final_risk_score'],
            "risk_category": risk_assessment['risk_category'],
            "fraud_probability": risk_assessment['fraud_probability'],
            "estimated_vehicle_value": risk_assessment['estimated_vehicle_value'],
            "detailed_report": detailed_report,
            "recommendations": risk_assessment['recommendations'],
            "requires_human_review": requires_review,
            "processing_timestamp": datetime.now().isoformat(),
            "data_sources": {
                "customer_analysis": customer_analysis,
                "vehicle_data": vehicle_data,
                "document_data": document_data
            }
        }

        print("✅ Insurance application processing completed successfully!")
        return result

    def analyze_vehicle_images(self, car_image_refs: List[str]) -> Dict[str, Any]:
        """
        Analyze car images to extract vehicle information.

        Args:
            car_image_refs: List of car image ObjectRef strings

        Returns:
            Dictionary containing vehicle analysis results
        """
        if not car_image_refs:
            return {}

        # Process first image (in a real implementation, process all images)
        first_image_ref = car_image_refs[0]

        try:
            # Use BigQuery ML to analyze image
            features_df = self.multimodal_processor.extract_car_image_features(first_image_ref)

            # Extract features (this is simplified - in reality would parse ML results)
            analysis_result = {
                'image_ref': first_image_ref,
                'estimated_value': 25000,  # Placeholder
                'condition': 'Good',       # Placeholder
                'make': 'TOYOTA',          # Placeholder
                'model': 'CAMRY',          # Placeholder
                'year': 2020,              # Placeholder
                'features_detected': ['front_view', 'clean_condition'],  # Placeholder
                'analysis_confidence': 0.85
            }

            return analysis_result

        except Exception as e:
            print(f"Error analyzing vehicle images: {str(e)}")
            return {
                'error': str(e),
                'estimated_value': 25000,
                'condition': 'Good',
                'make': 'UNKNOWN',
                'model': 'UNKNOWN',
                'year': 2020
            }

    def extract_personal_data(self, document_refs: List[str]) -> Dict[str, Any]:
        """
        Extract structured data from insurance documents.

        Args:
            document_refs: List of document ObjectRef strings

        Returns:
            Dictionary containing extracted personal data
        """
        if not document_refs:
            return {}

        # Process first document (in a real implementation, process all documents)
        first_doc_ref = document_refs[0]

        try:
            # Use BigQuery ML to process document
            doc_df = self.multimodal_processor.process_insurance_document(first_doc_ref)

            # Extract information (this is simplified - in reality would parse ML results)
            extracted_data = {
                'document_ref': first_doc_ref,
                'driving_record': 'Clean',        # Placeholder
                'license_status': 'Valid',        # Placeholder
                'address_verified': True,         # Placeholder
                'document_confidence': 0.90
            }

            return extracted_data

        except Exception as e:
            print(f"Error processing documents: {str(e)}")
            return {
                'error': str(e),
                'driving_record': 'Clean',
                'license_status': 'Valid',
                'address_verified': False
            }

    def generate_detailed_report(self, risk_assessment: Dict[str, Any],
                               customer_analysis: Dict[str, Any],
                               vehicle_data: Dict[str, Any]) -> str:
        """
        Use LLM to generate human-readable detailed report.

        Args:
            risk_assessment: Risk assessment results
            customer_analysis: Customer analysis data
            vehicle_data: Vehicle analysis data

        Returns:
            Generated report as string
        """
        customer_data = customer_analysis.get("structured_data", {})

        prompt = f"""
        Generate a comprehensive insurance premium analysis report based on the following data:

        CUSTOMER PROFILE:
        - Name: {customer_data.get('name', 'N/A')}
        - Age: {customer_data.get('age', 'N/A')}
        - Driving Experience: {customer_data.get('driving_years', 'N/A')} years
        - Location: {customer_data.get('location', 'N/A')}
        - Requested Coverage: {customer_data.get('coverage_type', 'N/A')}

        VEHICLE INFORMATION:
        - Make/Model: {vehicle_data.get('make', 'N/A')} {vehicle_data.get('model', 'N/A')}
        - Year: {vehicle_data.get('year', 'N/A')}
        - Estimated Value: ${vehicle_data.get('estimated_value', 'N/A')","}
        - Condition: {vehicle_data.get('condition', 'N/A')}

        RISK ASSESSMENT:
        - Risk Score: {risk_assessment.get('final_risk_score', 'N/A')}/100
        - Risk Category: {risk_assessment.get('risk_category', 'N/A')}
        - Fraud Probability: {risk_assessment.get('fraud_probability', 'N/A')}

        PREMIUM CALCULATION:
        - Annual Premium: ${risk_assessment.get('premium_amount', 'N/A')".2f"}

        RECOMMENDATIONS:
        {chr(10).join('- ' + rec for rec in risk_assessment.get('recommendations', []))}

        Please provide a professional insurance underwriting report that includes:
        1. Executive summary of the application
        2. Detailed risk analysis with supporting factors
        3. Premium calculation breakdown and justification
        4. Fraud detection assessment
        5. Final recommendations and next steps

        Format the report professionally with clear sections and bullet points.
        """

        try:
            # Use BigQuery ML to generate text
            query = f"""
            SELECT ML.GENERATE_TEXT(
                MODEL `{self.project_id}.{self.dataset_id}.text_generation_model`,
                '{prompt.replace(chr(10), ' ').replace("'", "\\'")}'
            ) as report
            """

            result = bpd.read_gbq(query)
            return result.iloc[0]['report'] if not result.empty else "Unable to generate report"

        except Exception as e:
            print(f"Error generating report: {str(e)}")
            return f"Error generating detailed report: {str(e)}"

    def store_application_results(self, application_id: str, customer_id: str,
                                risk_assessment: Dict[str, Any], car_image_refs: List[str] = None,
                                document_refs: List[str] = None):
        """
        Store application results in BigQuery for audit trail.

        Args:
            application_id: Application ID
            customer_id: Customer ID
            risk_assessment: Risk assessment results
            car_image_refs: List of car image ObjectRef strings
            document_refs: List of document ObjectRef strings
        """
        try:
            # Prepare data for insertion
            application_data = {
                'application_id': application_id,
                'customer_id': customer_id,
                'premium_quote': risk_assessment['premium_amount'],
                'risk_score': risk_assessment['final_risk_score'],
                'fraud_probability': risk_assessment['fraud_probability'],
                'processing_status': 'COMPLETED',
                'human_review_required': risk_assessment['fraud_probability'] > 0.7,
                'created_timestamp': datetime.now().isoformat(),
                'agent_processing_timestamp': datetime.now().isoformat()
            }

            # Insert into BigQuery
            table_id = f"{self.project_id}.{self.dataset_id}.insurance_applications"

            # Convert ObjectRef lists to arrays for BigQuery
            car_refs_array = car_image_refs if car_image_refs else []
            doc_refs_array = document_refs if document_refs else []

            query = f"""
            INSERT INTO `{table_id}` (application_id, customer_id, car_image_refs, document_refs,
                                    premium_quote, risk_score, fraud_probability, processing_status,
                                    human_review_required, created_timestamp, agent_processing_timestamp)
            VALUES ('{application_id}', '{customer_id}', {car_refs_array}, {doc_refs_array},
                    {risk_assessment['premium_amount']}, {risk_assessment['final_risk_score']},
                    {risk_assessment['fraud_probability']}, 'COMPLETED',
                    {risk_assessment['fraud_probability'] > 0.7}, CURRENT_TIMESTAMP(), CURRENT_TIMESTAMP())
            """

            # Execute query
            job = self.client.query(query)
            job.result()  # Wait for completion

            print(f"✅ Application results stored successfully: {application_id}")

        except Exception as e:
            print(f"❌ Error storing application results: {str(e)}")

    def notify_human_reviewer(self, customer_id: str, application_id: str, risk_assessment: Dict[str, Any]):
        """
        Notify human reviewer for applications requiring manual review.

        Args:
            customer_id: Customer ID
            application_id: Application ID
            risk_assessment: Risk assessment results
        """
        # In a real implementation, this would send notifications to:
        # - Email system
        # - Slack/Discord channels
        # - Internal dashboard
        # - Case management system

        review_reasons = []

        if risk_assessment['fraud_probability'] > 0.7:
            review_reasons.append("High fraud probability detected")

        if risk_assessment['final_risk_score'] > 80:
            review_reasons.append("Very high risk score")

        if risk_assessment['risk_category'] in ['Very High Risk', 'High Risk']:
            review_reasons.append("Risk category requires manual review")

        print(f"🚨 HUMAN REVIEW REQUIRED")
        print(f"Customer ID: {customer_id}")
        print(f"Application ID: {application_id}")
        print(f"Reasons: {', '.join(review_reasons)}")
        print(f"Risk Score: {risk_assessment['final_risk_score']}")
        print(f"Fraud Probability: {risk_assessment['fraud_probability']}")
        print(f"Premium Amount: ${risk_assessment['premium_amount']".2f"}")
        print("-" * 50)

    def batch_process_applications(self, status_filter: str = "PENDING") -> List[Dict[str, Any]]:
        """
        Batch process multiple insurance applications.

        Args:
            status_filter: Filter applications by status

        Returns:
            List of processing results
        """
        print(f"🔄 Starting batch processing for status: {status_filter}")

        # Get applications to process
        applications_df = self.multimodal_processor.batch_process_applications(status_filter)

        results = []

        for _, app in applications_df.iterrows():
            try:
                customer_id = app['customer_id']
                application_id = app['application_id']

                print(f"Processing application: {application_id} for customer: {customer_id}")

                # Process application (without ObjectRefs for batch processing)
                result = self.process_insurance_application(
                    customer_id=customer_id,
                    personal_info=json.loads(app.get('personal_info', '{}'))
                )

                results.append(result)

            except Exception as e:
                print(f"Error processing application {application_id}: {str(e)}")
                results.append({
                    "application_id": application_id,
                    "customer_id": customer_id,
                    "status": "ERROR",
                    "error": str(e)
                })

        print(f"✅ Batch processing completed. Processed {len(results)} applications.")
        return results

    def get_application_status(self, application_id: str) -> Dict[str, Any]:
        """
        Get the status of a specific application.

        Args:
            application_id: Application ID to check

        Returns:
            Dictionary containing application status
        """
        query = f"""
        SELECT
            application_id,
            customer_id,
            processing_status,
            premium_quote,
            risk_score,
            fraud_probability,
            human_review_required,
            created_timestamp,
            agent_processing_timestamp
        FROM `{self.project_id}.{self.dataset_id}.insurance_applications`
        WHERE application_id = '{application_id}'
        """

        try:
            result = bpd.read_gbq(query)

            if not result.empty:
                app_data = result.iloc[0]
                return {
                    "application_id": app_data['application_id'],
                    "customer_id": app_data['customer_id'],
                    "status": app_data['processing_status'],
                    "premium_amount": app_data['premium_quote'],
                    "risk_score": app_data['risk_score'],
                    "fraud_probability": app_data['fraud_probability'],
                    "human_review_required": app_data['human_review_required'],
                    "created_timestamp": str(app_data['created_timestamp']),
                    "processing_timestamp": str(app_data['agent_processing_timestamp'])
                }
            else:
                return {"error": "Application not found"}

        except Exception as e:
            return {"error": str(e)}


if __name__ == "__main__":
    # Example usage
    agent = InsuranceAIAgent()

    # Process a sample application
    result = agent.process_insurance_application(
        customer_id="CUST_001",
        personal_info={
            "name": "John Doe",
            "age": 35,
            "driving_years": 15,
            "location": "CA",
            "coverage_type": "Standard"
        }
    )

    print("Application Processing Result:")
    print(json.dumps(result, indent=2, default=str))

    # Check application status
    if "application_id" in result:
        status = agent.get_application_status(result["application_id"])
        print(f"\nApplication Status: {json.dumps(status, indent=2, default=str)}")
