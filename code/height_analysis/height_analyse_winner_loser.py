import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

CSV_DIR = "csv"
PNG_DIR = "png"


def init_out_dir():
    Path(CSV_DIR).mkdir(parents=True, exist_ok=True)
    Path(PNG_DIR).mkdir(parents=True, exist_ok=True)


def main():
    path = Path(f"{CSV_DIR}/data.csv")
    if not path.is_file():
        print("data.csv Is missing, please run data_csv.py before running this script.")
        return 1
    init_out_dir()
    df = pd.read_csv(path)

    # keep only main tier
    main = df[df["tier"] == "main"].copy()

    # It shouldn't matter but it is nicer to have perfectly consistent plots.
    rng = np.random.default_rng(0)
    rows = []
    # Amount of bootstrap samples. We have to use bootstrapping since heights
    # of the same players across different matches are not independent of
    # course.
    N = 2000
    # Since we use 95% CI.
    alpha = 0.05

    for year, group in main.groupby("year"):
        winner_ht = group["winner_ht"].to_numpy()
        loser_ht = group["loser_ht"].to_numpy()
        # Amount of matches
        n = len(group)

        # This is the actual difference in mean for the current year. The cast
        # is so it is not some numpy datatype.
        diff_mean = float(winner_ht.mean() - loser_ht.mean())

        boots = np.empty(N)
        idx = np.arange(n)
        for b in range(N):
            # Sample with replacement.
            s = rng.choice(idx, size=n, replace=True)
            # Compute the bootstrapped difference in mean.
            boots[b] = winner_ht[s].mean() - loser_ht[s].mean()

        # The lower 2.5%
        ci_lower = float(np.quantile(boots, alpha / 2))
        # The upper 97.5%
        ci_upper = float(np.quantile(boots, 1 - alpha / 2))

        rows.append(
            {
                "year": int(year),
                "n": n,
                "diff_mean": diff_mean,
                "ci_lower": ci_lower,
                "ci_upper": ci_upper,
            }
        )

    out = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)

    out.to_csv(f"{CSV_DIR}/winner_loser_ht_mean.csv", index=False)
    fig, ax = plt.subplots(figsize=(12, 8))

    x = out["year"]
    y = out["diff_mean"]

    ax.plot(x, y, color="green", label=f"Difference in mean height.")

    ax.fill_between(
        x,
        out["ci_lower"],
        out["ci_upper"],
        color="green",
        alpha=0.2,
        label=f"95% CI",
    )

    ax.axhline(0, linewidth=1, color="black")
    ax.legend()
    ax.grid(True)
    ax.set_title(f"Main tier: winner vs loser mean height difference per year (95% CI)")
    ax.set_xlabel("Year")
    ax.set_ylabel("Difference mean height (cm)")
    fig.savefig(f"{PNG_DIR}/winner_loser_ht_mean.png", bbox_inches="tight")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
