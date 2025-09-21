# 🚀 Deployment Guide for Intelligent Insurance Engine

## Streamlit Cloud Deployment

This guide helps you deploy the Intelligent Insurance Engine to Streamlit Cloud.

### Prerequisites

1. **GitHub Repository**: Your code should be in a public GitHub repository
2. **Google Cloud Project**: Set up with BigQuery, Cloud Storage, Vision API, and Document AI
3. **Service Account**: Create a service account with appropriate permissions

### Quick Deployment Steps

1. **Push to GitHub**:
   ```bash
   git add .
   git commit -m "Ready for deployment"
   git push origin main
   ```

2. **Deploy on Streamlit Cloud**:
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file to: `web_interface/insurance_app.py`
   - Add environment variables (see below)

### Environment Variables

Set these in your Streamlit Cloud deployment:

```
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
PROJECT_ID=intelligent-insurance-engine
PREMIUM_BUCKET=insurance-premium-applications
DATASET_ID=insurance_data
```

### Package Requirements

The `requirements.txt` file includes all necessary packages:

- `streamlit>=1.28.0` - Web interface
- `bigframes>=0.10.0` - BigQuery multimodal processing
- `google-cloud-bigquery>=3.11.0` - BigQuery integration
- `google-cloud-storage>=2.10.0` - Cloud Storage integration
- `google-cloud-vision>=3.4.0` - Vision API (optional)
- `google-cloud-documentai>=2.20.0` - Document AI (optional)
- `pandas>=2.0.0` - Data processing
- `faker>=19.0.0` - Sample data generation

### Troubleshooting

#### Common Issues

1. **Import Errors**: 
   - The app uses fallback implementations for optional packages
   - Check `deploy_check.py` to verify all packages are available

2. **Google Cloud Authentication**:
   - Ensure service account key is properly configured
   - Check that all required APIs are enabled

3. **BigQuery Permissions**:
   - Service account needs BigQuery Data Editor and Job User roles
   - Storage Admin role for Cloud Storage access

#### Testing Locally

Before deploying, test locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Run deployment check
python deploy_check.py

# Test Streamlit app
streamlit run web_interface/insurance_app.py
```

### Features Available in Deployment

✅ **Core Features**:
- Revolutionary agent architecture
- Communication protocol
- BigQuery AI integration
- Multimodal data processing
- Real-time workflow orchestration

⚠️ **Limited Features** (if Vision API/Document AI not available):
- Simplified image processing
- Mock document analysis
- Full functionality with fallback implementations

### Support

If you encounter issues:

1. Check the deployment logs in Streamlit Cloud
2. Run `python deploy_check.py` locally
3. Verify Google Cloud configuration
4. Check that all required APIs are enabled

### Success Indicators

Your deployment is successful when you see:

- ✅ Agent System Ready
- ✅ Communication Protocol Active  
- ✅ BigQuery AI Integration Complete
- ✅ Multimodal Processing Enabled

---

**Ready to transform insurance processing with BigQuery AI!** 🚀
