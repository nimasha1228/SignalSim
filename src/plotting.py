import matplotlib.pyplot as plt


def plot_spread_distribution(spread, mean, k, spread_threshold, save_path):

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
    plt.savefig(save_path, dpi=300, bbox_inches="tight")
    print(f"✅ Plot saved at: {save_path}")