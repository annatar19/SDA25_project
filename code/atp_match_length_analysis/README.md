
In this analysis I try to test the following:
**H0: Is there a significant difference in winrate between the 3 player archetypes? (sprinter, balanced, endurance)**
To test this, I assign archtypes to players based on their weighted win rates across different match lengths.

## Data cleaning

### Step 1: Calculate avg match length per year and use std dev to make 3 bins of short, balanced and long matches.
Where the 3 bins are;
 - short    < avg_yearly_match_length - std_dev
 - balanced = avg_yearly_match_length -+ std_dev
 - long     > avg_yearly_match_length + std_dev

atp_match_length_bins_year.py:
intput: read data
output: match_length_bins_by_year.csv

### Step 2: Clean all the data to only a few necessary columns per match;
match_id, year, winner_id, winner_name, winner_rank, won, minutes, loser_ etc
clean_matches.py
intput: read data
output: clean_matches.csv

### Step 3: Use the 3 bins match thresholds from the bins by year csv to mark every clean match with a bin
label_matches_by_bin.py:
intput: clean_matches.csv, match_length_bins_by_year.csv
output: matches_with_bins.csv

### Step 4: build_player_archetypes.py
intput: matches_with_bins.csv uses this to filter min matches played to make recent_matches.csv
and uses this filtered recent_matches build the player_archetypes.csv
output: player_archetypes.csv - contains all the games a player has played in which bins etc with their archetype

### Step 5: build_archetypes_matchups.py
intput: matches_recent.csv, player_archetypes.csv
output: archetype_matchups.csv

Builds a player level perspective, so every match row becomes a winner and loser row:
    player-a, archetype-a, rank-a, player-b, archetype-b, rank-b, a-won

-----

## significace tests

### Step 6: use a chi square test to test for H0.
test_archetype_significance.py:
input: archetype_matchups.csv
outputs: archetype_significance_results.csv

Result shows significant difference in winrate between player archetype, with sprinters wining the most.

### Step 7: make heatmap
plot_archetype_heatmap.py:
input: archetype_matchups.csv
outputs: archetype_matchup_heatmap.png

To further illustrate the matchup between player archetypes, I made the heatmap.

### Step 8: investigate ranking effect in my H0
I suspect sprinters win the most because they are simply better players with higher rank
Hence I add rank as a control variable in logistic regression model to control for its effect
And further test if player archetype still significantly affect winrate

