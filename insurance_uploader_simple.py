#!/usr/bin/env python3
"""
BigQuery AI Hackathon: Simplified Insurance Application Uploader
This is a deployment-friendly version without Vision API and Document AI dependencies.
"""

import os
import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import mimetypes

from google.cloud import storage
from google.cloud import bigquery
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InsuranceApplicationUploader:
    """
    Simplified version for deployment - handles uploading insurance application documents to Cloud Storage 
    and creating linked records in BigQuery with ObjectRef integration
    """
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('PROJECT_ID', 'intelligent-insurance-engine')
        
        # Initialize Google Cloud clients
        self.storage_client = storage.Client(project=self.project_id)
        self.bq_client = bigquery.Client(project=self.project_id)
        
        # Bucket configurations
        self.premium_bucket = os.getenv('PREMIUM_BUCKET', 'insurance-premium-applications')
        self.claims_bucket = os.getenv('CLAIMS_BUCKET', 'insurance-claims-processing')
        
        # BigQuery datasets
        self.premium_dataset = os.getenv('DATASET_ID', 'insurance_data')
        self.claims_dataset = "claims_processing_data"
        
        print(f"🚀 Initialized Insurance Application Uploader")
        print(f"   Project: {self.project_id}")
        print(f"   Premium Bucket: {self.premium_bucket}")
        print(f"   Dataset: {self.premium_dataset}")
        
    def create_buckets_and_folders(self):
        """Create the bucket structure if it doesn't exist"""
        print("🏗️ Creating bucket structure...")
        
        # Premium applications bucket structure
        premium_folders = [
            "auto-applications/vehicle-photos/",
            "auto-applications/driver-documents/", 
            "auto-applications/application-forms/",
            "property-applications/property-photos/",
            "property-applications/inspection-reports/",
            "property-applications/application-forms/",
            "health-applications/medical-records/",
            "health-applications/application-forms/"
        ]
        
        # Claims processing bucket structure
        claims_folders = [
            "auto-claims/accident-photos/",
            "auto-claims/police-reports/",
            "auto-claims/repair-estimates/",
            "property-claims/damage-photos/",
            "property-claims/inspection-reports/", 
            "property-claims/receipts/",
            "health-claims/medical-bills/",
            "health-claims/treatment-records/",
            "health-claims/receipts/"
        ]
        
        # Create buckets and folder structure
        for bucket_name, folders in [(self.premium_bucket, premium_folders), 
                                    (self.claims_bucket, claims_folders)]:
            try:
                bucket = self.storage_client.bucket(bucket_name)
                
                # Create bucket if it doesn't exist
                if not bucket.exists():
                    bucket = self.storage_client.create_bucket(bucket_name, location="US")
                    print(f"✅ Created bucket: {bucket_name}")
                else:
                    print(f"✅ Bucket already exists: {bucket_name}")
                
                # Create folder structure with .keep files
                for folder in folders:
                    blob = bucket.blob(f"{folder}.keep")
                    if not blob.exists():
                        blob.upload_from_string("")
                        print(f"   📁 Created folder: {folder}")
                    else:
                        print(f"   📁 Folder exists: {folder}")
                        
            except Exception as e:
                print(f"❌ Error creating bucket structure for {bucket_name}: {e}")
                raise

    def determine_file_path(self, application_type: str, document_type: str, 
                           application_id: str, filename: str) -> str:
        """Determine the appropriate Cloud Storage path based on document type"""
        
        file_extension = Path(filename).suffix
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_filename = f"{application_id}_{document_type}_{timestamp}{file_extension}"
        
        path_mapping = {
            "auto": {
                "vehicle_photo": f"auto-applications/vehicle-photos/{new_filename}",
                "driver_license": f"auto-applications/driver-documents/{new_filename}",
                "application_form": f"auto-applications/application-forms/{new_filename}",
                "registration": f"auto-applications/driver-documents/{new_filename}",
                "insurance_card": f"auto-applications/driver-documents/{new_filename}"
            },
            "property": {
                "property_photo": f"property-applications/property-photos/{new_filename}",
                "inspection_report": f"property-applications/inspection-reports/{new_filename}",
                "application_form": f"property-applications/application-forms/{new_filename}",
                "deed": f"property-applications/application-forms/{new_filename}",
                "appraisal": f"property-applications/inspection-reports/{new_filename}"
            },
            "health": {
                "medical_record": f"health-applications/medical-records/{new_filename}",
                "application_form": f"health-applications/application-forms/{new_filename}",
                "prescription": f"health-applications/medical-records/{new_filename}",
                "id_document": f"health-applications/application-forms/{new_filename}"
            }
        }
        
        return path_mapping.get(application_type, {}).get(document_type, 
                                                         f"{application_type}-applications/{new_filename}")

    def upload_file_to_gcs(self, local_file_path: str, gcs_file_path: str, 
                          bucket_name: str) -> str:
        """Upload a file to Google Cloud Storage"""
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blob = bucket.blob(gcs_file_path)
            
            # Determine content type
            content_type, _ = mimetypes.guess_type(local_file_path)
            if content_type:
                blob.content_type = content_type
            
            # Upload file
            with open(local_file_path, 'rb') as file_data:
                blob.upload_from_file(file_data, content_type=content_type)
            
            gcs_uri = f"gs://{bucket_name}/{gcs_file_path}"
            print(f"✅ Uploaded: {os.path.basename(local_file_path)} -> {gcs_uri}")
            
            return gcs_uri
            
        except Exception as e:
            print(f"❌ Error uploading file {local_file_path}: {e}")
            raise

    def process_document_with_ai(self, gcs_uri: str, document_type: str) -> Dict[str, Any]:
        """Simplified document processing without Vision API/Document AI"""
        
        extracted_info = {
            "gcs_uri": gcs_uri,
            "document_type": document_type,
            "processed_at": datetime.utcnow().isoformat(),
            "extraction_method": "simplified_processing",
            "extracted_data": {
                "note": "Simplified processing for deployment - Vision API/Document AI not available",
                "confidence_score": 0.5
            },
            "confidence_score": 0.5
        }
        
        print(f"🤖 Processing {document_type} with simplified AI...")
        print(f"   ⚠️ Note: Full Vision API/Document AI processing not available in deployment")
        
        return extracted_info

    def create_bigquery_tables(self):
        """Create BigQuery tables if they don't exist"""
        print("📊 Setting up BigQuery tables...")
        
        # Create datasets
        for dataset_id in [self.premium_dataset, self.claims_dataset]:
            try:
                dataset = bigquery.Dataset(f"{self.project_id}.{dataset_id}")
                dataset.location = "US"
                dataset.description = f"Insurance data for {dataset_id}"
                self.bq_client.create_dataset(dataset, exists_ok=True)
                print(f"✅ Created/verified dataset: {dataset_id}")
            except Exception as e:
                print(f"❌ Error creating dataset {dataset_id}: {e}")
                raise

        # Create applications table with ObjectRef support
        applications_schema = [
            bigquery.SchemaField("application_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("application_type", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("application_date", "TIMESTAMP"),
            bigquery.SchemaField("status", "STRING"),
            bigquery.SchemaField("documents_refs", "JSON"),  # ObjectRef data
            bigquery.SchemaField("ai_extractions", "JSON"),  # AI processing results
            bigquery.SchemaField("risk_score", "FLOAT"),
            bigquery.SchemaField("premium_quoted", "FLOAT"),
            bigquery.SchemaField("fraud_probability", "FLOAT"),
            bigquery.SchemaField("processing_notes", "STRING"),
            bigquery.SchemaField("created_at", "TIMESTAMP"),
            bigquery.SchemaField("updated_at", "TIMESTAMP"),
        ]
        
        table_id = f"{self.project_id}.{self.premium_dataset}.applications"
        table = bigquery.Table(table_id, schema=applications_schema)
        table.description = "Insurance applications with ObjectRef links to documents"
        
        try:
            self.bq_client.create_table(table, exists_ok=True)
            print("✅ Created/verified applications table")
        except Exception as e:
            print(f"❌ Error creating applications table: {e}")
            raise

        # Create customer profiles table
        customer_schema = [
            bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
            bigquery.SchemaField("personal_info", "JSON"),
            bigquery.SchemaField("created_timestamp", "TIMESTAMP"),
            bigquery.SchemaField("last_updated", "TIMESTAMP"),
            bigquery.SchemaField("processing_status", "STRING"),
        ]
        
        customer_table_id = f"{self.project_id}.{self.premium_dataset}.customer_profiles"
        customer_table = bigquery.Table(customer_table_id, schema=customer_schema)
        customer_table.description = "Customer profiles and personal information"
        
        try:
            self.bq_client.create_table(customer_table, exists_ok=True)
            print("✅ Created/verified customer profiles table")
        except Exception as e:
            print(f"❌ Error creating customer profiles table: {e}")
            raise

    def create_application_record(self, application_data: Dict[str, Any]) -> str:
        """Create application record in BigQuery with document references"""
        
        table_id = f"{self.project_id}.{self.premium_dataset}.applications"
        
        try:
            # Ensure the dataset and table exist
            self.create_bigquery_tables()
            
            table = self.bq_client.get_table(table_id)
            
            # Add timestamps
            current_time = datetime.utcnow()
            application_data["created_at"] = current_time.isoformat()
            application_data["updated_at"] = current_time.isoformat()
            application_data["application_date"] = current_time.isoformat()
            
            # Insert the record
            rows_to_insert = [application_data]
            errors = self.bq_client.insert_rows_json(table, rows_to_insert)
            
            if errors:
                print(f"❌ Errors inserting to BigQuery: {errors}")
                raise Exception(f"BigQuery insert failed: {errors}")
            else:
                print(f"✅ Created application record: {application_data['application_id']}")
                return application_data['application_id']
                
        except Exception as e:
            print(f"❌ Error creating application record: {e}")
            raise

    def create_customer_profile(self, customer_id: str, customer_info: Dict[str, Any]):
        """Create or update customer profile"""
        table_id = f"{self.project_id}.{self.premium_dataset}.customer_profiles"
        
        try:
            customer_data = {
                "customer_id": customer_id,
                "personal_info": json.dumps(customer_info),
                "created_timestamp": datetime.utcnow().isoformat(),
                "last_updated": datetime.utcnow().isoformat(),
                "processing_status": "ACTIVE"
            }
            
            table = self.bq_client.get_table(table_id)
            errors = self.bq_client.insert_rows_json(table, [customer_data])
            
            if errors:
                print(f"⚠️ Warning: Could not create customer profile: {errors}")
            else:
                print(f"✅ Created customer profile: {customer_id}")
                
        except Exception as e:
            print(f"⚠️ Warning: Error creating customer profile: {e}")

    def query_application(self, application_id: str) -> Dict[str, Any]:
        """Query application details from BigQuery"""
        
        query = f"""
        SELECT *
        FROM `{self.project_id}.{self.premium_dataset}.applications`
        WHERE application_id = @application_id
        """
        
        job_config = bigquery.QueryJobConfig(
            query_parameters=[
                bigquery.ScalarQueryParameter("application_id", "STRING", application_id)
            ]
        )
        
        try:
            query_job = self.bq_client.query(query, job_config=job_config)
            results = query_job.result()
            
            for row in results:
                return dict(row)
            
            return None
        except Exception as e:
            print(f"❌ Error querying application: {e}")
            return None

    def list_applications(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent applications"""
        
        query = f"""
        SELECT 
            application_id,
            customer_id,
            application_type,
            status,
            created_at
        FROM `{self.project_id}.{self.premium_dataset}.applications`
        ORDER BY created_at DESC
        LIMIT {limit}
        """
        
        try:
            query_job = self.bq_client.query(query)
            results = query_job.result()
            
            applications = []
            for row in results:
                applications.append(dict(row))
            
            return applications
        except Exception as e:
            print(f"❌ Error listing applications: {e}")
            return []


def create_sample_documents():
    """Create sample documents for testing"""
    print("📝 Creating sample documents for testing...")
    
    sample_dir = Path("sample_documents")
    sample_dir.mkdir(exist_ok=True)
    
    # Create sample text files (simulating documents)
    sample_files = [
        {
            "filename": "sample_vehicle_photo.txt",
            "content": "This is a sample vehicle photo document.\nVehicle: Toyota Camry 2020\nLicense Plate: ABC123\nCondition: Good",
            "document_type": "vehicle_photo"
        },
        {
            "filename": "sample_driver_license.txt", 
            "content": "Driver License\nName: John Doe\nLicense Number: D123456789\nExpiry: 2025-12-31\nClass: C",
            "document_type": "driver_license"
        },
        {
            "filename": "sample_application_form.txt",
            "content": "Insurance Application Form\nApplicant: John Doe\nCoverage Type: Comprehensive\nVehicle Year: 2020\nVehicle Make: Toyota",
            "document_type": "application_form"
        }
    ]
    
    created_files = []
    for file_info in sample_files:
        file_path = sample_dir / file_info["filename"]
        with open(file_path, 'w') as f:
            f.write(file_info["content"])
        
        created_files.append({
            "file_path": str(file_path),
            "document_type": file_info["document_type"]
        })
        print(f"✅ Created sample file: {file_path}")
    
    return created_files


def main():
    """Example usage of the InsuranceApplicationUploader"""
    
    print("🚀 BigQuery AI Hackathon - Insurance Application Uploader (Deployment Version)")
    print("=" * 80)
    
    # Configuration
    PROJECT_ID = os.getenv('PROJECT_ID', 'intelligent-insurance-engine')
    
    # Initialize uploader
    try:
        uploader = InsuranceApplicationUploader(PROJECT_ID)
    except Exception as e:
        print(f"❌ Error initializing uploader: {e}")
        print("💡 Make sure your Google Cloud credentials are set up correctly")
        return
    
    # Create bucket structure
    print("\n🏗️ Setting up infrastructure...")
    try:
        uploader.create_buckets_and_folders()
        print("✅ Infrastructure setup completed")
    except Exception as e:
        print(f"❌ Error setting up infrastructure: {e}")
        return
    
    print("\n✅ Simplified uploader ready for deployment!")
    print("💡 Note: This version uses simplified processing for deployment compatibility")


if __name__ == "__main__":
    main()
