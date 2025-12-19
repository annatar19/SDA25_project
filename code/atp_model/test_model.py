import pandas as pd
from scipy.stats import binomtest
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
    formulas.append(
        """
    result ~
        C(surface) +
        C(p1_handedness) + C(p2_handedness) +
        C(p1_archetype)  + C(p2_archetype)  +
        C(p1_favor) +
        I(p1_age - p2_age) +
        I(p1_ht  - p2_ht) +
        rel_ranking_points +
        I(p1_surface_winrate - p2_surface_winrate) +
        I(p1_streak - p2_streak)
    """
    )
    formulas.append(
        """
    result ~
        C(surface) +
        C(p1_handedness) + C(p2_handedness) +
        C(p1_archetype)  + C(p2_archetype)  +
        C(p1_favor) * p1_streak +
        I(p1_age - p2_age) +
        I(p1_ht  - p2_ht) +
        rel_ranking_points +
        I(p1_surface_winrate - p2_surface_winrate) +
        I(p1_streak - p2_streak)
    """
    )
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
    formulas.append(
        """
    result ~
        rel_ranking_points
    """
    )
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

    # Highest accuracy matched with the best age height formula.
    formulas.append(
        """result ~
        C(surface) +
        C(p1_handedness) + C(p2_handedness) +
        C(p1_archetype) + C(p2_archetype) +
        C(p1_favor) * p1_streak +
        bs(p1_age, df=6) + bs(p2_age, df=6) +
        bs(p1_ht, df=6) + bs(p2_ht, df=6) +
        rel_ranking_points +
        I(p1_surface_winrate - p2_surface_winrate) +
        I(p1_streak - p2_streak)"""
    )

    # Highest accuracy matched with the best age height formula + absolute
    # ranking points, no more relative. Slightly higher AUC
    formulas.append(
        """result ~
        C(surface) +
        C(p1_handedness) + C(p2_handedness) +
        C(p1_archetype) + C(p2_archetype) +
        C(p1_favor) * p1_streak +
        bs(p1_age, df=6) + bs(p2_age, df=6) +
        bs(p1_ht, df=6) + bs(p2_ht, df=6) +
        abs_ranking_points +
        I(p1_surface_winrate - p2_surface_winrate) +
        I(p1_streak - p2_streak)"""
    )

    return formulas


def test(train_df, test_df, formulas):
    rows = []
    for i, formula in enumerate(formulas):
        model = smf.logit(formula, data=train_df).fit()

        # How probable is our test data according to the model?
        p = model.predict(test_df)
        print(model.summary())

        y = test_df["result"].astype(int).values
        y_hat = (p >= 0.5).astype(int)

        # How likely would this accuracy be with guesses? Even amount of wins
        # and losses.
        k = int((y_hat == y).sum())
        pval_vs_50 = binomtest(k, len(y), p=0.5, alternative="greater").pvalue

        row = {
            "formula_no": i,
            "formula": formula,
            "accuracy_score": round(accuracy_score(y, y_hat) * 100, 2),
            "log_loss": log_loss(y, p),
            "brier_score_loss": brier_score_loss(y, p),
            "roc_auc_score": roc_auc_score(y, p),
            "pval_acc_gt_50": pval_vs_50,
        }
        print(f"accuracy: {row["accuracy_score"]}")
        print(f"logloss: {row["log_loss"]}")
        print(f"brier: {row["brier_score_loss"]}")
        print(f"auc: {row["roc_auc_score"]}")

        rows.append(row)
    return rows


def main():
    # df = pd.read_csv("atp_player_pairs_1991_2024.csv")
    df = pd.read_csv("../../data/tennis_atp_data/altered_data/filtered_data.csv")
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
    test_df = df.loc[is_test_year].copy()
    print(f"Test set length: {len(test_df)}")
    print("Test positive rate:", test_df["result"].mean())
    formulas = get_formulas()

    rows = test(train_df, test_df, formulas)
    # Otherwise the formula will display like it was defined in get_formulas(),
    # i.e. multiple lines.
    for row in rows:
        row["formula"] = re.sub(r"\s+", " ", row["formula"]).strip()
    results_df = pd.DataFrame(rows)

    results_df = results_df[
        [
            "formula_no",
            "formula",
            "accuracy_score",
            "pval_acc_gt_50",
            "log_loss",
            "brier_score_loss",
            "roc_auc_score",
        ]
    ]

    results_df.to_csv("model_results.csv", index=False)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
