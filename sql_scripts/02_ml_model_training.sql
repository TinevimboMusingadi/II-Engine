-- BigQuery AI Hackathon: Intelligent Insurance Engine
-- BigQuery ML Model Training Scripts
-- Phase 3: ML Model Training

-- =====================================================
-- RISK SCORING MODEL TRAINING
-- =====================================================

-- Create enhanced risk scoring model with more features
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.risk_scoring_model_v2`
OPTIONS(
  model_type='LOGISTIC_REG',
  input_label_cols=['risk_category'],
  l2_reg=0.1,
  max_iterations=100,
  early_stop=True
) AS
SELECT
  -- Customer demographics
  age,
  driving_years,
  CASE
    WHEN age < 25 THEN 1.5
    WHEN age < 35 THEN 1.2
    WHEN age < 50 THEN 1.0
    WHEN age < 65 THEN 1.1
    ELSE 1.3
  END as age_risk_factor,

  -- Location-based risk factors
  CASE location
    WHEN 'CA' THEN 1.2
    WHEN 'NY' THEN 1.5
    WHEN 'TX' THEN 1.1
    WHEN 'FL' THEN 1.4
    WHEN 'IL' THEN 1.0
    WHEN 'PA' THEN 1.1
    WHEN 'OH' THEN 1.0
    WHEN 'GA' THEN 1.3
    WHEN 'NC' THEN 1.2
    WHEN 'MI' THEN 1.1
    ELSE 1.0
  END as location_risk_factor,

  -- Vehicle-based factors
  car_value,
  CASE
    WHEN car_value > 50000 THEN 1.4
    WHEN car_value > 30000 THEN 1.2
    WHEN car_value > 15000 THEN 1.0
    ELSE 0.8
  END as car_value_risk_factor,

  -- Driving history
  previous_claims,
  CASE
    WHEN previous_claims = 0 THEN 0.7
    WHEN previous_claims = 1 THEN 1.0
    WHEN previous_claims = 2 THEN 1.3
    WHEN previous_claims >= 3 THEN 1.6
    ELSE 1.0
  END as claims_history_factor,

  -- Coverage type risk adjustment
  CASE coverage_type
    WHEN 'Basic' THEN 0.8
    WHEN 'Standard' THEN 1.0
    WHEN 'Premium' THEN 1.2
    ELSE 1.0
  END as coverage_risk_factor,

  -- Calculated risk category based on historical data patterns
  CASE
    WHEN (age < 25 AND previous_claims > 1) OR
         (location IN ('NY', 'FL') AND car_value > 40000) OR
         (previous_claims >= 3) THEN 'HIGH'
    WHEN (age < 35 AND previous_claims = 0 AND location NOT IN ('NY', 'FL')) OR
         (driving_years > 15 AND previous_claims <= 1) THEN 'LOW'
    ELSE 'MEDIUM'
  END as risk_category

FROM (
  SELECT
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.age') AS INT64) as age,
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.driving_years') AS INT64) as driving_years,
    JSON_EXTRACT_SCALAR(personal_info, '$.location') as location,
    CAST(COALESCE(estimated_value, 25000) AS FLOAT64) as car_value,
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.previous_claims') AS INT64) as previous_claims,
    JSON_EXTRACT_SCALAR(personal_info, '$.coverage_type') as coverage_type
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
  WHERE JSON_EXTRACT_SCALAR(personal_info, '$.age') IS NOT NULL
) customer_data;

-- =====================================================
-- PREMIUM CALCULATION MODEL TRAINING
-- =====================================================

-- Create enhanced premium calculation model
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.premium_calculation_model_v2`
OPTIONS(
  model_type='LINEAR_REG',
  input_label_cols=['premium_amount'],
  l2_reg=0.01,
  max_iterations=100,
  early_stop=True
) AS
SELECT
  -- Base features
  risk_score,
  coverage_type,
  car_value,
  location,

  -- Additional features for better prediction
  age,
  driving_years,
  previous_claims,

  -- Location factors
  CASE location
    WHEN 'CA' THEN 1.2
    WHEN 'NY' THEN 1.4
    WHEN 'TX' THEN 1.1
    WHEN 'FL' THEN 1.3
    ELSE 1.0
  END as location_factor,

  -- Coverage multipliers
  CASE coverage_type
    WHEN 'Basic' THEN 0.8
    WHEN 'Standard' THEN 1.0
    WHEN 'Premium' THEN 1.3
    ELSE 1.0
  END as coverage_multiplier,

  -- Risk-based base premium calculation
  CASE
    WHEN risk_score >= 80 THEN 1200
    WHEN risk_score >= 60 THEN 900
    WHEN risk_score >= 40 THEN 700
    WHEN risk_score >= 20 THEN 500
    ELSE 400
  END as base_premium,

  -- Final premium amount (what we want to predict)
  ROUND(
    CASE
      WHEN risk_score >= 80 THEN 1200
      WHEN risk_score >= 60 THEN 900
      WHEN risk_score >= 40 THEN 700
      WHEN risk_score >= 20 THEN 500
      ELSE 400
    END * CASE coverage_type
      WHEN 'Basic' THEN 0.8
      WHEN 'Standard' THEN 1.0
      WHEN 'Premium' THEN 1.3
      ELSE 1.0
    END * CASE location
      WHEN 'CA' THEN 1.2
      WHEN 'NY' THEN 1.4
      WHEN 'TX' THEN 1.1
      WHEN 'FL' THEN 1.3
      ELSE 1.0
    END * (1 + (car_value - 25000) * 0.00001) * (1 + GREATEST(0, previous_claims - 1) * 0.1),
    2
  ) as premium_amount

