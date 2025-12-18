import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import statsmodels.api as sm

from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, accuracy_score, roc_auc_score

from collections import defaultdict

RANDOM_SEED = 1

EXPERIMENT_NO = [1, 2, 3]
PLOT_DATA = True

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

# Experiment 1 / 2
# This experiment will analyse any direct correlation between winning streak with either winning or losing a game.
# It is expected that a high win streak will correlate to a higher probability of winning.

def experiment1(df, plot=True):
    winner_streaks = df["winner_streak"]
    loser_streaks = df["loser_streak"]
    win_streaks = pd.concat([winner_streaks, loser_streaks])

    outcomes = np.concatenate((np.ones(len(winner_streaks)), np.zeros(len(loser_streaks))))

    df = pd.DataFrame.from_dict({"win_streak": win_streaks,
                                 "outcome": outcomes})
    
    log_reg(df, "win_streak", "outcome", plot=plot, exp_no = 1)

# Experiment 2
# For the second experiment I am curious about the probability of winning a match, given that you are on a certain win streak.
# For this I will calculate win-coefficient per win streak. This will give a nice plot hopefully, showing increased odds for higher streaks.

def experiment2_1(df):
    # count all the streaks and how they translate to wins/losses
    wins_on_streak = defaultdict(int)
    loss_on_streak = defaultdict(int)

    for _, row in df.iterrows():
        wins_on_streak[str(row["winner_streak"])] += 1
        loss_on_streak[str(row["loser_streak"])] += 1
    
    # calculate coefficients per streak
    max_streak = max(pd.concat([df["winner_streak"], df["loser_streak"]]))
    streaks = np.arange(max_streak)
    win_coef = []
    for streak in streaks:
        win_coef.append(wins_on_streak[str(streak)] / (wins_on_streak[str(streak)] + loss_on_streak[str(streak)]))
    
    plt.plot(streaks, win_coef)
    plt.title("Win Rate per Win Streak")
    plt.xlabel("Win Streak")
    plt.ylabel("Win Rate")
    plt.show()

def experiment2_2(df):
    # win/loss ratio, laplace smoothed
    # count all the streaks and how they translate to wins/losses
    wins_on_streak = defaultdict(int)
    loss_on_streak = defaultdict(int)

    for _, row in df.iterrows():
        wins_on_streak[str(row["winner_streak"])] += 1
        loss_on_streak[str(row["loser_streak"])] += 1
    
    # calculate coefficients per streak
    max_streak = max(pd.concat([df["winner_streak"], df["loser_streak"]]))
    streaks = np.arange(max_streak)
    win_coef = []
    eps = 1
    for streak in streaks:
        win_coef.append(wins_on_streak[str(streak)] / (eps + loss_on_streak[str(streak)]))
    
    plt.plot(streaks, win_coef)
    plt.title("Win/Loss ratio per Win streak")
    plt.xlabel("Win streak")
    plt.ylabel("W/L ratio")
    plt.show()


    pass

# Experiment 3
# conditioning for skill level, using bins on the ranking_points
# No ranking point data is available until 1990 (ranking points is 0 for both winner and loser), 0 ranking points are dropped.
# ranking will be done based on differences in skill level. From previous experiments it was shown that relative skill is good predictor.
# relative skill will be calculated (playerA - playerB) / PlayerA
# 5 bins total
def experiment3_clean_and_bin(df):
    # drop rank points = 0
    mask = (df["winner_rank_points"] == 0) | (df["loser_rank_points"] == 0)
    df_clean = df[~mask].reset_index(drop=True)
    df_clean = add_shuffled_columns(df_clean, "winner_rank_points", "loser_rank_points",
                                    "playerA_rank_points", "playerB_rank_points", seed=RANDOM_SEED)

    # create bin players
    bins = [-np.inf, -0.5, -0.2, -0.05, 0.05, 0.2, 0.5, np.inf]
    labels = ["heavy_underdog", "moderate_underdog", "slight_underdog", "even",
              "slight_favorite", "moderate_favorite", "heavy_favorite"]

    df_clean["rel_diff"] = (df_clean["playerA_rank_points"] - df_clean["playerB_rank_points"]) / df_clean["playerA_rank_points"]
    df_clean["skill_bin"] = pd.cut(df_clean["rel_diff"], bins=bins, labels=labels)
    df_clean["playerA_win"] = (df_clean["playerA_rank_points"] == df_clean["winner_rank_points"]).astype(int)
    df_clean['playerA_streak'] = np.where(df_clean['playerA_rank_points'] == df_clean['winner_rank_points'],
                                    df_clean['winner_streak'], df_clean['loser_streak'])

    return df_clean

