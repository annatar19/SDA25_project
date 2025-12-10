import pandas as pd
import glob
import re

from collections import defaultdict

def load_tennis_data(
    path_pattern="../data/tennis_atp_data/unaltered_data/*",
    regex_pattern=r"/atp_matches_\d{4}.csv",
    usecols=None,
):
    """
    path_pattern - str
        Path to the csv's
    regex_pattern - str
        Regex pattern that filters to 'atp_matches_XXXX.csv' files to load
    usecols - list
        columns to load from each csv. If empty, all cols will be loaded
    """

    ATP_PATH = path_pattern

    # Matches atp_matches_XXXX.csv
    match_fn_pattern = re.compile(regex_pattern)

    # Will make a list of strings like:
    # '../data/tennis_atp/atp_matches_qual_chall_1996.csv'
    atp_csv_fns = glob.glob(ATP_PATH)

    csvs = []
    for fn in atp_csv_fns:
        match = re.search(match_fn_pattern, fn)
        if match:
            # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            # My ide gives an error but it works fine.
            df = pd.read_csv(fn, usecols=usecols)
            csvs.append(df)

    if not csvs:
        raise ValueError("no matching csv files, make sure the regex or path pattern is correct")

    # All the .csv into 1, the loaded columns that is.
    return pd.concat(csvs, ignore_index=True)

# load_data for 2000
# df = pd.read_csv(usecols = ["tourney_id", "tourney_date", "winner_id", "loser_id", "match_num"]).dropna()

df = load_tennis_data(path_pattern="./data/tennis_atp_data/unaltered_data/*", usecols = ["tourney_id", "tourney_date", "winner_id", "winner_rank_points", "loser_rank_points", "loser_id", "match_num"]).dropna()

df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="%Y%m%d")

df = df.sort_values(["tourney_date", "match_num"]).reset_index(drop=True)

win_streak_dict = defaultdict(int)
winner_streaks = []
loser_streaks = []

for _, row in df.iterrows():
    winner = row["winner_id"]
    loser = row["loser_id"]

    winner_streaks.append(win_streak_dict[winner])
    loser_streaks.append(win_streak_dict[loser])

    win_streak_dict[winner] += 1
    win_streak_dict[loser] = 0

df["winner_streak"] = winner_streaks
df["loser_streak"] = loser_streaks

df.to_csv("matches_with_win_streaks.csv", index=False)
