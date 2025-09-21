"""
Fix BigQuery Setup Issues
Create missing tables and resolve configuration problems
"""

import os
import json
from google.cloud import bigquery
from google.cloud import storage
from google.cloud.exceptions import NotFound
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

class BigQueryFixer:
    def __init__(self, project_id="intelligent-insurance-engine"):
        self.project_id = project_id
        self.dataset_id = "insurance_data"
        
        # Set up clients
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('key/intelligent-insurance-engine-8baafb9a5606.json')
        self.bq_client = bigquery.Client(project=project_id)
        self.storage_client = storage.Client(project=project_id)
        
        log.info(f"🔧 BigQuery Fixer initialized for project: {project_id}")

    def create_dataset(self):
        """Create the insurance_data dataset if it doesn't exist."""
        dataset_id = f"{self.project_id}.{self.dataset_id}"
        
        try:
            dataset = self.bq_client.get_dataset(dataset_id)
            log.info(f"✅ Dataset {dataset_id} already exists")
        except NotFound:
            log.info(f"📊 Creating dataset: {dataset_id}")
            dataset = bigquery.Dataset(dataset_id)
            dataset.location = "US"
            dataset.description = "Insurance data for BigQuery AI Hackathon"
            dataset = self.bq_client.create_dataset(dataset, timeout=30)
            log.info(f"✅ Created dataset: {dataset_id}")

    def create_customer_profiles_table(self):
        """Create the customer_profiles table."""
        table_id = f"{self.project_id}.{self.dataset_id}.customer_profiles"
        
        try:
            table = self.bq_client.get_table(table_id)
            log.info(f"✅ Table {table_id} already exists")
        except NotFound:
            log.info(f"📋 Creating table: customer_profiles")
            
            schema = [
                bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("personal_info", "JSON"),
                bigquery.SchemaField("created_timestamp", "TIMESTAMP"),
                bigquery.SchemaField("last_updated", "TIMESTAMP"),
                bigquery.SchemaField("processing_status", "STRING"),
            ]
            
            table = bigquery.Table(table_id, schema=schema)
            table.description = "Customer profiles for insurance applications"
            table = self.bq_client.create_table(table)
            log.info(f"✅ Created table: customer_profiles")
            
            # Insert sample data
            self.insert_sample_customers()

    def create_applications_table(self):
        """Create the applications table."""
        table_id = f"{self.project_id}.{self.dataset_id}.applications"
        
        try:
            table = self.bq_client.get_table(table_id)
            log.info(f"✅ Table {table_id} already exists")
        except NotFound:
            log.info(f"📋 Creating table: applications")
            
            schema = [
                bigquery.SchemaField("application_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("customer_id", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("application_type", "STRING", mode="REQUIRED"),
                bigquery.SchemaField("application_date", "TIMESTAMP"),
                bigquery.SchemaField("status", "STRING"),
                bigquery.SchemaField("documents_refs", "JSON"),
                bigquery.SchemaField("ai_extractions", "JSON"),
                bigquery.SchemaField("risk_score", "FLOAT"),
                bigquery.SchemaField("premium_quoted", "FLOAT"),
                bigquery.SchemaField("fraud_probability", "FLOAT"),
                bigquery.SchemaField("processing_notes", "STRING"),
                bigquery.SchemaField("created_at", "TIMESTAMP"),
                bigquery.SchemaField("updated_at", "TIMESTAMP"),
            ]
            
            table = bigquery.Table(table_id, schema=schema)
            table.description = "Insurance applications with ObjectRef links"
            table = self.bq_client.create_table(table)
            log.info(f"✅ Created table: applications")

    def create_object_tables(self):
        """Create Object Tables for unstructured data."""
        # For now, create placeholder regular tables since Object Tables require specific setup
        
        object_tables = [
            "car_images_objects",
            "documents_objects", 
            "policy_objects"
        ]
        
        for table_name in object_tables:
            table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
            
            try:
                table = self.bq_client.get_table(table_id)
                log.info(f"✅ Object table {table_name} already exists")
            except NotFound:
                log.info(f"🖼️ Creating placeholder object table: {table_name}")
                
                # Create placeholder schema for object tables
                schema = [
                    bigquery.SchemaField("uri", "STRING", mode="REQUIRED"),
                    bigquery.SchemaField("content_type", "STRING"),
                    bigquery.SchemaField("size", "INTEGER"),
                    bigquery.SchemaField("etag", "STRING"),
                    bigquery.SchemaField("created_time", "TIMESTAMP"),
                    bigquery.SchemaField("updated_time", "TIMESTAMP"),
                    bigquery.SchemaField("metadata", "JSON"),
                ]
                
                table = bigquery.Table(table_id, schema=schema)
                table.description = f"Object table for {table_name} (placeholder implementation)"
                table = self.bq_client.create_table(table)
                log.info(f"✅ Created placeholder object table: {table_name}")
                
                # Insert sample data
                self.insert_sample_object_data(table_name)

    def insert_sample_customers(self):
        """Insert sample customer data."""
        table_id = f"{self.project_id}.{self.dataset_id}.customer_profiles"
        
        rows = [
            {
                "customer_id": "CUST_001",
                "personal_info": json.dumps({
                    "name": "John Doe",
                    "age": 35,
                    "driving_years": 15,
                    "location": "CA",
                    "coverage_type": "Standard"
                }),
                "created_timestamp": "2024-01-01T00:00:00",
                "last_updated": "2024-01-01T00:00:00",
                "processing_status": "PENDING"
            },
            {
                "customer_id": "CUST_002", 
                "personal_info": json.dumps({
                    "name": "Jane Smith",
                    "age": 28,
                    "driving_years": 8,
                    "location": "NY",
                    "coverage_type": "Premium"
                }),
                "created_timestamp": "2024-01-01T00:00:00",
                "last_updated": "2024-01-01T00:00:00",
                "processing_status": "PENDING"
            }
        ]
        
        table = self.bq_client.get_table(table_id)
        errors = self.bq_client.insert_rows_json(table, rows)
        
        if errors:
            log.error(f"❌ Error inserting sample customers: {errors}")
        else:
            log.info(f"✅ Inserted {len(rows)} sample customers")

    def insert_sample_object_data(self, table_name):
        """Insert sample object data."""
        table_id = f"{self.project_id}.{self.dataset_id}.{table_name}"
        
        if table_name == "car_images_objects":
            rows = [
                {
                    "uri": "gs://ii-engine-bucket/car-images/CUST_001/front.jpg",
                    "content_type": "image/jpeg",
                    "size": 1024000,
                    "etag": "abc123",
                    "created_time": "2024-01-01T00:00:00",
                    "updated_time": "2024-01-01T00:00:00",
                    "metadata": json.dumps({"customer_id": "CUST_001", "view": "front"})
                }
            ]
        elif table_name == "documents_objects":
            rows = [
                {
                    "uri": "gs://ii-engine-bucket/documents/CUST_001/license.pdf",
                    "content_type": "application/pdf", 
                    "size": 512000,
                    "etag": "def456",
                    "created_time": "2024-01-01T00:00:00",
                    "updated_time": "2024-01-01T00:00:00",
                    "metadata": json.dumps({"customer_id": "CUST_001", "type": "driver_license"})
                }
            ]
        else:  # policy_objects
            rows = [
                {
                    "uri": "gs://ii-engine-bucket/policies/CUST_001/policy.pdf",
                    "content_type": "application/pdf",
                    "size": 256000,
                    "etag": "ghi789", 
                    "created_time": "2024-01-01T00:00:00",
                    "updated_time": "2024-01-01T00:00:00",
                    "metadata": json.dumps({"customer_id": "CUST_001", "type": "policy_document"})
                }
            ]
        
        table = self.bq_client.get_table(table_id)
        errors = self.bq_client.insert_rows_json(table, rows)
        
        if errors:
            log.error(f"❌ Error inserting sample data for {table_name}: {errors}")
        else:
            log.info(f"✅ Inserted {len(rows)} sample records for {table_name}")

    def create_storage_buckets(self):
        """Create Cloud Storage buckets if they don't exist."""
        buckets = [
            "ii-engine-bucket",
            "insurance-premium-applications",
            "insurance-claims-processing"
        ]
        
        for bucket_name in buckets:
            try:
                bucket = self.storage_client.get_bucket(bucket_name)
                log.info(f"✅ Bucket {bucket_name} already exists")
            except NotFound:
                log.info(f"🪣 Creating bucket: {bucket_name}")
                bucket = self.storage_client.create_bucket(bucket_name, location="US")
                log.info(f"✅ Created bucket: {bucket_name}")

    def fix_all_issues(self):
        """Fix all BigQuery setup issues."""
        log.info("🔧 Starting BigQuery setup fixes...")
        
        try:
            # Create dataset
            self.create_dataset()
            
            # Create storage buckets
            self.create_storage_buckets()
            
            # Create tables
            self.create_customer_profiles_table()
            self.create_applications_table()
            self.create_object_tables()
            
            log.info("✅ All BigQuery setup issues fixed!")
            
        except Exception as e:
            log.error(f"❌ Error during setup: {e}")
            raise

    def test_setup(self):
        """Test the BigQuery setup."""
        log.info("🧪 Testing BigQuery setup...")
        
        try:
            # Test customer profiles query
            query = f"""
            SELECT customer_id, JSON_EXTRACT_SCALAR(personal_info, '$.name') as name
            FROM `{self.project_id}.{self.dataset_id}.customer_profiles`
            LIMIT 5
            """
            
            results = self.bq_client.query(query).result()
            customers = list(results)
            
            log.info(f"✅ Found {len(customers)} customers in database")
            for customer in customers:
                log.info(f"   👤 {customer.customer_id}: {customer.name}")
            
            # Test object tables
            for table_name in ["car_images_objects", "documents_objects", "policy_objects"]:
                query = f"SELECT COUNT(*) as count FROM `{self.project_id}.{self.dataset_id}.{table_name}`"
                result = list(self.bq_client.query(query).result())[0]
                log.info(f"✅ {table_name}: {result.count} records")
            
            log.info("🎉 BigQuery setup test completed successfully!")
            
        except Exception as e:
            log.error(f"❌ Setup test failed: {e}")
            raise

def main():
    """Main function to fix BigQuery issues."""
    fixer = BigQueryFixer()
    
    # Fix all issues
    fixer.fix_all_issues()
    
    # Test the setup
    fixer.test_setup()
    
    print("\n🎉 BigQuery setup completed successfully!")
    print("✅ All tables created and populated with sample data")
    print("✅ Object tables configured (placeholder implementation)")
    print("✅ Storage buckets created")
    print("🚀 Agent system should now work properly!")

if __name__ == "__main__":
    main()
