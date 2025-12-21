import pandas as pd
import matplotlib.pyplot as plt


CSV_PATH = "match_length_bins_by_year.csv"
DATA_PATH = "../../data/tennis_atp_data/altered_data/archetype/"
PLOT_PATH = "../../graphs/archetype/"


def load_summary():
    df = pd.read_csv(DATA_PATH + CSV_PATH)
    df = df.sort_values("year")
    return df


def plot_match_length_thresholds(df):
    years = df["year"].to_numpy()
    mean = df["avg_minutes"].to_numpy()
    low = df["short_threshold"].to_numpy()
    high = df["long_threshold"].to_numpy()

    plt.figure(figsize=(9, 5))

    plt.plot(years, mean, label="Mean", linewidth=2)
    plt.plot(years, low, linestyle="--", label="Mean − SD")
    plt.plot(years, high, linestyle="--", label="Mean + SD")

    plt.xlabel("Year")
    plt.ylabel("Match duration (minutes)")
    plt.title("Match Length Thresholds by Year", fontsize=16, weight="bold")
    plt.legend()
    plt.grid(axis="y", linestyle="--", alpha=0.4)
    plt.tight_layout()

    print(f"Saving: {PLOT_PATH}match_length_thresholds.png")
    plt.savefig(PLOT_PATH + "match_length_thresholds.png", dpi=300)


def main():
    df = load_summary()
    plot_match_length_thresholds(df)


if __name__ == "__main__":
    main()
