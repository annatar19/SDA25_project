import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
from pathlib import Path
import statsmodels.formula.api as smf
from sklearn.model_selection import train_test_split
import shutil
from sklearn.metrics import accuracy_score, roc_auc_score, log_loss, brier_score_loss


def main():
    df = pd.read_csv("atp_player_pairs_1991_2024.csv")
    initial_len = len(df)
    print(f"Initial entry count: {initial_len}")
    df.dropna(subset=["p1_ht", "p2_ht", "p1_age", "p2_age"], inplace=True)
    drop_len = len(df)
    minimum_ht = 160
    df = df[(df["p1_ht"] >= minimum_ht) & (df["p2_ht"] >= minimum_ht)]
    ht_len = len(df)
    print(f"Filtering for heights removed: {drop_len - ht_len} entries.")
    minimum_age = 16
    maximum_age = 40
    df = df[
        (df["p1_age"].between(minimum_age, maximum_age))
        & (df["p2_age"].between(minimum_age, maximum_age))
    ]
    age_len = len(df)
    print(f"Filtering for ages removed: {ht_len- age_len} entries.")

    df["rel_ranking_points"] = df["rel_ranking_points"].fillna(0)
    df["p1_favor"] = df["p1_favor"].fillna("even")

    df.to_csv("filtered_data.csv")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
