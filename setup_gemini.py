#!/usr/bin/env python3
"""
BigQuery AI Hackathon: Intelligent Insurance Engine
Gemini API Setup Script
Configure Gemini 2.5 Flash Lite for LLM-powered agent system
"""

import os
import sys
from pathlib import Path

def setup_gemini_api():
    """Setup Gemini API key for LLM-powered agent system."""
    
    print("🧠 Setting up Gemini 2.5 Flash Lite for Intelligent Insurance Engine")
    print("=" * 70)
    
    # Check if API key is already set
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ GOOGLE_API_KEY already set: {api_key[:10]}...")
        return True
    
    print("\n📋 To use the LLM-powered agent system, you need a Gemini API key.")
    print("\n🔗 Get your API key from: https://makersuite.google.com/app/apikey")
    print("\n💡 You can set it in several ways:")
    print("   1. Environment variable: export GOOGLE_API_KEY='your_key_here'")
    print("   2. .env file: Add GOOGLE_API_KEY=your_key_here to .env")
    print("   3. System environment: Set GOOGLE_API_KEY in your system")
    
    # Try to create .env file
    env_file = Path('.env')
    if not env_file.exists():
        print(f"\n📝 Creating .env file template...")
        with open('.env', 'w') as f:
            f.write("# BigQuery AI Hackathon: Intelligent Insurance Engine\n")
            f.write("# Add your API keys here\n\n")
            f.write("# Gemini API Key for LLM-powered agent system\n")
            f.write("GOOGLE_API_KEY=your_gemini_api_key_here\n\n")
            f.write("# Google Cloud Project ID\n")
            f.write("GOOGLE_CLOUD_PROJECT=intelligent-insurance-engine\n")
            f.write("GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service-account-key.json\n")
        
        print("✅ Created .env file template")
        print("   Please edit .env and add your actual API keys")
    
    print("\n🚀 After setting up your API key, the agent system will automatically use:")
    print("   • Gemini 2.5 Flash Lite for intelligent tool selection")
    print("   • Enhanced report generation with AI insights")
    print("   • Advanced decision making for insurance processing")
    
    print("\n⚠️  Note: Without the API key, the system will use fallback rule-based routing")
    print("   The system will still work but won't have LLM-powered intelligence")
    
    return False

def test_gemini_connection():
    """Test Gemini API connection."""
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ GOOGLE_API_KEY not found")
            return False
        
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Test with a simple prompt
        response = model.generate_content("Hello, this is a test of the Gemini API.")
        
        if response.text:
            print("✅ Gemini API connection successful!")
            print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print("❌ Gemini API test failed - no response")
            return False
            
    except ImportError:
        print("❌ google-generativeai not installed")
        print("   Run: pip install google-generativeai")
        return False
    except Exception as e:
        print(f"❌ Gemini API test failed: {e}")
        return False

def main():
    """Main setup function."""
    print("🤖 BigQuery AI Hackathon: Intelligent Insurance Engine")
    print("   LLM-Powered Agent System Setup")
    print("=" * 50)
    
    # Setup API key
    api_configured = setup_gemini_api()
    
    if api_configured:
        print("\n🧪 Testing Gemini API connection...")
        if test_gemini_connection():
            print("\n🎉 Setup complete! Your agent system is ready for LLM-powered processing.")
        else:
            print("\n⚠️  API key is set but connection test failed. Check your key and try again.")
    else:
        print("\n📝 Please configure your API key and run this script again to test the connection.")
    
    print("\n🔧 Next steps:")
    print("   1. Set your GOOGLE_API_KEY environment variable")
    print("   2. Run: python setup_gemini.py (to test connection)")
    print("   3. Start the agent system: python -m streamlit run web_interface/insurance_app.py")
    print("   4. Or test directly: python test_agent_system.py")

if __name__ == "__main__":
    main()
