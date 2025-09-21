@echo off
echo 🚀 Activating Intelligent Insurance Engine environment...
call venv\Scripts\activate.bat
set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\PC\II-Engine\key\intelligent-insurance-engine-8baafb9a5606.json
set PROJECT_ID=intelligent-insurance-engine
echo ✅ Environment activated!
echo 💡 You can now run:
echo    - python insurance_uploader.py (test the uploader)
echo    - streamlit run web_interface/insurance_app.py (web interface)
echo    - jupyter notebook notebooks/01_intelligent_insurance_engine_demo.ipynb (demo)
cmd /k
