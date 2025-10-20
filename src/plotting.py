import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
import os
from metrics import *


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
    print(f"Spread Distribution plot saved at: {plots_dir_path}")


def plot_pnl_and_slippage_summary(df, plots_dir_path):
    """
    Plot PnL, slippage, and drawdown metrics in a 2-column layout:
    Left: Gross vs Net PnL + Max Drawdown curves.
    Right: Slippage curve + textual summary.
    """

    # --- Extract metrics using your helper functions ---
    gross_pnl, net_pnl = get_gross_and_net_pnl(df)
    avg_trade_pnl = calculate_average_trade_pnl(df)
    avg_slippage, total_trade_count = calculate_average_slippage(df)
    max_drawdown, max_drawdown_percentage = get_max_drawdown(df)

    # --- Convert timestamp ---
    df["exchange_time"] = pd.to_datetime(df["exchange_time"])
    x = df["exchange_time"]

    # --- Date formatter for axes ---
    datetime_formatter = mdates.DateFormatter("%Y-%m-%d %H:%M:%S")

    # --- Create 2-column grid ---
    fig = plt.figure(figsize=(14, 8))  # increased height for better visibility
    gs = fig.add_gridspec(2, 2, width_ratios=[2, 1], height_ratios=[1, 1], wspace=0.25, hspace=0.6)

    # ======================================================
    # (1,1) Gross vs Net PnL (Top Left)
    # ======================================================
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.plot(x, df["gross_pnl"], label="Gross PnL", color="green", linewidth=1.5)
    ax1.plot(x, df["net_pnl"], label="Net PnL", color="orange", linestyle="--", linewidth=1.5)
    ax1.axhline(y=avg_trade_pnl, color="blue", linestyle=":", linewidth=1.2,
                label=f"Avg Trade PnL ({avg_trade_pnl:.4f})")

    dd_idx = df["max_drawdown"].idxmax()
    dd_time = df.loc[dd_idx, "exchange_time"]
    dd_pnl = df.loc[dd_idx, "net_pnl"]
    ax1.scatter(dd_time, dd_pnl, color="red", s=60, zorder=5,
                label=f"Max Drawdown: {max_drawdown:.2f} ({max_drawdown_percentage:.2f}%)")

    ax1.set_title("Gross vs Net PnL with Avg Trade PnL & Max Drawdown")
    ax1.set_ylabel("PnL")
    ax1.legend()
    ax1.grid(True)
    ax1.xaxis.set_major_formatter(datetime_formatter)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=10, ha="right", fontsize=8)

    # ======================================================
    # (2,1) Max Drawdown Progression (Bottom Left)
    # ======================================================
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.plot(x, df["max_drawdown"], color="darkred", linewidth=1.5, label="Max Drawdown")
    ax2.set_title("Max Drawdown Progression Over Time")
    ax2.set_xlabel("Exchange Time")
    ax2.set_ylabel("Drawdown")
    ax2.legend()
    ax2.grid(True)
    ax2.xaxis.set_major_formatter(datetime_formatter)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=10, ha="right", fontsize=8)

    # ======================================================
    # (1,2) Slippage Curve (Top Right)
    # ======================================================
    ax3 = fig.add_subplot(gs[0, 1])
    ax3.plot(x, df["slippage"], color="salmon", linewidth=1.3, label="Slippage per Trade")
    ax3.axhline(y=avg_slippage, color="brown", linestyle=":", linewidth=1.2,
                label=f"Avg Slippage ({avg_slippage:.4f})")
    ax3.set_title("Slippage Over Time with Average Marker")
    ax3.set_ylabel("Slippage")
    ax3.legend()
    ax3.grid(True)
    ax3.xaxis.set_major_formatter(datetime_formatter)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=25, ha="right", fontsize=8)

    # ======================================================
    # (2,2) Summary Text Box (Bottom Right)
    # ======================================================
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")

    summary_text = (
        f"─────────────────────────────\n"
        f"Summary Metrics\n"
        f"─────────────────────────────\n"
        f"Total Trades: {int(total_trade_count)}\n"
        f"Average Trade PnL: {avg_trade_pnl:.6f}\n"
        f"Average Slippage: {avg_slippage:.6f}\n"
        f"Gross PnL: {gross_pnl:.6f}\n"
        f"Net PnL: {net_pnl:.6f}\n"
        f"Max Drawdown: {max_drawdown:.4f} ({max_drawdown_percentage:.2f}%)\n"
        f"─────────────────────────────\n"
    )

    ax4.text(0.05, 0.9, summary_text, fontsize=10, fontfamily="monospace",
             va="top", ha="left", linespacing=1.5,
             bbox=dict(facecolor="whitesmoke", alpha=0.9, boxstyle="round"))


    # Save and show
    combined_path = os.path.join(plots_dir_path, "pnl_slippage_dd_summary_grid.png")
    plt.savefig(combined_path, dpi=300, bbox_inches="tight")
    plt.show()

    # --- Print Summary ---
    print(summary_text)
    print(f"Combined plot saved to: {os.path.abspath(combined_path)}")
