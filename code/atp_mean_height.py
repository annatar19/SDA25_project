# Partly meant as a sortof template/example, partly exploration.
# Only uses the atp_matches_XXXX.csv data, not the doubles and such.
import pandas as pd
import glob
import re

ATP_PATH = "../data/tennis_atp/*"
# Matches atp_matches_XXXX.csv
match_fn_pattern = re.compile(r"/atp_matches_\d{4}.csv")

# More convenient
usecols = [
    "winner_id",
    "winner_name",
    "winner_ht",
    "loser_id",
    "loser_name",
    "loser_ht",
]

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
print(csvs)
