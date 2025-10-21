# How to Run and View Results

## **1. Clone the Repository**

```bash
git clone <your_repo_url>
```

## **2. Navigate to the Project Directory**

```bash
cd SignalSim
```

## **3. Run the Setup and Execution Script**

```bash
bash setup_and_run.sh
```

This script will automatically:

- Create the required Python environment  
- Install all necessary dependencies  
- Execute the `main.py` script to generate simulation results  

## **4. View the Results**

- Plots are saved in: `../output/plots/`  
- Results CSV is saved in: `../output/csvs/`  
- Log file is saved in: `../output/logs/`  
- Report notebook is available in: `report/`  
- You can open the notebook to view visual summaries and metrics.  

## **5. How to Run It Manually**

The first two steps are the same as above (**1** and **2**).  
Then follow the steps below:

#### Create a Virtual Environment

```bash
python -m venv <name_of_virtual_environment>
```

#### Activate the Virtual Environment

**Windows:**
```bash
<name_of_virtual_environment>\Scripts\activate
```

**Linux / macOS:**
```bash
source <name_of_virtual_environment>/bin/activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Run the Main Script

```bash
python main.py
```

## **6. How to Change Simulation Settings**

Simulation parameters can be modified in the **configuration file**, typically located at:

```
config/config.json
```

You can adjust these values to experiment with different simulation behaviors:

- **`seed`** → Ensures reproducibility of random events  
- **`strength_threshold`** → Signal strength required to trigger an order (set to 0.5 in the assessment)
- **`latency_in_secs`** → Delay before order execution  (set to 1 second in the assessment)
- **`open_order_size`** → Default order size per signal  (set to 1 in the assessment)
- **`ca` / `cb`** → Coefficients defining price aggressiveness boundaries  
- **`min_exec_prob_threshold`** → Minimum probability required for execution  
- **`spread_penalty_factor`** → Penalizes orders in wide-spread markets  
- **`commision_per_trade`** → Per-trade transaction cost applied in PnL calculations  