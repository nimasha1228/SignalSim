import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os


def plot_spread_distribution(spread, mean, k, spread_threshold, plots_dir_path):

    # Plot histogram
    plt.figure(figsize=(10,6))
    plt.hist(spread, bins=100, alpha=0.7, label="Spread distribution")

    # Mean line
    plt.axvline(mean, color="blue", linestyle="--", linewidth=2, 
                label=f"Mean = {mean:.6e}")

    # Threshold line
    plt.axvline(spread_threshold, color="red", linestyle="--", linewidth=2,
                label=f"Threshold = mean + {k}σ = {spread_threshold:.6e}")

    plt.title("Relative Bid-Ask Spread Distribution")
    plt.xlabel("Relative Spread ( (ask - bid) / bid )")
    plt.ylabel("Frequency")
    plt.legend()
    plt.grid(True)

    # Save
    file_save_path = os.path.join(plots_dir_path, "spread_distribution.png")
    plt.savefig(file_save_path, dpi=300, bbox_inches="tight")
    print(f"✅ Spread Distribution plot saved at: {plots_dir_path}")


def plot_exchange_order_delay(df, plots_dir_path, unit="ms"):
    # Compute delay
    if unit == "ms":
        df["delay"] = (df["exchange_time"] -df["order_sent_time"]).dt.total_seconds() * 1000
        ylabel = "Delay (ms)"
    else:
        df["delay"] = (df["exchange_time"] -df["order_sent_time"]).dt.total_seconds()
        ylabel = "Delay (s)"

    # Drop rows with missing order_sent_time
    df =df.dropna(subset=["order_sent_time"])

    # Plot
    plt.figure(figsize=(10, 5))
    plt.plot(df["exchange_time"], df["delay"], marker="o", linestyle="-", label="Delay")
    plt.xlabel("Exchange Time")
    plt.ylabel(ylabel)
    plt.title("Delay Between Order Sent Time and Received at Exchange")
    plt.grid(True)
    plt.legend()

    # Save 
    file_save_path = os.path.join(plots_dir_path, "execution_delay.png")
    plt.savefig(file_save_path, dpi=300, bbox_inches="tight")
    plt.close()


