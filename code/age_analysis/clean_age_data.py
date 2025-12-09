import pandas as pd
import re
from pathlib import Path
import shutil

# We currently only use the atp data. Note that the regex patterns will have to
# be altered for the other folders.
ATP_DATA_PATH = "../../data/tennis_atp_data/"

# Will match all the singles, doubles, and futures csvs.
DATA_FN_PATTERN = re.compile(
    r"/(?P<dataset>\w*)_matches(?:_(?P<match_type>[\w_]+))?_(?P<year>\d{4}).csv"
)

OUTPUT_DIR = "filtered_ages"


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
    out_fn = f"{path}/age_{match_type}.csv"
    df.to_csv(out_fn, index=False)


if __name__ == "__main__":
    # Only the id is needed to identify the player, but it is database specific
    # so to search online for a player you need a name. More readable also.
    cols = [
        "winner_id",
        "winner_name",
        "winner_age",
        "loser_id",
        "loser_name",
        "loser_age",
    ]

    clear_output()
    root = Path(ATP_DATA_PATH)
    for fn in root.rglob("*.csv"):
        fn_match = re.search(DATA_FN_PATTERN, str(fn))
        if fn_match:
            print(f"Processing: {fn}…")
            match_type = fn_match.group("match_type")
            # Doubles have different columns, and they are ignored for now.
            if match_type == "doubles":
                continue
            year = fn_match.group("year")
            df = pd.read_csv(fn, usecols=cols)  # pyright: ignore
            # Just to be sure. Invalid entries will be converted to "NaN" this
            # way. But with our data this will only happen to empty entries.
            df["winner_age"] = pd.to_numeric(df["winner_age"], errors="coerce")
            df["loser_age"] = pd.to_numeric(df["loser_age"], errors="coerce")
            # Matches with a missing age for either the winner or the loser are
            # dropped.
            df.dropna(subset=["winner_age", "loser_age"])
            # "atp_matches_2000.csv" will return a match_type of "None", this
            # converts "None" to "singles" and leaves the rest.
            match_type = match_type if match_type else "singles"
            write_output(df, year, match_type)
