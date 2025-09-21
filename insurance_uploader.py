#!/usr/bin/env python3
"""
BigQuery AI Hackathon: Insurance Application Document Uploader
This script handles uploading insurance documents and creating BigQuery records.
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
from google.cloud import vision
from google.cloud import documentai
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class InsuranceApplicationUploader:
    """
    Handles uploading insurance application documents to Cloud Storage 
    and creating linked records in BigQuery with ObjectRef integration
    """
    
    def __init__(self, project_id: str = None):
        self.project_id = project_id or os.getenv('PROJECT_ID', 'intelligent-insurance-engine')
        
        # Initialize Google Cloud clients
        self.storage_client = storage.Client(project=self.project_id)
        self.bq_client = bigquery.Client(project=self.project_id)
        self.vision_client = vision.ImageAnnotatorClient()
        
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
        """Extract text/information from uploaded documents using AI"""
        
        extracted_info = {
            "gcs_uri": gcs_uri,
            "document_type": document_type,
            "processed_at": datetime.utcnow().isoformat(),
            "extraction_method": None,
            "extracted_data": {},
            "confidence_score": 0.0
        }
        
        try:
            print(f"🤖 Processing {document_type} with AI...")
            
            if document_type in ["vehicle_photo", "property_photo", "driver_license", "insurance_card"]:
                # Use Vision API for image analysis
                image = vision.Image()
                image.source.image_uri = gcs_uri
                
                # OCR for text extraction
                response = self.vision_client.text_detection(image=image)
                texts = response.text_annotations
                
                if texts:
                    extracted_info["extracted_data"]["full_text"] = texts[0].description
                    extracted_info["extraction_method"] = "vision_ocr"
                    extracted_info["confidence_score"] = 0.85
                    print(f"   ✅ Extracted {len(texts[0].description)} characters of text")
                
                # Object detection for vehicle/property images
                if document_type in ["vehicle_photo", "property_photo"]:
                    objects = self.vision_client.object_localization(image=image).localized_object_annotations
                    if objects:
                        extracted_info["extracted_data"]["detected_objects"] = [
                            {"name": obj.name, "score": obj.score} for obj in objects[:5]  # Top 5 objects
                        ]
                        print(f"   ✅ Detected {len(objects)} objects in image")
                
                # Label detection for additional context
                labels = self.vision_client.label_detection(image=image).label_annotations
                if labels:
                    extracted_info["extracted_data"]["labels"] = [
                        {"description": label.description, "score": label.score} 
                        for label in labels[:10]  # Top 10 labels
                    ]
                    print(f"   ✅ Generated {len(labels)} labels for image")
                
            elif document_type in ["application_form", "inspection_report", "police_report"]:
                # For structured documents - placeholder for Document AI
                extracted_info["extraction_method"] = "document_ai_placeholder"
                extracted_info["extracted_data"]["note"] = "Document AI processing would be implemented here"
                extracted_info["confidence_score"] = 0.75
                print(f"   ⏳ Document AI processing placeholder for {document_type}")
                
        except Exception as e:
            print(f"❌ Error processing document with AI: {e}")
            extracted_info["error"] = str(e)
            extracted_info["confidence_score"] = 0.0
        
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
            application_data["created_at"] = current_time
            application_data["updated_at"] = current_time
            application_data["application_date"] = current_time
            
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

    def upload_application(self, customer_id: str, application_type: str, 
                          document_files: List[Dict[str, str]], 
                          customer_info: Dict[str, Any] = None) -> str:
        """
        Main method to upload an insurance application with documents
        
        Args:
            customer_id: Customer identifier
            application_type: 'auto', 'property', or 'health'
            document_files: List of dicts with 'file_path' and 'document_type' keys
            customer_info: Optional customer information dictionary
            
        Returns:
            application_id: Generated application ID
        """
        
        application_id = f"app_{str(uuid.uuid4())[:8]}"
        documents_refs = []
        ai_extractions = []
        
        print(f"\n🚀 Processing application {application_id}")
        print(f"   Customer: {customer_id}")
        print(f"   Type: {application_type}")
        print(f"   Documents: {len(document_files)}")
        
        # Ensure bucket structure exists
        self.create_buckets_and_folders()
        
        # Process each document
        for i, doc_file in enumerate(document_files, 1):
            local_file_path = doc_file['file_path']
            document_type = doc_file['document_type']
            
            print(f"\n📄 Processing document {i}/{len(document_files)}: {document_type}")
            
            if not os.path.exists(local_file_path):
                print(f"⚠️ Warning: File not found: {local_file_path}")
                continue
            
            # Determine Cloud Storage path
            gcs_path = self.determine_file_path(application_type, document_type, 
                                              application_id, os.path.basename(local_file_path))
            
            # Upload to Cloud Storage
            gcs_uri = self.upload_file_to_gcs(local_file_path, gcs_path, self.premium_bucket)
            
            # Create ObjectRef document reference
            doc_ref = {
                "document_type": document_type,
                "bucket": self.premium_bucket,
                "file_path": gcs_path,
                "uri": gcs_uri,
                "upload_date": datetime.utcnow().isoformat(),
                "original_filename": os.path.basename(local_file_path),
                "file_size": os.path.getsize(local_file_path),
                "content_type": mimetypes.guess_type(local_file_path)[0]
            }
            documents_refs.append(doc_ref)
            
            # Process with AI
            ai_result = self.process_document_with_ai(gcs_uri, document_type)
            ai_extractions.append(ai_result)
        
        # Create application record with ObjectRefs
        application_data = {
            "application_id": application_id,
            "customer_id": customer_id,
            "application_type": application_type,
            "status": "pending",
            "documents_refs": documents_refs,  # ObjectRef data
            "ai_extractions": ai_extractions,  # AI processing results
            "risk_score": None,  # To be calculated by ML model
            "premium_quoted": None,  # To be calculated by pricing model
            "fraud_probability": None,  # To be calculated by fraud detection
            "processing_notes": f"Uploaded {len(documents_refs)} documents with AI processing"
        }
        
        # Insert into BigQuery
        self.create_application_record(application_data)
        
        # Also create/update customer profile if provided
        if customer_info:
            self.create_customer_profile(customer_id, customer_info)
        
        print(f"\n🎉 Application {application_id} uploaded successfully!")
        print(f"   Documents uploaded: {len(documents_refs)}")
        print(f"   AI extractions: {len(ai_extractions)}")
        
        return application_id

    def create_customer_profile(self, customer_id: str, customer_info: Dict[str, Any]):
        """Create or update customer profile"""
        table_id = f"{self.project_id}.{self.premium_dataset}.customer_profiles"
        
        try:
            customer_data = {
                "customer_id": customer_id,
                "personal_info": customer_info,
                "created_timestamp": datetime.utcnow(),
                "last_updated": datetime.utcnow(),
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
            created_at,
            JSON_ARRAY_LENGTH(documents_refs) as document_count
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
    
    print("🚀 BigQuery AI Hackathon - Insurance Application Uploader")
    print("=" * 60)
    
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
    
    # Create sample documents for testing
    print("\n📝 Creating sample documents...")
    try:
        document_files = create_sample_documents()
        print("✅ Sample documents created")
    except Exception as e:
        print(f"❌ Error creating sample documents: {e}")
        return
    
    # Sample customer information
    customer_info = {
        "name": "John Doe",
        "age": 35,
        "driving_years": 15,
        "location": "CA",
        "coverage_type": "Standard",
        "previous_claims": 1,
        "email": "john.doe@example.com",
        "phone": "(555) 123-4567"
    }
    
    # Upload sample application
    print("\n🚀 Uploading sample auto insurance application...")
    try:
        application_id = uploader.upload_application(
            customer_id="cust_12345",
            application_type="auto", 
            document_files=document_files,
            customer_info=customer_info
        )
        
        print(f"🎉 Application uploaded successfully: {application_id}")
        
        # Query the application back
        print(f"\n🔍 Querying application details...")
        application_data = uploader.query_application(application_id)
        if application_data:
            print("✅ Application found in BigQuery:")
            print(f"   ID: {application_data['application_id']}")
            print(f"   Customer: {application_data['customer_id']}")
            print(f"   Type: {application_data['application_type']}")
            print(f"   Status: {application_data['status']}")
            print(f"   Documents: {len(application_data.get('documents_refs', []))}")
        else:
            print("❌ Application not found")
        
        # List recent applications
        print(f"\n📋 Recent applications:")
        applications = uploader.list_applications(5)
        for app in applications:
            print(f"   • {app['application_id']} | {app['customer_id']} | {app['application_type']} | {app['status']}")
        
    except Exception as e:
        print(f"❌ Error uploading application: {e}")
        return
    
    print("\n" + "=" * 60)
    print("✅ Demo completed successfully!")
    print("\n💡 Next steps:")
    print("   • Replace sample documents with real files")
    print("   • Integrate with the AI agent for premium calculation")
    print("   • Use the Streamlit web interface for easier uploads")
    print("   • Run the complete demo notebook")


if __name__ == "__main__":
    main()
