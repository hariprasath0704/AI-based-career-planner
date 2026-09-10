@echo off
title PathPilot AI Planner Launcher
echo ===================================================
echo           PathPilot AI Planner Launcher
echo ===================================================
echo.

:: Change directory to current script location to ensure correct paths
cd /d "%~dp0"

:: 1. Check for Virtual Environment
if not exist venv (
    echo [1/3] Creating virtual environment (venv) for isolation...
    py -m venv venv
    if errorlevel 1 (
        echo ERROR: Python launcher "py" not found. Please install Python.
        pause
        exit /b 1
    )
    
    echo [2/3] Activating environment and installing dependencies...
    call venv\Scripts\activate
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install packages. Check internet connection.
        pause
        exit /b 1
    )
) else (
    echo [1/2] Activating Python virtual environment (venv)...
    call venv\Scripts\activate
)

:: 2. Initialize Database & Seed
echo [2/2] Checking database status...
py database_init.py 2>nul || python database_init.py

:: 3. Launch Web Browser
echo.
echo Opening browser to http://127.0.0.1:8080 ...
start http://127.0.0.1:8080

:: 4. Start Server
echo Starting web application on port 8080...
echo (Using port 8080 to prevent conflicts with other running apps)
echo.
py app.py 8080 2>nul || python app.py 8080

pause
