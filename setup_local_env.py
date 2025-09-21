#!/usr/bin/env python3
"""
BigQuery AI Hackathon: Local Environment Setup Script
This script sets up your local environment for the Intelligent Insurance Engine project.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

class LocalEnvironmentSetup:
    """Setup local development environment for Google Cloud and BigQuery AI project"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.venv_path = self.project_root / "venv"
        self.key_file_path = self.project_root / "key" / "intelligent-insurance-engine-8baafb9a5606.json"
        
    def run_command(self, command, shell=True, check=True):
        """Run a shell command with error handling"""
        try:
            print(f"🔄 Running: {command}")
            result = subprocess.run(command, shell=shell, check=check, 
                                  capture_output=True, text=True)
            if result.stdout:
                print(f"✅ Output: {result.stdout.strip()}")
            return result
        except subprocess.CalledProcessError as e:
            print(f"❌ Error running command: {command}")
            print(f"❌ Error output: {e.stderr}")
            if check:
                raise
            return e
    
    def check_python(self):
        """Check if Python 3.8+ is available"""
        print("🐍 Checking Python version...")
        
        try:
            result = subprocess.run([sys.executable, "--version"], 
                                  capture_output=True, text=True)
            version = result.stdout.strip()
            print(f"✅ Found: {version}")
            
            # Check if version is 3.8+
            version_parts = version.split()[1].split('.')
            major, minor = int(version_parts[0]), int(version_parts[1])
            
            if major >= 3 and minor >= 8:
                return True
            else:
                print("❌ Python 3.8+ required")
                return False
                
        except Exception as e:
            print(f"❌ Error checking Python: {e}")
            return False
    
    def create_virtual_environment(self):
        """Create and activate virtual environment"""
        print("🏗️ Creating virtual environment...")
        
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return True
        
        try:
            # Create venv
            self.run_command(f"{sys.executable} -m venv {self.venv_path}")
            print("✅ Virtual environment created successfully")
            return True
        except Exception as e:
            print(f"❌ Error creating virtual environment: {e}")
            return False
    
    def get_venv_python(self):
        """Get the path to Python in the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "python.exe"
        else:  # Unix/Linux/macOS
            return self.venv_path / "bin" / "python"
    
    def get_venv_pip(self):
        """Get the path to pip in the virtual environment"""
        if os.name == 'nt':  # Windows
            return self.venv_path / "Scripts" / "pip.exe"
        else:  # Unix/Linux/macOS
            return self.venv_path / "bin" / "pip"
    
    def install_requirements(self):
        """Install required Python packages"""
        print("📦 Installing required packages...")
        
        pip_path = self.get_venv_pip()
        
        # Required packages for the project
        packages = [
            "google-cloud-storage",
            "google-cloud-bigquery", 
            "google-cloud-documentai",
            "google-cloud-vision",
            "pandas",
            "faker",
            "python-dotenv",
            "bigframes>=0.10.0",
            "streamlit>=1.28.0",
            "plotly>=5.15.0",
            "Pillow>=10.0.0",
            "numpy>=1.24.0",
            "requests>=2.31.0"
        ]
        
        for package in packages:
            try:
                print(f"📦 Installing {package}...")
                self.run_command(f"{pip_path} install {package}")
            except Exception as e:
                print(f"❌ Error installing {package}: {e}")
                return False
        
        print("✅ All packages installed successfully")
        return True
    
    def setup_google_cloud_auth(self):
        """Set up Google Cloud authentication"""
        print("🔐 Setting up Google Cloud authentication...")
        
        # Check if key file exists
        if not self.key_file_path.exists():
            print(f"❌ Service account key file not found: {self.key_file_path}")
            print("Please ensure your service account key is in the 'key' directory")
            return False
        
        # Validate JSON key file
        try:
            with open(self.key_file_path, 'r') as f:
                key_data = json.load(f)
                project_id = key_data.get('project_id', 'Unknown')
                print(f"✅ Found valid service account key for project: {project_id}")
        except Exception as e:
            print(f"❌ Invalid service account key file: {e}")
            return False
        
        # Set environment variable
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = str(self.key_file_path.absolute())
        print(f"✅ Set GOOGLE_APPLICATION_CREDENTIALS to: {self.key_file_path.absolute()}")
        
        return True
    
    def create_env_file(self):
        """Create .env file for environment variables"""
        print("📝 Creating .env file...")
        
        env_content = f"""# BigQuery AI Hackathon - Intelligent Insurance Engine
# Environment Variables

# Google Cloud Configuration
GOOGLE_APPLICATION_CREDENTIALS={self.key_file_path.absolute()}
PROJECT_ID=intelligent-insurance-engine

# BigQuery Configuration
DATASET_ID=insurance_data
PREMIUM_BUCKET=insurance-premium-applications
CLAIMS_BUCKET=insurance-claims-processing

