# Height analysis
This directory contains the age analysis code. The age analysis was performed by Stijn Jongbloed - 12902667.

It is largely just a rewrite of the height analysis code. To the point that it probably could have used the same code with a few arguments and ifs added. I wish this was the only instance of redundant coding…

## Data
The analysis is performed using the data found in `SDA25_project/data/tennis_atp_data/unaltered_data`. All the resulting csvs can be found inside `SDA25_project/data/tennis_atp_data/altered_data/age_analysis`. All the resulting pngs can be found inside `SDA25_project/graphs/age_analysis`.

The analysis only uses the 1 vs 1(singles) data of the data set, i.e. `atp_matches_XXXX.csv`(main), `atp_matches_qual_chall_2024.csv`, and `atp_matches_futures_XXXX.csv`, with the main tier being the heighest tier in proffesional tennis and futures the lowest.

`data_csv.py` Cleans the height data, i.e. extracts the columns and ensures that only valid entries remain, i.e. non-empty and numeric. The youngest player is 14.0 y/o, which is allowed according to the rulebook. I could not confirm that particular player, but neither could I justify dropping him based on the rules. The oldest player was 63.4 y/o, which appears to be valid(https://www.itftennis.com/en/players/helcio-barros-filho/800182315/bra/mt/s/activity/#pprofile-info-tabs). Therefore the entire agerange was included in the analysis.

An early attempt was made to confirm that player ids are truly unique, but it turned out there was no practical way to do this as the names are inconsistent. A player named "William" might be named "Will" in another tournament for instance, at least we assumed that this refers to the same person.

## Age tier analysis
 `age_analyse_tier.py` Analyses the difference in average ages between the 3 tiers. Unlike height age keeps increasing of course, and becomes a detriment at a certain point. Still, the analysis was performed as it might still reveal something interesting.

The analysis is performed by taking the mean age of all tennis players per year per tier. The data is per match, so only one age per player id is counted. The age of a player for a year is his age at his first appearance in that tier. Matches for each tier happen throughout the year, so this should not affect the age distribution.

One thing that was not accounted for however was that a player might appear in all 3 tiers, making it so that he no longer contributes to the result. To account for this bias a player really should only be counted for the heighest tier in which he appears.

The 95% CI(https://en.wikipedia.org/wiki/Confidence_interval) was computed using the Student's t-distribution(https://en.wikipedia.org/wiki/Student%27s_t-distribution). This was done because it is more convenient than bootstrapping. This is justifiable to a lesser degree than it was for height as age is presumably skewed to the younger side. However, there were sufficient samples, age is normal-ish, and by the central limit theorem the Student's t-distribution could be used. Also the datapoints are of course still independent, the age of player1 has no effect on the age of player2.

The results can be found in `age_tier_stats.csv` and seen in `age_stats_tier.png`. The main tier has a statistically significant greater age on average, to a greater degree than it was for height. It would appear that tennis players don't reach their prime until their mid to late twenties.

## Age main tier winner loser difference analysis
`age_analyse_winner_loser.py` Analyses the difference in average ages between winners and losers in the main tier and saves the result to `winner_loser_age_mean.csv`, as well as a plot in `winner_loser_age_mean.png`.

Only the main tier is used, but it is again seperated by year. Instead of individual player ages being used, the ages of all matches are being used. The idea behind this is that if player1 wins a match but loses the next, his effect is cancelled out, revealing clearer patterns.

The downside of this however was that ages were no longer independent, since the age of player1 in his second match is of course not independent from his age in the first match. Because of this bootstrapping was used instead of the Student's t-distribution to compute the 95% CI of the mean age difference.

The results show a statistically significant age difference between winners and losers over the years, although the data appears unclear over on which side that advantage lies, recently is has been an advantage to be younger it appears.
## Logistic regression
`logit_csv.py` Converts the age data to a form useful for training the logistic regression models. The age data is per match with winner columns and loser columns. For the logistic regression these rows are duplicated, the players switched between rows, and a column for the match result from the perspective of the first player is added. A row with a match in which Alice beated Bob results in an Alice-Bob-outcome=1 row as well as a Bob-Alice-outcome=0 row for instance. This is done so the model is also trained to predict losses instead of only wins, as well as other reasons. The result is stored in `logit.csv`.

`model.py` Tests various Patsy formulas for the logistic regression model by training models on the data and stores the results in `model_results.csv`. The results were not used in the presentation, thought it formed the basis for the final model which was used. Attempts were made to generate heatmaps of winning probabilties for various age matchups. The results were interesting, but they were removed from the final version of the repository.
## Scripts
`run_all.sh` Runs all the code in this directory.
