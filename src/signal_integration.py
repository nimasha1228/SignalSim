import pandas as pd
from logger_config import logger, log_blank_line




def classify_signal(strength, threshold):
    if strength > threshold:
        return "Buy"
    elif strength < -threshold:
        return "Sell"
    else:
        return "Hold"



def integrate_signals(quotes_validated_df,signals_validated_df,matched_csv_path,strength_threshold):
    log_blank_line()
    logger.info("-------- Signal integration and classification --------")
    logger.info("===============================================")

    merged = pd.merge(quotes_validated_df, signals_validated_df, on="timestamp", how="left")
    merged["signal_strength"] = merged["signal_strength"].fillna(0)
    merged["action"] = merged["signal_strength"].apply(lambda x: classify_signal(x, threshold=strength_threshold))


    action_map = {
    "Buy": 1,
    "Sell": -1,
    "Hold": 0}

    merged['action_int'] = merged['action'].map(action_map)

    merged.to_csv(matched_csv_path, index=False)

    logger.info(f"INFO: Signal integration and classification completed successfully.")

    return merged