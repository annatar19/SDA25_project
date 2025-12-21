"""
Author: Stijn Jongbloed - 12902667

This file contains the code to generate the csv used for logistic regression on
the age data.
"""

import pandas as pd
from pathlib import Path

# Originally the in- and output was stored within a directory next to the code,
# but it was decided to seperate data and code.
CSV_DIR = "../../data/tennis_atp_data/altered_data/age_analysis"


def init_out_dir():
    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)


def main():
    print("Building the logit csv…")
    path = Path(f"{CSV_DIR}/data.csv")
    if not path.is_file():
        print("data.csv Is missing, please run data_csv.py before running this script.")
        return 1
    init_out_dir()
    df = pd.read_csv(path)

    # keep only main tier
    df = df[df["tier"] == "main"].copy()

    df = df.reset_index(drop=True)
    df["match_id"] = df.index

    # Winner perspective
    winners = df.rename(
        columns={
            "winner_id": "p1_id",
            "winner_age": "p1_age",
            "loser_id": "p2_id",
            "loser_age": "p2_age",
        }
    ).copy()
    # p1 Won.
    winners["win"] = 1

    # Loser perspective
    losers = df.rename(
        columns={
            "loser_id": "p1_id",
            "loser_age": "p1_age",
            "winner_id": "p2_id",
            "winner_age": "p2_age",
        }
    ).copy()
    # p1 Lost.
    losers["win"] = 0

    # Will get an unnamed column otherwise, not sure why.
    keep = [
        "year",
        "p1_id",
        "p1_age",
        "p2_id",
        "p2_age",
        "win",
    ]

    logit = pd.concat([winners[keep], losers[keep]], ignore_index=True)
    n = len(logit)
    logit.dropna(inplace=True)
    percent = n - len(logit)
    percent /= n
    percent *= 100
    print(
        f"\tDropped {n-len(logit)} entries containing NaN, which was {round(percent, 1)}%."
    )

    print(f"\tWritning the logit csv to {CSV_DIR}/logit.csv…")
    logit.to_csv(f"{CSV_DIR}/logit.csv", index=True)
    print("Done building the logit csv!\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
