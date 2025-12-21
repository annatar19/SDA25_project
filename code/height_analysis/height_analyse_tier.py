import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
from pathlib import Path

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

    # We are looking for the total mean per tier, so winners and losers should
    # be combined.
    winners = df[["year", "tier", "winner_id", "winner_ht"]].rename(
        columns={"winner_id": "id", "winner_ht": "ht"}
    )
    losers = df[["year", "tier", "loser_id", "loser_ht"]].rename(
        columns={"loser_id": "id", "loser_ht": "ht"}
    )
    heights = pd.concat([winners, losers], ignore_index=True)

    # Not dropping duplicates would cause winners to be overcounted, creating
    # a bias. We only care what heights exist per tier, not how they performed.
    # For this analysis at least.
    heights = heights.drop_duplicates(subset=["year", "tier", "id"])

    # Gets the heights into separate year-tier groups.
    groups = heights.groupby(["year", "tier"])["ht"]
    # Creates an out dataframe with number of heights per group, their mean and
    # std. reset_index Turns it into normal columns.
    out = groups.agg(n="count", mean="mean", std="std").reset_index()

    # The CI is computed using the Student's t-distribution:
    # https://en.wikipedia.org/wiki/Confidence_interval
    # Should be fine since height is normally distributed and n is large enough.
    # Standard error.
    out["se"] = out["std"] / np.sqrt(out["n"])
    # Two-sided 95% t-critical value with n-1 degrees of freedom
    out["tcrit"] = stats.t.ppf(0.975, df=out["n"] - 1)
    out["ci_lower"] = out["mean"] - out["tcrit"] * out["se"]
    out["ci_upper"] = out["mean"] + out["tcrit"] * out["se"]

    # Those columns were for computing, they are not useful for our conclusion.
    out = out.drop(columns=["std", "se", "tcrit"]).sort_values(["tier", "year"])

    out.to_csv(f"{CSV_DIR}/height_tier_stats.csv")

    fig, ax = plt.subplots(figsize=(12, 8))

    for tier, groups in out.groupby("tier"):
        x = groups["year"]
        y = groups["mean"]
        lower = groups["ci_lower"]
        upper = groups["ci_upper"]

        ax.plot(x, y, label=f"{tier} Mean height")
        ax.fill_between(x, lower, upper, alpha=0.2, label=f"{tier} 95% CI")

    ax.legend()
    ax.grid(True)
    ax.set_title("Mean height per tier per year with 95% CI")
    ax.set_xlabel("Year")
    ax.set_ylabel("Height (cm)")

    fig.savefig(f"{PNG_DIR}/height_stats_tier.png", bbox_inches="tight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
