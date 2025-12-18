SDA25 project repository for group 3

## About surface_analyis

The folder containts the following folders

- `data_loader/`: scripts for loading RAW data and preprocessing for use in winrates analysis
- `surface_acerates_analysis.py`: used to analyze acerates differences in surfaces to see whether it is worth investigating more
- `surface_winrates_analysis.py`: used to test the significance of winrates per surface for each player

## Usage of load_data.py and make_winrate_data.py in data_loader folder

#### load_data.py:

- `input`: all ATP singles csv files in `../../../data/tennis_atp_data/unaltered_data`
- `output`: a single DataFrame containing all csv files from a range of years defined by the parameter regex_pattern

Can change the following params:
path_pattern, no need for change it is the default path to csv files
regex_pattern, defines which year range of csvs to use
usecols, defines which columns to keep in output

#### make_winrate_data.py:

- `input`: DataFrame from `load_data.py`
- `output`: preprocessed csv with added surface_winrate for each player and result (player 1 wins) needed for logistic regression model in `surface_winrates_analysis.py`

`Core process`:
1. Sorts code chronologically, making sure matches are processed in time order, for correct calculation of surface winrate
2. Uses `Tenisser` class to track wins/losses per surface for each player. Only for the surfaces Grass, Hard and Clay. As carpet is not played on anymore and thus not of use for predicting modern matches
3. Uses laplace smoothing to avoid extreme values when players have very few matches (newcomers)
4. Matches recorded in both perspectives (loser and winner). So each match is represented twice, allowing for logistic regression as we now have 2 classes player1_won = 1 or 0
5. Update winrates and continue

## Usage of surface_acerates_analysis.py and surface_winrates_analysis.py in main folder

#### surface_winrates_analysis.py:

- `input`: preprocessed CSV from `make_winrate_data.py` (`../../data/tennis_atp_data/altered_data/surface_winrate_dataset.csv`)
- `output`: Console print of logistic regression model summary and corresponding ROC AUC and Accuracy. Might add a file output to this

`Core process`:
1. Load `surface_winrate_dataset.csv` and ability to adjust `    return data[data['rank_diff'].abs() <= 50]` to check for either closes matches that is a rank difference of 50. or set it to infinite to test without filter. Allows for focusing more on effect of surface winrate
2. Split data chronologically into training (first 80% of data) and test sets (last 20%) to preserve the time series. As training on future years to then accidentaly both test on past and future years makes no sense.
3. fit logistic regression per surface, since surfaces do differ it would be nice to see whether we see it back in the metrics.
- Rank diff model only
- Winrate diff model only
- Rank and Winrate diff model
3 model types to thoroughly test
4. Evaluates each model on the test set using:
Accuracy, ROC AUC and summaries of regression

#### surface_acerates_analysis.py:

- `input`: 
- `output`:

`Core process`:
