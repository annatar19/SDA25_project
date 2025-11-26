# Partly meant as a sortof template/example, partly exploration.
# Only uses the atp_matches_XXXX.csv data, not the doubles and such.
import pandas as pd
import glob
import re

ATP_PATH = "../data/tennis_atp_data/unaltered_data/*"
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
        df = pd.read_csv(fn, usecols=usecols)  # pyright: ignore
        csvs.append(df)
# All the .csv into 1, the loaded columns that is.
data = pd.concat(csvs, ignore_index=True)

winners = data[
    ["winner_id", "winner_name", "winner_ht"]
].rename(  # pyright: ignore[reportCallIssue]
    columns={
        "winner_id": "id",
        "winner_name": "name",
        "winner_ht": "ht",
    }
)

losers = data[
    ["loser_id", "loser_name", "loser_ht"]
].rename(  # pyright: ignore[reportCallIssue]
    columns={
        "loser_id": "id",
        "loser_name": "name",
        "loser_ht": "ht",
    }
)

# Simply pastes the rows together. The ignore_index makes it so that the index
# of the loser portion of data does not start at 0, it starts at len(winners).
data = pd.concat([winners, losers], ignore_index=True)

# The orders data by the id field, so rows with the same id will be grouped
# together. agg Creates columns with the names on the lhs of '=', the rhs are
# functions. ("name", "nunique") counts unique values of name within a id group.
# Preferably this is 1 of course.
check = data.groupby("id").agg(
    n_names=("name", "nunique"),
    names=("name", lambda x: sorted(set(x))),
    n_heights=("ht", "nunique"),
    heights=("ht", lambda x: sorted(set(x.dropna()))),
)

# conflicts, ids with multiple names or heights.
conflicts = check[(check["n_names"] > 1) | (check["n_heights"] > 1)]

if conflicts.size > 0:
    print(f"There are {conflicts.size} conflicts:")
    # print(conflicts.head(20))  # pyright: ignore[reportAttributeAccessIssue]
else:
    print("No conflicts.")

# This works like numpy boolean indexing. It will select the rows from check
# for which those conditions are true, and .index will return just the indices.
no_conflict_ids = check[
    (check["n_names"] == 1) & (check["n_heights"] <= 1)
].index  # pyright: ignore

# Selects the players with ids that had no conflicts. The drop_duplicates is
# needed because of the duplicate ids of players that played in multiple
# matches.
players_no_conflict = data[
    data["id"].isin(no_conflict_ids)  # pyright: ignore
].drop_duplicates(subset=["id"])


print(players_no_conflict["ht"].mean())
print(players_no_conflict["ht"].std())
