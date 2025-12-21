
In this analysis I try to test the following:  

**H0: Is there a significant difference in winrate between the 3 player archetypes? (sprinter, balanced, endurance)**  

To test this;
1) I calculated the average match length per year from 1991 to 2024. I made 3 bins using 1 standard deviation as a threshold on top of the mean.
2) Going through all match data from 1991 to 2024, I use these 3 bins mapping each match as short/med/long.
3) I build a per player profile of how many matches total they played, and calculated there respective win rate in each of these 3 match length bins.
4) Using a weighted highest win rate as the mapping of each players playing style archetype. Highest weighted win rate maps as;
    - short = sprinter
    - med = balanced
    - long = endurance

5) Using this per player defined archetype, we map this archetype back on orginal data. This time mapping the archetype to the player_id. Instead of mapping the defined match length bin to the match playtime.
6) This match level data consisting of player archetypes is used to test for significance with chi-square. Also logistic regression to control for rank. And later another logistic regression test is done to see how adding opponent archetype matters, visualized in a predicted win rate heatmap.


## Files
SCRIPTS: (in order of execution: data cleaning -> testing -> plot for presentation)
- match_length_bin_by_years.py
- clean_matches.py
- label_matches_by_bin.py
- build_player_archetypes.py
- build_archetypes_matchups.py
- data_cleaning_for_model.py
- test_archetype_significance.py
- test_archetype_heatmap.py
- test_logit_rank_control.py
- plot_match_length.py

DATA:
 - data/atp_tennis_match/unaltered_data/archetype/*

GRAPHS:
 - graphs/archetype/*

## Data cleaning

### Step 1: Calculate avg match length per year and use std dev to make 3 bins of short, balanced and long matches.
Where the 3 bins are;
 - short    < avg_yearly_match_length - std_dev
 - balanced = avg_yearly_match_length -+ std_dev
 - long     > avg_yearly_match_length + std_dev

match_length_bins_by_year.py  
- INPUT:  
    - data/atp_tennis_match/unaltered_data/.. 1991 to 2024
- OUTPUT:
    - match_length_bins_by_year.csv

### Step 2: Clean all the data to only a few necessary columns per match;
match_id, year, winner_id, winner_name, winner_rank, won, minutes, loser_ etc

clean_matches.py  
- INPUT:
    - data/atp_tennis_match/unaltered_data/.. 1991 to 2024
- OUTPUT:
    - clean_matches.csv

### Step 3: Use the 3 bins match thresholds from the bins by year csv to mark every clean match with a bin
label_matches_by_bin.py  
- INPUT:
    - clean_matches.csv
    - match_length_bins_by_year.csv
- OUTPUT:
    - matches_with_bins.csv

### Step 4: Build player archetypes table
build_player_archetypes.py  
- INPUT:
    - matches_with_bins.csv
    - recent_matches.csv    (Made during running of build_player_archetypes.py)
- OUTPUT:
    - player_archetypes.csv

Uses matches_with_bins.csv to filter min matches played to make recent_matches.csv
and uses this filtered recent_matches to build the player_archetypes.csv

### Step 5: Building player archetype together with matchups table
build_archetypes_matchups.py  
- INTPUT:
    - matches_recent.csv
    - player_archetypes.csv
- OUTPUT:
    - archetype_matchups.csv

Builds a player level perspective table, so every match row becomes a winner and loser row:
player-a, archetype-a, rank-a, player-b, archetype-b, rank-b, a-won


### Step 6: (not part of analysis) Data cleaning for prediction model
data_cleaning_for_model.py  
- INTPUT:
    - matches_recent.csv
    - archetype_matchups.csv
- OUTPUT:
    - matches_with_archetypes.csv

Merges most recent matches with the archetype_matchup table, providing one big table of all
the match data and archetype appended to it.

-----

## Significace Tests

### Step 1: use a chi square test to test for H0.
test_archetype_significance.py  
- INPUT:
    - archetype_matchups.csv
- OUTPUT:
    - archetype_winrate.png (PLOT)

Result shows significant difference in winrate between player archetype, with sprinters wining the most.

### Step 2: make heatmap
test_archetype_heatmap.py  
- INPUT:
    - archetype_matchups.csv
- OUTPUT:
    - archetype_matchups_heatmap.png (PLOT)

To further illustrate the matchup between player archetypes, I made the heatmap of the actual data.

### Step 3: investigate ranking effect in my H0
test_logit_rank_control.py  
- INPUT:
    - archetype_matchups.csv
- OUTPUT:
    - predicted_win_rate.png (PLOT)
    - win_rate_vs_rank.png (PLOT)
    - rank_controlled_matchup_heatmap.png (PLOT)

I suspect sprinters win the most because they are simply better players with higher rank
Hence I add rank as a control variable in logistic regression model to control for its effect
And further test if player archetype still significantly affect winrate.

### Step 4: (not part of analysis) A presentation only visual to represent the 3 bins
plot_match_length.py  
- INPUT:
    - match_length_bins_by_year.csv
- OUTPUT:
    - match_length_thresholds.png (PLOT)

Plots the mean match length and mean+stdev and mean-stdev per year from 1991 to 2024.
