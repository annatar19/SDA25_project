"""
Author: Stijn Jongbloed - 12902667

This file contains the code to generate the csv used for logistic regression on
the height data.
"""

import pandas as pd
from pathlib import Path

# Originally the in- and output was stored within a directory next to the code,
# but it was decided to seperate data and code.
CSV_DIR = "../../data/tennis_atp_data/altered_data/height_analysis"


def init_out_dir():
    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)


def main():
    print("Building the logit csv…")
    path = Path(f"{CSV_DIR}/height_data.csv")
    if not path.is_file():
        print(
            "heigh_data.csv Is missing, please run data_csv.py before running this script."
        )
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
            "winner_ht": "p1_ht",
            "loser_id": "p2_id",
            "loser_ht": "p2_ht",
        }
    ).copy()
    # p1 Won.
    winners["win"] = 1

    # Loser perspective
    losers = df.rename(
        columns={
            "loser_id": "p1_id",
            "loser_ht": "p1_ht",
            "winner_id": "p2_id",
            "winner_ht": "p2_ht",
        }
    ).copy()
    # p1 Lost.
    losers["win"] = 0

    # keep common match fields + player/opp fields
    keep = [
        "year",
        "p1_id",
        "p1_ht",
        "p2_id",
        "p2_ht",
        "win",
    ]

    logit = pd.concat([winners[keep], losers[keep]], ignore_index=True)
    n = len(logit)
    logit.dropna(inplace=True)
    percent = n - len(logit)
    percent /= n
    percent *= 100
    print(
        f"Dropped {n-len(logit)} entries containing NaN, which was {round(percent, 1)}%."
    )

    print(f"\tWritning the logit csv to {CSV_DIR}/logit.csv…")
    logit.to_csv(f"{CSV_DIR}/logit.csv", index=False)
    print("Done building the logit csv!\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
