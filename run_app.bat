@echo off
title AI Photo Upscaler & Face Restorer - Launcher
color 0A

echo ====================================================
echo      AI Photo Enhancer - Auto Environment Setup
echo ====================================================
echo.

:: 1. Check Python installation
py -3.10 --version >nul 2>&1
if %errorlevel% neq 0 (
    python --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not added to PATH!
        echo Please install Python 3.10 and try again.
        pause
        exit /b
    )
)

:: 2. Create Virtual Environment if it doesn't exist
if not exist ".venv" (
    echo [INFO] Creating Virtual Environment (.venv)...
    py -3.10 -m venv .venv 2>nul || python -m venv .venv
    echo [INFO] Virtual Environment created successfully.
)

:: 3. Activate Virtual Environment
echo [INFO] Activating Virtual Environment...
call .venv\Scripts\activate.bat

:: 4. Upgrade pip & Install requirements
echo [INFO] Checking and installing required packages...
python -m pip install --upgrade pip

:: PyTorch (with CUDA support)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

:: UI & AI Libraries
pip install customtkinter pillow opencv-python numpy realesrgan gfpgan

:: 5. Launch the Application
echo.
echo ====================================================
echo           Launching AI Photo Enhancer...
echo ====================================================
echo.
python app.py

pause