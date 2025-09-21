@echo off
echo 🚀 Launching State-of-the-Art AI Insurance Agent
echo ==================================================
echo.

REM Activate virtual environment and run the app
call venv\Scripts\activate.bat
python run_streamlit_app.py

echo.
echo Press any key to exit...
pause > nul