FROM (
  SELECT
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.age') AS INT64) as age,
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.driving_years') AS INT64) as driving_years,
    JSON_EXTRACT_SCALAR(personal_info, '$.location') as location,
    CAST(JSON_EXTRACT_SCALAR(personal_info, '$.previous_claims') AS INT64) as previous_claims,
    CAST(COALESCE(estimated_value, 25000) AS FLOAT64) as car_value,
    JSON_EXTRACT_SCALAR(personal_info, '$.coverage_type') as coverage_type,
    CAST((ABS(FARM_FINGERPRINT(TO_JSON_STRING(personal_info))) % 100) AS FLOAT64) as risk_score
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
  WHERE JSON_EXTRACT_SCALAR(personal_info, '$.age') IS NOT NULL
) training_data;

-- =====================================================
-- FRAUD DETECTION MODEL TRAINING
-- =====================================================

-- Create enhanced fraud detection model
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.fraud_detection_model_v2`
OPTIONS(
  model_type='ANOMALY_DETECTION',
  contamination=0.1  -- 10% of data expected to be anomalies
) AS
SELECT
  -- Claim features
  claim_amount,
  time_to_claim_hours,
  previous_claims_count,
  risk_score,
  documentation_score,

  -- Additional fraud indicators
  CASE
    WHEN claim_amount > 50000 THEN 1.5
    WHEN claim_amount > 25000 THEN 1.2
    WHEN claim_amount > 10000 THEN 1.0
    ELSE 0.8
  END as claim_amount_indicator,

  CASE
    WHEN time_to_claim_hours < 24 THEN 1.4  -- Very quick claims are suspicious
    WHEN time_to_claim_hours < 72 THEN 1.1  -- Quick claims are somewhat suspicious
    WHEN time_to_claim_hours > 720 THEN 1.2 -- Very delayed claims are suspicious
    ELSE 1.0
  END as timing_indicator,

  CASE
    WHEN previous_claims_count >= 3 THEN 1.6
    WHEN previous_claims_count = 2 THEN 1.3
    WHEN previous_claims_count = 1 THEN 1.1
    ELSE 0.9
  END as history_indicator,

  CASE
    WHEN risk_score > 70 THEN 1.3
    WHEN risk_score > 50 THEN 1.1
    ELSE 1.0
  END as risk_indicator,

  CASE
    WHEN documentation_score < 50 THEN 1.5
    WHEN documentation_score < 75 THEN 1.2
    ELSE 1.0
  END as documentation_indicator,

  -- Fraud score (0 = legitimate, 1 = suspicious)
  CASE
    WHEN (claim_amount > 30000 AND time_to_claim_hours < 48) OR
         (previous_claims_count >= 3 AND claim_amount > 20000) OR
         (risk_score > 80 AND documentation_score < 60) THEN 1
    WHEN (claim_amount > 15000 AND time_to_claim_hours < 24) OR
         (previous_claims_count >= 2 AND documentation_score < 70) THEN 1
    ELSE 0
  END as is_fraud

FROM (
  SELECT
    CAST((ABS(FARM_FINGERPRINT(customer_id)) % 50000) + 1000 AS FLOAT64) as claim_amount,
    CAST(ABS(FARM_FINGERPRINT(customer_id + '_time')) % 168 + 1 AS FLOAT64) as time_to_claim_hours,
    CAST(ABS(FARM_FINGERPRINT(customer_id + '_claims')) % 5 AS INT64) as previous_claims_count,
    CAST((ABS(FARM_FINGERPRINT(customer_id + '_risk')) % 100) AS FLOAT64) as risk_score,
    CAST((ABS(FARM_FINGERPRINT(customer_id + '_doc')) % 100) AS FLOAT64) as documentation_score
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
) fraud_training_data;

-- =====================================================
-- MODEL EVALUATION QUERIES
-- =====================================================

-- Evaluate risk scoring model
SELECT
  'Risk Scoring Model' as model_name,
  COUNT(*) as total_predictions,
  COUNTIF(predicted_risk_category = risk_category) as correct_predictions,
  ROUND(COUNTIF(predicted_risk_category = risk_category) / COUNT(*) * 100, 2) as accuracy,
  COUNTIF(predicted_risk_category = 'HIGH' AND risk_category = 'HIGH') as true_positives,
  COUNTIF(predicted_risk_category = 'HIGH' AND risk_category != 'HIGH') as false_positives,
  COUNTIF(predicted_risk_category != 'HIGH' AND risk_category = 'HIGH') as false_negatives
FROM (
  SELECT
    ML.PREDICT(
      MODEL `intelligent-insurance-engine.insurance_data.risk_scoring_model_v2`,
      (
        SELECT
          age,
          driving_years,
          CASE location
            WHEN 'CA' THEN 1.2
            WHEN 'NY' THEN 1.5
            WHEN 'TX' THEN 1.1
            WHEN 'FL' THEN 1.4
            ELSE 1.0
          END as location_risk_factor,
          car_value,
          previous_claims,
          CASE coverage_type
            WHEN 'Basic' THEN 0.8
            WHEN 'Standard' THEN 1.0
            WHEN 'Premium' THEN 1.2
            ELSE 1.0
          END as coverage_risk_factor
        FROM UNNEST([
          STRUCT(25 as age, 3 as driving_years, 'CA' as location, 25000 as car_value, 0 as previous_claims, 'Basic' as coverage_type),
          STRUCT(35 as age, 10 as driving_years, 'NY' as location, 35000 as car_value, 1 as previous_claims, 'Standard' as coverage_type),
          STRUCT(45 as age, 20 as driving_years, 'TX' as location, 45000 as car_value, 2 as previous_claims, 'Premium' as coverage_type)
        ])
      )
    ).predicted_risk_category,
    'MEDIUM' as risk_category
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
  LIMIT 100
);

-- Evaluate premium calculation model
SELECT
  'Premium Calculation Model' as model_name,
  COUNT(*) as total_predictions,
  AVG(ABS(predicted_premium_amount - premium_amount)) as mean_absolute_error,
  AVG(ABS(predicted_premium_amount - premium_amount) / premium_amount) as mean_absolute_percentage_error,
  CORR(predicted_premium_amount, premium_amount) as correlation
FROM (
  SELECT
    ML.PREDICT(
      MODEL `intelligent-insurance-engine.insurance_data.premium_calculation_model_v2`,
      (
        SELECT
          risk_score,
          coverage_type,
          car_value,
          location,
          age,
          driving_years,
          previous_claims
        FROM UNNEST([
          STRUCT(65.0 as risk_score, 'Basic' as coverage_type, 25000 as car_value, 'CA' as location, 35 as age, 15 as driving_years, 1 as previous_claims),
          STRUCT(45.0 as risk_score, 'Standard' as coverage_type, 35000 as car_value, 'NY' as location, 28 as age, 8 as driving_years, 0 as previous_claims),
          STRUCT(25.0 as risk_score, 'Premium' as coverage_type, 45000 as car_value, 'TX' as location, 42 as age, 22 as driving_years, 2 as previous_claims)
        ])
      )
    ).predicted_premium_amount,
    850.0 as premium_amount
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
  LIMIT 100
);

-- Evaluate fraud detection model
SELECT
  'Fraud Detection Model' as model_name,
  COUNT(*) as total_predictions,
  COUNTIF(is_anomaly = TRUE) as anomalies_detected,
  ROUND(COUNTIF(is_anomaly = TRUE) / COUNT(*) * 100, 2) as anomaly_rate,
  AVG(anomaly_probability) as avg_anomaly_probability
FROM (
  SELECT
    ML.DETECT_ANOMALIES(
      MODEL `intelligent-insurance-engine.insurance_data.fraud_detection_model_v2`,
      (
        SELECT
          claim_amount,
          time_to_claim_hours,
          previous_claims_count,
          risk_score,
          documentation_score
        FROM UNNEST([
          STRUCT(25000.0 as claim_amount, 24.0 as time_to_claim_hours, 0 as previous_claims_count, 45.0 as risk_score, 85.0 as documentation_score),
          STRUCT(15000.0 as claim_amount, 2.0 as time_to_claim_hours, 3 as previous_claims_count, 75.0 as risk_score, 45.0 as documentation_score),
          STRUCT(800.0 as claim_amount, 168.0 as time_to_claim_hours, 0 as previous_claims_count, 35.0 as risk_score, 90.0 as documentation_score)
        ])
      )
    ).*
  FROM `intelligent-insurance-engine.insurance_data.customer_profiles`
  LIMIT 100
);

-- =====================================================
-- MODEL DEPLOYMENT SCRIPTS
-- =====================================================

-- Update default models to use the new versions
ALTER TABLE `intelligent-insurance-engine.insurance_data.risk_scoring_model`
SET OPTIONS(
  description = 'Risk scoring model (deprecated - use v2)',
  labels = [('version', 'v1'), ('status', 'deprecated')]
);

-- Create aliases for easier model reference
CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.risk_model`
AS SELECT * FROM `intelligent-insurance-engine.insurance_data.risk_scoring_model_v2`;

CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.premium_model`
AS SELECT * FROM `intelligent-insurance-engine.insurance_data.premium_calculation_model_v2`;

CREATE OR REPLACE MODEL `intelligent-insurance-engine.insurance_data.fraud_model`
AS SELECT * FROM `intelligent-insurance-engine.insurance_data.fraud_detection_model_v2`;
