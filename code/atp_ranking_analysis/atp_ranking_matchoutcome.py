# correlational analysis of the ranking of two players during a match, and the match outcome
# There are two variables influencing match outcome winner_rank_points and loser_rank_points (nominal)
# one outcome variable: winning type, categorical

import pandas as pd
import numpy as np

from sklearn.datasets import make_classification
from matplotlib import pyplot as plt
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

from scipy import stats

USE_COLS = ["tourney_id", "tourney_name", "match_num", 
             "winner_id", "winner_rank", "winner_rank_points", 
             "loser_id", "loser_rank", "loser_rank_points"]

RANDOM_SEED = 2


def read_atp(filename):
    """
    simple script for single datafile, for testing purposes, to adjusted for the entire dataset, or subset by years
    """
    
    df = pd.read_csv(filename, usecols=USE_COLS)

    return df

tennis_df = read_atp("SDA25_project/data/tennis_atp_data/unaltered_data/atp_matches_2000.csv")

def log_reg(df, x_col_name, y_col_name):
    plt.scatter(df[x_col_name], df[y_col_name])
    plt.show()

    x_val = df[[x_col_name]]
    y_val = df[y_col_name]

    train_x, test_x, train_y, test_y = train_test_split(x_val, y_val, random_state = 42)

    log_reg_high_rank_wins = LogisticRegression()
    log_reg_high_rank_wins.fit(train_x, train_y)

    print(log_reg_high_rank_wins.coef_)
    print(log_reg_high_rank_wins.intercept_)

    pred_y = log_reg_high_rank_wins.predict(test_x)
    print(confusion_matrix(test_y, pred_y))

# EXPERIMENT 1
def get_dif_data(df):
    df_filtered = df[["winner_rank_points", "loser_rank_points"]]
    df_filtered["dif_score"] = (df_filtered["winner_rank_points"] - df_filtered["loser_rank_points"]).abs()
    df_filtered["higher_rank_win"] = (df_filtered["winner_rank_points"] > df_filtered["loser_rank_points"]).astype(int) # hoe omgaan met hetzelfde aantal punter
    df_filtered = df_filtered.dropna()

    log_reg(df_filtered, "dif_score", "higher_rank_win")
    
    return df_filtered

def experiment1(tennis_df):
    """
    First experiment: logistic regression for the p(high_rank_score_wins | absolute_difference_score)
    """
    df = get_dif_data(tennis_df)
    print(df.head())

    plt.scatter(df["dif_score"], df["higher_rank_win"])
    plt.show()

    x_val = df[["dif_score"]]
    y_val = df["higher_rank_win"]

    train_x, test_x, train_y, test_y = train_test_split(x_val, y_val, random_state = 42)

    log_reg_high_rank_wins = LogisticRegression()
    log_reg_high_rank_wins.fit(train_x, train_y)

    print(log_reg_high_rank_wins.coef_)
    print(log_reg_high_rank_wins.intercept_)

    pred_y = log_reg_high_rank_wins.predict(test_x)
    print(confusion_matrix(test_y, pred_y))

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

def experiment2(tennis_df):
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

    log_reg(df, "dif_score", "playerA_win")

# EXPERIMENT 3
def experiment3(tennis_df):
    """
    Third experiment. Now instead of using absolute difference scores between playerA and playerB, the relative difference is used: (pA_score - pB_score) / pA_score.
    Differences between very high ranking players now correlate with lower difference scores than differences between low ranking.
    Differnces between high and low ranking result in very high difference scores.

    Some big outliers presented themselves, they are taken out. Outliers selection was based on z-scores > 3
    """
    df = tennis_df[["winner_rank_points", "loser_rank_points"]].dropna()
    
    df = add_shuffled_columns(df, "winner_rank_points", "loser_rank_points", 
                              "playerA_rank_points", "playerB_rank_points", seed=RANDOM_SEED)
    

    df["rel_dif_score"] = (df["playerA_rank_points"] - df["playerB_rank_points"]) / df["playerA_rank_points"]
    df["playerA_win"] = (df["playerA_rank_points"] == df["winner_rank_points"]).astype(int)

    # remove outliers
    df = df[np.abs(stats.zscore(df["rel_dif_score"])) < 3]
    
    log_reg(df, "rel_dif_score", "playerA_win")

experiment3(tennis_df)