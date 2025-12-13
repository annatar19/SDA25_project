import pandas as pd

# Load only recent matches (not full history)
matches = pd.read_csv("matches_recent.csv")

# Load archetypes
arch = pd.read_csv("player_archetypes.csv")[["player_id","archetype"]]

# Merge player archetypes
matches = matches.merge(
    arch.rename(columns={"player_id":"player_id","archetype":"player_archetype"}),
    on="player_id",
    how="inner"
)

# Merge opponent archetypes
matches = matches.merge(
    arch.rename(columns={"player_id":"opponent_id","archetype":"opponent_archetype"}),
    on="opponent_id",
    how="inner"
)

# Select relevant columns
matchups = matches[[
    "player_id", "player_archetype", "player_rank",
    "opponent_id", "opponent_archetype", "opponent_rank",
    "won"
]]

matchups.to_csv("archetype_matchups.csv", index=False)
print("Saved archetype_matchups.csv")
