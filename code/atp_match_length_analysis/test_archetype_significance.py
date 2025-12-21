import pandas as pd
import numpy as np
from scipy.stats import chi2_contingency
import matplotlib.pyplot as plt

DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"
PLOT_PATH = "../../graphs/archetype/"


def test_sig(df):
    contingency = pd.crosstab(df['player_archetype'], df['won'])
    chi2, p, dof, expected = chi2_contingency(contingency)
    return p


def plot_win_rate_by_group(df, p_value):
    win_rates = df.groupby('player_archetype')['won'].mean().sort_values()

    plt.figure(figsize=(8, 6))

    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(win_rates)))
    bars = plt.bar(win_rates.index, win_rates.values, color=colors)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width()/2,
            height + 0.015,
            f"{height:.2f}",
            ha='center', va='bottom', fontsize=11
        )

    plt.grid(axis='y', linestyle='--', alpha=0.4)
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 1)

    plt.ylabel("Win Rate")
    # plt.xlabel("Player Archetype")
    plt.title("Win Rate by Archetype", fontsize=16, weight='bold')

    significance = "significant" if p_value < 0.05 else "not significant"

    plt.subplots_adjust(bottom=0.20)

    if p_value < 0.001:
        p_text = "p < 0.001"
    else:
        p_text = f"p = {p_value:.5f}"

    plt.figtext(
        0.5, 0.02,
        f"Chi-square test: {p_text} ({significance})",
        ha='center',
        fontsize=11
    )

    return plt


if __name__ == "__main__":
    data_file_path = DATA_PATH + "archetype_matchups.csv"
    df = pd.read_csv(data_file_path)[['player_id', 'player_archetype', 'won']]

    p_value = test_sig(df)
    b_plot = plot_win_rate_by_group(df, p_value)

    print(f"Saving: {PLOT_PATH}archetype_winrates.png")
    b_plot.savefig(PLOT_PATH + "archetype_winrate.png", dpi=300)
