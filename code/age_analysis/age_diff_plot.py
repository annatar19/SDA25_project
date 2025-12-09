from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shutil


OUTPUT_DIR = "age_delta_mean_plots"


def refresh_output():
    p = Path(OUTPUT_DIR)
    if p.exists():
        shutil.rmtree(p)
    p.mkdir(parents=True, exist_ok=True)
    return p


def main():

    # TODO TEST OF BESTAAT
    df = pd.read_csv("age_diff_means.csv")
    refresh_output()

    for col in ["futures", "qual_chall", "singles", "total"]:
        sub = df[["year", col]].dropna()
        x = sub["year"].to_numpy(dtype=float)
        y = sub[col].to_numpy(dtype=float)

        plt.figure(figsize=(8, 6))
        plt.scatter(x, y)

        slope, intercept = np.polyfit(x, y, 1)
        x_hat = np.linspace(x.min(), x.max(), 200)
        y_hat = slope * x_hat + intercept
        plt.plot(x_hat, y_hat)
        plt.title(f"{col} per year")

        plt.xlabel("year")
        plt.ylabel(f"Average age difference for {col} over the years")
        plt.tight_layout()
        plt.grid(True)
        plt.savefig(f"{OUTPUT_DIR}/{col}.png")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
