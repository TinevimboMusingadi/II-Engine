@echo off
echo 🚀 BigQuery AI Hackathon - Intelligent Insurance Engine Setup
echo ================================================================

echo.
echo 📋 This script will:
echo    1. Create a Python virtual environment
echo    2. Install required Google Cloud libraries
echo    3. Set up authentication with your service account key
echo    4. Test the connection to Google Cloud
echo    5. Create sample documents and test the uploader

echo.
pause

echo.
echo 🐍 Running Python setup script...
python setup_local_env.py

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ Setup completed successfully!
    echo.
    echo 💡 Next steps:
    echo    1. Run: activate_env.bat
    echo    2. Test uploader: python insurance_uploader.py
    echo    3. Start web interface: streamlit run web_interface/insurance_app.py
    echo.
    echo 🎯 Ready for the BigQuery AI Hackathon!
) else (
    echo ❌ Setup failed. Please check the error messages above.
)

echo.
pause
