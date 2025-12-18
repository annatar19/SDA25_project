import pandas as pd
import numpy as np
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


def plot_winrate_barchart(summary, p_value=None, z_value=None):
    """
    Win rate bar chart
    """

    win_rates = (
        summary.loc[["L", "R"], "Win Rate"]
        .rename(index={"L": "Left-handed", "R": "Right-handed"})
        .sort_values()
    )

    plt.figure(figsize=(8, 6))

    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(win_rates)))
    bars = plt.bar(win_rates.index, win_rates.values, color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 0.01,
            f"{height:.3f}",
            ha="center",
            va="bottom",
            fontsize=11
        )

    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.xticks(rotation=0)
    plt.ylim(0, 1)

    plt.ylabel("Win Rate")
    plt.title(
        "Win Rate Comparison: Left vs Right-Handed Players",
        fontsize=16,
        weight="bold"
    )

    plt.subplots_adjust(bottom=0.23)

    if p_value is not None and z_value is not None:
        significance = "significant" if p_value < 0.05 else "not significant"

        if p_value < 0.001:
            p_text = "p < 0.001"
        else:
            p_text = f"p = {p_value:.5f}"

        # Difference (Right - Left) in percentage points
        pL = win_rates["Left-handed"]
        pR = win_rates["Right-handed"]
        nL = summary.loc["L", "Total Matches"]
        nR = summary.loc["R", "Total Matches"]

        diff = pR - pL
        diff_pp = diff * 100

        # 95% CI for the difference in proportions (normal approx)
        se_diff = np.sqrt(pR * (1 - pR) / nR + pL * (1 - pL) / nL)
        ci_low_pp = (diff - 1.96 * se_diff) * 100
        ci_high_pp = (diff + 1.96 * se_diff) * 100

        plt.figtext(
            0.5, 0.08,
            f"Two-proportion z-test: z = {z_value:.2f}, {p_text} ({significance})\n"
            f"Difference (Right − Left) = {diff_pp:.2f} percentage points\n"
            f"95% CI for difference: [{ci_low_pp:.2f}, {ci_high_pp:.2f}] percentage points",
            ha="center",
            fontsize=11
        )


def plot_total_match_appearances_by_hand(summary):
    """
    plt graph 1
    """

    counts = (
        summary.loc[["L", "R"], "Total Matches"]
        .rename(index={"L": "Left-handed", "R": "Right-handed"})
    )

    plt.figure(figsize=(8, 6))

    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(counts)))
    bars = plt.bar(counts.index, counts.values, color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + height * 0.01,
            f"{int(height):,}",
            ha="center", va="bottom", fontsize=11
        )

    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.xticks(rotation=0)
    plt.ylim(0, counts.max() * 1.10)

    plt.ylabel("Total Match Appearances")
    plt.title("ATP Match Appearances by Player Handedness",
              fontsize=16, weight="bold")

    total_matches = counts.sum()
    left_pct = 100 * counts["Left-handed"] / total_matches
    right_pct = 100 * counts["Right-handed"] / total_matches

    plt.subplots_adjust(bottom=0.20)

    plt.figtext(
        0.5, 0.1,
        f"Left-handed: {left_pct:.1f}%   |   Right-handed: {right_pct:.1f}% of all matches",
        ha="center",
        fontsize=11
    )

    return plt


def main():
    winrate_summary = load_winrate_summary()

    # Context plot
    plot_total_match_appearances_by_hand(winrate_summary)

    # Statistical test
    z, p = two_proportion_z_test(
        wins_R=winrate_summary.loc["R", "Wins"],
        wins_L=winrate_summary.loc["L", "Wins"],
        total_R=winrate_summary.loc["R", "Total Matches"],
        total_L=winrate_summary.loc["L", "Total Matches"]
    )

    # Result plot
    plot_winrate_barchart(winrate_summary, p_value=p, z_value=z)

    plt.show()


if __name__ == "__main__":
    main()
