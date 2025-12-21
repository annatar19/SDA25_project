# Main model
This directory contains the code for the main prediction model of our project.

## Data
We combined the data from our own analysis using `clean_data.py` and `load_match_data.py`. Note that rerunning the latter somehow yield different model results than the one presented, do not run it if you want to repeat our results, or you'll have to run `git restore` on the data.

All i/o data for the code in the directory can be found in `SDA25_project/data/tennis_atp_data/altered_data/atp_model`, although `load_match_data.py` also uses the initial data in `SDA25_project/data/tennis_atp_data/unaltered_data`.

The raw data, as well as our analysis data has a row per match, with columns for the various fields. For the logistic regression these rows are duplicated, the players switched between rows, and a column for the match result from the perspective of the first player is added. A row with a match in which Alice beated Bob results in an Alice-Bob-outcome=1 row as well as a Bob-Alice-outcome=0 row for instance. This is done so the model is also trained to predict losses instead of only wins, as well as other reasons.

## Training the models
Both training and testing is done by `test_model.py`. Currently 7 models have been defined. The models used in the presentation are Formula 0(Basic model), Formula 1(Basic model + win-streak), and Formula 3(Rel. ranking model (baseline)).

Patsy formulas were used to define our models. The training was done on the main tier of the singles(1 v 1) atp data, starting from the year 1991.

Note that the first tourney date is `1990-12-31`, the dataset counts that within `1991`, presumably because most of the the tourney took place within that year. Our code however counts tournaments like that in the year of the first date, so `1990` in this case. But our models do not use years, so the date does not matter.

The reason we start with the `1991` set is because that was the first year from which all of our data could be build, early years have a lot of data missing.

Our training set are the years 2022, 2023, and 2024. This is roughly 10%, and the most recent years. Since the goal of our model is to predict the present we test on the most recent years.

## Testing the models
We tested our models by comparing their predictions agains the test set and computing 4 metrics from that, Accuracy, Log Loss, Brier score and ROC AUC. We only used the first 2. Accuracy compares predicted outcome with actual outcomes. If the set had 2 wins and 2 losses, and our model predicted 3 wins and one loss, the Accuracy would be 75%, presuming of course that the predicted wins were the actual wins and such. With Accuracy higher is better.

Our data contains a 50/50 split of wins and losses, so based on guesses one would expect an Accuracy of 50%.

We included Log Loss because it adds nuance, Accuracy does not care how confidently right or wrong the predict. Log Loss does, giving us a more complete picture. With Log Loss lower is better, and with 50/50 guesses one would expect a log loss of ln(2). Most of the time Accuracy and Log Loss were in agreement when ranking models, a exception being formula 5, which had the highest Accuracy but a worse Log Loss compared to the runner-up.

To see if the resulting Accuracy was statistically significant, i.e. not possible through random guesses, we added a binomial test.
