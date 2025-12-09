# atp_hand.py
#
# Small script for analysing ATP tennis match data by dominant hand.
# Loads all the yearly match CSV files turn each match into two player-
# perspective rows (winner and loser), and then calculates:
# - overall win rates for left/right handed players
# - win rates of each matchup type (RvsR, RvsL, LvsR, LvsL)
# - a very rough rank-controlled version using rank difference bins
#
# Graph plot is saved under graphs folder
# - Results seem to show any meaningful difference in win rates between
# left handed and right handed players. The raw matchups are already super
# close with a slight (~2% disavantage for left handed players) this could be
# because of a rank bias, where there are more right handed players, therefore
# left handed players play against more high ranked players. Even taking this
# bias into account and recalculating winrates with a rough rank difference
# using bins, we see that it almost equals out to 50/50. Showing that there is
# no meaninfull difference in the dominant hand winrates of a player.


import pandas as pd
import numpy as np
import glob
import re
from pathlib import Path
import matplotlib.pyplot as plt

DATA_DIR = Path(__file__).resolve().parents[2] / "data/tennis_atp_data/unaltered_data"

# change these for different year analysis rgane
YEAR_START = 1991
YEAR_END = 2024

USECOLS = [
    "tourney_id",
    "winner_id",
    "winner_hand",
    "winner_rank",
    "loser_id",
    "loser_hand",
    "loser_rank"
]


# find all yearly files from year start to year end globals
def list_year_files(dir_path=DATA_DIR, y0=YEAR_START, y1=YEAR_END):
    files = glob.glob(str(dir_path / "atp_matches_*.csv"))
    rx = re.compile(r"atp_matches_(\d{4})\.csv$")
    out = []
    for f in files:
        m = rx.search(Path(f).name)
        if m:
            y = int(m.group(1))
            if y0 <= y <= y1:
                out.append((y, f))
    out.sort()
    return [f for _, f in out]


# keep L/R only drop others
def normalize_hand(s):
    s = s.astype(str).str.strip().str.upper()
    s = s.replace({"": np.nan, "U": np.nan})
    return s.where(s.isin(["L", "R"]), np.nan)


def load_matches():
    files = list_year_files()

    dfs = []
    for fn in files:
        cols = pd.read_csv(fn, nrows=0).columns
        use = [c for c in USECOLS if c in cols]
        if not use:
            continue
        df = pd.read_csv(fn, usecols=use)
        if "winner_hand" in df:
            df["winner_hand"] = normalize_hand(df["winner_hand"])
        if "loser_hand" in df:
            df["loser_hand"] = normalize_hand(df["loser_hand"])

        dfs.append(df)

    if not dfs:
        raise ValueError("Column not be here")

    return pd.concat(dfs, ignore_index=True)


# turn each match into 2 rows (player pov): winner (won=1), loser (won=0)
# and also computes the player rank difference between the matchup
def build_hand_pov(df):
    m = df[[
        "winner_id", "winner_hand", "winner_rank",
        "loser_id", "loser_hand", "loser_rank"
    ]].dropna().copy()

    rows = []
    for _, r in m.iterrows():
        # winners row
        rows.append({
            "hand": r["winner_hand"],
            "opp_hand": r["loser_hand"],
            "won": 1,
            "rank": r["winner_rank"],
            "opp_rank": r["loser_rank"],
            "rank_diff": r["loser_rank"] - r["winner_rank"],
        })

        # losers row
        rows.append({
            "hand": r["loser_hand"],
            "opp_hand": r["winner_hand"],
            "won": 0,
            "rank": r["loser_rank"],
            "opp_rank": r["winner_rank"],
            "rank_diff": r["winner_rank"] - r["loser_rank"],
        })

    pov = pd.DataFrame(rows)

    # keep only those with actual data (L/R and not nan)
    pov = pov[pov["hand"].isin(("L", "R")) & pov["opp_hand"].isin(("L", "R"))]
    pov = pov.reset_index(drop=True)

    return pov


