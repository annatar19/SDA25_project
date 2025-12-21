# This file analyzes whether the type of sruface effects the ace rates significantly,
# so for example is the acerates on clay really equal to acerates on grass? since
# logically clay is a slower surface than grass.
# INPUT: raw csv's (using data_loader/load_data.py)
# OUTPUT: Plot of acerates, terminal prompt result of ANOVA test
# NULL HYPOTHESIS = There is no difference in ace_rates between the different surfaces

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from data_loader.load_data import load_tennis_data


def preprocess_data(data):
    # Removing rows that are NaN for ace and svpt as both needed for acerate calculation
    # Removing invalid row, by making sure svpt is greater than 0
    # Removing the surface carpet, as not played on anymore and low # data
    print(f"\ninitial data size = {len(data)}")
    data = data.dropna(subset=['w_ace', 'w_svpt', 'l_ace', 'l_svpt'])
    data = data[(data['w_svpt'] > 0) & (data['l_svpt'] > 0)]
    data = data[data['surface'].isin(['Hard', 'Clay', 'Grass'])]
    print(f"data size after preprocess = {len(data)}")
    return data


def acerates_per_surfacec(data):
    # Splitting match row data in 2 rows, 1 for each player, and naming them equally
    # Reasoning: We want to aggregate on player level, rather than calculating acerate
    # per match (which we did initially). Doing this ensures independency. As now a single
    # player that played 100+ matches wont constantly be reused to calculate the acerate
    # We can then use ANOVA correctly on this now that it is independent.
    winner_df = data[['winner_id', 'surface', 'w_ace', 'w_svpt']].copy()
    winner_df.columns = ['player_id', 'surface', 'aces', 'svpt']
    loser_df = data[['loser_id', 'surface', 'l_ace', 'l_svpt']].copy()
    loser_df.columns = ['player_id', 'surface', 'aces', 'svpt']
    df_concateed = pd.concat([winner_df, loser_df], ignore_index=True)

    player_surface = (
        df_concateed
        .groupby(['player_id', 'surface'])
        .agg(total_aces=('aces', 'sum'), total_svpt=('svpt', 'sum'))
        .reset_index()
    )
    player_surface['ace_rate'] = (player_surface['total_aces'] / player_surface['total_svpt']) * 100

    return player_surface


def run_anova(player_surface):
    # Quick analysis to check means
    hard_aces = player_surface[player_surface['surface'] == 'Hard']['ace_rate'].values
    clay_aces = player_surface[player_surface['surface'] == 'Clay']['ace_rate'].values
    grass_aces = player_surface[player_surface['surface'] == 'Grass']['ace_rate'].values
    print("\nAce rates (mean per player per surface):")
    for surface, data_subset in [('Grass', grass_aces), ('Hard', hard_aces), ('Clay', clay_aces)]:
        print(f"  {surface}: mean = {np.mean(data_subset):.2f}%")

    # ANOVA test, since we have 3 classes. F stat doesnt seem all to important
    # https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f_oneway.html
    _, p_value = stats.f_oneway(hard_aces, clay_aces, grass_aces)
    print(f"p-value: {p_value:.5e}")

    if p_value < 0.05:
        print("REJECT null hypothesis (surface has significant effect on ace rates)")
    else:
        print("FAIL TO REJECT null hypothesis (surface does NOT have significant effect)")

    return hard_aces, clay_aces, grass_aces


def plot_ace_rates(player_surface):
    # Visualisation
    colors = {'Grass': 'green', 'Hard': 'blue', 'Clay': 'orange'}
    surfaces = ['Grass', 'Hard', 'Clay']

    plt.figure(figsize=(15, 12))

    for surface in surfaces:
        data_per = player_surface[player_surface['surface'] == surface]['ace_rate']

        plt.hist(
            data_per,
            bins=50,
            alpha=0.5,
            color=colors[surface],
            density=True,
            edgecolor='black',
            linewidth=0.1,
            label=surface
        )

        mean_val = data_per.mean()
        plt.axvline(mean_val, color=colors[surface], linestyle='--', linewidth=2)

        plt.text(
            mean_val,
            plt.ylim()[1]*0.95,
            f'{mean_val:.2f}%',
            ha='center',
            fontsize=15,
            fontweight='bold',
            color="black"
        )

    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    # because of the long tail decided to limit to 0-25% this way it can fit in
    # PPTX slide
    plt.xlim([0, 25])
    plt.xlabel('Ace Rate (% of service points)', fontsize=20)
    plt.ylabel('Density', fontsize=20)
    plt.title('Ace rate by court surface (per player, 2000-2024)', fontsize=25)
    plt.legend(fontsize=20)
    plt.grid(True, alpha=0.25, linestyle='--')
    plt.tight_layout()
    plt.savefig('../../graphs/surface/surfaces_acerates.png')
    return


def main():
    data = load_tennis_data(
            path_pattern="../../data/tennis_atp_data/unaltered_data/*",
            regex_pattern=r"/atp_matches_(198[0-9]|199[0-9]|20[0-1][0-9]|202[0-4])\.csv",
            usecols=[
                    'tourney_date', 'surface', 'tourney_level',
                    'w_ace', 'w_svpt', 'l_ace', 'l_svpt', 'winner_id', 'loser_id'])
    preprocessed_df = preprocess_data(data)
    player_acerates = acerates_per_surfacec(preprocessed_df)
    print("\nANOVA test:")
    run_anova(player_acerates)
    print("\nVISUALISATIE go to ../../graphs/surface/surfaces_acerates.png")
    plot_ace_rates(player_acerates)


if __name__ == "__main__":
    main()
