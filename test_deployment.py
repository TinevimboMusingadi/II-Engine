#!/usr/bin/env python3
"""
Test script to verify deployment compatibility
"""

import sys
import os

print("🧪 Testing deployment compatibility...")
print("=" * 50)

# Test 1: Basic imports
print("1. Testing basic imports...")
try:
    import streamlit as st
    print("   ✅ Streamlit imported successfully")
except ImportError as e:
    print(f"   ❌ Streamlit import failed: {e}")

try:
    import pandas as pd
    print("   ✅ Pandas imported successfully")
except ImportError as e:
    print(f"   ❌ Pandas import failed: {e}")

try:
    from google.cloud import storage
    print("   ✅ Google Cloud Storage imported successfully")
except ImportError as e:
    print(f"   ❌ Google Cloud Storage import failed: {e}")

try:
    from google.cloud import bigquery
    print("   ✅ Google Cloud BigQuery imported successfully")
except ImportError as e:
    print(f"   ❌ Google Cloud BigQuery import failed: {e}")

# Test 2: Google Cloud Vision (optional)
print("\n2. Testing Google Cloud Vision (optional)...")
try:
    from google.cloud import vision
    print("   ✅ Google Cloud Vision imported successfully")
except ImportError as e:
    print(f"   ⚠️ Google Cloud Vision not available: {e}")

# Test 3: Google Cloud Document AI (optional)
print("\n3. Testing Google Cloud Document AI (optional)...")
try:
    from google.cloud import documentai
    print("   ✅ Google Cloud Document AI imported successfully")
except ImportError as e:
    print(f"   ⚠️ Google Cloud Document AI not available: {e}")

# Test 4: BigFrames
print("\n4. Testing BigFrames...")
try:
    import bigframes
    print("   ✅ BigFrames imported successfully")
except ImportError as e:
    print(f"   ❌ BigFrames import failed: {e}")

# Test 5: Agent core imports
print("\n5. Testing agent core imports...")
try:
    from insurance_agent_core import InsuranceOrchestratorAgent
    print("   ✅ InsuranceOrchestratorAgent imported successfully")
except ImportError as e:
    print(f"   ❌ InsuranceOrchestratorAgent import failed: {e}")

try:
    from insurance_agent_core import InMemoryCommunicationProtocol
    print("   ✅ InMemoryCommunicationProtocol imported successfully")
except ImportError as e:
    print(f"   ❌ InMemoryCommunicationProtocol import failed: {e}")

# Test 6: Simplified uploader
print("\n6. Testing simplified uploader...")
try:
    from insurance_uploader_simple import InsuranceApplicationUploader
    print("   ✅ Simplified uploader imported successfully")
except ImportError as e:
    print(f"   ❌ Simplified uploader import failed: {e}")

# Test 7: Streamlit app
print("\n7. Testing Streamlit app import...")
try:
    sys.path.append('web_interface')
    import insurance_app
    print("   ✅ Streamlit app imported successfully")
except ImportError as e:
    print(f"   ❌ Streamlit app import failed: {e}")
except Exception as e:
    print(f"   ⚠️ Streamlit app import had issues: {e}")

print("\n" + "=" * 50)
print("🎯 Deployment compatibility test completed!")
print("=" * 50)
