# This file runs logistic regression on 3 different formulas. rankdiff only, winrate
# diff only and both
# INPUT: csv from make_winrate_data
# OUTPUT logit summaries and auc/acc
import pandas as pd
import statsmodels.formula.api as smf
from sklearn.metrics import accuracy_score, roc_auc_score


# Can limit rank_diff to close matches or simply all matches, using it to
# check the effect of winrate in matches where rank_diff matters less
# since logistic regression will always take the best factor, which in
# most cases will be rank
def load_data_wr(path):
    data = pd.read_csv(path)
    return data[(data['p2_rank'] - data['p1_rank']).abs() <= 50]


# 80/20 chronologically
def split_train_test(data):
    train_data = data[data['tourney_date'] < data['tourney_date'].quantile(0.8)]
    test_data = data[data['tourney_date'] >= data['tourney_date'].quantile(0.8)]
    return train_data, test_data


def fitlogit(formule, train_data, test_data, model_name):
    model = smf.logit(formule, train_data).fit(disp=0)
    print(f"\n{model_name}")
    # print(model.summary())

    y_test = test_data['player1_won']
    y_pred_prob = model.predict(test_data)
    y_pred_class = (y_pred_prob >= 0.5).astype(int)

    print("Accuracy:", accuracy_score(y_test, y_pred_class))
    print("ROC AUC:", roc_auc_score(y_test, y_pred_prob))
    return model


# Printing results per surface to see it differences clearer
def main():
    data = load_data_wr("../../data/tennis_atp_data/"
                        "altered_data/surface_analysis/surface_winrate_1991_2024.csv")

    surfaces = ['Hard', 'Clay', 'Grass']
    for s in surfaces:
        data_s = data[data['surface'] == s]
        train_data, test_data = split_train_test(data_s)

        formula_rank = "player1_won ~ I(p2_rank - p1_rank)"
        fitlogit(formula_rank, train_data, test_data, f"Rank difference only (surface={s})")

        formula_wr = "player1_won ~ I(p1_surface_winrate - p2_surface_winrate)"
        fitlogit(formula_wr, train_data, test_data,
                 f"Surface winrate difference only (surface={s})")

        formula = "player1_won ~ I(p2_rank - p1_rank) + I(p1_surface_winrate - p2_surface_winrate)"
        fitlogit(formula, train_data, test_data, f"Rank and winrate differences (surface={s})")


if __name__ == "__main__":
    main()
