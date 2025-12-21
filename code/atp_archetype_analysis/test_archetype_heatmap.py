import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"
PLOT_PATH = "../../graphs/archetype/"

df = pd.read_csv(DATA_PATH + "archetype_matchups.csv")

archetypes = ["Sprinter", "Balanced", "Endurance"]
matrix = pd.DataFrame(index=archetypes, columns=archetypes, dtype=float)

for a1 in archetypes:
    for a2 in archetypes:
        subset = df[
            (df["player_archetype"] == a1) &
            (df["opponent_archetype"] == a2)
        ]

        wins = subset["won"].sum()
        total = subset.shape[0]

        matrix.loc[a1, a2] = wins / total if total > 0 else None

plt.figure(figsize=(7, 6))
sns.heatmap(matrix.astype(float), annot=True, cmap="RdYlGn", vmin=0.3, vmax=0.5)
plt.title("Archetype Matchup Win Rates", fontsize=16, weight='bold')

print(f"Saving: {PLOT_PATH}archetype_matchups_heatmap.png")
plt.savefig(PLOT_PATH + "archetype_matchups_heatmap.png", dpi=300)
