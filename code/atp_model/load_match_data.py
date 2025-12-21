import pandas as pd
import glob
import re
import os
import numpy as np

from collections import defaultdict


# 1) Load raw ATP matches & keep only needed columns
def load_clean_matches(
    path_pattern="../../data/tennis_atp_data/unaltered_data/*",
    regex=r"atp_matches_(199[1-9]|20[0-1][0-9]|202[0-4])\.csv$",
):
    """
    Loads ATP matches for 1991–2024 (based on filename), and returns a dataframe
    with the columns required to build player-pair rows. This function DOES NOT
    expand into p1/p2 yet — see `build_player_pairs` below.
    """
    pattern = re.compile(regex)
    files = glob.glob(path_pattern)
    dfs = []

    usecols = [
        "tourney_id",
        "tourney_date",
        "match_num",
        "surface",
        "winner_id",
        "winner_hand",
        "winner_ht",
        "winner_age",
        "winner_rank_points",
        "loser_id",
        "loser_hand",
        "loser_ht",
        "loser_age",
        "loser_rank_points",
    ]

    for fn in files:
        base = os.path.basename(fn)
        if not pattern.search(base):
            continue

        df = pd.read_csv(fn, usecols=lambda c: c in usecols, low_memory=False)

        # Ensure all expected columns exist
        for col in usecols:
            if col not in df.columns:
                df[col] = pd.NA

        # Coerce numeric fields
        for col in [
            "winner_ht",
            "winner_age",
            "winner_rank_points",
            "loser_ht",
            "loser_age",
            "loser_rank_points",
            "tourney_date",
        ]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        # Normalize handedness
        def _norm_hand(x):
            if pd.isna(x):
                return pd.NA
            x = str(x).strip().upper()
            if x in {"R", "L", "U"}:
                return x
            return x  # keep anything else as-is (e.g., 'A')

        df["winner_hand"] = df["winner_hand"].map(_norm_hand)
        df["loser_hand"] = df["loser_hand"].map(_norm_hand)

        df = df[usecols]
        dfs.append(df)

    if not dfs:
        return pd.DataFrame(columns=usecols)

    return pd.concat(dfs, ignore_index=True)


# 2) Build player-pair rows
def build_player_pairs(
    matches_df: pd.DataFrame, expand_symmetry: bool = True
) -> pd.DataFrame:
    """
    Constructs the final dataset with p1_* and p2_* attributes and 'result'.
    If expand_symmetry=True, returns two rows per match:
      - winner->p1 (result=1)
      - loser->p1  (result=0)
    """
    # Winner as p1, loser as p2
    p1_win = pd.DataFrame(
        {
            "tourney_date": matches_df["tourney_date"],
            "tourney_id": matches_df["tourney_id"],
            "surface": matches_df["surface"],
            "match_num": matches_df["match_num"],
            "p1_id": matches_df["winner_id"],
            "p1_age": matches_df["winner_age"],
            "p1_ht": matches_df["winner_ht"],
            "p1_handedness": matches_df["winner_hand"],
            "p1_ranking_points": matches_df["winner_rank_points"],
            "p2_id": matches_df["loser_id"],
            "p2_age": matches_df["loser_age"],
            "p2_ht": matches_df["loser_ht"],
            "p2_handedness": matches_df["loser_hand"],
            "p2_ranking_points": matches_df["loser_rank_points"],
            "result": 1,
        }
    )

    if not expand_symmetry:
        out = p1_win
    else:
        # Loser as p1, winner as p2
        p1_lose = pd.DataFrame(
            {
                "tourney_date": matches_df["tourney_date"],
                "tourney_id": matches_df["tourney_id"],
                "surface": matches_df["surface"],
                "match_num": matches_df["match_num"],
                "p1_id": matches_df["loser_id"],
                "p1_age": matches_df["loser_age"],
                "p1_ht": matches_df["loser_ht"],
                "p1_handedness": matches_df["loser_hand"],
                "p1_ranking_points": matches_df["loser_rank_points"],
                "p2_id": matches_df["winner_id"],
                "p2_age": matches_df["winner_age"],
                "p2_ht": matches_df["winner_ht"],
                "p2_handedness": matches_df["winner_hand"],
                "p2_ranking_points": matches_df["winner_rank_points"],
                "result": 0,
            }
        )
        out = pd.concat([p1_win, p1_lose], ignore_index=True)

    # Dtypes
    for col in ["p1_id", "p2_id", "tourney_date"]:
        out[col] = pd.to_numeric(out[col], errors="coerce").astype("Int64")
    for col in [
        "p1_age",
        "p1_ht",
        "p1_ranking_points",
        "p2_age",
        "p2_ht",
        "p2_ranking_points",
    ]:
        out[col] = pd.to_numeric(out[col], errors="coerce")
    out["result"] = out["result"].astype("int8")
    out["p1_handedness"] = out["p1_handedness"].astype("string")
    out["p2_handedness"] = out["p2_handedness"].astype("string")

    return out


