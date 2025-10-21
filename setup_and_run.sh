#!/usr/bin/env bash
set -e

# === CONFIGURATION ===
ENV_NAME="signal_sim_env"
PY_VER="3.11"
MAIN_SCRIPT="src/main.py"
REQ_FILE="requirements.txt"

echo "=========================================="
echo "Setting up Signal Simulation Framework (Conda Only)"
echo "=========================================="

# === CHECK CONDA ===
if ! command -v conda &> /dev/null; then
    echo "Conda not found!"
    echo "Please install Miniconda or Anaconda before running this script."
    echo "Download: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# === SOURCE CONDA SETUP ===
CONDA_BASE=$(conda info --base)
source "$CONDA_BASE/etc/profile.d/conda.sh"

# === CREATE ENVIRONMENT ===
if ! conda env list | grep -q "$ENV_NAME"; then
    echo "Creating Conda environment '$ENV_NAME' with Python $PY_VER..."
    conda create -y -n "$ENV_NAME" "python=$PY_VER"
else
    echo "Environment '$ENV_NAME' already exists. Skipping creation."
fi

# === ACTIVATE ENVIRONMENT ===
echo "Activating Conda environment..."
conda activate "$ENV_NAME"

echo "------------------------------------------"
echo "Active Conda environment: $CONDA_DEFAULT_ENV"
python --version
echo "------------------------------------------"

# === INSTALL DEPENDENCIES ===
if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies..."
    pip install --upgrade pip
    pip install -r "$REQ_FILE"
else
    echo "requirements.txt not found, skipping dependency installation."
fi

# === RUN MAIN SCRIPT ===
echo "Running main script..."
python "$MAIN_SCRIPT"

echo "All done! Simulation finished successfully."
