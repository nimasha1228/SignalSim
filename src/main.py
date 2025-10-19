import pandas as pd
import numpy as np 
import json
import os
from pathlib import Path

from validation import validate_signals, validate_quotes 
from signal_integration import integrate_signals
from simulator import simulation
from metrics import RealTimePnL
from plotting import *
from metrics import *

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
    SPREAD_PENALTY_FACTOR = config["simulation"]["spread_penalty_factor"]
    C_a = config["simulation"]["ca"]
    C_b = config["simulation"]["cb"]
    MIN_EXEC_PROB_THRESHOLD = config["simulation"]["min_exec_prob_threshold"]
    MIN_PRICE_AGGRESSIVENESS = config["simulation"]["min_price_aggressiveness"]
    COMMISION_PER_TRADE = config["simulation"]["commision_per_trade"]

    signals_csv_path = os.path.join(PROJECT_ROOT,config["data"]["signals_csv_path"])
    quotes_csv_path = os.path.join(PROJECT_ROOT,config["data"]["quotes_csv_path"])

    signals_validated_csv_path = os.path.join(PROJECT_ROOT,config["data"]["signals_validated_csv_path"])
    quotes_validated_csv_path = os.path.join(PROJECT_ROOT,config["data"]["quotes_validated_csv_path"])

    plots_dir_path = os.path.join(PROJECT_ROOT,config["output"]["plots"])
    os.makedirs(plots_dir_path, exist_ok=True)

    matched_csv_path = os.path.join(PROJECT_ROOT,config["data"]["matched_csv_path"])

    results_path = os.path.join(PROJECT_ROOT, config["output"]["results_csv"])
    os.makedirs(results_path, exist_ok=True)
    results_csv = os.path.join(results_path, "results.csv")



    # --- Call Validation Functions ---
    signals_validated_df = validate_signals(signals_csv_path, quotes_csv_path, signals_validated_csv_path)
    quotes_validated_df = validate_quotes(quotes_csv_path, quotes_validated_csv_path, K, plots_dir_path)
    matched_df = integrate_signals(quotes_validated_df,signals_validated_df,matched_csv_path,STRENGTH_THRESHOLD)
    plot_action_vs_signal_strength(matched_df, plots_dir_path, strength_threshold=0.5)
                                                
    pnl_obj = RealTimePnL(COMMISION_PER_TRADE)
    results_df, total_received_signal_count = simulation(matched_df, OPEN_ORDER_SIZE, pnl_obj, SPREAD_PENALTY_FACTOR, C_a, C_b, MIN_PRICE_AGGRESSIVENESS,  MIN_EXEC_PROB_THRESHOLD)
    results_df.to_csv(results_csv, index=False)

    num_of_trades = get_total_num_of_trades(results_df)

    max_drawdown = get_max_drawdown(results_df)
    gross_pnl, net_pnl = get_gross_and_net_pnl(results_df)
    avg_trade_pnl = calculate_average_trade_pnl(results_df)
    avg_slippage = calculate_average_slippage(results_df)
    
    print("total_received_signal_count:",total_received_signal_count," num_of_trades:", num_of_trades, "avg_trade_pnl:",avg_trade_pnl)
    # print("gross_pnl:",gross_pnl," net_pnl:", net_pnl, " avg_slippage:", avg_slippage," max_drawdown:",max_drawdown)
    print("avg_slippage:", avg_slippage)









    



if __name__ == "__main__":
    main()