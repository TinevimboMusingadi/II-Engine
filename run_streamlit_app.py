"""
Launcher script for the State-of-the-Art AI Insurance Agent Streamlit App
"""

import os
import sys
import subprocess

def launch_streamlit_app():
    """Launch the Streamlit app with proper environment setup."""
    
    print("🚀 Launching State-of-the-Art AI Insurance Agent")
    print("=" * 50)
    
    # Set up environment
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.path.abspath(r'key\intelligent-insurance-engine-8baafb9a5606.json')
    os.environ['PROJECT_ID'] = 'intelligent-insurance-engine'
    
    # Check if virtual environment is activated
    venv_python = os.path.join('venv', 'Scripts', 'python.exe')
    venv_streamlit = os.path.join('venv', 'Scripts', 'streamlit.exe')
    
    if not os.path.exists(venv_python):
        print("❌ Virtual environment not found!")
        print("Please run: python -m venv venv && venv\\Scripts\\activate && pip install -r requirements.txt")
        return False
    
    print("✅ Virtual environment found")
    print("✅ Environment configured")
    print("🤖 Starting AI Agent Web Interface...")
    print()
    print("🌐 The app will open at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print()
    
    try:
        # Launch Streamlit
        cmd = [venv_streamlit, 'run', 'web_interface/insurance_app.py', '--server.port', '8501']
        subprocess.run(cmd, check=True)
        
    except KeyboardInterrupt:
        print("\n🛑 Streamlit app stopped by user")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error launching Streamlit: {e}")
        return False
        
    except FileNotFoundError:
        print("❌ Streamlit not found in virtual environment")
        print("Please install: pip install streamlit")
        return False

if __name__ == "__main__":
    success = launch_streamlit_app()
    if success:
        print("✅ App launched successfully!")
    else:
        print("❌ Failed to launch app")
