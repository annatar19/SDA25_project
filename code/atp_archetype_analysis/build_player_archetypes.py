import pandas as pd

DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"

N_LAST_MATCHES = 100
MIN_MATCHES = 50
MIN_BIN_MATCHES = 10


def filter_recent_matches(df):
    df = df.sort_values(["player_id", "year"])
    return df.groupby("player_id").tail(N_LAST_MATCHES).reset_index(drop=True)


def filter_player_counts(df):
    counts = df["player_id"].value_counts()
    eligible = counts[counts >= MIN_MATCHES].index
    return df[df["player_id"].isin(eligible)]


def compute_player_bin_stats(df):
    df["length_bin"] = df["length_bin"].astype(str).str.strip().str.lower()

    grouped = df.groupby(["player_id", "length_bin"]).agg(
        matches=("won", "size"),
        wins=("won", "sum")
    ).reset_index()

    grouped["winrate"] = grouped["wins"] / grouped["matches"]

    pivot = grouped.pivot(index="player_id", columns="length_bin",
                          values=["matches", "wins", "winrate"])
    pivot.columns = [f"{m}_{b}" for m, b in pivot.columns]
    pivot = pivot.fillna(0).reset_index()
    return pivot


def assign_archetype(row):
    wr_s = row.get("winrate_short", 0.0)
    wr_m = row.get("winrate_medium", 0.0)
    wr_l = row.get("winrate_long", 0.0)
    m_s = int(row.get("matches_short", 0))
    m_l = int(row.get("matches_long", 0))

    if wr_s >= wr_m and wr_s >= wr_l and m_s >= MIN_BIN_MATCHES:
        return "Sprinter"
    if wr_l >= wr_m and wr_l >= wr_s and m_l >= MIN_BIN_MATCHES:
        return "Endurance"
    return "Balanced"


if __name__ == "__main__":
    print(f"Loading: {DATA_PATH}matches_with_bins.csv")
    df = pd.read_csv(DATA_PATH + "matches_with_bins.csv")
    df.columns = df.columns.str.strip()

    # recency + coverage filters
    df = filter_recent_matches(df)
    print(f"Saving: {DATA_PATH}matches_recent.csv")
    df.to_csv(DATA_PATH + "matches_recent.csv", index=False)

    df = filter_player_counts(df)

    print("Computing bin stats…")
    stats = compute_player_bin_stats(df)

    print("Assigning archetypes…")
    stats["archetype"] = stats.apply(assign_archetype, axis=1)

    print(f"Saving: {DATA_PATH}player_archetypes.csv")
    stats.to_csv(DATA_PATH + "player_archetypes.csv", index=False)
    print("Done.")
