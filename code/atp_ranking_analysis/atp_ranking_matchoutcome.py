# correlational analysis of the ranking of two players during a match, and the match outcome
# There are two variables influencing match outcome winner_rank_points and loser_rank_points (nominal)
# one outcome variable: winning type, categorical

import pandas as pd
import numpy as np
import re
import glob

from sklearn.datasets import make_classification
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score

from scipy import stats

# list of the experiments you want to run. Valid experiment numbers are 1, 2 and 3
EXPERIMENT_NO = [1, 2, 3]
PLOT_DATA = True

USE_COLS = ["tourney_id", "tourney_name", "match_num", 
             "winner_id", "winner_rank", "winner_rank_points", 
             "loser_id", "loser_rank", "loser_rank_points"]

RANDOM_SEED = 8

def load_tennis_data(
    path_pattern="../data/tennis_atp_data/unaltered_data/*",
    regex_pattern=r"/atp_matches_(199[1-9]|200\d|201\d|202\d|2025)\.csv",
    usecols=None,
):
    """
    path_pattern - str
        Path to the csv's
    regex_pattern - str
        Regex pattern that filters to 'atp_matches_XXXX.csv' files to load
    usecols - list
        columns to load from each csv. If empty, all cols will be loaded
    """

    ATP_PATH = path_pattern

    # Matches atp_matches_XXXX.csv
    match_fn_pattern = re.compile(regex_pattern)

    # Will make a list of strings like:
    # '../data/tennis_atp/atp_matches_qual_chall_1996.csv'
    atp_csv_fns = glob.glob(ATP_PATH)

    csvs = []
    for fn in atp_csv_fns:
        match = re.search(match_fn_pattern, fn)
        if match:
            # https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html
            # My ide gives an error but it works fine.
            df = pd.read_csv(fn, usecols=usecols)
            csvs.append(df)

    if not csvs:
        raise ValueError("no matching csv files, make sure the regex or path pattern is correct")

    # All the .csv into 1, the loaded columns that is.
    return pd.concat(csvs, ignore_index=True)

def log_reg(df, x_col_name, y_col_name, plot=True, exp_no = None):
    if plot:
        plt.scatter(df[x_col_name], df[y_col_name])
        plt.show()

    x_val = df[[x_col_name]]
    y_val = df[y_col_name]

    train_x, test_x, train_y, test_y = train_test_split(x_val, y_val, random_state = RANDOM_SEED)

    log_reg_high_rank_wins = LogisticRegression()
    log_reg_high_rank_wins.fit(train_x, train_y)

    if exp_no == None:
        exp_no = ""

    print(f"______________________________________\nResults experiment {exp_no}\n______________________________________\n")

    print(f"Beta-coef: {log_reg_high_rank_wins.coef_}")
    print(f"Intercept: {log_reg_high_rank_wins.intercept_}")

    pred_y = log_reg_high_rank_wins.predict(test_x)
    pred_prob = log_reg_high_rank_wins.predict_proba(test_x)[:, 1]

    print(f"\nConfusion mat:\n{confusion_matrix(test_y, pred_y)}\n")

    acc = accuracy_score(test_y, pred_y)
    print(f"Accuracy: {acc:.3f}")

    auc = roc_auc_score(test_y, pred_prob)
    print(f"ROC-AUC: {auc:.3f}")

# EXPERIMENT 1
def get_dif_data(df):
    df_filtered = df[["winner_rank_points", "loser_rank_points"]]
    df_filtered["dif_score"] = (df_filtered["winner_rank_points"] - df_filtered["loser_rank_points"]).abs()
    df_filtered["higher_rank_win"] = (df_filtered["winner_rank_points"] > df_filtered["loser_rank_points"]).astype(int) # hoe omgaan met hetzelfde aantal punter
    df_filtered = df_filtered.dropna()
    
    return df_filtered

def experiment1(tennis_df, plot=True):
    """
    First experiment: logistic regression for the p(high_rank_score_wins | absolute_difference_score)
    """
    df = get_dif_data(tennis_df)
    
    log_reg(df, "dif_score", "higher_rank_win", plot=plot, exp_no=1)

# EXPERIMENT 2
def add_shuffled_columns(df, col1, col2, new1, new2, seed=None):
    if seed is not None:
        np.random.seed(seed)

    swap_mask = np.random.rand(len(df)) < 0.5  # True = swap

    df = df.copy()

    df[new1] = df[col1]
    df[new2] = df[col2]

    df.loc[swap_mask, new1] = df.loc[swap_mask, col2]
    df.loc[swap_mask, new2] = df.loc[swap_mask, col1]

    return df

def experiment2(tennis_df, plot=True):
    """
    Second experiment.
    In this one instead of looking at the probability of the player with the highest score winning, 
    I randomly shuffled the winner and loser scores and see if there is a correlation between playerA winning and the difference score: playerA_rank_points - playerB_rank_points.
    """
    df = tennis_df[["winner_rank_points", "loser_rank_points"]].dropna()
    
    df = add_shuffled_columns(df, "winner_rank_points", "loser_rank_points", 
                              "playerA_rank_points", "playerB_rank_points", seed=RANDOM_SEED)
    
    df["dif_score"] = df["playerA_rank_points"] - df["playerB_rank_points"]
    df["playerA_win"] = (df["playerA_rank_points"] == df["winner_rank_points"]).astype(int)

    log_reg(df, "dif_score", "playerA_win", plot=plot, exp_no=2)

# EXPERIMENT 3
def experiment3(tennis_df, plot=True):
    """
    Third experiment. Now instead of using absolute difference scores between playerA and playerB, the relative difference is used: (pA_score - pB_score) / pA_score.
    Differences between very high ranking players now correlate with lower difference scores than differences between low ranking.
    Differnces between high and low ranking result in very high difference scores.

    Some big outliers presented themselves, they are taken out. Outliers selection was based on z-scores > 3
    """
    df = tennis_df[["winner_rank_points", "loser_rank_points"]].dropna()
    
    df = add_shuffled_columns(df, "winner_rank_points", "loser_rank_points", 
                              "playerA_rank_points", "playerB_rank_points", seed=RANDOM_SEED)
    
    # remove 0 ranking_point values
    df = df[df["playerA_rank_points"] != 0]
    
    df["rel_dif_score"] = (df["playerA_rank_points"] - df["playerB_rank_points"]) / df["playerA_rank_points"]
    df["playerA_win"] = (df["playerA_rank_points"] == df["winner_rank_points"]).astype(int)

    # remove outliers
    # df = df[np.abs(stats.zscore(df["rel_dif_score"])) < 3]
    
    log_reg(df, "rel_dif_score", "playerA_win", plot=plot, exp_no=3)


def main():
    tennis_df = load_tennis_data(path_pattern="./data/tennis_atp_data/unaltered_data/*", usecols = USE_COLS).dropna()

    if len(EXPERIMENT_NO) == 0 or len(EXPERIMENT_NO) > 3:
        raise Exception("Invalid EXPERIMENT_NO length")

    for exp_no in EXPERIMENT_NO:
        if not isinstance(exp_no, int) or exp_no < 0 or exp_no > 3:
            raise Exception("Invalid experiment number. Check EXPERIMENT_NO global")
        
        if exp_no == 1:
            experiment1(tennis_df, plot=PLOT_DATA)
        if exp_no == 2:
            experiment2(tennis_df, plot=PLOT_DATA)
        if exp_no == 3:
            experiment3(tennis_df, plot=PLOT_DATA)

if __name__=="__main__":
    main()