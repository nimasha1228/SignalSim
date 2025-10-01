import pandas as pd
import numpy as np 
import json
import os
from pathlib import Path

from validation import validate_signals, validate_quotes 
from signal_integration import integrate_signals
from simulator import simulation
from metrics import RealTimePnL

# --- Path Setup ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load the config file correctly
config_path = os.path.join(PROJECT_ROOT,"config","config.json")



def main():
    
    # Load config.json
    with open(config_path, "r") as f:
        config = json.load(f)

    STRENGTH_THRESHOLD = config["simulation"]["strength_threshold"]  
    LATENCY = config["simulation"]["latency_in_secs"] 
    OPEN_ORDER_SIZE = config["simulation"]["open_order_size"] 
    K = config["validation"]["k"] 

    signals_csv_path = os.path.join(PROJECT_ROOT,config["data"]["signals_csv_path"])
    quotes_csv_path = os.path.join(PROJECT_ROOT,config["data"]["quotes_csv_path"])

    signals_validated_csv_path = os.path.join(PROJECT_ROOT,config["data"]["signals_validated_csv_path"])
    quotes_validated_csv_path = os.path.join(PROJECT_ROOT,config["data"]["quotes_validated_csv_path"])

    plots_saving_path = os.path.join(PROJECT_ROOT,config["output"]["plots"])
    os.makedirs(plots_saving_path, exist_ok=True)

    matched_csv_path = os.path.join(PROJECT_ROOT,config["data"]["matched_csv_path"])

    results_path = os.path.join(PROJECT_ROOT, config["output"]["results_csv"])
    os.makedirs(results_path, exist_ok=True)
    results_csv = os.path.join(results_path, "results.csv")



    # --- Call Validation Functions ---
    signals_validated_df = validate_signals(signals_csv_path, quotes_csv_path, signals_validated_csv_path)
    quotes_validated_df = validate_quotes(quotes_csv_path, quotes_validated_csv_path, K, plots_saving_path)
    
    matched_df = integrate_signals(quotes_validated_df,signals_validated_df,matched_csv_path,STRENGTH_THRESHOLD)

    pnl_obj = RealTimePnL()
    results_df = simulation(matched_df, OPEN_ORDER_SIZE, pnl_obj)
    results_df.to_csv(results_csv, index=False)






    



if __name__ == "__main__":
    main()