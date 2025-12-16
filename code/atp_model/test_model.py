import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
import shutil
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss


TEST_YEARS = [2022, 2023, 2024]


def get_bounds(training_data, testing_data):
    min_ht = min(
        training_data["all"][["player_ht", "opponent_ht"]].min().min(),
        testing_data["all"][["player_ht", "opponent_ht"]].min().min(),
    )
    max_ht = max(
        training_data["all"][["player_ht", "opponent_ht"]].max().max(),
        testing_data["all"][["player_ht", "opponent_ht"]].max().max(),
    )
    return min_ht, max_ht


def get_formulas():
    """
    This function serves to separate the formulas from the rest of the code
    """
    formulas = []
    formulas.append(
        f"win ~ "
        f"bs(player_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht}) + "
        f"bs(opponent_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
    )
    formulas.append(f"win ~ " f"bs(player_ht - opponent_ht, df=5)")
    formulas.append("win ~ player_ht - opponent_ht")  # plain linear diff
    formulas.append("win ~ I(player_ht - opponent_ht) + I(player_ht + opponent_ht)")
    formulas.append("win ~ I(player_ht - opponent_ht) + I((player_ht + opponent_ht)/2)")
    formulas.append("win ~ bs(player_ht - opponent_ht, df=5)")
    formulas.append("win ~ bs((player_ht + opponent_ht)/2, df=5)")
    formulas.append(
        "win ~ bs(player_ht - opponent_ht, df=5) + bs((player_ht + opponent_ht)/2, df=5)"
    )
    formulas.append(
        f"win ~ bs(player_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
        f" + bs(opponent_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
        f" + I(player_ht - opponent_ht)"
    )

    formulas.append(
        f"win ~ bs(player_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
        f" * bs(opponent_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
    )  # includes main effects + interaction

    formulas.append(
        f"win ~ bs(player_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
        f" + bs(opponent_ht, df=5, lower_bound={min_ht}, upper_bound={max_ht})"
        f" + bs(player_ht - opponent_ht, df=5)"
    )
    return formulas


def test(formulas):
    rows = []
    for formula in formulas:
        for tier in training_data.keys():
            train_df = training_data[tier]
            test_df = testing_data[tier]
            model = smf.logit(formula, data=train_df).fit()

            # How probable is our test data according to the model?
            p_test = model.predict(test_df)
            print(model.summary())
            print(model.pvalues.iloc[1])
            print(model.pvalues.iloc[2])

            # break
            y_test = test_df["win"].astype(int).values
            y_hat = (p_test >= 0.5).astype(int)

            accuracy = accuracy_score(y_test, y_hat)
            # accuracy = round(accuracy * 100, 2)
            row = {"formula": formula, "tier": tier, "accuracy": accuracy}
            rows.append(row)


def main():

    df = pd.read_csv("atp_player_pairs_1991_2024.csv")
    len_raw = len(df)
    print(f"Length raw input: {len_raw}")
    df.dropna(inplace=True)
    len_non_na = len(df)
    print(
        f"dropna dropped {len_raw- len_non_na} rows, which is {((len_raw- len_non_na)/len_raw*100):.1f}%."
    )

    # min_ht, max_ht = get_bounds(training_data, testing_data)
    # formulas = []

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