# 3) Build a player_id to archetype table from matches_with_archetypes.csv
def make_archetype_lookup_from_matches(csv_path: str) -> pd.DataFrame:
    """
    From a file with columns:
      - player_id, player_archetype
      - opponent_id, opponent_archetype
    produce a 2-col DataFrame: [player_id, archetype],
    choosing the most frequent non-null archetype per player.
    """
    df = pd.read_csv(csv_path, low_memory=False)

    a1 = df[["player_id", "player_archetype"]].rename(
        columns={"player_archetype": "archetype"}
    )
    a2 = df[["opponent_id", "opponent_archetype"]].rename(
        columns={"opponent_id": "player_id", "opponent_archetype": "archetype"}
    )

    arche = pd.concat([a1, a2], ignore_index=True)

    # Clean and drop empties
    arche["archetype"] = (
        arche["archetype"].astype("string").str.strip().replace({"": pd.NA})
    )
    arche = arche.dropna(subset=["archetype"])

    # Most frequent archetype per player
    counts = (
        arche.groupby(["player_id", "archetype"])
        .size()
        .reset_index(name="n")
        .sort_values(["player_id", "n"], ascending=[True, False])
    )
    winners = counts.drop_duplicates(subset=["player_id"], keep="first")

    # Align dtypes for merging
    winners["player_id"] = pd.to_numeric(winners["player_id"], errors="coerce").astype(
        "Int64"
    )
    return winners[["player_id", "archetype"]]


