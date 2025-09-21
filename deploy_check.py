#!/usr/bin/env python3
"""
Deployment check script for Streamlit Cloud
"""

import sys
import os

def check_deployment():
    """Check if all required packages are available for deployment"""
    
    print("🔍 Checking deployment requirements...")
    print("=" * 50)
    
    # Required packages
    required_packages = [
        'streamlit',
        'pandas', 
        'numpy',
        'google.cloud.bigquery',
        'google.cloud.storage',
        'bigframes'
    ]
    
    # Optional packages
    optional_packages = [
        'google.cloud.vision',
        'google.cloud.documentai'
    ]
    
    missing_required = []
    missing_optional = []
    
    # Check required packages
    print("📦 Checking required packages...")
    for package in required_packages:
        try:
            if '.' in package:
                # Handle submodule imports
                module_parts = package.split('.')
                module = __import__(package)
                for part in module_parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} - MISSING")
            missing_required.append(package)
    
    # Check optional packages
    print("\n📦 Checking optional packages...")
    for package in optional_packages:
        try:
            if '.' in package:
                # Handle submodule imports
                module_parts = package.split('.')
                module = __import__(package)
                for part in module_parts[1:]:
                    module = getattr(module, part)
            else:
                __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ⚠️ {package} - Not available (using fallback)")
            missing_optional.append(package)
    
    # Check agent core
    print("\n🤖 Checking agent core...")
    try:
        from insurance_agent_core import InsuranceOrchestratorAgent
        print("   ✅ Agent core imported successfully")
    except ImportError as e:
        print(f"   ❌ Agent core import failed: {e}")
        missing_required.append('insurance_agent_core')
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 DEPLOYMENT SUMMARY")
    print("=" * 50)
    
    if not missing_required:
        print("✅ All required packages are available!")
        print("🚀 Ready for deployment!")
        
        if missing_optional:
            print(f"\n⚠️ Optional packages not available: {', '.join(missing_optional)}")
            print("💡 Using simplified fallback implementations")
        
        return True
    else:
        print(f"❌ Missing required packages: {', '.join(missing_required)}")
        print("🔧 Please install missing packages before deployment")
        return False

if __name__ == "__main__":
    success = check_deployment()
    sys.exit(0 if success else 1)
