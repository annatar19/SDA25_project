import pandas as pd
import glob
import re
import os


def load_clean_matches(path_pattern="../../data/tennis_atp_data/unaltered_data/*",
                       regex=r"atp_matches_(199[1-9]|20[0-1][0-9]|202[0-4])\.csv$"):
    """
    Loads essential ATP match columns including player ranks.
    Returns a raw clean dataset before expanding winner/loser rows.
    """

    pattern = re.compile(regex)
    files = glob.glob(path_pattern)

    dfs = []

    for fn in files:
        base = os.path.basename(fn)
        m = pattern.search(base)
        if not m:
            continue

        year = int(m.group(1))

        df = pd.read_csv(fn, usecols=[
            "winner_id", "winner_name", "winner_rank",
            "loser_id", "loser_name", "loser_rank",
            "minutes"
        ])

        df["year"] = year

        # Clean minutes
        df["minutes"] = pd.to_numeric(df["minutes"], errors="coerce")
        df = df.dropna(subset=["minutes"])

        # Unique match identifier
        df["match_id"] = df.index.astype(str) + "_" + str(year)

        dfs.append(df)

    return pd.concat(dfs, ignore_index=True)


def explode_win_loss(clean_df):
    """
    Converts each match into two rows:
        - winner perspective
        - loser perspective
    Includes player_rank and opponent_rank
    """

    winners = pd.DataFrame({
        "match_id": clean_df["match_id"],
        "year": clean_df["year"],

        "player_id": clean_df["winner_id"],
        "player_name": clean_df["winner_name"],
        "player_rank": clean_df["winner_rank"],

        "opponent_id": clean_df["loser_id"],
        "opponent_name": clean_df["loser_name"],
        "opponent_rank": clean_df["loser_rank"],

        "won": 1,
        "minutes": clean_df["minutes"]
    })

    losers = pd.DataFrame({
        "match_id": clean_df["match_id"],
        "year": clean_df["year"],

        "player_id": clean_df["loser_id"],
        "player_name": clean_df["loser_name"],
        "player_rank": clean_df["loser_rank"],

        "opponent_id": clean_df["winner_id"],
        "opponent_name": clean_df["winner_name"],
        "opponent_rank": clean_df["winner_rank"],

        "won": 0,
        "minutes": clean_df["minutes"]
    })

    return pd.concat([winners, losers], ignore_index=True)


if __name__ == "__main__":
    print("Loading ATP matches with rank data...")
    df_clean = load_clean_matches()

    print("Expanding into player-level rows...")
    df_expanded = explode_win_loss(df_clean)

    print("Saving clean_matches.csv...")
    df_expanded.to_csv("clean_matches.csv", index=False)

    print("Done.")