def experiment3_1():
    df = pd.read_csv("./code/atp_win_streak_analysis/experiment3_data.csv")

    # List of skill bins
    skill_bins = ["heavy_underdog", "moderate_underdog", "slight_underdog", "even",
                  "slight_favorite", "moderate_favorite", "heavy_favorite"]

    # Dictionary to store results
    models = {}

    # Logistic regression per skill bin
    for bin_name in skill_bins:
        bin_data = df[df['skill_bin'] == bin_name]
        if len(bin_data) < 10:  # Skip very small bins
            continue
        X = sm.add_constant(bin_data['playerA_streak'])  # Add intercept
        y = bin_data['playerA_win']
        model = sm.Logit(y, X).fit(disp=0)
        models[bin_name] = model
    
    return models, df

def plot_experiment3_1(df, models):
    skill_bins = ["heavy_underdog", "moderate_underdog", "slight_underdog", "even",
                "slight_favorite", "moderate_favorite", "heavy_favorite"]

    # Prepare plot
    plt.figure(figsize=(10, 6))

    streak_range = range(int(df['playerA_streak'].min()), int(df['playerA_streak'].max()) + 1)

    for bin_name, model in models.items():
        X_pred = sm.add_constant(streak_range)
        y_pred = model.predict(X_pred)
        plt.plot(streak_range, y_pred, label=bin_name)

    plt.xlabel("PlayerA Win Streak")
    plt.ylabel("Probability of Winning Next Match")
    plt.title("Effect of Win Streak by Skill Bin")
    plt.legend()
    plt.grid(True)
    plt.show()

def print_experiment3_results(models):
    pass

def experiment3_2(plot=True):
    df = pd.read_csv("./code/atp_win_streak_analysis/experiment3_data.csv")
    skill_bins = ["heavy_underdog", "moderate_underdog", "slight_underdog", "even",
                "slight_favorite", "moderate_favorite", "heavy_favorite"]
    
    for skill_bin in skill_bins:
        bin_data = df[df['skill_bin'] == skill_bin]
        print(f"----------------------\n{skill_bin}\n----------------------\n")
        log_reg(bin_data, "playerA_streak", "playerA_win", plot=plot, exp_no = {skill_bin})

def main():
    tennis_df = pd.read_csv("./code/atp_win_streak_analysis/matches_with_win_streaks.csv")

    if len(EXPERIMENT_NO) == 0 or len(EXPERIMENT_NO) > 3:
        raise Exception("Invalid EXPERIMENT_NO length")

    for exp_no in EXPERIMENT_NO:
        if not isinstance(exp_no, int) or exp_no < 0 or exp_no > 3:
            raise Exception("Invalid experiment number. Check EXPERIMENT_NO global")
        
        if exp_no == 1:
            experiment1(tennis_df, plot=PLOT_DATA)
        if exp_no == 2:
            if PLOT_DATA:
                experiment2_1(tennis_df)
                experiment2_2(tennis_df)
        if exp_no == 3:
            models, bin_df = experiment3_1()
            if PLOT_DATA:
                plot_experiment3_1(bin_df, models)
            experiment3_2(plot=PLOT_DATA)

if __name__=="__main__":
    main()