import numpy as np
import pandas as pd
from scipy import stats
from pathlib import Path
import matplotlib.pyplot as plt

CSV_DIR = "csv"
PNG_DIR = "png"


def init_out_dir():
    p = Path(CSV_DIR)
    p.mkdir(parents=True, exist_ok=True)
    p = Path(PNG_DIR)
    p.mkdir(parents=True, exist_ok=True)


def main():
    path = Path(f"{CSV_DIR}/data.csv")
    if not path.is_file():
        print("data.csv Is missing, please run data_csv.py before running this script.")
        return 1
    init_out_dir()
    df = pd.read_csv(path)

    # keep only main tier
    main = df[df["tier"] == "main"].copy()

    # Compute mean and CI for winners. Duplicates are fine now, ages that win
    # but then lose are canceled out that way.
    groups = main.groupby(["year"])["winner_age"]
    # Creates an out dataframe with number of ages(not unique) per group, their
    # mean and std. reset_index Turns it into normal columns.
    winners = groups.agg(n="count", mean="mean", std="std").reset_index()

    # The CI is computed using the Student's t-distribution:
    # https://en.wikipedia.org/wiki/Confidence_interval
    # Assumed to be fine due to central limit theorem.
    winners["se"] = winners["std"] / np.sqrt(winners["n"])
    # Two-sided 95% t-critical value with n-1 degrees of freedom
    winners["tcrit"] = stats.t.ppf(0.975, df=winners["n"] - 1)
    winners["ci_lower"] = winners["mean"] - winners["tcrit"] * winners["se"]
    winners["ci_upper"] = winners["mean"] + winners["tcrit"] * winners["se"]

    # Those columns were for computing, they are not useful for our conclusion.
    winners = winners.drop(columns=["std", "se", "tcrit"]).sort_values(["year"])

    # Compute mean and CI for winners.
    groups = main.groupby(["year"])["loser_age"]
    losers = groups.agg(n="count", mean="mean", std="std").reset_index()

    losers["se"] = losers["std"] / np.sqrt(losers["n"])
    # Two-sided 95% t-critical value with n-1 degrees of freedom
    losers["tcrit"] = stats.t.ppf(0.975, df=losers["n"] - 1)
    losers["ci_lower"] = losers["mean"] - losers["tcrit"] * losers["se"]
    losers["ci_upper"] = losers["mean"] + losers["tcrit"] * losers["se"]

    # Those columns were for computing, they are not useful for our conclusion.
    losers = losers.drop(columns=["std", "se", "tcrit"]).sort_values(["year"])

    winners["cat"] = "winner"
    losers["cat"] = "loser"

    out = pd.concat([winners, losers], ignore_index=True)

    out.to_csv(f"{CSV_DIR}/winner_loser_age_mean.csv")
    fig, ax = plt.subplots(figsize=(12, 8))

    for category, group in out.groupby("cat"):
        group = group.sort_values("year")
        x = group["year"]
        y = group["mean"]

        ax.plot(x, y, label=f"{category} mean age")

        ax.fill_between(
            x,
            group["ci_lower"],
            group["ci_upper"],
            alpha=0.2,
            label=f"{category} 95% CI",
        )

    ax.legend()
    ax.grid(True)
    ax.set_title(f"Main tier: winner vs loser mean age per year (95% CI)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Age (Years)")
    fig.savefig(f"{PNG_DIR}/winner_loser_age_mean.png", bbox_inches="tight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
