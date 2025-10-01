import pandas as pd
import numpy as numpy
from pathlib import Path
import os
from logger_config import logger, log_blank_line
from plotting import plot_spread_distribution



def validate_signals(signals_csv_path, quotes_csv_path, signals_validated_csv_path):
    logger.info("-------- Signal Data Validation Report --------")
    logger.info("===============================================")

    signals_raw_df = pd.read_csv(signals_csv_path) 
    quotes_raw_df = pd.read_csv(quotes_csv_path) 
    initial_row_count = len(signals_raw_df)

    # --- Normalize timestamp columns ---
    signals_raw_df["timestamp"] = pd.to_datetime(
        signals_raw_df["timestamp"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )
    quotes_raw_df["timestamp"] = pd.to_datetime(
        quotes_raw_df["timestamp"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )

    # ------------------------- Null Values Check -------------------------
    null_count = signals_raw_df.isnull().sum().sum()
    if null_count > 0:
        logger.info(f"FLAG: {null_count} row(s) with null values found.")
        signals_raw_df.dropna(inplace=True)
        signals_raw_df.reset_index(drop=True, inplace=True)
        logger.info("ACTION: Dropped all rows containing null values.")
    else:
        logger.info("PASS: No null values found.")

    # ------------------------- Timestamp Alignment Check -----------------
    aligned = signals_raw_df['timestamp'].isin(quotes_raw_df['timestamp'])
    num_misaligned = (~aligned).sum()
    if num_misaligned == 0:
        logger.info("PASS: All signal timestamps are aligned with quotes.")
    else:
        logger.info(f"FLAG: Found {num_misaligned} misaligned signal row(s).")
        signals_raw_df = signals_raw_df[aligned]
        logger.info(f"ACTION: Removed {num_misaligned} misaligned signal row(s).")

    # ------------------------- Summary Report ----------------------------
    final_row_count = len(signals_raw_df)
    total_rows_dropped = initial_row_count - final_row_count

    log_blank_line()
    logger.info(f"Rows checked (Initial): {initial_row_count}")
    logger.info(f"Rows dropped (Total): {total_rows_dropped}")
    logger.info(f"Rows remaining (Final): {final_row_count}")
    log_blank_line()

    signals_raw_df.to_csv(signals_validated_csv_path, index=False)
    return signals_raw_df




def validate_quotes(quotes_csv_path, quotes_validated_csv_path, k, plots_saving_path):

    logger.info("-------- Quote Data Validation Report --------")
    logger.info("==============================================")

    quotes_raw_df = pd.read_csv(quotes_csv_path) 
    initial_row_count = len(quotes_raw_df)

    # --- Normalize timestamp columns ---
    quotes_raw_df["timestamp"] = pd.to_datetime(
        quotes_raw_df["timestamp"].astype(str).str.replace(",", ".", regex=False),
        errors="coerce"
    )


    # -----------------------------------Duplicate Row Check----------------------------------------------
    has_duplicates = quotes_raw_df.duplicated().any()

    if has_duplicates:
        logger.info("FLAG: Detected duplicate rows.")
        
        # Drop duplicate rows
        quotes_raw_df.drop_duplicates(subset=quotes_raw_df.columns, keep="first", inplace=True)
        rows_dropped = initial_row_count - len(quotes_raw_df)
        logger.info(f"ACTION: Removed {rows_dropped} duplicate row(s) from dataset.")
    else:
        logger.info("PASS: No duplicate rows found.")


    
    # ----------------Check for strictly increasing timestamps (Monotonicity Check)----------------------
    if not quotes_raw_df['timestamp'].is_monotonic_increasing:
        logger.info("FLAG: Timestamps are not strictly increasing. Sorting by timestamp.")

        quotes_raw_df = quotes_raw_df.sort_values('timestamp').reset_index(drop=True)
        logger.info(f"ACTION: Sorted timestamps.")

    else:
        logger.info("PASS: Timestamps are already strictly increasing.")


    # --------------------------------checking null values----------------------------------------------
    null_count = quotes_raw_df.isnull().sum().sum()

    if null_count > 0:
        logger.info(f"FLAG: Detected {null_count} row(s) with null values.")
        
        # Drop rows with null values
        quotes_raw_df.dropna(inplace=True)
        quotes_raw_df.reset_index(drop=True, inplace=True)
        logger.info("ACTION: Removed all rows containing null values.")
    else:
        logger.info("PASS: No null values found in dataset.")

    

    # -----------------------------------Bid <= Ask------------------------------------------------------
    invalid_spread = quotes_raw_df[quotes_raw_df['bid_price'] > quotes_raw_df['ask_price']]
    invalid_count = len(invalid_spread)

    if invalid_count > 0:
        logger.info(f"FLAG: Detected {invalid_count} row(s) where bid_price > ask_price.")
        
        # Remove invalid rows
        quotes_raw_df = quotes_raw_df[quotes_raw_df['bid_price'] <= quotes_raw_df['ask_price']]
        logger.info(f"ACTION: Removed {invalid_count} bid > ask row(s) from dataset.")
    else:
        logger.info("PASS: No rows found with bid_price > ask_price.")



    # -----------------------------------Spread threshold------------------------------------------------
    spread = (quotes_raw_df['ask_price'] - quotes_raw_df['bid_price']) / quotes_raw_df['bid_price']
    mean = spread.mean()
    std = spread.std()
    spread_threshold = mean + k * std   # flag anything > k standard deviations away

    # Add a flag column for spread validation
    quotes_raw_df['spread_flag'] = (spread > spread_threshold).astype(int)  # 1 = flagged, 0 = valid

    invalid_rows_count = quotes_raw_df['spread_flag'].sum()

    if invalid_rows_count > 0:
        logger.info(f"FLAG: {invalid_rows_count} row(s) with spread > {spread_threshold:.6f} identified and flagged.")
    else:
        logger.info(f"PASS: No rows with spread > {spread_threshold:.6f} found.")

    save_path = os.path.join(plots_saving_path, "spread_distribution.png")
    plot_spread_distribution(spread, mean, k, spread_threshold, save_path)


    # -----------------------------------Positive Volume Check---------------------------------------------
    is_volume_valid = (quotes_raw_df['bid_qty'] > 0) & (quotes_raw_df['ask_qty'] > 0)
    num_invalid_rows = (~is_volume_valid).sum()

    if num_invalid_rows == 0:
        logger.info("PASS: All volume values are positive.")
    else:
        logger.info(f"FLAG: Found {num_invalid_rows} row(s) with non-positive volume.")
        
        # Remove invalid rows
        quotes_raw_df = quotes_raw_df[is_volume_valid]
        logger.info(f"ACTION: Removed {num_invalid_rows} row(s) with non-positive volume.")




    # --- SUMMARY REPORT ---
    final_row_count = len(quotes_raw_df)
    total_rows_dropped = initial_row_count - final_row_count
    
    # Create the full report content as a list of strings
    log_blank_line()
    logger.info(f"Rows checked (Initial): {initial_row_count}")
    logger.info(f"Rows dropped (Total): {total_rows_dropped}")
    logger.info(f"Rows remaining (Final): {final_row_count}")


    quotes_validated_df = quotes_raw_df 
    quotes_validated_df.to_csv(quotes_validated_csv_path, index=False) 

    return quotes_validated_df