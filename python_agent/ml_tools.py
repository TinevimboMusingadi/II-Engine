"""
BigQuery AI Hackathon: Intelligent Insurance Engine
ML Tools Integration Module
Phase 2: AI Agent Core Development
"""

import bigframes.pandas as bpd
from typing import Dict, Any, Optional, Union
import json
import numpy as np
from datetime import datetime

# Configuration
PROJECT_ID = "intelligent-insurance-engine"
DATASET_ID = "insurance_data"

class InsuranceMLTools:
    """
    Tool collection for the AI agent to call ML models.
    Integrates with BigQuery ML models for insurance processing.
    """

    def __init__(self, project_id: str = PROJECT_ID, dataset_id: str = DATASET_ID):
        """
        Initialize ML Tools with BigQuery ML models.

        Args:
            project_id: Google Cloud project ID
            dataset_id: BigQuery dataset ID
        """
        self.project_id = project_id
        self.dataset_id = dataset_id

    def risk_scoring_tool(self, customer_data: Dict[str, Any]) -> float:
        """
        Tool: Risk Assessment Model
        Input: Customer demographics + car data
        Output: Risk score (0-100)

        Args:
            customer_data: Dictionary containing customer information

        Returns:
            Risk score as float (0-100)
        """
        # Extract features from customer data
        age = customer_data.get('age', 30)
        driving_years = customer_data.get('driving_years', 5)
        location = customer_data.get('location', 'UNKNOWN')
        car_value = customer_data.get('car_value', 25000)
        previous_claims = customer_data.get('previous_claims', 0)

        # Location risk factors (simplified mapping)
        location_risk_factors = {
            'CA': 1.2, 'NY': 1.5, 'TX': 1.1, 'FL': 1.4,
            'IL': 1.0, 'PA': 1.1, 'OH': 1.0, 'GA': 1.3,
            'NC': 1.2, 'MI': 1.1
        }

        location_risk = location_risk_factors.get(location, 1.0)

        # Prepare data for prediction
        prediction_data = {
            'age': [age],
            'driving_years': [driving_years],
            'location_risk_factor': [location_risk],
            'car_value': [car_value],
            'previous_claims': [previous_claims]
        }

        # Create temporary table for prediction
        temp_table = f"{self.dataset_id}.temp_risk_prediction_{int(datetime.now().timestamp())}"

        # Use BigQuery ML for prediction
        query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{temp_table}` AS
        SELECT * FROM UNNEST([{json.dumps(prediction_data)}]);

        SELECT
            ML.PREDICT(
                MODEL `{self.project_id}.{self.dataset_id}.risk_scoring_model`,
                (
                    SELECT
                        age,
                        driving_years,
                        location_risk_factor,
                        car_value,
                        previous_claims
                    FROM `{self.project_id}.{temp_table}`
                )
            ) as predictions
        """

        try:
            result = bpd.read_gbq(query)

            # Clean up temp table
            cleanup_query = f"DROP TABLE IF EXISTS `{self.project_id}.{temp_table}`"
            bpd.read_gbq(cleanup_query)

            if not result.empty:
                prediction = result.iloc[0]['predictions']
                # Convert prediction to risk score (0-100)
                risk_score = min(100, max(0, float(prediction) * 100))
                return risk_score
            else:
                return 50.0  # Default risk score

        except Exception as e:
            print(f"Error in risk scoring: {str(e)}")
            return 50.0  # Default risk score

    def premium_calculation_tool(self, risk_score: float, coverage_type: str,
                                car_value: float = 25000, location: str = 'CA') -> float:
        """
        Tool: Premium Calculation Model
        Input: Risk score + coverage preferences
        Output: Premium amount

        Args:
            risk_score: Risk score (0-100)
            coverage_type: Type of coverage (Basic, Standard, Premium)
            car_value: Value of the car
            location: Customer location

        Returns:
            Premium amount as float
        """
        # Coverage multipliers
        coverage_multipliers = {
            'Basic': 0.8,
            'Standard': 1.0,
            'Premium': 1.3
        }

        # Location premium factors
        location_factors = {
            'CA': 1.2, 'NY': 1.4, 'TX': 1.1, 'FL': 1.3,
            'IL': 1.0, 'PA': 1.1, 'OH': 1.0, 'GA': 1.2,
            'NC': 1.1, 'MI': 1.0
        }

        coverage_mult = coverage_multipliers.get(coverage_type, 1.0)
        location_factor = location_factors.get(location, 1.0)

        # Base premium calculation
        base_premium = 500  # Base annual premium
        risk_adjustment = risk_score * 10  # $10 per risk point
        car_value_adjustment = car_value * 0.002  # 0.2% of car value
        coverage_adjustment = base_premium * (coverage_mult - 1)
        location_adjustment = base_premium * (location_factor - 1)

        premium = (base_premium + risk_adjustment + car_value_adjustment +
                  coverage_adjustment + location_adjustment)

        return max(300, premium)  # Minimum premium of $300

    def fraud_detection_tool(self, claim_data: Dict[str, Any]) -> float:
        """
        Tool: Fraud Detection Model
        Input: Combined claim information
        Output: Fraud probability (0-1)

        Args:
            claim_data: Dictionary containing claim information

        Returns:
            Fraud probability as float (0-1)
        """
        # Extract features from claim data
        claim_amount = claim_data.get('claim_amount', 0)
        time_to_claim = claim_data.get('time_to_claim_hours', 24)
        previous_claims = claim_data.get('previous_claims_count', 0)
        risk_score = claim_data.get('risk_score', 50)
        documentation_score = claim_data.get('documentation_score', 75)

        # Prepare data for anomaly detection
        detection_data = {
            'claim_amount': [claim_amount],
            'time_to_claim_hours': [time_to_claim],
            'previous_claims_count': [previous_claims],
            'risk_score': [risk_score],
            'documentation_score': [documentation_score]
        }

        # Create temporary table for detection
        temp_table = f"{self.dataset_id}.temp_fraud_detection_{int(datetime.now().timestamp())}"

        # Use BigQuery ML for anomaly detection
        query = f"""
        CREATE OR REPLACE TABLE `{self.project_id}.{temp_table}` AS
        SELECT * FROM UNNEST([{json.dumps(detection_data)}]);

        SELECT
            ML.DETECT_ANOMALIES(
                MODEL `{self.project_id}.{self.dataset_id}.fraud_detection_model`,
                (
                    SELECT
                        claim_amount,
                        time_to_claim_hours,
                        previous_claims_count,
                        risk_score,
                        documentation_score
                    FROM `{self.project_id}.{temp_table}`
                )
            ) as anomalies
        """

        try:
            result = bpd.read_gbq(query)

            # Clean up temp table
            cleanup_query = f"DROP TABLE IF EXISTS `{self.project_id}.{temp_table}`"
            bpd.read_gbq(cleanup_query)

            if not result.empty:
                anomaly_result = result.iloc[0]['anomalies']
                # Extract fraud probability from anomaly detection result
                fraud_prob = min(1.0, max(0.0, float(anomaly_result)))
                return fraud_prob
            else:
                return 0.0  # Default no fraud

        except Exception as e:
            print(f"Error in fraud detection: {str(e)}")
            return 0.0  # Default no fraud

    def vehicle_valuation_tool(self, car_data: Dict[str, Any]) -> float:
        """
        Tool: Vehicle Valuation Model
        Input: Car specifications and condition
        Output: Estimated vehicle value

        Args:
            car_data: Dictionary containing car information

        Returns:
            Estimated vehicle value as float
        """
        # Extract car features
        make = car_data.get('make', 'UNKNOWN')
        model = car_data.get('model', 'UNKNOWN')
        year = car_data.get('year', 2020)
        mileage = car_data.get('mileage', 50000)
        condition = car_data.get('condition', 'Good')

        # Base values by make (simplified)
        make_base_values = {
            'TOYOTA': 25000, 'HONDA': 24000, 'FORD': 22000,
            'CHEVROLET': 21000, 'NISSAN': 20000, 'BMW': 35000,
            'MERCEDES': 38000, 'AUDI': 32000, 'LEXUS': 30000
        }

        base_value = make_base_values.get(make.upper(), 20000)

        # Age depreciation (assuming current year is 2024)
        age = 2024 - year
        age_depreciation = age * 1500  # $1500 per year depreciation

        # Mileage depreciation
        mileage_depreciation = (mileage - 50000) * 0.1  # $0.10 per mile over 50k

        # Condition adjustments
        condition_adjustments = {
            'Excellent': 1.2,
            'Very Good': 1.1,
            'Good': 1.0,
            'Fair': 0.9,
            'Poor': 0.7
        }

        condition_mult = condition_adjustments.get(condition, 1.0)

        # Calculate estimated value
        estimated_value = (base_value - age_depreciation - mileage_depreciation) * condition_mult

        return max(1000, estimated_value)  # Minimum value of $1000

    def comprehensive_risk_assessment(self, customer_data: Dict[str, Any],
                                    vehicle_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive risk assessment combining all available data.

        Args:
            customer_data: Customer demographic and history data
            vehicle_data: Vehicle specifications and condition data

        Returns:
            Dictionary containing comprehensive risk assessment
        """
        # Calculate individual risk components
        base_risk_score = self.risk_scoring_tool(customer_data)

        # Vehicle-based risk adjustments
        vehicle_value = self.vehicle_valuation_tool(vehicle_data)
        vehicle_risk_adjustment = 0

        # High-value vehicles have higher risk
        if vehicle_value > 50000:
            vehicle_risk_adjustment += 10
        elif vehicle_value > 30000:
            vehicle_risk_adjustment += 5

        # Vehicle age affects risk
        vehicle_age = 2024 - vehicle_data.get('year', 2020)
        if vehicle_age > 10:
            vehicle_risk_adjustment += 8
        elif vehicle_age > 5:
            vehicle_risk_adjustment += 3

        # Final risk score
        final_risk_score = min(100, base_risk_score + vehicle_risk_adjustment)

        # Calculate premium based on final risk
        premium_amount = self.premium_calculation_tool(
            final_risk_score,
            customer_data.get('coverage_type', 'Standard'),
            vehicle_value,
            customer_data.get('location', 'CA')
        )

        # Fraud assessment
        fraud_probability = self.fraud_detection_tool({
            'claim_amount': premium_amount * 0.5,  # Assume potential claim is 50% of premium
            'time_to_claim_hours': 24,
            'previous_claims_count': customer_data.get('previous_claims', 0),
            'risk_score': final_risk_score,
            'documentation_score': 85  # Assume good documentation
        })

        return {
            'base_risk_score': base_risk_score,
            'vehicle_risk_adjustment': vehicle_risk_adjustment,
            'final_risk_score': final_risk_score,
            'estimated_vehicle_value': vehicle_value,
            'premium_amount': premium_amount,
            'fraud_probability': fraud_probability,
            'risk_category': self._categorize_risk(final_risk_score),
            'recommendations': self._generate_recommendations(final_risk_score, fraud_probability)
        }

    def _categorize_risk(self, risk_score: float) -> str:
        """
        Categorize risk score into descriptive categories.

        Args:
            risk_score: Risk score (0-100)

        Returns:
            Risk category string
        """
        if risk_score >= 80:
            return "Very High Risk"
        elif risk_score >= 60:
            return "High Risk"
        elif risk_score >= 40:
            return "Medium Risk"
        elif risk_score >= 20:
            return "Low Risk"
        else:
            return "Very Low Risk"

    def _generate_recommendations(self, risk_score: float, fraud_probability: float) -> List[str]:
        """
        Generate recommendations based on risk assessment.

        Args:
            risk_score: Risk score (0-100)
            fraud_probability: Fraud probability (0-1)

        Returns:
            List of recommendation strings
        """
        recommendations = []

        if risk_score > 70:
            recommendations.append("Consider higher premium due to elevated risk factors")
            recommendations.append("Recommend defensive driving course for premium reduction")

        if risk_score > 50:
            recommendations.append("Suggest comprehensive coverage review")

        if fraud_probability > 0.7:
            recommendations.append("Manual review required due to high fraud indicators")
        elif fraud_probability > 0.4:
            recommendations.append("Additional documentation verification recommended")

        if risk_score < 30:
            recommendations.append("Eligible for premium discounts")
            recommendations.append("Good candidate for loyalty programs")

        return recommendations


if __name__ == "__main__":
    # Example usage
    ml_tools = InsuranceMLTools()

    # Sample customer data
    customer_data = {
        'age': 35,
        'driving_years': 15,
        'location': 'CA',
        'previous_claims': 1,
        'coverage_type': 'Standard'
    }

    vehicle_data = {
        'make': 'TOYOTA',
        'model': 'CAMRY',
        'year': 2020,
        'mileage': 45000,
        'condition': 'Good'
    }

    # Calculate risk score
    risk_score = ml_tools.risk_scoring_tool(customer_data)
    print(f"Risk Score: {risk_score}")

    # Calculate premium
    premium = ml_tools.premium_calculation_tool(risk_score, 'Standard', 25000, 'CA')
    print(f"Premium Amount: ${premium".2f"}")

    # Comprehensive assessment
    assessment = ml_tools.comprehensive_risk_assessment(customer_data, vehicle_data)
    print("Comprehensive Assessment:")
    print(json.dumps(assessment, indent=2))
