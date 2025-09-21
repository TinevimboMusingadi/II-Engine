"""
Test file upload functionality to Cloud Storage
"""

import os
import json
from datetime import datetime
from google.cloud import storage
import tempfile
from PIL import Image
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

def create_test_files():
    """Create test files for upload."""
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    
    # Create a test image
    img = Image.new('RGB', (100, 100), color='blue')
    image_path = os.path.join(temp_dir, 'test_car.jpg')
    img.save(image_path, 'JPEG')
    
    # Create a test document
    doc_path = os.path.join(temp_dir, 'test_license.txt')
    with open(doc_path, 'w') as f:
        f.write("Test driver license document\nName: John Doe\nLicense: ABC123456")
    
    return image_path, doc_path

def test_upload_to_bucket():
    """Test uploading files to Cloud Storage."""
    
    # Set up credentials
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath('key/intelligent-insurance-engine-8baafb9a5606.json')
    
    # Initialize client
    storage_client = storage.Client(project="intelligent-insurance-engine")
    bucket_name = "insurance-premium-applications"
    
    try:
        # Get the bucket
        bucket = storage_client.bucket(bucket_name)
        
        # Create test files
        image_path, doc_path = create_test_files()
        
        log.info(f"📁 Created test files:")
        log.info(f"   🖼️ Image: {image_path}")
        log.info(f"   📄 Document: {doc_path}")
        
        # Upload image
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_blob_name = f"auto-applications/vehicle-photos/test_car_{timestamp}.jpg"
        image_blob = bucket.blob(image_blob_name)
        
        with open(image_path, 'rb') as f:
            image_blob.upload_from_file(f, content_type='image/jpeg')
        
        image_uri = f"gs://{bucket_name}/{image_blob_name}"
        log.info(f"✅ Uploaded image: {image_uri}")
        
        # Upload document
        doc_blob_name = f"auto-applications/driver-documents/test_license_{timestamp}.txt"
        doc_blob = bucket.blob(doc_blob_name)
        
        with open(doc_path, 'rb') as f:
            doc_blob.upload_from_file(f, content_type='text/plain')
        
        doc_uri = f"gs://{bucket_name}/{doc_blob_name}"
        log.info(f"✅ Uploaded document: {doc_uri}")
        
        # List files in bucket
        log.info(f"\n📂 Files in bucket {bucket_name}:")
        blobs = bucket.list_blobs(prefix="auto-applications/")
        for blob in blobs:
            if not blob.name.endswith('/'):  # Skip folder markers
                log.info(f"   📄 {blob.name} ({blob.size} bytes)")
        
        # Clean up local files
        os.remove(image_path)
        os.remove(doc_path)
        os.rmdir(os.path.dirname(image_path))
        
        return image_uri, doc_uri
        
    except Exception as e:
        log.error(f"❌ Upload test failed: {e}")
        raise

def test_streamlit_upload_simulation():
    """Simulate what happens when files are uploaded via Streamlit."""
    
    log.info("\n🎬 SIMULATING STREAMLIT FILE UPLOAD")
    log.info("=" * 50)
    
    try:
        # Upload test files
        image_uri, doc_uri = test_upload_to_bucket()
        
        # Create application data like Streamlit would
        application_data = {
            "customer_id": f"CUST_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "personal_info": {
                "name": "Test Customer",
                "age": 35,
                "driving_years": 15,
                "location": "CA",
                "coverage_type": "Standard"
            },
            "car_image_refs": [image_uri],
            "document_refs": [doc_uri]
        }
        
        log.info(f"📋 Created application data:")
        log.info(json.dumps(application_data, indent=2))
        
        log.info(f"\n✅ SUCCESS: Files uploaded and ready for agent processing!")
        log.info(f"🖼️ Car image: {image_uri}")
        log.info(f"📄 Document: {doc_uri}")
        
        return application_data
        
    except Exception as e:
        log.error(f"❌ Streamlit simulation failed: {e}")
        raise

def main():
    """Main test function."""
    log.info("🧪 Testing file upload functionality...")
    
    try:
        # Test the upload process
        application_data = test_streamlit_upload_simulation()
        
        log.info(f"\n🎉 FILE UPLOAD TEST SUCCESSFUL!")
        log.info(f"✅ Files are now in Cloud Storage")
        log.info(f"✅ Application data ready for agent processing")
        log.info(f"🚀 The Streamlit app file uploads should now work!")
        
    except Exception as e:
        log.error(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 All file upload tests passed!")
    else:
        print("\n⚠️ Some tests failed - check the logs above")
