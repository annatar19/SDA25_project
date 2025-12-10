# This extracts the height data that we currently use, performs basic filtering,
# and outputs the dataframes as cleaned csvs.
import pandas as pd
import glob
import re
from pathlib import Path
import shutil

# We currently only use the atp data. Note that the regex patterns will have to
# be altered for the other folders.
ATP_DATA_PATH = "../../data/tennis_atp_data/unaltered_data/*"

# Will match all the singles and doubles csvs for all 3 datasets.
DATA_FN_PATTERN = re.compile(
    r"/(?P<dataset>\w*)_matches(?:_(?P<match_type>[\w_]+))?_(?P<year>\d{4}).csv"
)

OUTPUT_DIR = "filtered_heights"


# To clear the output folder.
def clear_output():
    p = Path(OUTPUT_DIR)
    if p.exists():
        shutil.rmtree(p)
    return p


# Writes one of the filtered dataframes to the proper directory.
def write_output(df, year, match_type):
    path = f"{OUTPUT_DIR}/{year}"
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    out_fn = f"{path}/ht_{match_type}.csv"
    df.to_csv(out_fn, index=False)


if __name__ == "__main__":
    singles_cols = [
        "winner_id",
        "winner_name",
        "winner_ht",
        "loser_id",
        "loser_name",
        "loser_ht",
    ]

    # The shortest tennis player in the dataset is Jorge Brian Panta Herreros,
    # who is 3 cm tall according to the data. Looking at pictures he seems to
    # at least be taller than a tennis ball, so this data appears to be wrong.
    # The smallest player whose height could be verified was Ryuki Matsuda:
    # https://www.atptour.com/en/players/ryuki-matsuda/m0g0/overview, so we'll
    # take his height as the minimum. This drops 9 players from our set. The
    # next shortest would have been Ilija Vucic at 145 cm according to the data,
    # this might also be possible but
    # https://www.atptour.com/en/players/p-p/v624/overview states that his
    # length is 188 cm, which based on pictures does seem more likely.
    height_minimum = 157
    # Reilly Opelka(https://www.atptour.com/en/players/reilly-opelka/o522/overview)
    # is the tallest player in our dataset at 211 cm, and his length appears to
    # be valid. No need for filtering, this is just for the formality.
    height_maximum = 211

    clear_output()

    fns = glob.glob(ATP_DATA_PATH)
    for fn in fns:
        fn_match = re.search(DATA_FN_PATTERN, fn)
        if fn_match:
            match_type = fn_match.group("match_type")
            # Doubles have different columns, and they are ignored for now.
            if match_type == "doubles":
                continue
            year = fn_match.group("year")
            df = pd.read_csv(fn, usecols=singles_cols)  # pyright: ignore
            # Just to be sure. Invalid entries will be converted to "NaN" this
            # way. But with our data this will only happen to empty entries.
            df["winner_ht"] = pd.to_numeric(df["winner_ht"], errors="coerce")
            df["loser_ht"] = pd.to_numeric(df["loser_ht"], errors="coerce")
            df.dropna(subset=["winner_ht", "loser_ht"], inplace=True)
            # Only select rows where both the winner and loser had heights
            # above the minimum.
            df = df[
                (df["winner_ht"] >= height_minimum) & (df["loser_ht"] >= height_minimum)
            ]
            # "atp_matches_2000.csv" will return a match_type of "None", this
            # converts "None" to "singles" and leaves the rest.
            match_type = match_type if match_type else "singles"
            write_output(df, year, match_type)
