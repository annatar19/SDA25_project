import pandas as pd
import re
from pathlib import Path


INPUT_DIR = "../../data/tennis_atp_data/unaltered_data/"
OUTPUT_DIR = "csv"
OUT_FN = f"{OUTPUT_DIR}/data.csv"

FP_PATTERN = re.compile(
    r"/(?P<dataset>\w*)_matches(?:_(?P<match_tier>[\w_]+))?_(?P<year>\d{4}).csv"
)


def init_out_dir():
    p = Path(OUTPUT_DIR)
    p.mkdir(parents=True, exist_ok=True)


def main():
    data_path = Path(INPUT_DIR)
    if not data_path.exists():
        print(
            "The raw data does not exist, this script is probably being called from the wrong place."
        )
        return 1

    init_out_dir()

    cols = [
        "tourney_date",
        "winner_id",
        "winner_ht",
        "loser_id",
        "loser_ht",
    ]

    csvs = []
    print("Reading and combining data…")
    for fn in data_path.rglob("*.csv"):
        re_match = re.search(FP_PATTERN, str(fn))
        if re_match:
            match_tier = re_match.group("match_tier")
            if match_tier == "doubles":
                continue
            match_year = int(re_match.group("year"))
            print(f"\tProcessing {fn}…")
            df = pd.read_csv(fn, usecols=cols)

            # Left out errors coerce so I'll know if a date is missing.
            df["tourney_date"] = pd.to_datetime(
                df["tourney_date"], format="%Y%m%d"  # , errors="coerce"
            )
            # Tourneys at the end of december are stored in the data of next
            # year, this is so that distinction is not lost.
            df["year"] = match_year
            # The main tier will be "None" in the match group.
            df["tier"] = match_tier if match_tier else "main"
            csvs.append(df)
    df = pd.concat(csvs, ignore_index=True)
    print("Cleaning data…")
    raw_len = len(df)
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

    df["winner_ht"] = pd.to_numeric(df["winner_ht"], errors="coerce")
    df["loser_ht"] = pd.to_numeric(df["loser_ht"], errors="coerce")

    # Also drops rows where the heights are missing.
    df = df[(df["winner_ht"] >= height_minimum) & (df["loser_ht"] >= height_minimum)]
    ht_len = len(df)

    ht_dropped = raw_len - ht_len
    ht_dropped_percent = ht_dropped / raw_len * 100
    print(
        f"\tCleaning height caused {ht_dropped} entries to be dropped, which is {(ht_dropped_percent):.1f}% of the total."
    )

    df.to_csv(OUT_FN)
    print(f"Wrote the data to {OUT_FN}!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
