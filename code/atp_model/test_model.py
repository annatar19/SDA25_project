import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
import shutil
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss


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
    # C is category. I More or less just creates a new column based on the
    # formula inside ().
    # formulas.append(
    #     """
    # result ~
    #     C(surface) +
    #     C(p1_handedness) + C(p2_handedness) +
    #     C(p1_archetype)  + C(p2_archetype)  +
    #     C(p1_favor) +
    #     I(p1_age - p2_age) +
    #     I(p1_ht  - p2_ht) +
    #     rel_ranking_points +
    #     I(p1_surface_winrate - p2_surface_winrate) +
    #     I(p1_streak - p2_streak)
    # """
    # )
    # formulas.append(
    #     """
    # result ~
    #     C(surface) +
    #     C(p1_handedness) + C(p2_handedness) +
    #     C(p1_archetype)  + C(p2_archetype)  +
    #     C(p1_favor) * p1_streak +
    #     I(p1_age - p2_age) +
    #     I(p1_ht  - p2_ht) +
    #     rel_ranking_points +
    #     I(p1_surface_winrate - p2_surface_winrate) +
    #     I(p1_streak - p2_streak)
    # """
    # )
    # formulas.append(
    #     """
    # result ~
    #     C(surface) +
    #     C(p1_handedness) + C(p2_handedness) +
    #     C(p1_archetype)  + C(p2_archetype)  +
    #     C(p1_favor) * p1_streak +
    #     I(p1_age - p2_age) +
    #     bs(p1_ht, df=5) +
    #     bs(p2_ht, df=5) +
    #     rel_ranking_points +
    #     I(p1_surface_winrate - p2_surface_winrate) +
    #     I(p1_streak - p2_streak)
    # """
    # )
    # formulas.append(
    #     """
    # result ~
    #     rel_ranking_points
    # """
    # )

    formulas.append(
        """
    result ~
        C(surface) +
        C(p1_handedness) + C(p2_handedness) +
        C(p1_archetype)  + C(p2_archetype)  +
        C(p1_favor) * p1_streak +
        I(p1_age - p2_age) +
        bs(p1_ht, df=5) +
        bs(p2_ht, df=5) +
        rel_ranking_points +
        I(p1_surface_winrate - p2_surface_winrate) +
        I(p1_streak - p2_streak)
    """
    )

    return formulas


def test(train_df, test_df, formulas):
    # rows = []
    for formula in formulas:
        model = smf.logit(formula, data=train_df).fit()

        # How probable is our test data according to the model?
        p_test = model.predict(test_df)
        print(model.summary())

        # break
        y_test = test_df["result"].astype(int).values
        y_hat = (p_test >= 0.5).astype(int)

        accuracy = accuracy_score(y_test, y_hat)
        accuracy = round(accuracy * 100, 2)
        print(f"accuracy: {accuracy}")
        # row = {"formula": formula, "tier": tier, "accuracy": accuracy}
        # rows.append(row)


def main():
    # df = pd.read_csv("atp_player_pairs_1991_2024.csv")
    df = pd.read_csv("filtered_data.csv")
    len_raw = len(df)
    print(f"Length raw input: {len_raw}")
    # Won't touch categories.
    df.dropna(inplace=True)
    len_non_na = len(df)
    print(
        f"dropna dropped {len_raw- len_non_na} rows, which is {((len_raw- len_non_na)/len_raw*100):.1f}%."
    )
    # So we can split test and train based on date.
    df["tourney_date"] = pd.to_datetime(
        df["tourney_date"], format="%Y-%m-%d", errors="coerce"
    )

    train_years = {year for year in range(1968, 2022)}
    test_years = {2022, 2023, 2024}
    is_test_year = df["tourney_date"].dt.year.isin(test_years)

    is_train_year = df["tourney_date"].dt.year.isin(train_years)

    train_df = df.loc[is_train_year].copy()
    # train_df = df.loc[~is_test_year].copy()
    test_df = df.loc[is_test_year].copy()
    formulas = get_formulas()

    # print(train_df)
    test(train_df, test_df, formulas)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