# matchup to string helper
def matchup_code(h, oh):
    if h == "R" and oh == "R":
        return "RvsR"
    if h == "R" and oh == "L":
        return "RvsL"
    if h == "L" and oh == "R":
        return "LvsR"

    return "LvsL"


# compute winrates for each matchup type by grouping on hand vs opp_hand
def winrates_by_matchup(pov):
    # make the matchup labels
    labels = [matchup_code(h, oh) for h, oh in zip(pov["hand"], pov["opp_hand"])]

    # assign the labels onto the dataframe, group by matchup, average the won
    wr = (
        pov.assign(matchup=labels)
            .groupby("matchup")["won"]
            .mean()
            .reindex(["RvsR", "RvsL", "LvsR", "LvsL"])
    )

    return wr


# overall R vs L, ignoring opponent hand
def overall_hand_winrates(pov):
    return pov.groupby("hand")["won"].mean().reindex(["R", "L"])


# super rough rank control with bins
def rank_controlled_by_matchup(pov):
    bins = (-999, -200, -100, -50, -10, 10, 50, 100, 200, 999)

    # make matchup labels
    labels = [matchup_code(h, oh) for h, oh in zip(pov["hand"], pov["opp_hand"])]
    b = pov.copy()
    b["matchup"] = labels

    # put rows into rank difference bins
    b["bin"] = pd.cut(b["rank_diff"], bins=bins, labels=False, include_lowest=True)

    # compute a per bin win rate
    per_bin = b.groupby(["matchup", "bin"])["won"].mean().unstack("bin")

    # return the mean of those win rates per bin
    return per_bin.mean(axis=1).reindex(["RvsR", "RvsL", "LvsR", "LvsL"])


# tiny helper for the position of the winrate numbers on the bars
def _annotate(ax):
    for p in ax.patches:
        ax.text(
            p.get_x()+p.get_width()/2,
            p.get_height()+0.002,
            f"{p.get_height():.3f}",
            ha="center",
            va="bottom",
            fontsize=8
        )


def plot_hand_winrates(overall_hand, matchup_rates, matchup_adj):
    fig, axs = plt.subplots(1, 3, figsize=(12, 4))

    axs[0].bar(overall_hand.index, overall_hand.values)
    axs[0].set_title("Overall Win Rate by Hand")
    axs[0].set_ylim(0.45, 0.55)
    axs[0].set_ylabel("Win rate")
    axs[0].grid(alpha=0.3, linestyle="--")
    _annotate(axs[0])

    axs[1].bar(matchup_rates.index, matchup_rates.values)
    axs[1].set_title("Matchup Win Rates (Hand vs Opp Hand)")
    axs[1].set_ylim(0.45, 0.55)
    axs[1].grid(alpha=0.3, linestyle="--")
    _annotate(axs[1])

    axs[2].bar(matchup_adj.index, matchup_adj.values)
    axs[2].set_title("Rank-Controlled Matchup Win Rates")
    axs[2].set_ylim(0.45, 0.55)
    axs[2].grid(alpha=0.3, linestyle="--")
    _annotate(axs[2])

    plt.suptitle("ATP Handedness Win Rates (1991–2024)")
    plt.tight_layout()
    plt.show()


def main():
    df = load_matches()
    pov = build_hand_pov(df)

    overall = overall_hand_winrates(pov)
    matchup = winrates_by_matchup(pov)
    rank_matchup = rank_controlled_by_matchup(pov)

    # print("Overall win rate by hand:\n", overall.round(4))
    # print("\nMatchup win rates (raw):\n", matchup.round(4))
    # print("\nMatchup win rates (rank-controlled):\n", adj.round(4))

    # plot
    plot_hand_winrates(overall, matchup, rank_matchup)


if __name__ == "__main__":
    main()
