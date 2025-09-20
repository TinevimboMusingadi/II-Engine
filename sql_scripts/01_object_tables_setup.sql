-- BigQuery AI Hackathon: Intelligent Insurance Engine
-- Object Tables and ObjectRef Implementation
-- Phase 1: Data Infrastructure Setup

-- =====================================================
-- OBJECT TABLES FOR UNSTRUCTURED DATA
-- =====================================================

-- Create Object Table for car images
CREATE OR REPLACE EXTERNAL TABLE `intelligent-insurance-engine.insurance_data.car_images_objects`
WITH CONNECTION `us-central1.bigquery-connection`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://ii-engine-bucket/car-images/*']
);

-- Create Object Table for insurance documents
CREATE OR REPLACE EXTERNAL TABLE `intelligent-insurance-engine.insurance_data.documents_objects`
WITH CONNECTION `us-central1.bigquery-connection`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://ii-engine-bucket/insurance-documents/*']
);

-- Create Object Table for policy documents
CREATE OR REPLACE EXTERNAL TABLE `intelligent-insurance-engine.insurance_data.policy_objects`
WITH CONNECTION `us-central1.bigquery-connection`
OPTIONS (
  object_metadata = 'SIMPLE',
  uris = ['gs://ii-engine-bucket/policy-documents/*']
);

-- =====================================================
-- MAIN DATA STRUCTURES WITH OBJECTREF
-- =====================================================

-- Customer profiles table
CREATE OR REPLACE TABLE `intelligent-insurance-engine.insurance_data.customer_profiles` (
  customer_id STRING NOT NULL,
  personal_info JSON,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  processing_status STRING DEFAULT 'PENDING'
);

-- Insurance applications table with ObjectRef
CREATE OR REPLACE TABLE `intelligent-insurance-engine.insurance_data.insurance_applications` (
  application_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  car_image_refs ARRAY<OBJECTREF>,
  document_refs ARRAY<OBJECTREF>,
  personal_info JSON,
  application_data JSON,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  processing_status STRING DEFAULT 'PENDING',
  agent_processing_timestamp TIMESTAMP,
  premium_quote FLOAT64,
  risk_score FLOAT64,
  fraud_probability FLOAT64,
  human_review_required BOOLEAN DEFAULT FALSE
);

-- Claims processing table
CREATE OR REPLACE TABLE `intelligent-insurance-engine.insurance_data.insurance_claims` (
  claim_id STRING NOT NULL,
  customer_id STRING NOT NULL,
  application_id STRING,
  car_image_refs ARRAY<OBJECTREF>,
  document_refs ARRAY<OBJECTREF>,
  claim_data JSON,
  created_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP(),
  processing_status STRING DEFAULT 'PENDING',
  premium_amount FLOAT64,
  risk_score FLOAT64,
  fraud_probability FLOAT64,
  claim_amount FLOAT64,
  approval_status STRING DEFAULT 'PENDING'
);

-- =====================================================
-- VIEWS FOR MULTIMODAL DATA PROCESSING
-- =====================================================

-- Combined customer view with ObjectRef metadata
CREATE OR REPLACE VIEW `intelligent-insurance-engine.insurance_data.customer_multimodal_view` AS
SELECT
  c.customer_id,
  c.personal_info,
  c.created_timestamp,
  c.processing_status,
  -- Car images from Object Table
  ARRAY_AGG(
    STRUCT(
      i.uri AS image_uri,
      i.content_type AS content_type,
      i.size AS file_size,
      i.last_modified AS last_modified
    )
  ) as car_images,
  -- Documents from Object Table
  ARRAY_AGG(
    STRUCT(
      d.uri AS document_uri,
      d.content_type AS content_type,
      d.size AS file_size,
      d.last_modified AS last_modified
    )
  ) as documents
FROM `intelligent-insurance-engine.insurance_data.customer_profiles` c
LEFT JOIN `intelligent-insurance-engine.insurance_data.car_images_objects` i
  ON c.customer_id = REGEXP_EXTRACT(i.uri, r'car-images/([^/]+)')
LEFT JOIN `intelligent-insurance-engine.insurance_data.documents_objects` d
  ON c.customer_id = REGEXP_EXTRACT(d.uri, r'documents/([^/]+)')
GROUP BY c.customer_id, c.personal_info, c.created_timestamp, c.processing_status;

-- =====================================================
-- SAMPLE DATA INSERTION (for demo purposes)
-- =====================================================

-- Insert sample customer profile
INSERT INTO `intelligent-insurance-engine.insurance_data.customer_profiles` (customer_id, personal_info, processing_status)
VALUES
  ('CUST_001', JSON('{"name": "John Doe", "age": 35, "driving_years": 15, "location": "CA", "coverage_type": "Standard"}'), 'PENDING'),
  ('CUST_002', JSON('{"name": "Jane Smith", "age": 28, "driving_years": 8, "location": "NY", "coverage_type": "Premium"}'), 'PENDING'),
  ('CUST_003', JSON('{"name": "Mike Johnson", "age": 42, "driving_years": 22, "location": "TX", "coverage_type": "Basic"}'), 'PENDING');

-- =====================================================
-- BIGQUERY ML MODELS SETUP
-- =====================================================

-- Risk Scoring Model (placeholder - will be trained in Phase 3)
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.risk_scoring_model`
OPTIONS(
  model_type='LOGISTIC_REG',
  input_label_cols=['risk_category']
) AS
SELECT
  age,
  driving_years,
  location_risk_factor,
  car_value,
  previous_claims,
  CASE
    WHEN RAND() < 0.3 THEN 'HIGH'
    WHEN RAND() < 0.6 THEN 'MEDIUM'
    ELSE 'LOW'
  END as risk_category
FROM UNNEST([
  STRUCT(25, 3, 1.2, 25000, 0),
  STRUCT(35, 10, 1.0, 35000, 1),
  STRUCT(45, 20, 0.8, 45000, 2),
  STRUCT(30, 8, 1.1, 30000, 0),
  STRUCT(40, 15, 0.9, 40000, 1)
]);

-- Premium Calculation Model (placeholder - will be trained in Phase 3)
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.premium_calculation_model`
OPTIONS(
  model_type='LINEAR_REG',
  input_label_cols=['premium_amount']
) AS
SELECT
  risk_score,
  coverage_type,
  car_value,
  location_factor,
  base_premium + (risk_score * 100) + (car_value * 0.001) as premium_amount
FROM UNNEST([
  STRUCT(65, 'Basic', 25000, 1.0, 800),
  STRUCT(45, 'Standard', 35000, 1.1, 1200),
  STRUCT(25, 'Premium', 45000, 1.2, 1800),
  STRUCT(55, 'Basic', 30000, 0.9, 950),
  STRUCT(35, 'Standard', 40000, 1.0, 1400)
]);

-- Fraud Detection Model (placeholder - will be trained in Phase 3)
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.fraud_detection_model`
OPTIONS(
  model_type='ANOMALY_DETECTION'
) AS
SELECT
  claim_amount,
  time_to_claim_hours,
  previous_claims_count,
  risk_score,
  documentation_score
FROM UNNEST([
  STRUCT(2500, 24, 0, 45, 85),
  STRUCT(15000, 2, 3, 75, 45),
  STRUCT(800, 168, 0, 35, 90),
  STRUCT(3200, 12, 1, 55, 78),
  STRUCT(12500, 1, 2, 80, 52)
]);
