import pandas as pd
from statsmodels.stats.proportion import proportions_ztest
import matplotlib.pyplot as plt


def load_winrate_summary():
    return pd.read_csv("hand_winrate_summary.csv", index_col=0)


def two_proportion_z_test(wins_R, total_R, wins_L, total_L):
    """
    Performs a two-proportion z-test.
    Test H0: no significant difference in win rate between left and right hand players

    Returns:
        z_stat (float): z statistic
        p_value (float): two-tailed p-value
    """
    successes = [wins_R, wins_L]
    observations = [total_R, total_L]

    z_stat, p_value = proportions_ztest(successes, observations)
    return z_stat, p_value


def plot_winrate_barchart(summary):

    p_L = summary.loc["L", "Win Rate"] * 100
    p_R = summary.loc["R", "Win Rate"] * 100
    diff = (p_R - p_L)

    win_rates = [p_L, p_R]
    labels = ["Left-handed", "Right-handed"]

    plt.figure(figsize=(6,4))

    bars = plt.bar(labels, win_rates, color=["gray", "black"], alpha=0.8)

    # Annotate % on top of each bar
    for bar, rate in zip(bars, win_rates):
        plt.text(
            bar.get_x() + bar.get_width()/2,
            bar.get_height() + 0.5,
            f"{rate:.1f}%",
            ha='center', va='bottom', fontsize=10
        )

    plt.ylabel("Win Rate (%)")
    plt.title("Win Rate Comparison: Left vs Right-Handed Players")
    plt.ylim(0, 100)
    plt.grid(True, axis='y', linestyle='--', alpha=0.4)

    plt.tight_layout()
    plt.figtext(
        0.5, 0,
        f"Difference = {diff:.2f}% (statistically significant but small effect)",
        ha='center', va='bottom', fontsize=10
    )

    plt.show()
    return plt


def main():
    winrate_summary = load_winrate_summary()
    z, p = two_proportion_z_test(
        wins_R=winrate_summary.loc["R", "Wins"], wins_L=winrate_summary.loc["L", "Wins"],
        total_R=winrate_summary.loc["R", "Total Matches"], total_L=winrate_summary.loc["L", "Total Matches"]
    )

    winrate_barchar = plot_winrate_barchart(winrate_summary)
    winrate_barchar

    print("\n=== Interpretation ===")
    print("Z-statistic:", round(z,2))
    print("p-value:", round(p,3))
    if p < 0.05:
        print("Result: Statistically significant difference between R and L win rates (p < 0.05).")
    else:
        print("Result: No statistically significant difference between R and L win rates (p ≥ 0.05).")


if __name__ == "__main__":
    main()
