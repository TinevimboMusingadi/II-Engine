"""
BigQuery AI Hackathon: Intelligent Insurance Engine
BigFrames Multimodal Data Processing Module
Phase 1: Data Infrastructure Setup
"""

import bigframes.pandas as bpd
import pandas as pd
from typing import List, Dict, Any, Optional
import json
from google.cloud import bigquery
from google.cloud import storage

# Configuration
PROJECT_ID = "intelligent-insurance-engine"
DATASET_ID = "insurance_data"

class BigFramesMultimodalProcessor:
    """
    BigFrames-based multimodal data processing for insurance applications.
    Handles structured and unstructured data fusion using BigQuery Object Tables.
    """

    def __init__(self, project_id: str = PROJECT_ID, dataset_id: str = DATASET_ID):
        """
        Initialize BigFrames multimodal processor.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id
        self.client = bigquery.Client(project=project_id)

    def create_multimodal_dataframe(self, customer_id: Optional[str] = None) -> bpd.DataFrame:
        """
        Create a multimodal dataframe combining structured and unstructured data.

        Args:
            customer_id: Optional customer ID filter

        Returns:
            BigFrames DataFrame with multimodal data
        """
        # Base query for customer data
        base_query = f"""
        SELECT
            customer_id,
            JSON_EXTRACT_SCALAR(personal_info, '$.name') as customer_name,
            JSON_EXTRACT_SCALAR(personal_info, '$.age') as age,
            JSON_EXTRACT_SCALAR(personal_info, '$.driving_years') as driving_years,
            JSON_EXTRACT_SCALAR(personal_info, '$.location') as location,
            JSON_EXTRACT_SCALAR(personal_info, '$.coverage_type') as coverage_type,
            processing_status,
            created_timestamp
        FROM `{self.project_id}.{self.dataset_id}.customer_profiles`
        """

        if customer_id:
            base_query += f" WHERE customer_id = '{customer_id}'"

        # Load structured data
        structured_df = bpd.read_gbq(base_query)

        # Load ObjectRef metadata for car images
        images_query = f"""
        SELECT
            REGEXP_EXTRACT(uri, r'car-images/([^/]+)') as customer_id,
            ARRAY_AGG(
                STRUCT(
                    uri as image_uri,
                    content_type,
                    size as file_size,
                    updated_time as last_modified
                )
            ) as car_images
        FROM `{self.project_id}.{self.dataset_id}.car_images_objects`
        GROUP BY customer_id
        """

        images_df = bpd.read_gbq(images_query)

        # Load ObjectRef metadata for documents
        docs_query = f"""
        SELECT
            REGEXP_EXTRACT(uri, r'documents/([^/]+)') as customer_id,
            ARRAY_AGG(
                STRUCT(
                    uri as document_uri,
                    content_type,
                    size as file_size,
                    last_modified
                )
            ) as documents
        FROM `{self.project_id}.{self.dataset_id}.documents_objects`
        GROUP BY customer_id
        """

        docs_df = bpd.read_gbq(docs_query)

        # Join structured data with ObjectRef metadata
        multimodal_df = structured_df.join(images_df, on='customer_id', how='left')
        multimodal_df = multimodal_df.join(docs_df, on='customer_id', how='left')

        return multimodal_df

    def extract_car_image_features(self, image_objectref: str) -> bpd.DataFrame:
        """
        Extract features from car images using BigQuery ML.

        Args:
            image_objectref: ObjectRef string for the car image

        Returns:
            BigFrames DataFrame with extracted features
        """
        query = f"""
        SELECT
            ML.EXTRACT_IMAGE_FEATURES(
                '{image_objectref}',
                'CAR_ANALYSIS'
            ) as car_features,
            ML.EXTRACT_TEXT(
                '{image_objectref}',
                'OCR'
            ) as extracted_text
        """

        return bpd.read_gbq(query)

    def process_insurance_document(self, document_objectref: str) -> bpd.DataFrame:
        """
        Process insurance documents using BigQuery ML.

        Args:
            document_objectref: ObjectRef string for the document

        Returns:
            BigFrames DataFrame with extracted document data
        """
        query = f"""
        SELECT
            ML.PROCESS_DOCUMENT(
                '{document_objectref}',
                'INSURANCE_FORM'
            ) as extracted_data,
            ML.EXTRACT_TEXT(
                '{document_objectref}',
                'OCR'
            ) as document_text
        """

        return bpd.read_gbq(query)

    def analyze_customer_data(self, customer_id: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of customer data including multimodal sources.

        Args:
            customer_id: Customer ID to analyze

        Returns:
            Dictionary containing analysis results
        """
        # Get multimodal dataframe for customer
        customer_df = self.create_multimodal_dataframe(customer_id)

        if customer_df.empty:
            return {"error": f"No data found for customer {customer_id}"}

        # Extract customer information
        customer_info = customer_df.iloc[0]

        analysis = {
            "customer_id": customer_id,
            "structured_data": {
                "name": customer_info.get("customer_name"),
                "age": int(customer_info.get("age", 0)) if customer_info.get("age") else None,
                "driving_years": int(customer_info.get("driving_years", 0)) if customer_info.get("driving_years") else None,
                "location": customer_info.get("location"),
                "coverage_type": customer_info.get("coverage_type")
            },
            "unstructured_data": {
                "car_images_count": len(customer_info.get("car_images", [])) if customer_info.get("car_images") else 0,
                "documents_count": len(customer_info.get("documents", [])) if customer_info.get("documents") else 0,
                "car_images": customer_info.get("car_images", []),
                "documents": customer_info.get("documents", [])
            },
            "processing_status": customer_info.get("processing_status"),
            "created_timestamp": str(customer_info.get("created_timestamp", ""))
        }

        return analysis

    def batch_process_applications(self, status_filter: str = "PENDING") -> bpd.DataFrame:
        """
        Batch process insurance applications for analysis.

        Args:
            status_filter: Filter applications by processing status

        Returns:
            BigFrames DataFrame with batch processing results
        """
        query = f"""
        SELECT
            a.application_id,
            a.customer_id,
            a.premium_quote,
            a.risk_score,
            a.fraud_probability,
            a.human_review_required,
            a.processing_status,
            c.personal_info,
            -- Aggregate ObjectRef counts
            ARRAY_LENGTH(a.car_image_refs) as car_image_count,
            ARRAY_LENGTH(a.document_refs) as document_count
        FROM `{self.project_id}.{self.dataset_id}.insurance_applications` a
        LEFT JOIN `{self.project_id}.{self.dataset_id}.customer_profiles` c
          ON a.customer_id = c.customer_id
        WHERE a.processing_status = '{status_filter}'
        ORDER BY a.created_timestamp DESC
        """

        return bpd.read_gbq(query)

    def generate_processing_report(self, customer_id: str) -> str:
        """
        Generate a comprehensive processing report using LLM.

        Args:
            customer_id: Customer ID for report generation

        Returns:
            Generated report as string
        """
        analysis = self.analyze_customer_data(customer_id)

        if "error" in analysis:
            return f"Error generating report: {analysis['error']}"

        # Create prompt for LLM
        prompt = f"""
        Generate a comprehensive insurance application processing report based on the following data:

        Customer Information:
        - Name: {analysis['structured_data']['name']}
        - Age: {analysis['structured_data']['age']}
        - Driving Experience: {analysis['structured_data']['driving_years']} years
        - Location: {analysis['structured_data']['location']}
        - Requested Coverage: {analysis['structured_data']['coverage_type']}

        Data Sources:
        - Car Images Available: {analysis['unstructured_data']['car_images_count']}
        - Insurance Documents Available: {analysis['unstructured_data']['documents_count']}
        - Processing Status: {analysis['processing_status']}

        Please provide:
        1. Summary of customer profile and requested coverage
        2. Assessment of data completeness for processing
        3. Recommendations for next steps in the insurance application process
        4. Risk factors to consider based on the provided information

        Format the report in a professional, easy-to-read manner.
        """

        # Use BigQuery ML to generate text
        query = f"""
        SELECT ML.GENERATE_TEXT(
            MODEL `{self.project_id}.{self.dataset_id}.text_generation_model`,
            '{prompt}'
        ) as report
        """

        try:
            result = bpd.read_gbq(query)
            return result.iloc[0]['report'] if not result.empty else "Unable to generate report"
        except Exception as e:
            return f"Error generating report: {str(e)}"

