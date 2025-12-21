## Files

- hand_data_prep.py
- hand_significance_test.py

## Dominant Hand Analysis

1. hand_data_prep.py
- INPUT: all ATP data from 1991-2024
- OUTPUT: data/tennis_atp_data/altered_data/hand/hand_winrate_summary.csv

Cleans all matches by extracting winner and loser with their respective hand.

2. hand_significance_test.py
- INPUT: data/tennis_atp_data/altered_data/hand/hand_winrate_summary.csv
- OUTPUT: 2 plots to graphs/hand/..
    - total_match_appearances.png
    - winrate_barchart.png

This script plots total match appearances by player hand.
Also plots the winrate comparison of left vs right handed players.
Performs a two-proportional z-test to test for statistical significance.

## Results

The two-proportional z-test finds statistical significance in the difference
in win rates between the left and right handed players. However, the actual
effect size is small. The difference in win rate is approximately 1 percentage
point.

