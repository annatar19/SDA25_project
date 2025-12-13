import pandas as pd
import numpy as np
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
from scipy.stats import chi2


df = pd.read_csv("archetype_matchups.csv")

# Ensure rank is numeric
df["player_rank"] = pd.to_numeric(df["player_rank"], errors="coerce")

# Fit logistic regression
model = smf.logit("won ~ player_archetype + player_rank", data=df).fit(disp=False)

print(model.summary2().as_text())

# Plot 1: Predicted Win Probability per Archetype (Rank Held Constant)
# ---- Plot 1 (styled): Predicted Win Probability per Archetype (Rank Held Constant) ----
mean_rank = df["player_rank"].mean()
archetypes = df["player_archetype"].unique()

pred_data = pd.DataFrame({
    "player_archetype": archetypes,
    "player_rank": mean_rank
})
pred_data["pred_prob"] = model.predict(pred_data)

# Likelihood-ratio test to get overall p-value for the archetype block
# H0: archetype has no effect after controlling for rank
reduced = smf.logit("won ~ player_rank", data=df).fit(disp=False)
lr_stat = 2 * (model.llf - reduced.llf)
df_diff = int(model.df_model - reduced.df_model)  # degrees of freedom difference
p_arch = 1 - chi2.cdf(lr_stat, df_diff)

# --- consistent styling with your bar chart function ---
plt.figure(figsize=(8, 6))

# same blue palette
colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(pred_data)))
bars = plt.bar(pred_data["player_archetype"], pred_data["pred_prob"], color=colors)

# value labels
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + 0.015, f"{h:.2f}",
             ha="center", va="bottom", fontsize=11)

# grid / axes formatting
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.xticks(rotation=45, ha="right")
plt.ylim(0, 1)
plt.ylabel("Predicted Win Probability")
# plt.xlabel("Player Archetype")  # keep off for consistency
plt.title("Predicted Win Rate per Archetype (Rank Held Constant)", fontsize=16, weight="bold")

# bottom caption: p-value formatting and significance flag
significance = "significant" if p_arch < 0.05 else "not significant"
p_text = "p < 0.001" if p_arch < 0.001 else f"p = {p_arch:.5f}"

# make space for caption and draw it
plt.subplots_adjust(bottom=0.20)  # ensure caption isn’t cut off
plt.figtext(0.5, 0.02,
            f"Logit (rank-controlled), archetype effect (LR test): {p_text} ({significance})",
            ha="center", fontsize=11)

# save/show
plt.savefig("8a_predicted_win_rate.png", dpi=300)
plt.show()


# Plot 2: Win Probability vs Rank by Archetype
rank_range = np.linspace(df["player_rank"].min(), df["player_rank"].max(), 100)

plt.figure(figsize=(7, 5))
for a in archetypes:
    temp = pd.DataFrame({
        "player_archetype": [a]*len(rank_range),
        "player_rank": rank_range
    })
    preds = model.predict(temp).to_numpy()
    plt.plot(rank_range, preds, label=str(a))

plt.xlabel("Player Rank")
plt.ylabel("Predicted Win Probability")
plt.title("Win Probability vs Rank by Archetype")
plt.legend()
plt.tight_layout()
plt.savefig("8b_win_rate_vs_rank")
plt.show()

# Plot 3: Rank-controlled matchup heatmap from logistic regression
# Include both player & opponent archetypes (and both ranks) so the
# predicted probability can vary across the 3×3 matchup grid while controlling for skill.

# Make sure opponent_rank exists and is numeric (skip if already numeric)
df["opponent_rank"] = pd.to_numeric(df["opponent_rank"], errors="coerce")

# Fit an extended model that knows about the opponent as well
matchup_model = smf.logit(
    "won ~ player_archetype + opponent_archetype + player_rank + opponent_rank",
    data=df
).fit(disp=False)

# Define the order for rows/cols
archetype_order = ["Sprinter", "Balanced", "Endurance"]
# Fall back to whatever exists in the data (keeps your script robust)
present = pd.unique(pd.concat([df["player_archetype"], df["opponent_archetype"]], ignore_index=True))
archetypes_for_grid = [a for a in archetype_order if a in present] + [a for a in present if a not in archetype_order]

# Predict at fixed ranks (use means so we isolate archetype effects)
mean_player_rank = df["player_rank"].mean()
mean_opp_rank = df["opponent_rank"].mean()

grid = pd.DataFrame(
    [(pa, oa, mean_player_rank, mean_opp_rank)
     for pa in archetypes_for_grid
     for oa in archetypes_for_grid],
    columns=["player_archetype", "opponent_archetype", "player_rank", "opponent_rank"]
)

grid["pred_prob"] = matchup_model.predict(grid)

# Pivot to a matrix: rows = player archetype, cols = opponent archetype
mat = grid.pivot(index="player_archetype", columns="opponent_archetype", values="pred_prob")
mat = mat.reindex(index=archetypes_for_grid, columns=archetypes_for_grid)

# Heatmap, use same 0–1 range as the raw heatmap for visual comparability.
plt.figure(figsize=(7, 6))
im = plt.imshow(mat.values, vmin=0.3, vmax=0.5, cmap="RdYlGn")
plt.xticks(np.arange(len(archetypes_for_grid)), archetypes_for_grid, rotation=45, ha="right")
plt.yticks(np.arange(len(archetypes_for_grid)), archetypes_for_grid)
plt.title("Predicted Rank-Controlled Matchup Heatmap")
cbar = plt.colorbar(im)

# Annotate each cell with the predicted probability
for i in range(mat.shape[0]):
    for j in range(mat.shape[1]):
        plt.text(j, i, f"{mat.iat[i, j]:.2f}", ha="center", va="center")

plt.tight_layout()
plt.savefig("8c_rank_controlled_matchup_heatmap.png", dpi=300)
plt.show()
