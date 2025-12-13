import pandas as pd
import glob
import re


def load_tennis_data(
    path_pattern="../../data/tennis_atp_data/unaltered_data/*",
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


def load_clean_tennis_data():
    df = load_tennis_data(
        regex_pattern=r"/atp_matches_(199[1-9]|20[0-1][0-9]|202[0-4])\.csv",
        usecols=["winner_hand", "tourney_id", "loser_hand"]
    )
    for col in ["winner_hand", "loser_hand"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.upper()
            .where(lambda s: s.isin(["R", "L"]))  # keep only R/L; else NaN
        )
    return df


def count_total_appearence_in_matches(df_clean):
    return (
        pd.concat([df_clean["winner_hand"], df_clean["loser_hand"]], ignore_index=True)
        .value_counts()
    )


def count_wins(df_clean):
    # Count wins (how often a hand appears as winner)
    return df_clean["winner_hand"].value_counts()


def build_summary(df_wins, df_total):
    # combine totoal and wins, calculate winrate
    summary = pd.DataFrame(
        {
            "Wins": df_wins.astype(int),
            "Total Matches": df_total.astype(int),
        }
    )
    summary["Win Rate"] = (summary["Wins"] / summary["Total Matches"]).fillna(0.0)
    return summary


def main():
    clean_data = load_clean_tennis_data()
    total_appearence = count_total_appearence_in_matches(clean_data)
    wins = count_wins(clean_data)
    summary = build_summary(df_wins=wins, df_total=total_appearence)
    summary.to_csv("hand_winrate_summary.csv")


if __name__ == "__main__":
    main()
