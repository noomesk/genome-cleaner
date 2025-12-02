@echo off
REM Genome Cleaner - Helper Script (Batch version for Command Prompt)
REM This script activates the virtual environment and runs the Streamlit application

echo.
echo ========================================
echo   Genome Cleaner - Starting Application
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found!
    echo.
    echo Please create a virtual environment first:
    echo   python -m venv venv
    echo   venv\Scripts\activate.bat
    echo   pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if streamlit is installed
echo [INFO] Checking dependencies...
python -c "import streamlit" 2>nul
if errorlevel 1 (
    echo [ERROR] Streamlit not installed in virtual environment!
    echo [INFO] Installing dependencies...
    pip install -r requirements.txt
)

REM Run the application
echo.
echo [SUCCESS] Starting Streamlit application...
echo [INFO] The app will open in your browser at http://localhost:8501
echo.
echo Press Ctrl+C to stop the application
echo.

streamlit run app.py