def plot_and_save_max_drawdown(df, plots_dir_path):
    """
    Calculate and plot Maximum Drawdown (MDD), and save the figure.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing per-trade or per-step PnL.
    pnl_col : str, default "pnl_per_trade"
        Column name containing PnL values.
    save_path : str, default "max_drawdown_plot.png"
        File path to save the plot (PNG format recommended).

    Returns
    -------
    max_drawdown : float
        Maximum drawdown value.
    max_drawdown_pct : float
        Maximum drawdown percentage.
    """

    # --- Extract PnL array ---
    pnl = df["gross_pnl_per_trade"].to_numpy(dtype=float)
    cum_pnl = np.cumsum(pnl)
    running_max = np.maximum.accumulate(cum_pnl)
    drawdown = cum_pnl - running_max

    # --- Find max drawdown (most negative dip) ---
    max_dd_idx = np.argmin(drawdown)
    max_dd = drawdown[max_dd_idx]

    # --- Plot ---
    plt.figure(figsize=(10,6))
    plt.plot(cum_pnl, label="Cumulative PnL", color='blue')
    plt.plot(running_max, '--', label="Running Max", color='gray')
    plt.fill_between(np.arange(len(cum_pnl)), cum_pnl, running_max, color='red', alpha=0.25)
    plt.scatter(max_dd_idx, cum_pnl[max_dd_idx], color='red', marker='o', s=60,
                label=f"Max Drawdown = {max_dd:.2f}")
    plt.title("Equity Curve with Maximum Drawdown (Absolute PnL)")
    plt.xlabel("Trade Index")
    plt.ylabel("Cumulative PnL")
    plt.legend()
    plt.grid(True)


    # --- Save Plot ---
    os.makedirs(os.path.dirname(plots_dir_path) or ".", exist_ok=True)
    save_path = os.path.join(plots_dir_path, "max_drawdown_plot.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"📁 Plot saved at: {os.path.abspath(save_path)}")

    return max_dd


def plot_and_analyze_pnl(df, plots_dir_path):

    # --- Ensure directory exists ---
    os.makedirs(plots_dir_path, exist_ok=True)

    # --- Prepare data ---
    df = df.copy()
    df["exchange_time"] = pd.to_datetime(df["exchange_time"])
    df["realized_pnl"] = df["realized_pnl"].astype(float)
    df["unrealized_pnl"] = df["unrealized_pnl"].astype(float)
    df["total_pnl"] = df["realized_pnl"] + df["unrealized_pnl"]

    # --- Compute Metrics ---
    gross_pnl = df["realized_pnl"].sum()
    net_pnl = df["total_pnl"].iloc[-1] - df["total_pnl"].iloc[0]

    # Count trades = nonzero realized pnl events
    num_trades = (df["realized_pnl"] != 0).sum()
    avg_trade_pnl = gross_pnl / num_trades if num_trades > 0 else 0.0

    # --- Plot ---
    plt.figure(figsize=(12, 6))
    plt.plot(df["exchange_time"], df["total_pnl"], label="Total PnL", color="blue", linewidth=2)
    plt.plot(df["exchange_time"], df["realized_pnl"], label="Realized PnL", color="green", linestyle="--", linewidth=1.8)
    plt.plot(df["exchange_time"], df["unrealized_pnl"], label="Unrealized PnL", color="orange", linestyle=":", linewidth=1.8)
    plt.fill_between(df["exchange_time"], df["unrealized_pnl"], alpha=0.1, color="orange")

    # --- Format datetime axis ---
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.gcf().autofmt_xdate()


    plt.title("PnL Evolution Over Time", fontsize=14, fontweight="bold")
    plt.xlabel("Time", fontsize=12)
    plt.ylabel("PnL", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # --- Save plot ---
    save_path = os.path.join(plots_dir_path, "pnl_analysis.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ PnL plot saved to: {save_path}")
    print(f"📈 Gross PnL: {gross_pnl:.2f}, Net PnL: {net_pnl:.2f}, Avg Trade PnL: {avg_trade_pnl:.4f}, Trades: {num_trades}")

    # --- Return summary ---
    return {
        "gross_pnl": gross_pnl,
        "net_pnl": net_pnl,
        "average_trade_pnl": avg_trade_pnl,
        "num_trades": num_trades
    }



def plot_execution_probability_scatter(df, plots_dir_path, min_exec_prob_threshold):

    # --- Ensure directory exists ---
    os.makedirs(plots_dir_path, exist_ok=True)

    # --- Validate column ---
    if "prob_exec" not in df.columns:
        print("⚠️ Column 'prob_exec' not found in DataFrame.")
        return

    # --- Prepare data ---
    df = df.copy()
    if "exchange_time" in df.columns:
        df["exchange_time"] = pd.to_datetime(df["exchange_time"])
        x_axis = df["exchange_time"]
        xlabel = "Time"
    else:
        x_axis = range(len(df))
        xlabel = "Simulation Step"

    # --- Round for clarity ---
    df["prob_exec"] = df["prob_exec"].round(4)

    # --- Scatter plot ---
    plt.figure(figsize=(12, 6))

    if "signal" in df.columns:
        # Color by signal: +1 = Buy, -1 = Sell, 0 = Hold
        colors = df["signal"].map({1: "blue", -1: "red", 0: "gray"})
        plt.scatter(x_axis, df["prob_exec"], c=colors, alpha=0.7, s=40, label="Execution Probability")
        plt.scatter([], [], color="blue", label="Buy")
        plt.scatter([], [], color="red", label="Sell")
        plt.scatter([], [], color="gray", label="Hold")
    else:
        plt.scatter(x_axis, df["prob_exec"], color="purple", alpha=0.7, s=40, label="Execution Probability")

    # --- Threshold line ---
    plt.axhline(min_exec_prob_threshold, color="black", linestyle="--", linewidth=1,
                label=f"Min Exec Threshold ({min_exec_prob_threshold})")

    # --- Formatting ---
    plt.title("Execution Probability Scatter Plot", fontsize=14, fontweight="bold")
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel("Execution Probability", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # --- Format datetime axis if applicable ---
    if "exchange_time" in df.columns:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate(rotation=30)

    # --- Save plot ---
    save_path = os.path.join(plots_dir_path, "execution_prob_scatter.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Execution probability scatter plot saved to: {save_path}")
    print(f"📊 Threshold line used: {min_exec_prob_threshold}")


def plot_line_column(df, column_name, plots_dir_path):
 
    # --- Ensure directory exists ---
    os.makedirs(plots_dir_path, exist_ok=True)

    # --- Validate column ---
    if column_name not in df.columns:
        print(f"⚠️ Column '{column_name}' not found in DataFrame.")
        return

    # --- Prepare data ---
    df = df.copy()
    if "exchange_time" in df.columns:
        df["exchange_time"] = pd.to_datetime(df["exchange_time"])
        x_axis = df["exchange_time"]
        xlabel = "Time"
    else:
        x_axis = range(len(df))
        xlabel = "Simulation Step"

    # --- Round numeric data for clarity ---
    if pd.api.types.is_numeric_dtype(df[column_name]):
        df[column_name] = df[column_name].round(4)

    # --- Line plot ---
    plt.figure(figsize=(12, 6))
    plt.plot(x_axis, df[column_name], color="blue", linewidth=1.5, label=column_name.replace("_", " ").title())

    # --- Formatting ---
    plt.title(f"{column_name.replace('_', ' ').title()} Line Plot", fontsize=14, fontweight="bold")
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(column_name.replace("_", " ").title(), fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # --- Format datetime axis if applicable ---
    if "exchange_time" in df.columns:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate(rotation=30)

    # --- Save plot ---
    save_path = os.path.join(plots_dir_path, f"{column_name}_line_plot.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Line plot for '{column_name}' saved to: {save_path}")


def plot_signal_vs_spread_flag(df, plots_dir_path):
    """
    Plot signal vs spread_flag and save the plot.

    Args:
        df (pd.DataFrame): DataFrame containing 'signal' and 'spread_flag' columns.
        plots_dir_path (str): Directory path to save the plot.
    """

    # --- Ensure directory exists ---
    os.makedirs(plots_dir_path, exist_ok=True)

    # --- Validate required columns ---
    required_cols = {"signal", "spread_flag"}
    if not required_cols.issubset(df.columns):
        print(f"⚠️ DataFrame must contain the columns: {required_cols}")
        return

    # --- Prepare data ---
    df = df.copy()
    if "exchange_time" in df.columns:
        df["exchange_time"] = pd.to_datetime(df["exchange_time"])
        x_axis = df["exchange_time"]
        xlabel = "Time"
    else:
        x_axis = range(len(df))
        xlabel = "Simulation Step"

    # --- Round for clarity ---
    if pd.api.types.is_numeric_dtype(df["signal"]):
        df["signal"] = df["signal"].round(3)

    # --- Create figure ---
    plt.figure(figsize=(12, 6))

    # --- Plot signal (line) ---
    plt.plot(x_axis, df["signal"], color="blue", linewidth=1.5, label="Signal")

    # --- Overlay spread_flag (scaled for visibility) ---
    spread_scaled = df["spread_flag"] * df["signal"].abs().max()
    plt.step(x_axis, spread_scaled, color="red", linestyle="--", linewidth=1.2, label="Spread Flag (scaled)")

    # --- Formatting ---
    plt.title("Signal vs Spread Flag", fontsize=14, fontweight="bold")
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel("Signal Value", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # --- Format datetime axis if applicable ---
    if "exchange_time" in df.columns:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate(rotation=30)

    # --- Save plot ---
    save_path = os.path.join(plots_dir_path, "signal_vs_spread_flag.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Signal vs Spread Flag plot saved to: {save_path}")

def plot_action_vs_signal_strength(matched_df, plots_dir_path, strength_threshold=0.5):

    # --- Ensure directory exists ---
    os.makedirs(plots_dir_path, exist_ok=True)

    # --- Validate required columns ---
    required_cols = {"action_int", "signal_strength"}
    if not required_cols.issubset(matched_df.columns):
        print(f"⚠️ DataFrame must contain the columns: {required_cols}")
        return

    # --- Prepare data ---
    df = matched_df.copy()
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        x_axis = df["timestamp"]
        xlabel = "Time"
    else:
        x_axis = range(len(df))
        xlabel = "Simulation Step"

    # --- Round for clarity ---
    df["signal_strength"] = df["signal_strength"].round(4)

    # --- Create figure ---
    plt.figure(figsize=(12, 6))

    # --- Plot signal strength as line ---
    plt.plot(x_axis, df["signal_strength"], color="blue", linewidth=1.5, label="Signal Strength")

    # --- Overlay action_int (scaled for visibility) ---
    action_scaled = df["action_int"] * df["signal_strength"].abs().max()
    plt.step(x_axis, action_scaled, color="orange", linewidth=1.5, linestyle="--", label="Action Int (scaled)")

    # --- Threshold line ---
    plt.axhline(y=strength_threshold, color="green", linestyle="--", linewidth=1.2,
                label=f"Strength Threshold (+{strength_threshold})")
    plt.axhline(y=-strength_threshold, color="green", linestyle="--", linewidth=1.2,
                label=f"Strength Threshold (-{strength_threshold})")

    # --- Formatting ---
    plt.title("Action vs Signal Strength", fontsize=14, fontweight="bold")
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel("Signal Strength / Action (scaled)", fontsize=12)
    plt.legend()
    plt.grid(True, linestyle="--", alpha=0.6)
    plt.tight_layout()

    # --- Format datetime axis if applicable ---
    if "timestamp" in df.columns:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
        plt.gcf().autofmt_xdate(rotation=30)

    # --- Save plot ---
    save_path = os.path.join(plots_dir_path, "action_vs_signal_strength.png")
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"✅ Action vs Signal Strength plot saved to: {save_path}")
    print(f"📊 Threshold line marked at ±{strength_threshold}")