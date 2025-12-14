import pandas as pd

# --- file paths (edit if needed) ---
MATCHES_CSV = "matches_recent.csv"
ARCHETYPES_CSV = "archetype_matchups.csv"
OUT_CSV = "matches_with_archetypes.csv"

# --- load ---
matches = pd.read_csv(MATCHES_CSV)
arch = pd.read_csv(ARCHETYPES_CSV)

# --- build a unified (player_id -> archetype) map ---
cols = []
if {"player_id", "player_archetype"}.issubset(arch.columns):
    a1 = arch[["player_id", "player_archetype"]].rename(
        columns={"player_id": "id", "player_archetype": "archetype"}
    )
    cols.append(a1)

# Some archetype files also have opponent archetypes; include them if present.
if {"opponent_id", "opponent_archetype"}.issubset(arch.columns):
    a2 = arch[["opponent_id", "opponent_archetype"]].rename(
        columns={"opponent_id": "id", "opponent_archetype": "archetype"}
    )
    cols.append(a2)

if not cols:
    raise ValueError(
        "archetype_matchups.csv is missing required columns. "
        "Need either (player_id, player_archetype) or (opponent_id, opponent_archetype)."
    )

archetype_map = pd.concat(cols, ignore_index=True)

# Drop exact duplicate rows
archetype_map = archetype_map.drop_duplicates()

# --- (optional) sanity check: conflicting archetypes for same player id ---
conflicts = (
    archetype_map.groupby("id")["archetype"]
    .nunique()
    .reset_index(name="unique_archetypes")
)
bad = conflicts[conflicts["unique_archetypes"] > 1]["id"].tolist()
if bad:
    print(f"Warning: {len(bad)} players have conflicting archetypes. "
          f"Keeping the first encountered value. Example IDs: {bad[:10]}")

# Keep the first archetype per id (after drop_duplicates this is stable)
archetype_map = archetype_map.drop_duplicates(subset=["id"], keep="first")

# --- merge into match-level data ---
# player side
merged = matches.merge(
    archetype_map.rename(columns={"id": "player_id", "archetype": "player_archetype"}),
    on="player_id",
    how="left",
)

# opponent side
merged = merged.merge(
    archetype_map.rename(columns={"id": "opponent_id", "archetype": "opponent_archetype"}),
    on="opponent_id",
    how="left",
)

# --- save ---
merged.to_csv(OUT_CSV, index=False)
print(f"Saved: {OUT_CSV}")
print(
    merged[["match_id", "player_id", "player_archetype", "opponent_id", "opponent_archetype"]]
    .head(10)
    .to_string(index=False)
)
