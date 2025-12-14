# Anaylzing whether surfaces really do differ from eachother significantly. Will help with
# checking whether surface is a necesarry factor for our final match prediciton model.
# Could expand to match time whether it increases but ace rates should be enough evidence

import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from data_loader.load_data import load_tennis_data

# NULL HYPOTHESIS = There is no difference in ace_rates between the different surfaces
data = load_tennis_data(
    path_pattern="../data/tennis_atp_data/unaltered_data/*",
    regex_pattern=r"/atp_matches_(199[7-9]|20[0-1][0-9]|202[0-4])\.csv",  # 1997-2024
    usecols=[
        'tourney_date', 'surface', 'tourney_level', 'w_ace', 'w_svpt',
        'l_ace', 'l_svpt']
)

# ============================================================================
# preprocess data
# ============================================================================

print(f"\ninitial data size = {len(data)}")

# all matches with missing ace or serve points are dropped
data = data.dropna(subset=['w_ace', 'w_svpt', 'l_ace', 'l_svpt'])

# there seem to be some matches with a svpt that is 0, so we filter to avoid warning
data = data[(data['w_svpt'] > 0) & (data['l_svpt'] > 0)]

# skipping carpet as not used in current tennis and since data from
# before 2000's is mainly incomplete we just avoid carpet
data = data[data['surface'].isin(['Hard', 'Clay', 'Grass'])]
print(f"data size after preprocess = {len(data)}")

# combining aces of both the loser and winner, thus checking total ace rate per match
data['total_aces'] = data['w_ace'] + data['l_ace']
data['total_svpt'] = data['w_svpt'] + data['l_svpt']
data['ace_rate'] = (data['total_aces'] / data['total_svpt']) * 100

print("\nmatches per surface:")
for i in ['Grass', 'Hard', 'Clay']:
    n = len(data[data['surface'] == i])
    print(f"  {i} = {n}")

# ============================================================================
# analyzing data
# ============================================================================

# split data in to the 3 surfaces
hard_aces = data[data['surface'] == 'Hard']['ace_rate'].values
clay_aces = data[data['surface'] == 'Clay']['ace_rate'].values
grass_aces = data[data['surface'] == 'Grass']['ace_rate'].values

# quick overview of means per surface
print("\nace rates (mean)")
for surface, data_subset in [('Grass', grass_aces), ('Hard', hard_aces), ('Clay', clay_aces)]:
    print(f"  {surface}: mean = {np.mean(data_subset):.2f}%")

# anova test
print("\n1. anova test:")
f_stat, p_value = stats.f_oneway(hard_aces, clay_aces, grass_aces)
print(f"F-statistic: {f_stat:.4f}")
print(f"p-value: {p_value}")

if p_value < 0.05:
    print("REJECT null hypothesis (surface does have significant effect on ace_rates)")
else:
    print("FAIL TO REJECT null hypothesis (surface does NOT have significant effect on ace_rates)")

# ============================================================================
# visualisatie
# ============================================================================

colors = {'Grass': 'green', 'Hard': 'blue', 'Clay': 'orange'}
surfaces = ['Grass', 'Hard', 'Clay']

plt.figure(figsize=(20, 12))

for surface in surfaces:
    data_per = data[data['surface'] == surface]['ace_rate']

    plt.hist(
        data_per,
        bins=50,
        alpha=0.5,
        color=colors[surface],
        density=True,
        edgecolor='black',
        linewidth=0.1,
        label=surface
    )

    mean_val = data_per.mean()
    plt.axvline(mean_val, color=colors[surface], linestyle='--', linewidth=2)

    plt.text(
        mean_val,
        plt.ylim()[1]*0.95,
        f'{mean_val:.2f}%',
        ha='center',
        fontsize=15,
        fontweight='bold',
        color="black"
    )

# had a really long tail, because of outliers
# decided to limit the x axis to 0 - 30 percent
plt.xlim([0, 30])
plt.xlabel('Ace Rate (% of service points)')
plt.ylabel('Density')
plt.title(f'Ace rate by court surface (n={len(data):,} matches over the years 1997-2024)')
plt.legend()
plt.grid(True, alpha=0.25, linestyle='--')
plt.tight_layout()
plt.savefig('../../graphs/surface/surfaces_acerates.png')

# Real comparisons match time / ace rates per surface on this site
# #https://worldtennismagazine.com/from-clay-to-grass-how-tennis-court-surfaces-influence-playing-styles-and-strategy/26636