# Development Settings
ENVIRONMENT=development
DEBUG=True
"""
        
        env_file_path = self.project_root / ".env"
        
        try:
            with open(env_file_path, 'w') as f:
                f.write(env_content)
            print(f"✅ Created .env file: {env_file_path}")
            return True
        except Exception as e:
            print(f"❌ Error creating .env file: {e}")
            return False
    
    def test_google_cloud_connection(self):
        """Test Google Cloud connection"""
        print("🧪 Testing Google Cloud connection...")
        
        python_path = self.get_venv_python()
        
        test_script = '''
import os
from google.cloud import bigquery
from google.cloud import storage

try:
    # Test BigQuery connection
    bq_client = bigquery.Client()
    print(f"✅ BigQuery connection successful")
    print(f"   Project: {bq_client.project}")
    
    # Test Cloud Storage connection  
    storage_client = storage.Client()
    print(f"✅ Cloud Storage connection successful")
    print(f"   Project: {storage_client.project}")
    
    print("🎉 All Google Cloud services connected successfully!")
    
except Exception as e:
    print(f"❌ Error connecting to Google Cloud: {e}")
    print("Please check your service account key and permissions")
'''
        
        try:
            # Write test script to temporary file
            test_file = self.project_root / "test_connection.py"
            with open(test_file, 'w') as f:
                f.write(test_script)
            
            # Run test script with venv python
            result = self.run_command(f"{python_path} {test_file}")
            
            # Clean up test file
            test_file.unlink()
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"❌ Error testing connection: {e}")
            return False
    
    def create_activation_scripts(self):
        """Create scripts to easily activate the environment"""
        print("📜 Creating activation scripts...")
        
        # Windows batch script
        if os.name == 'nt':
            activate_script = self.project_root / "activate_env.bat"
            script_content = f"""@echo off
echo 🚀 Activating Intelligent Insurance Engine environment...
call {self.venv_path}\\Scripts\\activate.bat
set GOOGLE_APPLICATION_CREDENTIALS={self.key_file_path.absolute()}
echo ✅ Environment activated!
echo 💡 You can now run: python insurance_uploader.py
echo 💡 Or start Streamlit: streamlit run web_interface/insurance_app.py
cmd /k
"""
        else:
            # Unix/Linux/macOS script
            activate_script = self.project_root / "activate_env.sh"
            script_content = f"""#!/bin/bash
echo "🚀 Activating Intelligent Insurance Engine environment..."
source {self.venv_path}/bin/activate
export GOOGLE_APPLICATION_CREDENTIALS="{self.key_file_path.absolute()}"
echo "✅ Environment activated!"
echo "💡 You can now run: python insurance_uploader.py"
echo "💡 Or start Streamlit: streamlit run web_interface/insurance_app.py"
bash
"""
        
        try:
            with open(activate_script, 'w') as f:
                f.write(script_content)
            
            # Make executable on Unix systems
            if os.name != 'nt':
                os.chmod(activate_script, 0o755)
            
            print(f"✅ Created activation script: {activate_script}")
            return True
        except Exception as e:
            print(f"❌ Error creating activation script: {e}")
            return False
    
    def run_setup(self):
        """Run the complete setup process"""
        print("🚀 Starting BigQuery AI Hackathon Local Environment Setup")
        print("=" * 60)
        
        steps = [
            ("Checking Python version", self.check_python),
            ("Creating virtual environment", self.create_virtual_environment),
            ("Installing required packages", self.install_requirements),
            ("Setting up Google Cloud authentication", self.setup_google_cloud_auth),
            ("Creating .env file", self.create_env_file),
            ("Testing Google Cloud connection", self.test_google_cloud_connection),
            ("Creating activation scripts", self.create_activation_scripts)
        ]
        
        for step_name, step_func in steps:
            print(f"\n📋 {step_name}...")
            try:
                if not step_func():
                    print(f"❌ Failed: {step_name}")
                    return False
            except Exception as e:
                print(f"❌ Error in {step_name}: {e}")
                return False
        
        print("\n" + "=" * 60)
        print("🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        
        if os.name == 'nt':
            print("   1. Run: activate_env.bat")
        else:
            print("   1. Run: ./activate_env.sh")
        
        print("   2. Test the insurance uploader: python insurance_uploader.py")
        print("   3. Start the web interface: streamlit run web_interface/insurance_app.py")
        print("   4. Run the demo notebook: jupyter notebook notebooks/01_intelligent_insurance_engine_demo.ipynb")
        
        print("\n🔗 Useful commands:")
        print("   • Check BigQuery datasets: bq ls")
        print("   • List Cloud Storage buckets: gsutil ls")
        print("   • View project info: gcloud config list")
        
        return True


def main():
    """Main function to run the setup"""
    setup = LocalEnvironmentSetup()
    
    try:
        success = setup.run_setup()
        if success:
            print("\n✅ Environment setup completed successfully!")
            sys.exit(0)
        else:
            print("\n❌ Environment setup failed!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during setup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
