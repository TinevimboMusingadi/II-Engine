# 🚀 Quick Setup Guide - Intelligent Insurance Engine

## Local Environment Setup for BigQuery AI Hackathon

This guide will help you set up the complete local development environment for the Intelligent Insurance Engine project.

---

## 🏁 Quick Start (Windows)

1. **Double-click to run**: `run_setup.bat`
2. **Follow the prompts** - the script will handle everything automatically
3. **When complete, run**: `activate_env.bat`
4. **Test the system**: `python insurance_uploader.py`

---

## 🏁 Quick Start (Mac/Linux)

1. **Run the setup script**: `./run_setup.sh`
2. **Follow the prompts** - the script will handle everything automatically  
3. **When complete, run**: `./activate_env.sh`
4. **Test the system**: `python insurance_uploader.py`

---

## 📋 What the Setup Does

### 1. **Virtual Environment**
- Creates a Python virtual environment (`venv/`)
- Isolates project dependencies from your system Python

### 2. **Package Installation**
Installs all required libraries:
- `google-cloud-storage` - Cloud Storage integration
- `google-cloud-bigquery` - BigQuery integration  
- `google-cloud-documentai` - Document processing
- `google-cloud-vision` - Image analysis
- `bigframes` - BigQuery DataFrames
- `streamlit` - Web interface
- `pandas`, `numpy` - Data processing
- And more...

### 3. **Google Cloud Authentication**
- Uses your service account key: `key/intelligent-insurance-engine-8baafb9a5606.json`
- Sets up environment variables automatically
- Tests the connection to verify everything works

### 4. **Project Structure**
- Creates `.env` file with configuration
- Sets up activation scripts for easy environment management
- Creates sample documents for testing

---

## 🔧 Manual Setup (If Automated Setup Fails)

### Step 1: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux  
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Packages
```bash
pip install google-cloud-storage google-cloud-bigquery google-cloud-documentai google-cloud-vision pandas faker python-dotenv bigframes streamlit plotly Pillow numpy requests
```

### Step 3: Set Environment Variables
```bash
# Windows
set GOOGLE_APPLICATION_CREDENTIALS=key\intelligent-insurance-engine-8baafb9a5606.json

# Mac/Linux
export GOOGLE_APPLICATION_CREDENTIALS="key/intelligent-insurance-engine-8baafb9a5606.json"
```

### Step 4: Test Connection
```bash
python -c "from google.cloud import bigquery; print('✅ BigQuery connected:', bigquery.Client().project)"
```

---

## 🧪 Testing Your Setup

### 1. **Test the Insurance Uploader**
```bash
python insurance_uploader.py
```
This will:
- Create Google Cloud Storage buckets
- Set up BigQuery tables
- Upload sample documents
- Test AI processing
- Create application records

### 2. **Test the Web Interface**
```bash
streamlit run web_interface/insurance_app.py
```
This will:
- Start the Streamlit web application
- Open your browser to the interface
- Allow you to upload files and test the full workflow

### 3. **Run the Demo Notebook**
```bash
jupyter notebook notebooks/01_intelligent_insurance_engine_demo.ipynb
```
This will:
- Show the complete end-to-end workflow
- Demonstrate all BigQuery AI features
- Process multimodal data with AI

---

## 🔍 Troubleshooting

### ❌ "Command not found" errors
- Make sure Python 3.8+ is installed
- Try `python3` instead of `python`
- On Windows, try `py` instead of `python`

### ❌ Google Cloud authentication errors
- Verify your service account key file exists: `key/intelligent-insurance-engine-8baafb9a5606.json`
- Check the file has valid JSON content
- Ensure your service account has the required permissions:
  - BigQuery Admin
  - Storage Admin
  - Vision API User
  - Document AI User

### ❌ Permission errors
- Make sure your Google Cloud project is active
- Verify billing is enabled on your project
- Check that required APIs are enabled:
  - BigQuery API
  - Cloud Storage API
  - Vision API
  - Document AI API

### ❌ Package installation errors
- Try upgrading pip: `pip install --upgrade pip`
- Use `--user` flag: `pip install --user package-name`
- Try installing packages one by one

---

## 📁 Generated Files After Setup

```
intelligent-insurance-engine/
├── venv/                           # Virtual environment
├── .env                           # Environment variables
├── activate_env.bat              # Windows activation script
├── activate_env.sh               # Unix activation script
├── sample_documents/             # Test documents
│   ├── sample_vehicle_photo.txt
│   ├── sample_driver_license.txt
│   └── sample_application_form.txt
└── test_connection.py           # Connection test script (temporary)
```

---

## 🎯 Next Steps After Setup

1. **Explore the Code**
   - `insurance_uploader.py` - Document upload and processing
   - `python_agent/` - AI agent components
   - `web_interface/` - Streamlit web app
   - `sql_scripts/` - BigQuery setup scripts

2. **Customize for Your Use Case**
   - Modify document types in `insurance_uploader.py`
   - Add new ML models in `python_agent/ml_tools.py`
   - Enhance the web interface in `web_interface/insurance_app.py`

3. **Deploy to Production**
   - Set up Cloud Run for the web interface
   - Configure Cloud Functions for automated processing
   - Set up monitoring and logging

4. **Prepare for the Hackathon**
   - Create your demo video
   - Document your innovations
   - Test the complete workflow
   - Prepare your presentation

---

## 💡 Tips for Success

- **Test Early**: Run the setup as soon as possible to identify any issues
- **Document Everything**: Keep notes on what you change or customize
- **Use Sample Data**: The provided sample documents help test without real data
- **Monitor Resources**: Keep an eye on Google Cloud usage and costs
- **Ask for Help**: If you get stuck, the error messages usually point to the solution

---

## 🏆 Ready for the Hackathon!

Once setup is complete, you'll have:
- ✅ Complete BigQuery AI environment
- ✅ Multimodal data processing capabilities  
- ✅ AI-powered document analysis
- ✅ Web interface for easy testing
- ✅ Sample data and workflows
- ✅ All tools ready for development

**Good luck with the BigQuery AI Hackathon! 🚀**
