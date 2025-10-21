@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 Setting up Signal Simulation Framework (Conda Only)
echo ==========================================

set ENV_NAME=signal_sim_env
set PY_VER=3.11
set MAIN_SCRIPT=src\main.py
set REQ_FILE=requirements.txt

:: --- Check if Conda is installed ---
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Conda not found!
    echo Please install Miniconda or Anaconda first.
    echo Download: https://docs.conda.io/en/latest/miniconda.html
    pause
    exit /b 1
)

:: --- Check if environment exists ---
for /f "tokens=*" %%i in ('conda env list ^| findstr /C:"%ENV_NAME%"') do set FOUND_ENV=%%i

if not defined FOUND_ENV (
    echo Creating Conda environment "%ENV_NAME%" with Python %PY_VER%...
    call conda create -y -n %ENV_NAME% python=%PY_VER%
) else (
    echo Environment "%ENV_NAME%" already exists. Skipping creation.
)

echo Activating environment...
call conda activate %ENV_NAME%

echo ------------------------------------------
echo Active Conda environment: %CONDA_DEFAULT_ENV%
python --version
echo ------------------------------------------

if exist %REQ_FILE% (
    echo Installing dependencies...
    python -m pip install --upgrade pip
    python -m pip install -r %REQ_FILE%
) else (
    echo ⚠️ requirements.txt not found, skipping dependency installation.
)

echo Running main script...
python %MAIN_SCRIPT%

echo ✅ All done! Simulation finished successfully.
pause
