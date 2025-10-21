@echo off
setlocal enabledelayedexpansion

echo ==========================================
echo Setting up Signal Simulation Framework
echo ==========================================

set ENV_NAME=signal_sim_env
set PY_VER=3.11
set MAIN_SCRIPT=src\main.py
set REQ_FILE=requirements.txt
set VENV_DIR=.venv_%ENV_NAME%

:: --- Check if Conda is installed ---
where conda >nul 2>nul
if %errorlevel% neq 0 (
    echo Conda not found! Falling back to Python virtual environment.
    goto :USE_VENV
)

:: --- Conda found: use Conda environment ---
echo Conda detected. Using Conda environment setup.

set FOUND_ENV=
for /f "tokens=*" %%i in ('conda env list ^| findstr /C:"%ENV_NAME%"') do set FOUND_ENV=%%i

if not defined FOUND_ENV (
    echo Creating Conda environment "%ENV_NAME%" with Python %PY_VER%...
    call conda create -y -n %ENV_NAME% python=%PY_VER%

    echo Installing dependencies for the first time...
    call conda activate %ENV_NAME%
    if exist %REQ_FILE% (
        python -m pip install --upgrade pip
        python -m pip install -r %REQ_FILE%
    ) else (
        echo requirements.txt not found, skipping dependency installation.
    )
) else (
    echo Environment "%ENV_NAME%" already exists. Skipping creation and dependency installation.
    call conda activate %ENV_NAME%
)

echo ------------------------------------------
echo Active Conda environment: %CONDA_DEFAULT_ENV%
python --version
echo ------------------------------------------

echo Running main script...
python %MAIN_SCRIPT%

echo All done! Simulation finished successfully.
pause
exit /b 0


:: ===== FALLBACK: PYTHON VENV =====
:USE_VENV
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo Python not found! Please install Python 3.10+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

if not exist %VENV_DIR% (
    echo Creating Python virtual environment...
    python -m venv %VENV_DIR%

    echo Installing dependencies for the first time...
    call %VENV_DIR%\Scripts\activate.bat
    if exist %REQ_FILE% (
        python -m pip install --upgrade pip
        python -m pip install -r %REQ_FILE%
    ) else (
        echo requirements.txt not found, skipping dependency installation.
    )
) else (
    echo Virtual environment already exists. Skipping creation and dependency installation.
    call %VENV_DIR%\Scripts\activate.bat
)

echo ------------------------------------------
echo Active virtual environment: %VENV_DIR%
python --version
echo ------------------------------------------

echo Running main script...
python %MAIN_SCRIPT%

echo All done! Simulation finished successfully.
pause
exit /b 0
