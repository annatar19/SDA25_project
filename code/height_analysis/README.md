# Height analysis
This directory contains the height analysis code. The height analysis was performed by Stijn Jongbloed - 12902667.

## Data
The analysis is performed using the data found in `SDA25_project/data/tennis_atp_data/unaltered_data`. All the resulting csvs can be found inside `SDA25_project/data/tennis_atp_data/altered_data/height_analysis`. All the resulting pngs can be found inside `SDA25_project/graphs/height_analysis`.

The analysis only uses the 1 vs 1(singles) data of the data set, i.e. `atp_matches_XXXX.csv`(main), `atp_matches_qual_chall_2024.csv`, and `atp_matches_futures_XXXX.csv`, with the main tier being the heighest tier in proffesional tennis and futures the lowest.

`data_csv.py` Cleans the height data, i.e. extracts the columns and ensures that only valid entries remain, i.e. non-empty and numeric. It also filters for valid heights, the shortest confirmed player is 157 cm, so that is the lower bound. This dropped a 3 cm tall player from our dataset amongst others. The tallest confirmed, and so the upperbound, is 211 cm. There were no players taller than that.

An early attempt was made to confirm that player ids are truly unique, but it turned out there was no practical way to do this as the names are inconsistent. A player named "William" might be named "Will" in another tournament for instance, at least we assumed that this refers to the same person. Likewise verifying height data was not possible since some players are still growing and heights can differ between measurements even for mature players.

## Height tier analysis
 `height_analyse_tier.py` Analyses the difference in average heights between the 3 tiers. The idea is that if there is a statistically significant advantage to having a greater or lower height in tennis, that difference would show between the different tiers of proffesional tennis.

The analysis is performed by taking the mean of all tennis players per year per tier. The data is per match, so only one height per player id is counted. Otherwise if you play one match in a tier in a year your height is counted once for the mean, but playing 8 times would give the appearance of 8 players with iddentical heights. A downside of this approach is that the height you have for your first match will be your height for the entire year. This might not be valid for 16 y/o players for instance.

One thing that was not accounted for however was that a player might appear in all 3 tiers, making it so that he no longer contributes to the result. To account for this bias a player really should only be counted for the heighest tier in which he appears.

The 95% CI(https://en.wikipedia.org/wiki/Confidence_interval) was computed using the Student's t-distribution(https://en.wikipedia.org/wiki/Student%27s_t-distribution). This was done because it is more convenient than bootstrapping. It works because height is normally distributed, there is a sufficient amound of datapoints(players), and the datapoints are independent, the height of player1 has no effect on the height of player2.

The results can be found in `height_tier_stats.csv` and seen in `height_stats_tier.png`. The main tier has a statistically significant greater height on average, at least for the recent years.

## Height main tier winner loser difference analysis
`height_analyse_winner_loser.py` Analyses the difference in average heights between winners and losers in the main tier and saves the result to `winner_loser_ht_mean.csv`, as well as a plot in `winner_loser_ht_mean.png`.

Only the main tier is used, but it is again seperated by year. Instead of individual player heights being used, the heights of all matches are being used. The idea behind this is that if player1 wins a match but loses the next, his effect is cancelled out, revealing clearer patterns.

The downside of this however was that heights were no longer independent, since the height of player1 in his second match is ofcourse not independent from his height in the first match. Because of this bootstrapping was used instead of the Student's t-distribution to compute the 95% CI of the mean height difference.

The results show a clear and statistically significant height difference between winners and losers for recent years, with winners being taller on average.
## Logistic regression
`logit_csv.py` Converts the height data to a form useful for training the logistic regression models. The height data is per match with winner columns and loser columns. For the logistic regression these rows are duplicated, the players switched between rows, and a column for the match result from the perspective of the first player is added. A row with a match in which Alice beated Bob results in an Alice-Bob-outcome=1 row as well as a Bob-Alice-outcome=0 row for instance. This is done so the model is also trained to predict losses instead of only wins, as well as other reasons. The result is stored in `logit.csv`.

`model.py` Tests various Patsy formulas for the logistic regression model by training models on the data and stores the results in `model_results.csv`. The results were not used in the presentation, thought it formed the basis for the final model which was used. Attempts were made to generate heatmaps of winning probabilties for various height matchups. The results were interesting, but they were removed from the final version of the repository.
## Scripts
`run_all.sh` Runs all the code in this directory.