def create_sample_multimodal_data():
    """
    Create sample multimodal data for testing and demonstration.
    """
    # Sample customer data
    sample_data = [
        {
            "customer_id": "CUST_001",
            "personal_info": {
                "name": "John Doe",
                "age": 35,
                "driving_years": 15,
                "location": "CA",
                "coverage_type": "Standard"
            },
            "car_images": [
                {"uri": "gs://ii-engine-bucket/car-images/CUST_001/car_front.jpg", "content_type": "image/jpeg"},
                {"uri": "gs://ii-engine-bucket/car-images/CUST_001/car_side.jpg", "content_type": "image/jpeg"}
            ],
            "documents": [
                {"uri": "gs://ii-engine-bucket/documents/CUST_001/drivers_license.pdf", "content_type": "application/pdf"},
                {"uri": "gs://ii-engine-bucket/documents/CUST_001/insurance_form.pdf", "content_type": "application/pdf"}
            ]
        },
        {
            "customer_id": "CUST_002",
            "personal_info": {
                "name": "Jane Smith",
                "age": 28,
                "driving_years": 8,
                "location": "NY",
                "coverage_type": "Premium"
            },
            "car_images": [
                {"uri": "gs://ii-engine-bucket/car-images/CUST_002/car_dashboard.jpg", "content_type": "image/jpeg"}
            ],
            "documents": [
                {"uri": "gs://ii-engine-bucket/documents/CUST_002/policy_application.pdf", "content_type": "application/pdf"}
            ]
        }
    ]

    return sample_data

if __name__ == "__main__":
    # Example usage
    processor = BigFramesMultimodalProcessor()

    # Create multimodal dataframe
    multimodal_df = processor.create_multimodal_dataframe()
    print("Multimodal DataFrame created successfully")
    print(f"Shape: {multimodal_df.shape}")

    # Analyze sample customer
    analysis = processor.analyze_customer_data("CUST_001")
    print("Customer analysis completed")
    print(json.dumps(analysis, indent=2))
