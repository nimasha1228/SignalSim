#!/bin/bash
set -e  # Exit immediately if a command fails

# === CONFIGURATION ===
ENV_NAME="signal_sim_env"
PY_VER="3.10"
MAIN_SCRIPT="main.py"
REQ_FILE="requirements.txt"

echo "=========================================="
echo "🚀 Setting up Signal Simulation Framework"
echo "=========================================="

# === CHECK CONDA ===
if command -v conda &> /dev/null; then
    echo "✅ Conda detected. Using Conda environment setup."

    # Create env if not exists
    if ! conda env list | grep -q "$ENV_NAME"; then
        echo "Creating Conda environment '$ENV_NAME'..."
        conda create -y -n "$ENV_NAME" python=$PY_VER
    else
        echo "Environment '$ENV_NAME' already exists. Skipping creation."
    fi

    echo "Activating Conda environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate "$ENV_NAME"

    # Install dependencies
    if [ -f "$REQ_FILE" ]; then
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r "$REQ_FILE"
    else
        echo "⚠️ requirements.txt not found, skipping dependency installation."
    fi

    echo "Running main script..."
    python "$MAIN_SCRIPT"

else
    echo "⚠️ Conda not found. Falling back to Python venv."
    ENV_DIR=".venv_$ENV_NAME"

    # Create venv if not exists
    if [ ! -d "$ENV_DIR" ]; then
        echo "Creating virtual environment..."
        python3 -m venv "$ENV_DIR"
    fi

    echo "Activating virtual environment..."
    source "$ENV_DIR/bin/activate"

    # Install dependencies
    if [ -f "$REQ_FILE" ]; then
        echo "Installing dependencies..."
        pip install --upgrade pip
        pip install -r "$REQ_FILE"
    else
        echo "⚠️ requirements.txt not found, skipping dependency installation."
    fi

    echo "Running main script..."
    python "$MAIN_SCRIPT"
fi

echo "✅ All done! Simulation finished successfully."