# 4) Merge archetypes into the matches dataset
def add_player_archetypes(
    matches_df: pd.DataFrame, archetypes_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Adds 'p1_archetype' and 'p2_archetype' columns to matches_df.
    If a player has no archetype, NaN is inserted.
    archetypes_df must have columns: ['player_id', 'archetype'].
    """
    if not {"player_id", "archetype"}.issubset(archetypes_df.columns):
        raise ValueError("archetypes_df must contain: player_id, archetype")

    # Ensure types line up
    mdf = matches_df.copy()
    mdf["p1_id"] = pd.to_numeric(mdf["p1_id"], errors="coerce").astype("Int64")
    mdf["p2_id"] = pd.to_numeric(mdf["p2_id"], errors="coerce").astype("Int64")

    arch = archetypes_df.copy()
    arch["player_id"] = pd.to_numeric(arch["player_id"], errors="coerce").astype(
        "Int64"
    )

    # Merge for p1 and p2
    out = mdf.merge(
        arch.rename(columns={"player_id": "p1_id", "archetype": "p1_archetype"}),
        on="p1_id",
        how="left",
    )
    out = out.merge(
        arch.rename(columns={"player_id": "p2_id", "archetype": "p2_archetype"}),
        on="p2_id",
        how="left",
    )

    return out


# 5) Add surface winrates
def add_surface_winrates(data):
    """
    Adds p1_surface_winrate and p2_surface_winrate columns.
    Must be called on dataset sorted by tourney_date.
    """
    # Skipping carpet
    df = data[data["surface"].isin(["Hard", "Clay", "Grass"])].copy()
    # sorting as it wasnt in chronological order, which would ruin the winrate calculation
    df = df.sort_values("tourney_date").reset_index(drop=True)

    # wouldve preferred doing it with classes as its cleaner for me
    # tracking player wins and losses per surface
    players = {}
    wr_p1 = []
    wr_p2 = []

    for _, row in df.iterrows():
        p1_id, p2_id = row["p1_id"], row["p2_id"]
        surface = row["surface"]
        result = row["result"]

        for player_id in [p1_id, p2_id]:
            if player_id not in players:
                # tennissers wins and losses per surface
                players[player_id] = {
                    "Grass": {"wins": 0, "losses": 0},
                    "Hard": {"wins": 0, "losses": 0},
                    "Clay": {"wins": 0, "losses": 0},
                }

        for player_id, list_wr in [(p1_id, wr_p1), (p2_id, wr_p2)]:
            total = (
                players[player_id][surface]["wins"]
                + players[player_id][surface]["losses"]
            )
            # if total played matches on that surface is under 10 make winrate 0.5
            wr = (players[player_id][surface]["wins"] + 1) / (total + 2)
            list_wr.append(wr)

        players[p1_id][surface]["wins" if result == 1 else "losses"] += 1
        players[p2_id][surface]["wins" if result == 0 else "losses"] += 1

    df["p1_surface_winrate"] = wr_p1
    df["p2_surface_winrate"] = wr_p2

    return df


# 6) Add relative ranking points
def add_relative_ranking_points(data):
    """
    Add a column of relative ranking points from perspective of P1
    Calculation for relative ranking points =
        (P1_ranking_points - P2_ranking_points) / P1_ranking_points
    """

    df = data

    df["p1_ranking_points"] = pd.to_numeric(df["p1_ranking_points"], errors="coerce")
    df["p2_ranking_points"] = pd.to_numeric(df["p2_ranking_points"], errors="coerce")

    rel_points = []
    for _, row in df.iterrows():
        if pd.notna(row["p1_ranking_points"]) and pd.notna(row["p2_ranking_points"]):
            if row["p1_ranking_points"] == 0:
                rel_points.append(np.nan)  # avoid division by zero
            else:
                rel_points.append(
                    (row["p1_ranking_points"] - row["p2_ranking_points"])
                    / row["p1_ranking_points"]
                )
        else:
            rel_points.append(np.nan)

    if len(rel_points) == len(df):
        df["rel_ranking_points"] = rel_points
    else:
        raise ValueError(
            f"Length mismatch: DataFrame has {len(df)} rows, "
            f"but rel_points has {len(rel_points)} elements."
        )

    return df


# 7) Add win streak per player
def add_win_streak(data):
    df = data

    df["tourney_date"] = pd.to_datetime(df["tourney_date"], format="%Y%m%d")

    df = df.sort_values(["tourney_date", "match_num"]).reset_index(drop=True)

    win_streak_dict = defaultdict(int)
    p1_streaks = []
    p2_streaks = []

    for _, row in df.iterrows():
        p1_id = row["p1_id"]
        p2_id = row["p2_id"]

        p1_streaks.append(win_streak_dict[p1_id])
        p2_streaks.append(win_streak_dict[p2_id])

        win_streak_dict[p1_id] += 1
        win_streak_dict[p2_id] = 0

    df["p1_streak"] = p1_streaks
    df["p2_streak"] = p2_streaks

    return df


# 8) Add p1_favor
def add_favor(data):
    df = data

    bins = [-np.inf, -0.5, -0.2, -0.05, 0.05, 0.2, 0.5, np.inf]
    labels = [
        "heavy_underdog",
        "moderate_underdog",
        "slight_underdog",
        "even",
        "slight_favorite",
        "moderate_favorite",
        "heavy_favorite",
    ]

    df["p1_favor"] = pd.cut(df["rel_ranking_points"], bins=bins, labels=labels)

    return df


# 9) Add absolute ranking points
def add_absolute_ranking_points(data):
    """
    Add a column of relative ranking points from perspective of P1
    Calculation for relative ranking points =
        (P1_ranking_points - P2_ranking_points) / P1_ranking_points
    """

    df = data

    df["p1_ranking_points"] = pd.to_numeric(df["p1_ranking_points"], errors="coerce")
    df["p2_ranking_points"] = pd.to_numeric(df["p2_ranking_points"], errors="coerce")

    abs_points = []
    for _, row in df.iterrows():
        if pd.notna(row["p1_ranking_points"]) and pd.notna(row["p2_ranking_points"]):
            abs_points.append((row["p1_ranking_points"] - row["p2_ranking_points"]))
        else:
            abs_points.append(np.nan)

    if len(abs_points) == len(df):
        df["abs_ranking_points"] = abs_points
    else:
        raise ValueError(
            f"Length mismatch: DataFrame has {len(df)} rows, "
            f"but rel_points has {len(abs_points)} elements."
        )

    return df


if __name__ == "__main__":
    RAW_MATCHES_GLOB = "../../data/tennis_atp_data/unaltered_data/*"
    ARCHETYPES_CSV = (
        "../../data/tennis_atp_data/altered_data/archetype/matches_with_archetypes.csv"
    )
    OUTPUT_CSV = "../../data/tennis_atp_data/altered_data/atp_model/atp_player_pairs_1991_2024.csv"

    # Build base dataset
    matches = load_clean_matches(RAW_MATCHES_GLOB)
    dataset = build_player_pairs(matches, expand_symmetry=True)

    # Build player_id to archetype lookup & merge
    archetypes_df = make_archetype_lookup_from_matches(ARCHETYPES_CSV)
    dataset_with_arch = add_player_archetypes(dataset, archetypes_df)

    # Add surface winrates
    dataset_with_surface = add_surface_winrates(dataset_with_arch)

    # Add relative ranking points
    dataset_with_rel_ranking_points = add_relative_ranking_points(dataset_with_surface)

    # Add win streaks per player
    dataset_with_winstreaks = add_win_streak(dataset_with_rel_ranking_points)

    # # Instead of rebuilding dataset, read the currently built dataset
    # cur_dataset = pd.read_csv(OUTPUT_CSV)

    # Add p1_favor
    dataset_with_p1favor = add_favor(dataset_with_winstreaks)

    # Add abs rankpoints
    dataset_with_abs_rank_points = add_absolute_ranking_points(dataset_with_p1favor)

    # Add abs_ranking_points

    # Save final CSV
    dataset_with_abs_rank_points.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved: {OUTPUT_CSV}  (rows={len(dataset_with_abs_rank_points):,})")
