# How to Run and View Results

## **1. Clone the Repository**

```bash
git clone <your_repo_url>
```

## **2. Navigate to the Project Directory**

```bash
cd SignalSim
```

---

## **3. Choose Your Platform**

### 🪟 **For Windows Users**

Run the following file:

```bash
setup_and_run.bat
```

You can either **double-click** it in File Explorer  
or execute it from Command Prompt / PowerShell:

```bash
setup_and_run.bat
```

This will:

- Create and activate a Conda environment (`signal_sim_env`)
- Install all required dependencies from `requirements.txt`
- Run the `main.py` script automatically

---

### 🍎 **For macOS / Linux Users**

Run the following bash script in your terminal:

```bash
bash setup_and_run.sh
```

Or make it executable once and run directly:

```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

This will perform the same automated setup:
- Create a Conda environment (`signal_sim_env`)
- Install dependencies
- Run the main simulation script

---

## **4. View the Results**

- Plots are saved in: `../output/plots/`  
- Reports and notebooks are available in: `report/`  
- You can open the notebook to view simulation summaries and metrics.

---

## **5. How to Run It Manually (Optional)**

If you prefer to set up manually instead of using the scripts:

### reate a Conda Environment

```bash
conda create -n signal_sim_env python=3.11
conda activate signal_sim_env
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Main Script

```bash
python main.py
```

---

## **6. How to Change Simulation Settings**

Simulation parameters are defined in the configuration file, typically:

```
config/config.json
```

Example section:

```json
"simulation": {
  "seed": 10,
  "strength_threshold": 0.5,
  "latency_in_secs": 1,
  "open_order_size": 1,
  "ca": 1.005,
  "cb": 0.999,
  "min_price_aggressiveness": 0.8,
  "min_exec_prob_threshold": 0.75,
  "spread_penalty_factor": 0.5,
  "commision_per_trade": 0.001
}
```

### Explanation of Key Parameters

| Parameter | Description |
|------------|--------------|
| `seed` | Ensures reproducibility of random elements |
| `strength_threshold` | Minimum signal strength to trigger an order |
| `latency_in_secs` | Delay before order execution (set to **1 second** in the assessment) |
| `open_order_size` | Default quantity per trade |
| `ca`, `cb` | Coefficients defining price aggressiveness boundaries |
| `min_price_aggressiveness` | Minimum normalized aggressiveness for sending orders |
| `min_exec_prob_threshold` | Minimum acceptable probability for execution |
| `spread_penalty_factor` | Penalizes execution probability in wide-spread markets |
| `commision_per_trade` | Transaction cost per trade used in PnL calculations |

---

**This setup ensures full reproducibility on any system with Conda installed.**  
The `.bat` and `.sh` scripts automate everything — no manual steps are required.
