@echo off
REM ========================================
REM LangGraph Multi-Agent System Installer
REM Windows Version
REM ========================================

echo ========================================
echo LangGraph Multi-Agent System
echo Installation Script for Windows
echo ========================================
echo.

REM Check Python version
echo [1/7] Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo SUCCESS: Python %PYTHON_VERSION% detected
echo.

REM Check if virtual environment exists
if not exist "venv\" (
    echo [2/7] Creating virtual environment...
    python -m venv venv
    echo SUCCESS: Virtual environment created
) else (
    echo [2/7] Virtual environment already exists
)
echo.

REM Activate virtual environment
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo SUCCESS: pip upgraded
echo.

REM Install requirements
echo [5/7] Installing dependencies...
echo This may take 2-5 minutes...
pip install -r requirements.txt --quiet

if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo Try running: pip install -r requirements.txt
    pause
    exit /b 1
)

echo SUCCESS: Dependencies installed
echo.

REM Check for .env file
echo [6/7] Checking for API keys...
if not exist ".env" (
    echo WARNING: .env file not found
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo ========================================
    echo IMPORTANT: Configure your API keys
    echo ========================================
    echo.
    echo Please edit .env and add your API keys:
    echo   1. GROQ_API_KEY - Get from https://console.groq.com/
    echo   2. TAVILY_API_KEY - Get from https://tavily.com/
    echo.
    echo After adding keys, run this script again.
    echo.
    pause
    exit /b 0
)

findstr /C:"your_groq_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo WARNING: Please add your GROQ_API_KEY to .env
    echo Get it from: https://console.groq.com/
    pause
    exit /b 1
)

findstr /C:"your_tavily_api_key_here" .env >nul
if %errorlevel% equ 0 (
    echo WARNING: Please add your TAVILY_API_KEY to .env
    echo Get it from: https://tavily.com/
    pause
    exit /b 1
)

echo SUCCESS: API keys configured
echo.

REM Generate dataset
echo [7/7] Setting up system...
echo Generating financial dataset...
python src\data\generate_dataset.py

if %errorlevel% neq 0 (
    echo ERROR: Failed to generate dataset
    pause
    exit /b 1
)

echo SUCCESS: Dataset generated
echo.

REM Initialize vector store
echo Initializing vector store...
python src\utils\vector_store.py

if %errorlevel% neq 0 (
    echo ERROR: Failed to initialize vector store
    pause
    exit /b 1
)

echo SUCCESS: Vector store initialized
echo.

REM Run tests
echo Running system tests...
echo.
python test_system.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo SUCCESS: Installation Complete!
    echo ========================================
    echo.
    echo Next steps:
    echo.
    echo 1. Keep this window open or activate venv:
    echo    venv\Scripts\activate.bat
    echo.
    echo 2. Launch the Streamlit UI:
    echo    streamlit run app.py
    echo.
    echo 3. Open your browser to:
    echo    http://localhost:8501
    echo.
    echo 4. Click 'Initialize System' in sidebar
    echo.
    echo 5. Start asking questions!
    echo.
    echo ========================================
    echo Example queries:
    echo   - What is artificial intelligence?
    echo   - What's the latest AI news?
    echo   - What was TechNova's Q1 2024 revenue?
    echo ========================================
    echo.
) else (
    echo.
    echo ERROR: Some tests failed
    echo Please check the error messages above
    echo See TROUBLESHOOTING.md for solutions
    echo.
)

pause