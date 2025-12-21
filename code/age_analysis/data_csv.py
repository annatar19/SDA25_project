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
            "The raw data does not exist, this script is probably being called"
            " from the wrong place."
        )
        return 1

    init_out_dir()

    cols = [
        "tourney_date",
        "winner_id",
        "winner_age",
        "loser_id",
        "loser_age",
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

    # The youngest player is 14, which is valid according to
    # 2025-rulebook-chapter-7_the-competition_23dec.pdf.
    # Therefore there is no minimum age.
    # The oldest player in the dataset is Barros Filho at 63.4 years old, which
    # does appear to be valid. https://www.itftennis.com/en/players/helcio-barros-filho/800182315/bra/mt/s/activity/#pprofile-info-tabs
    # Therefore there is no maximum age.
    df["winner_age"] = pd.to_numeric(df["winner_age"], errors="coerce")
    df["loser_age"] = pd.to_numeric(df["loser_age"], errors="coerce")
    df.dropna(inplace=True)

    age_len = len(df)

    age_dropped = raw_len - age_len
    age_dropped_percent = age_dropped / raw_len * 100
    print(
        f"\tCleaning age caused {age_dropped} entries to be dropped, which is"
        f" {(age_dropped_percent):.1f}% of the total."
    )

    df.to_csv(OUT_FN)
    print(f"Wrote the data to {OUT_FN}!")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
