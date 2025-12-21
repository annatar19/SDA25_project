import pandas as pd

DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"

# Load only recent matches (not full history)
matches = pd.read_csv(DATA_PATH + "matches_recent.csv")

# Load archetypes
arch = pd.read_csv(DATA_PATH + "player_archetypes.csv")[["player_id", "archetype"]]

# Merge player archetypes
matches = matches.merge(
    arch.rename(columns={"player_id": "player_id", "archetype": "player_archetype"}),
    on="player_id",
    how="inner"
)

# Merge opponent archetypes
matches = matches.merge(
    arch.rename(columns={"player_id": "opponent_id", "archetype": "opponent_archetype"}),
    on="opponent_id",
    how="inner"
)

# Select relevant columns
matchups = matches[[
    "player_id", "player_archetype", "player_rank",
    "opponent_id", "opponent_archetype", "opponent_rank",
    "won"
]]

print(f"Saving: {DATA_PATH}archetype_matchups.csv")
matchups.to_csv(DATA_PATH + "archetype_matchups.csv", index=False)
