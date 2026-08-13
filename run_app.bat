@echo off
title AI Photo Upscaler and Face Restorer Pro
color 0A

echo ====================================================
echo      AI Photo Enhancer - Auto Environment Setup
echo ====================================================
echo.

:: 1. Detect Python Installation
set "PY_CMD="
py -3.10 --version >nul 2>&1
if %errorlevel% equ 0 set "PY_CMD=py -3.10"
if not "%PY_CMD%"=="" goto PYTHON_FOUND

python --version >nul 2>&1
if %errorlevel% equ 0 set "PY_CMD=python"

:PYTHON_FOUND
if not "%PY_CMD%"=="" goto CHECK_VENV

echo [ERROR] Python is not installed or not added to PATH!
echo Please install Python 3.10 and check "Add Python to PATH".
echo.
pause
exit /b 1

:CHECK_VENV
echo [INFO] Using Python command: %PY_CMD%

:: 2. Check Virtual Environment
if exist ".venv\Scripts\activate.bat" goto ACTIVATE_VENV

echo [INFO] Creating Virtual Environment (.venv)...
%PY_CMD% -m venv .venv
if errorlevel 1 goto VENV_ERROR
echo [INFO] Virtual Environment created successfully.

:ACTIVATE_VENV
echo [INFO] Activating Virtual Environment...
call .venv\Scripts\activate.bat
if errorlevel 1 goto ACTIVATE_ERROR
goto INSTALL_DEPS

:VENV_ERROR
echo [ERROR] Failed to create virtual environment!
pause
exit /b 1

:ACTIVATE_ERROR
echo [ERROR] .venv folder is incomplete or corrupted. Delete .venv folder and try again.
pause
exit /b 1

:INSTALL_DEPS
:: 3. Upgrade pip and Install dependencies
echo [INFO] Checking and installing required packages...
python -m pip install --upgrade pip

:: PyTorch (with CUDA support)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

:: UI and AI Libraries
pip install customtkinter pillow opencv-python numpy realesrgan gfpgan

:: 4. Launch Application
echo.
echo ====================================================
echo           Launching AI Photo Enhancer...
echo ====================================================
echo.
python app.py

pause